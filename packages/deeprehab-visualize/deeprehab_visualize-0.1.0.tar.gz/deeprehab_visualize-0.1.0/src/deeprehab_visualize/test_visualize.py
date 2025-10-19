"""
Tests for the deeprehab-visualize package.
"""

import numpy as np
import sys
import os

# Add the src directory to the path so we can import the package
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from deeprehab_visualize import (
    draw_skeleton,
    generate_svg
)


class MockLandmark:
    """Mock landmark class for testing."""
    def __init__(self, x, y, z=0, visibility=1.0):
        self.x = x
        self.y = y
        self.z = z
        self.visibility = visibility


def test_draw_skeleton():
    """Test drawing skeleton on a frame."""
    # Create a simple test frame
    frame = np.zeros((480, 640, 3), dtype=np.uint8)
    
    # Create test landmarks with full visibility
    landmarks = [MockLandmark(0, 0, visibility=1.0) for _ in range(33)]
    
    # Set specific positions for key landmarks
    # Left leg: [23→25→27]
    landmarks[23] = MockLandmark(0.2, 0.5, visibility=1.0)  # Left hip
    landmarks[25] = MockLandmark(0.2, 0.7, visibility=1.0)  # Left knee
    landmarks[27] = MockLandmark(0.2, 0.9, visibility=1.0)  # Left ankle
    
    # Right leg: [24→26→28]
    landmarks[24] = MockLandmark(0.8, 0.5, visibility=1.0)  # Right hip
    landmarks[26] = MockLandmark(0.8, 0.7, visibility=1.0)  # Right knee
    landmarks[28] = MockLandmark(0.8, 0.9, visibility=1.0)  # Right ankle
    
    # Left arm: [11→13→15]
    landmarks[11] = MockLandmark(0.2, 0.3, visibility=1.0)  # Left shoulder
    landmarks[13] = MockLandmark(0.1, 0.4, visibility=1.0)  # Left elbow
    landmarks[15] = MockLandmark(0.0, 0.5, visibility=1.0)  # Left wrist
    
    # Right arm: [12→14→16]
    landmarks[12] = MockLandmark(0.8, 0.3, visibility=1.0)  # Right shoulder
    landmarks[14] = MockLandmark(0.9, 0.4, visibility=1.0)  # Right elbow
    landmarks[16] = MockLandmark(1.0, 0.5, visibility=1.0)  # Right wrist
    
    # Hip: [23→24]
    # Shoulders: [11→12]
    # Left shoulder to left hip: [11→23]
    # Right shoulder to right hip: [12→24]
    # (These connections are already defined by the above points)
    
    # Draw skeleton on frame
    result_frame = draw_skeleton(frame, landmarks)
    
    # Check that the result is a numpy array with the same shape
    assert isinstance(result_frame, np.ndarray)
    assert result_frame.shape == frame.shape
    print("✅ draw_skeleton test passed")


def test_generate_svg():
    """Test generating SVG from landmarks."""
    # Create test landmarks with full visibility
    landmarks = [MockLandmark(0, 0, visibility=1.0) for _ in range(33)]
    
    # Set specific positions for key landmarks
    # Left leg: [23→25→27]
    landmarks[23] = MockLandmark(0.2, 0.5, visibility=1.0)  # Left hip
    landmarks[25] = MockLandmark(0.2, 0.7, visibility=1.0)  # Left knee
    landmarks[27] = MockLandmark(0.2, 0.9, visibility=1.0)  # Left ankle
    
    # Right leg: [24→26→28]
    landmarks[24] = MockLandmark(0.8, 0.5, visibility=1.0)  # Right hip
    landmarks[26] = MockLandmark(0.8, 0.7, visibility=1.0)  # Right knee
    landmarks[28] = MockLandmark(0.8, 0.9, visibility=1.0)  # Right ankle
    
    # Left arm: [11→13→15]
    landmarks[11] = MockLandmark(0.2, 0.3, visibility=1.0)  # Left shoulder
    landmarks[13] = MockLandmark(0.1, 0.4, visibility=1.0)  # Left elbow
    landmarks[15] = MockLandmark(0.0, 0.5, visibility=1.0)  # Left wrist
    
    # Right arm: [12→14→16]
    landmarks[12] = MockLandmark(0.8, 0.3, visibility=1.0)  # Right shoulder
    landmarks[14] = MockLandmark(0.9, 0.4, visibility=1.0)  # Right elbow
    landmarks[16] = MockLandmark(1.0, 0.5, visibility=1.0)  # Right wrist
    
    # Generate SVG
    svg_string = generate_svg(landmarks, (640, 480))
    
    # Check that result is a string
    assert isinstance(svg_string, str)
    # Check that it contains SVG elements
    assert "<svg" in svg_string
    assert "</svg>" in svg_string
    print("✅ generate_svg test passed")


def run_all_tests():
    """Run all tests."""
    print("Running tests for deeprehab-visualize package...")
    
    test_draw_skeleton()
    test_generate_svg()
    
    print("All tests passed! 🎉")


if __name__ == "__main__":
    run_all_tests()