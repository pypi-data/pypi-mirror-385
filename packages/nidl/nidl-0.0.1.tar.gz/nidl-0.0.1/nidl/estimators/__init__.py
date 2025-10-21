##########################################################################
# NSAp - Copyright (C) CEA, 2025
# Distributed under the terms of the CeCILL-B license, as published by
# the CEA-CNRS-INRIA. Refer to the LICENSE file or to
# http://www.cecill.info/licences/Licence_CeCILL-B_V1-en.html
# for details.
##########################################################################

""" This modules details the public API you should use and implement for a
nidl compatible estimator, as well as the estimators available in nidl.
"""

from .base import (
    BaseEstimator,
    ClassifierMixin,
    ClusterMixin,
    RegressorMixin,
    TransformerMixin,
)
