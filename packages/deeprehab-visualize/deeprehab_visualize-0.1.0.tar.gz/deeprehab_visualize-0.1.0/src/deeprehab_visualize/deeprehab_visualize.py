"""
DeepRehab Visualization Package
===============================

This module provides visualization functions for DeepRehab pose data and analysis results.
"""

import cv2
import numpy as np
import svgwrite


def draw_skeleton(frame, landmarks):
    """
    Draw skeleton on an OpenCV image.
    
    Args:
        frame: OpenCV format image (BGR channels)
        landmarks: List of 33 Landmark objects
        
    Returns:
        OpenCV format image with skeleton annotations
    """
    # Define connections for key body parts
    connections = [
        # Left leg: [23→25→27]
        (23, 25), (25, 27),
        # Right leg: [24→26→28]
        (24, 26), (26, 28),
        # Left arm: [11→13→15]
        (11, 13), (13, 15),
        # Right arm: [12→14→16]
        (12, 14), (14, 16),
        # Hip: [23→24]
        (23, 24),
        # Shoulders: [11→12]
        (11, 12),
        # Left shoulder to left hip: [11→23]
        (11, 23),
        # Right shoulder to right hip: [12→24]
        (12, 24)
    ]
    
    # Create a copy of the frame to draw on
    annotated_frame = frame.copy()
    height, width = frame.shape[:2]
    
    # Draw connections (skeleton lines)
    for start_idx, end_idx in connections:
        if (start_idx < len(landmarks) and end_idx < len(landmarks) and
            hasattr(landmarks[start_idx], 'visibility') and 
            hasattr(landmarks[end_idx], 'visibility') and
            landmarks[start_idx].visibility > 0.5 and 
            landmarks[end_idx].visibility > 0.5):
            
            start_x = int(landmarks[start_idx].x * width)
            start_y = int(landmarks[start_idx].y * height)
            end_x = int(landmarks[end_idx].x * width)
            end_y = int(landmarks[end_idx].y * height)
            
            # Draw line for skeleton connection
            cv2.line(annotated_frame, (start_x, start_y), (end_x, end_y), 
                    (0, 255, 0), 2)
    
    # Draw landmarks (keypoints)
    for idx, landmark in enumerate(landmarks):
        if hasattr(landmark, 'visibility') and landmark.visibility > 0.5:
            x = int(landmark.x * width)
            y = int(landmark.y * height)
            # Draw circle for keypoint
            cv2.circle(annotated_frame, (x, y), 3, (0, 0, 255), -1)
    
    return annotated_frame


def generate_svg(landmarks, img_size=(640, 480)):
    """
    Generate SVG string containing skeleton and keypoints.
    
    Args:
        landmarks: List of 33 Landmark objects
        img_size: Image dimensions (width, height), default (640, 480)
        
    Returns:
        Complete SVG string
    """
    width, height = img_size
    
    # Create SVG drawing
    dwg = svgwrite.Drawing(size=(str(width), str(height)))
    
    # Define connections for key body parts
    connections = [
        # Left leg: [23→25→27]
        (23, 25), (25, 27),
        # Right leg: [24→26→28]
        (24, 26), (26, 28),
        # Left arm: [11→13→15]
        (11, 13), (13, 15),
        # Right arm: [12→14→16]
        (12, 14), (14, 16),
        # Hip: [23→24]
        (23, 24),
        # Shoulders: [11→12]
        (11, 12),
        # Left shoulder to left hip: [11→23]
        (11, 23),
        # Right shoulder to right hip: [12→24]
        (12, 24)
    ]
    
    # Draw connections (skeleton lines)
    for start_idx, end_idx in connections:
        if (start_idx < len(landmarks) and end_idx < len(landmarks) and
            hasattr(landmarks[start_idx], 'visibility') and 
            hasattr(landmarks[end_idx], 'visibility')):
            
            # Determine opacity based on visibility
            start_visibility = landmarks[start_idx].visibility
            end_visibility = landmarks[end_idx].visibility
            opacity = 1.0 if (start_visibility > 0.5 and end_visibility > 0.5) else 0.3
            
            # Convert normalized coordinates to pixel coordinates
            start_x = landmarks[start_idx].x * width
            start_y = landmarks[start_idx].y * height
            end_x = landmarks[end_idx].x * width
            end_y = landmarks[end_idx].y * height
            
            # Draw line for skeleton connection
            line = dwg.line(start=(start_x, start_y), end=(end_x, end_y), 
                           stroke="#00ff00", stroke_width=2)
            line.fill(opacity=opacity)
            dwg.add(line)
    
    # Draw landmarks (keypoints)
    for idx, landmark in enumerate(landmarks):
        if hasattr(landmark, 'visibility'):
            # Determine opacity based on visibility
            opacity = 1.0 if landmark.visibility > 0.5 else 0.3
            
            # Convert normalized coordinates to pixel coordinates
            x = landmark.x * width
            y = landmark.y * height
            
            # Draw circle for keypoint
            circle = dwg.circle(center=(x, y), r=3, fill="#ff0000")
            circle.fill(opacity=opacity)
            dwg.add(circle)
    
    # Return SVG as string
    return dwg.tostring()