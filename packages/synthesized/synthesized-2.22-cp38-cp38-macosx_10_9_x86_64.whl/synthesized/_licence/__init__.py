"""Synthesized Licence and feature flagging subpackage.

This subpackage contains the licence and feature flagging functionality for Synthesized.
It is used to load the licence key, verify the licence, and check that given features are
enabled.

The order of license events that occur on startup is as follows:
- Check if GCloud environment variables have been set
  If not
  - Check if the licence key is set as an environment variable or in the default file location.
      If not:
        - prompt the user to obtain a trial licence key
        - save the licence key.
  If so:
  - create gcloud client and check with gcloud.

- Verify the licence key:



Utility functions related to the licence are defined in the `licence` submodule. There are two
public global variables defined here.

    - `licence.EXPIRY_DATE`: The expiry date of the licence.
    - `licence.FEATURES`: The features enabled by the licence.

These variables are never used directly when evaluating the licence. Instead, these
variables are always redetermined from `_KEY` – an RSA encrypted string. This way user can't
change available features or expiry date,

Most importantly, the `verify` function can be used throughout the codebase to check that the
licence is valid for a given feature.

Modules:
    analytics.py: Util functions for tracking usage (gcloud)
    exceptions.py: Possible licence exceptions.
    features.py: Optional features are defined here.
    gcloud.py: GCloud client and related functions.
    licence.py: Licence loading and verifying functions.
"""
import sys

from synthesized._licence.exceptions import (
    FeatureUnavailableError,
    GoogleCloudConnectionError,
    GoogleCloudError,
    LicenceError,
    LicenceExpiredError,
    LicenceSignatureError,
    LicenceWarning,
)
from synthesized._licence.features import OptionalFeature

from . import gcloud

from synthesized._licence.prompt import prompt_for_licence  # isort: skip

from synthesized._licence import licence  # isort: skip

from .analytics import (  # isort:skip
    track,
)


if gcloud.is_gcloud_env_set():
    gcloud.create_client()
    verify = gcloud.verify
    permissions_check = gcloud.permissions_check
else:
    verify = licence.verify
    permissions_check = licence.permissions_check
    if not licence.is_key_set():
        key = prompt_for_licence()
        licence.try_set_licence_key(key)

try:
    verify()

except LicenceError as e:
    sys.exit(str(e))

__all__ = [
    "OptionalFeature",
    "verify",
    "LicenceError",
    "LicenceExpiredError",
    "LicenceWarning",
    "GoogleCloudConnectionError",
    "GoogleCloudError",
    "FeatureUnavailableError",
    "LicenceSignatureError",
    "GoogleCloudConnectionError",
    "GoogleCloudError",
    "gcloud",
    "track",
]
