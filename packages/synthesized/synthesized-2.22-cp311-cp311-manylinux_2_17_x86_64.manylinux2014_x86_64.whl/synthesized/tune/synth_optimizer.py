import logging
from typing import Any, Callable, Dict, List, Optional, Union

import pandas as pd
from ax.modelbridge.generation_strategy import GenerationStep, GenerationStrategy
from ax.modelbridge.registry import Models
from ax.plot.contour import interact_contour
from ax.plot.slice import plot_slice
from ax.service.ax_client import AxClient
from ax.service.utils.best_point import (
    get_best_parameters_from_model_predictions,
    get_best_raw_objective_point,
)
from ax.utils.notebook.plotting import init_notebook_plotting, render
from ray import tune
from ray.tune.search.ax import AxSearch

from synthesized import EventSynthesizer, HighDimSynthesizer, TimeSeriesSynthesizer
from synthesized.config import DeepStateConfig, HighDimConfig

SynthesizerType = Union[HighDimSynthesizer, TimeSeriesSynthesizer, EventSynthesizer]

logger = logging.getLogger(__name__)


class SynthOptimizer:
    """A class for synthesizer optimization.

    Args:
        orig_df: The original dataframe used to train the synthesizer.
        build_and_train_function (Callable) returns SynthesizerType: A function that builds and
            trains a synthetic model based on the given parameterization and the original dataframe.
            Must have signature (parameterization, orig_df)
        loss_name (Optional[str]): The name of the loss metric to use in the optimization. Defaults
            to None. If None then the "mean_loss" of the model is used.
        custom_loss_function (Optional[Callable]): A custom loss function.
            Defaults to None. If None is suppled then the "mean_loss" of the model is used.
        max_parallelism (int): The maximum number of parallel trials. Defaults to 4.
        num_cpus (int): The number of CPUs to use for optimization. Defaults to 4.
        **model_kwargs: Keyword arguments to pass to pass on instantiation of the model.
    """

    def __init__(
        self,
        orig_df,
        parameters: List[Dict[str, Any]],
        synthetic_model: str = "HighDimSynthesizer",
        build_and_train_function: Optional[
            Callable[[Dict[str, Any], pd.DataFrame], SynthesizerType]
        ] = None,
        loss_name: Optional[str] = None,
        custom_loss_function: Optional[Callable] = None,
        max_parallelism: int = 4,
        num_cpus: int = 4,
        **model_kwargs,
    ):
        self.synthetic_model = synthetic_model
        self.model_kwargs = model_kwargs
        build_and_train_function = build_and_train_function or self.default_build_and_train_function
        self.parameters = parameters

        self.hyperparam_loss: Callable = custom_loss_function or self.default_loss_function

        self.loss_name = loss_name if loss_name else "mean_loss"
        self.axc = self.create_parameter_client(
            loss_name=self.loss_name, max_parallelism=max_parallelism
        )

        self.train_evaluate = self.create_train_evaluate_function(
            build_and_train_function, self.hyperparam_loss, orig_df
        )

        self.num_cpus = num_cpus

    @staticmethod
    def default_loss_function(synth: SynthesizerType, orig_df: pd.DataFrame) -> Dict[str, Any]:
        """
        The default loss function for the optimizer. Uses the `total_loss` from the engine.

        Args:
            synth (SynthesizerType): The synthesizer to evaluate.
            orig_df (pd.DataFrame): The original dataframe used to train the synthesizer.

        Returns:
            Dict: A dictionary containing the loss and the global step.

        """

        if isinstance(synth, HighDimSynthesizer):
            loss = synth._engine.history.history["total_loss"][  # pylint: disable=protected-access
                -1
            ]
            global_step = synth.optimizer.iterations.numpy().item()

        else:
            loss = synth._engine.history.history["total_loss"][  # pylint: disable=protected-access
                -1
            ].mean()

            global_step = (
                synth._engine.optimizer.iterations.numpy().item()  # pylint: disable=protected-access
            )

        return dict(
            mean_loss=loss,
            global_step=global_step,
        )

    def default_build_and_train_function(
        self, parameters: Dict[str, Any], data: pd.DataFrame
    ) -> SynthesizerType:
        """The default build and train function for the optimizer. parameters are passed to a
        config object which is used to instantiate and train a synthetic model.

        Args:
            parameters (Dict[str, Any]): The parameters to use for the config.
            data (pd.DataFrame): The original dataframe used to train the synthesizer.

        Returns:
            The trained synthesizer.

        """
        if self.synthetic_model == "HighDimSynthesizer":
            high_dim_config = HighDimConfig(**parameters)
            high_dim_synth = HighDimSynthesizer.from_df(
                data, config=high_dim_config, **self.model_kwargs
            )
            high_dim_synth.learn(df_train=data, verbose=0)
            return high_dim_synth
        elif self.synthetic_model == "TimeSeriesSynthesizer":
            deep_state_config = DeepStateConfig(**parameters)
            time_series_synth = TimeSeriesSynthesizer(
                df=data, config=deep_state_config, **self.model_kwargs
            )
            time_series_synth.learn()
            return time_series_synth
        else:
            raise ValueError(
                f"""synthetic_model must be one of ['HighDimSynthesizer', 'TimeSeriesSynthesizer'].
                Got {self.synthetic_model}"""
            )

    @staticmethod
    def create_train_evaluate_function(
        build_and_train_function: Callable, optimization_function: Callable, orig_df: pd.DataFrame
    ) -> Callable:
        """
        Creates a function that joins `build_and_train_function` with `optimization_function`.

        Args:
            build_and_train_function (Callable): A function that builds and trains a synthetic model
                based on the given parameterization and the original dataframe.
                Must have signature (parameterization, orig_df)
            optimization_function (Callable): A function that evaluates the synthesizer.
                Must have signature (synth, orig_df)
            orig_df (pd.DataFrame): The original dataframe used to train the synthesizer.

        Returns:
            Callable: A function that joins `build_and_train_function` with `optimization_function`.

        """

        def train_func(parameterization):
            synth = build_and_train_function(parameterization, orig_df)
            results = optimization_function(synth, orig_df)
            return results

        return train_func

    def create_parameter_client(self, loss_name: str, max_parallelism: int = 4) -> AxClient:
        """Creates an AxClient for the given loss function.

        The AxClient will conduct 10 SOBOL trials and then the rest of the trials will be conducted using GPEI.

        Args:
            loss_name (str): The name of the loss metric to use in the optimization.
            max_parallelism (int): The maximum number of parallel trials. Defaults to 4.

        Returns:
            AxClient: The AxClient for the given loss function.
        """

        gs = GenerationStrategy(
            steps=[
                GenerationStep(
                    model=Models.SOBOL,
                    num_trials=10,
                    min_trials_observed=9,
                    max_parallelism=max_parallelism,
                    enforce_num_trials=True,
                    model_kwargs={"deduplicate": True, "seed": None},
                    model_gen_kwargs=None,
                ),
                GenerationStep(
                    model=Models.GPEI,
                    num_trials=-1,
                    min_trials_observed=0,
                    max_parallelism=max_parallelism,
                    enforce_num_trials=True,
                    model_kwargs=None,
                    model_gen_kwargs=None,
                ),
            ]
        )

        axc = AxClient(
            generation_strategy=gs, verbose_logging=False, enforce_sequential_optimization=False
        )
        axc.create_experiment(
            name="sdk_tuning", parameters=self.parameters, objective_name=loss_name, minimize=True
        )

        return axc

    def optimize(self, num_samples: int) -> tune.analysis:
        """Performs optimization using the ray.tune library.

        Args:
            num_samples (int): The number of samples to evaluate.

        Returns:
            tune.Analysis: The analysis results of the optimization.
        """
        if num_samples < 10:
            logger.warning(
                f"""'num_samples' ({num_samples}) is less than 10. Will only conduct random search.
                Bayesian optimisation results will not be available."""
            )

        analysis = tune.run(
            self.train_evaluate,
            num_samples=num_samples,
            search_alg=AxSearch(
                ax_client=self.axc
            ),  # Note that the argument here is the `AxClient`.
            verbose=1,  # Set this level to 1 to see status updates and to 2 to also see trial results.
            # To use GPU, specify: resources_per_trial={"gpu": 1}.
            resources_per_trial={"cpu": self.num_cpus},
            max_failures=3,
            progress_reporter=tune.JupyterNotebookReporter(overwrite=True, max_progress_rows=100),
        )

        return analysis

    def get_best_params(self) -> Dict[str, Any]:
        """Retrieves the best parameters from the optimization trials.

        Returns:
            Dict: A dictionary containing the best raw and estimated parameters.
        """

        # Gets the best parameters from comparing all trials
        params_raw, params_raw_mean_value = get_best_raw_objective_point(self.axc.experiment)

        # Gets the parameters by predicting with the bayesian model
        params_estimate, (
            params_estimate_mean_value,
            params_estimate_variance,
        ) = get_best_parameters_from_model_predictions(self.axc.experiment, Models)

        return dict(
            params_raw=params_raw,
            params_raw_mean_value=params_raw_mean_value,
            params_estimate=params_estimate,
            params_estimate_mean_value=params_estimate_mean_value,
            params_estimate_variance=params_estimate_variance,
        )

    def plot_results(self, metric_name=None) -> None:
        """Plots the results of the optimization.

        Args:
            metric_name (str): The name of the metric to plot against each parameter.
            Defaults to "mean_loss" which is the default loss used if a custom_hyperparameter_loss is not defined.
        """

        init_notebook_plotting()
        render(self.axc.get_feature_importances())
        metric_name = self.loss_name if metric_name is None else metric_name

        param_names = [param["name"] for param in self.parameters]
        for param_name in param_names:
            try:
                render(
                    plot_slice(
                        self.axc.generation_strategy.model, param_name, metric_name=metric_name
                    )
                )
            except ValueError:
                pass

        render(interact_contour(self.axc.generation_strategy.model, metric_name=metric_name))

        render(self.axc.get_optimization_trace())

    def get_trial_results_as_df(self) -> pd.DataFrame:
        """Retrieves the trial results as a pandas DataFrame.

        Returns:
            pandas.DataFrame: The trial results.
        """
        return self.axc.get_trials_data_frame()
