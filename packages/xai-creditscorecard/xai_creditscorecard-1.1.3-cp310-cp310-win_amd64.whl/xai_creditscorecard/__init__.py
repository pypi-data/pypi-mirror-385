"""XAI Credit Scorecard - SHAP-based credit scoring system."""

__version__ = "1.1.3"
__author__ = "Rivalani Hlongwane"

from .scorecard_shap import createScorecard_SHAP, count_zeros_before_non_zero

__all__ = ['createScorecard_SHAP', 'count_zeros_before_non_zero']
