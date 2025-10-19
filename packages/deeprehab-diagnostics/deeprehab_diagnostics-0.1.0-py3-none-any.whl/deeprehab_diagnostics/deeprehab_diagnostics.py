"""
DeepRehab Diagnostics Package
============================

This module provides diagnostic functions for DeepRehab movement analysis results.
"""

from typing import List, Dict, Any, Optional
from dataclasses import dataclass
import numpy as np


@dataclass
class DiagnosticResult:
    """
    Diagnostic result for a movement analysis.
    
    Attributes:
        movement_type: Type of movement analyzed
        asymmetry_score: Score indicating left/right asymmetry (0-1, where 0 is perfectly symmetric)
        stability_score: Score indicating movement stability (0-1, where 1 is perfectly stable)
        range_of_motion: Dictionary of joint angles or ranges
        recommendations: List of recommended improvements
        risk_factors: List of identified risk factors
    """
    movement_type: str
    asymmetry_score: float
    stability_score: float
    range_of_motion: Dict[str, float]
    recommendations: List[str]
    risk_factors: List[str]


def analyze_movement_symmetry(left_angles: Dict[str, float], 
                             right_angles: Dict[str, float]) -> float:
    """
    Analyze symmetry between left and right side movements.
    
    Args:
        left_angles: Dictionary of joint angles for left side
        right_angles: Dictionary of joint angles for right side
        
    Returns:
        Asymmetry score (0-1, where 0 is perfectly symmetric)
    """
    # Calculate differences between left and right angles
    differences = []
    common_joints = set(left_angles.keys()) & set(right_angles.keys())
    
    for joint in common_joints:
        # Calculate absolute difference normalized by average angle
        avg_angle = (left_angles[joint] + right_angles[joint]) / 2
        if avg_angle != 0:
            diff = abs(left_angles[joint] - right_angles[joint]) / avg_angle
            differences.append(min(diff, 1.0))  # Cap at 1.0
    
    # Return average asymmetry score
    if differences:
        return min(np.mean(differences), 1.0)
    else:
        return 0.0


def analyze_movement_stability(angle_series: List[Dict[str, float]]) -> float:
    """
    Analyze stability of movement across frames.
    
    Args:
        angle_series: List of dictionaries containing angles for each frame
        
    Returns:
        Stability score (0-1, where 1 is perfectly stable)
    """
    if len(angle_series) < 2:
        return 1.0  # Perfectly stable if only one frame
    
    # Calculate standard deviation for each joint across frames
    joints = angle_series[0].keys()
    joint_stabilities = []
    
    for joint in joints:
        angles = [frame.get(joint, 0) for frame in angle_series]
        # Calculate coefficient of variation (std/mean)
        mean_angle = np.mean(angles)
        if mean_angle != 0:
            cv = np.std(angles) / abs(mean_angle)
            # Convert to stability score (0-1, where 1 is stable)
            stability = max(0, 1 - cv)
            joint_stabilities.append(stability)
        else:
            joint_stabilities.append(1.0)
    
    # Return average stability across all joints
    return np.mean(joint_stabilities) if joint_stabilities else 1.0


def generate_recommendations(asymmetry_score: float, 
                           stability_score: float,
                           range_of_motion: Dict[str, float]) -> List[str]:
    """
    Generate recommendations based on diagnostic results.
    
    Args:
        asymmetry_score: Movement asymmetry score
        stability_score: Movement stability score
        range_of_motion: Dictionary of joint ranges of motion
        
    Returns:
        List of recommendations
    """
    recommendations = []
    
    # Asymmetry recommendations
    if asymmetry_score > 0.15:
        recommendations.append("Significant asymmetry detected between left and right sides. Consider unilateral strengthening exercises.")
    elif asymmetry_score > 0.05:
        recommendations.append("Mild asymmetry detected. Monitor for progression.")
    
    # Stability recommendations
    if stability_score < 0.7:
        recommendations.append("Poor movement stability detected. Consider slow, controlled movements to improve stability.")
    elif stability_score < 0.85:
        recommendations.append("Moderate movement stability. Continue with stability training.")
    
    # Range of motion recommendations
    for joint, angle in range_of_motion.items():
        if "knee" in joint.lower() and angle < 90:
            recommendations.append(f"Reduced {joint} flexion. Consider flexibility training.")
        elif "shoulder" in joint.lower() and angle < 160:
            recommendations.append(f"Reduced {joint} flexion. Consider shoulder mobility exercises.")
    
    return recommendations


def identify_risk_factors(asymmetry_score: float, 
                        stability_score: float,
                        range_of_motion: Dict[str, float]) -> List[str]:
    """
    Identify potential risk factors based on diagnostic results.
    
    Args:
        asymmetry_score: Movement asymmetry score
        stability_score: Movement stability score
        range_of_motion: Dictionary of joint ranges of motion
        
    Returns:
        List of identified risk factors
    """
    risk_factors = []
    
    # Asymmetry risk factors
    if asymmetry_score > 0.2:
        risk_factors.append("High movement asymmetry increases injury risk")
    elif asymmetry_score > 0.1:
        risk_factors.append("Moderate movement asymmetry may increase injury risk")
    
    # Stability risk factors
    if stability_score < 0.6:
        risk_factors.append("Poor movement stability increases injury risk")
    elif stability_score < 0.8:
        risk_factors.append("Moderate movement stability may increase injury risk")
    
    # Range of motion risk factors
    for joint, angle in range_of_motion.items():
        if "knee" in joint.lower() and angle < 80:
            risk_factors.append(f"Severely limited {joint} flexion increases injury risk")
        elif "shoulder" in joint.lower() and angle < 150:
            risk_factors.append(f"Severely limited {joint} flexion increases injury risk")
    
    return risk_factors


def diagnose_movement(movement_type: str,
                     left_angles: Dict[str, float],
                     right_angles: Dict[str, float],
                     angle_series: List[Dict[str, float]]) -> DiagnosticResult:
    """
    Perform comprehensive movement diagnostics.
    
    Args:
        movement_type: Type of movement being analyzed
        left_angles: Dictionary of joint angles for left side
        right_angles: Dictionary of joint angles for right side
        angle_series: List of dictionaries containing angles for each frame
        
    Returns:
        DiagnosticResult with comprehensive analysis
    """
    # Calculate asymmetry score
    asymmetry_score = analyze_movement_symmetry(left_angles, right_angles)
    
    # Calculate stability score
    stability_score = analyze_movement_stability(angle_series)
    
    # Combine left and right angles for range of motion analysis
    range_of_motion = {}
    for joint, angle in left_angles.items():
        range_of_motion[f"left_{joint}"] = angle
    for joint, angle in right_angles.items():
        range_of_motion[f"right_{joint}"] = angle
    
    # Generate recommendations
    recommendations = generate_recommendations(
        asymmetry_score, stability_score, range_of_motion)
    
    # Identify risk factors
    risk_factors = identify_risk_factors(
        asymmetry_score, stability_score, range_of_motion)
    
    return DiagnosticResult(
        movement_type=movement_type,
        asymmetry_score=asymmetry_score,
        stability_score=stability_score,
        range_of_motion=range_of_motion,
        recommendations=recommendations,
        risk_factors=risk_factors
    )


def analyze_squat_errors(angles: dict) -> dict:
    """
    Analyze common errors in deep squat movement.
    
    Args:
        angles: Dictionary containing joint angles and other measurements
        
    Returns:
        Dictionary of detected errors
    """
    errors = {}
    
    # Check for knee valgus (knees collapsing inward)
    if angles["left_knee"] < 120:
        errors["knee_valgus"] = True
    
    # Check for excessive trunk lean
    if angles.get("trunk_tilt", 0) > 20:
        errors["trunk_lean"] = angles["trunk_tilt"]
    
    # Check for asymmetry between left and right knee angles
    left_knee = angles.get("left_knee", 0)
    right_knee = angles.get("right_knee", 0)
    knee_difference = abs(left_knee - right_knee)
    if knee_difference > 15:
        errors["asymmetry"] = knee_difference
    
    return errors


def generate_feedback(errors: dict) -> str:
    """
    Generate professional rehabilitation feedback based on detected errors.
    
    Args:
        errors: Dictionary of detected errors from analyze_squat_errors
        
    Returns:
        Professional, concise, and actionable feedback string
    """
    feedback_parts = []
    
    # Generate feedback for knee valgus
    if errors.get("knee_valgus"):
        feedback_parts.append("Knee valgus detected. Strengthen gluteus medius and practice hip abduction exercises.")
    
    # Generate feedback for trunk lean
    if "trunk_lean" in errors:
        trunk_lean = errors["trunk_lean"]
        feedback_parts.append(f"Excessive trunk lean ({trunk_lean:.1f}°). Improve ankle dorsiflexion and posterior chain mobility.")
    
    # Generate feedback for asymmetry
    if "asymmetry" in errors:
        asymmetry = errors["asymmetry"]
        feedback_parts.append(f"Significant knee angle asymmetry ({asymmetry:.1f}°). Address strength and mobility imbalances between limbs.")
    
    # If no errors detected
    if not feedback_parts:
        return "Good squat form. Continue current training protocol."
    
    return " ".join(feedback_parts)