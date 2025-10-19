"""
Tests for the deeprehab-diagnostics package.
"""

import sys
import os

# Add the src directory to the path so we can import the package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from deeprehab_diagnostics import (
    DiagnosticResult,
    analyze_movement_symmetry,
    analyze_movement_stability,
    generate_recommendations,
    identify_risk_factors,
    diagnose_movement,
    analyze_squat_errors,
    generate_feedback
)


def test_analyze_movement_symmetry():
    """Test symmetry analysis function."""
    # Test perfectly symmetric movements
    left_angles = {"knee": 90, "shoulder": 180}
    right_angles = {"knee": 90, "shoulder": 180}
    symmetry_score = analyze_movement_symmetry(left_angles, right_angles)
    assert symmetry_score == 0.0, f"Expected 0.0, got {symmetry_score}"
    
    # Test asymmetric movements
    left_angles = {"knee": 90, "shoulder": 180}
    right_angles = {"knee": 45, "shoulder": 90}
    symmetry_score = analyze_movement_symmetry(left_angles, right_angles)
    assert 0 < symmetry_score < 1, f"Expected between 0 and 1, got {symmetry_score}"
    
    print("✅ analyze_movement_symmetry test passed")


def test_analyze_movement_stability():
    """Test stability analysis function."""
    # Test perfectly stable movement
    angle_series = [
        {"knee": 90, "shoulder": 180},
        {"knee": 90, "shoulder": 180},
        {"knee": 90, "shoulder": 180}
    ]
    stability_score = analyze_movement_stability(angle_series)
    assert stability_score == 1.0, f"Expected 1.0, got {stability_score}"
    
    # Test unstable movement
    angle_series = [
        {"knee": 90, "shoulder": 180},
        {"knee": 45, "shoulder": 90},
        {"knee": 135, "shoulder": 270}
    ]
    stability_score = analyze_movement_stability(angle_series)
    assert 0 <= stability_score <= 1, f"Expected between 0 and 1, got {stability_score}"
    
    print("✅ analyze_movement_stability test passed")


def test_generate_recommendations():
    """Test recommendation generation function."""
    # Test with good scores and normal range of motion
    recommendations = generate_recommendations(0.02, 0.95, {"knee": 100, "shoulder": 170})
    assert isinstance(recommendations, list), "Recommendations should be a list"
    
    # Test with poor scores
    recommendations = generate_recommendations(0.25, 0.5, {"knee": 70, "shoulder": 140})
    assert len(recommendations) > 0, "Should have recommendations for poor scores"
    
    print("✅ generate_recommendations test passed")


def test_identify_risk_factors():
    """Test risk factor identification function."""
    # Test with good scores and normal range of motion
    risk_factors = identify_risk_factors(0.02, 0.95, {"knee": 100, "shoulder": 170})
    assert isinstance(risk_factors, list), "Risk factors should be a list"
    
    # Test with poor scores
    risk_factors = identify_risk_factors(0.3, 0.4, {"knee": 60, "shoulder": 120})
    assert len(risk_factors) > 0, "Should have risk factors for poor scores"
    
    print("✅ identify_risk_factors test passed")


def test_diagnose_movement():
    """Test comprehensive movement diagnosis function."""
    left_angles = {"knee": 95.5, "shoulder": 165.2}
    right_angles = {"knee": 92.3, "shoulder": 162.1}
    angle_series = [
        {"knee": 95.5, "shoulder": 165.2},
        {"knee": 94.8, "shoulder": 164.7},
        {"knee": 95.2, "shoulder": 165.0},
        {"knee": 94.9, "shoulder": 164.8}
    ]
    
    result = diagnose_movement("Deep Squat", left_angles, right_angles, angle_series)
    
    # Check that result is a DiagnosticResult instance
    assert isinstance(result, DiagnosticResult), "Result should be a DiagnosticResult instance"
    
    # Check that all fields are present
    assert hasattr(result, 'movement_type')
    assert hasattr(result, 'asymmetry_score')
    assert hasattr(result, 'stability_score')
    assert hasattr(result, 'range_of_motion')
    assert hasattr(result, 'recommendations')
    assert hasattr(result, 'risk_factors')
    
    print("✅ diagnose_movement test passed")


def test_analyze_squat_errors():
    """Test squat error analysis function."""
    # Test knee valgus detection
    angles = {"left_knee": 110, "right_knee": 130}
    errors = analyze_squat_errors(angles)
    assert errors.get("knee_valgus") is True, "Should detect knee valgus"
    
    # Test trunk lean detection
    angles = {"left_knee": 130, "right_knee": 130, "trunk_tilt": 25}
    errors = analyze_squat_errors(angles)
    assert "trunk_lean" in errors, "Should detect trunk lean"
    
    # Test asymmetry detection
    angles = {"left_knee": 100, "right_knee": 130}
    errors = analyze_squat_errors(angles)
    assert "asymmetry" in errors, "Should detect asymmetry"
    
    print("✅ analyze_squat_errors test passed")


def test_generate_feedback():
    """Test feedback generation function."""
    # Test feedback for knee valgus
    errors = {"knee_valgus": True}
    feedback = generate_feedback(errors)
    assert "Knee valgus" in feedback, "Should generate feedback for knee valgus"
    
    # Test feedback for trunk lean
    errors = {"trunk_lean": 25.5}
    feedback = generate_feedback(errors)
    assert "trunk lean" in feedback, "Should generate feedback for trunk lean"
    
    # Test feedback for asymmetry
    errors = {"asymmetry": 20.5}
    feedback = generate_feedback(errors)
    assert "asymmetry" in feedback, "Should generate feedback for asymmetry"
    
    # Test feedback for good form
    errors = {}
    feedback = generate_feedback(errors)
    assert "Good squat form" in feedback, "Should generate positive feedback for good form"
    
    print("✅ generate_feedback test passed")


def run_all_tests():
    """Run all tests."""
    print("Running tests for deeprehab-diagnostics package...")
    
    test_analyze_movement_symmetry()
    test_analyze_movement_stability()
    test_generate_recommendations()
    test_identify_risk_factors()
    test_diagnose_movement()
    test_analyze_squat_errors()
    test_generate_feedback()
    
    print("All tests passed! 🎉")


if __name__ == "__main__":
    run_all_tests()