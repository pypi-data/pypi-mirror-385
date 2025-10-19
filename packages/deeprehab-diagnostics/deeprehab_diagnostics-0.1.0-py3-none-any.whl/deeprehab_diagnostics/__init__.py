"""
DeepRehab Diagnostics Package
============================

This package provides diagnostic functions for DeepRehab movement analysis results.
"""

__version__ = "0.1.0"

from .deeprehab_diagnostics import (
    DiagnosticResult,
    analyze_movement_symmetry,
    analyze_movement_stability,
    generate_recommendations,
    identify_risk_factors,
    diagnose_movement,
    analyze_squat_errors,
    generate_feedback
)

__all__ = [
    "DiagnosticResult",
    "analyze_movement_symmetry",
    "analyze_movement_stability",
    "generate_recommendations",
    "identify_risk_factors",
    "diagnose_movement",
    "analyze_squat_errors",
    "generate_feedback"
]