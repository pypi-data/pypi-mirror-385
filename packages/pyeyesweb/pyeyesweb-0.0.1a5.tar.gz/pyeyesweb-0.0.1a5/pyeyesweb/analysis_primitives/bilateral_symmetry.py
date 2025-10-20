"""
Bilateral Symmetry Analysis for Motion Capture Data

Below are a few research paper references:
1. "Movement Symmetry Assessment by Bilateral Motion Data Fusion" (2018)
   Link: https://pubmed.ncbi.nlm.nih.gov/29993408/
   Provides Canonical Correlation Analysis (CCA) methodology and introduces bilateral motion data fusion concepts

2. "Symmetry Analysis of Manual Wheelchair Propulsion Using Motion Capture Techniques" (2022)
   Link: https://www.mdpi.com/2073-8994/14/6/1164/htm
   Provides coefficient of variation calculation method and shows marker-based symmetry comparison approach

3. General bilateral coordination research concepts from multiple biomechanics papers
   Phase synchronization using Hilbert transform and bilateral symmetry index calculations

Note: Specific implementation details are adapted for a real-time MoCap analysis. Must be tested by us at CP.
"""

import numpy as np
import warnings
from sklearn.cross_decomposition import CCA

from pyeyesweb.data_models.thread_safe_buffer import ThreadSafeHistoryBuffer
from pyeyesweb.utils.signal_processing import compute_phase_synchronization
from pyeyesweb.utils.validators import validate_window_size, validate_and_normalize_filter_params


class BilateralSymmetryAnalyzer:
    """
    Real-time bilateral symmetry analysis for motion capture data.
    
    Based on research methods from bilateral motion data fusion and 
    wheelchair propulsion symmetry analysis papers.

    Read more in the [User Guide](/PyEyesWeb/user_guide/theoretical_framework/analysis_primitives/bilateral_symmetry/).
    """
    
    def __init__(self, window_size=100, joint_pairs=None, filter_params=None):
        """
        Initialize bilateral symmetry analyzer.

        Args:
            window_size: Number of frames for sliding window analysis
            joint_pairs: List of tuples defining bilateral joint pairs
            filter_params: Optional tuple of (lowcut_hz, highcut_hz, sampling_rate_hz)
                          for band-pass filtering. If None, no filtering is applied.
        """
        self.window_size = validate_window_size(window_size)
        # Use ThreadSafeHistoryBuffer instead of deque + lock
        self.history = ThreadSafeHistoryBuffer(maxlen=self.window_size)
        
        # Default joint pairs for standard MoCap setup
        if joint_pairs is None:
            self.joint_pairs = [
                (4, 5),   # left_shoulder, right_shoulder
                (6, 7),   # left_elbow, right_elbow
                (8, 9),   # left_wrist, right_wrist
                (10, 11), # left_hip, right_hip
                (12, 13), # left_knee, right_knee
                (14, 15), # left_ankle, right_ankle
            ]
        else:
            self.joint_pairs = joint_pairs

        # validate and normalize filter params
        self.filter_params = validate_and_normalize_filter_params(filter_params)
            
    def _compute_bilateral_symmetry_index(self, left_data, right_data):
        """
        Compute Bilateral Symmetry Index based on research methodology.
        
        Inspired by wheelchair propulsion research paper method:
        Compares mirrored bilateral movements and calculates relative differences.
        
        Args:
            left_data: (n_frames, 3) array of left joint positions
            right_data: (n_frames, 3) array of right joint positions
            
        Returns:
            float: Symmetry index (0-1, where 1 is perfect symmetry)
        """
        # Mirror right side data across sagittal plane (flip x-coordinate)
        right_mirrored = right_data.copy()
        right_mirrored[:, 0] *= -1  # Flip x-axis for bilateral comparison
        
        # Calculate relative differences (from wheelchair research)
        diff = np.abs(left_data - right_mirrored)
        sum_val = np.abs(left_data) + np.abs(right_mirrored)
        
        # Avoid division by zero
        sum_val = np.where(sum_val == 0, 1e-8, sum_val)
        
        # Relative asymmetry percentage
        relative_asymmetry = np.mean(diff / sum_val) * 100
        
        # Convert to symmetry index (100% asymmetry = 0 symmetry)
        symmetry_index = max(0, 1 - (relative_asymmetry / 100))
        
        return symmetry_index
    

    def _compute_cca_correlation(self, left_data, right_data):
        """
        Compute canonical correlation between bilateral data.
        
        Based on "Movement Symmetry Assessment by Bilateral Motion Data Fusion" paper
        methodology using Canonical Correlation Analysis.
        
        Args:
            left_data: (n_frames, 3) left joint data
            right_data: (n_frames, 3) right joint data
            
        Returns:
            float: Canonical correlation (0-1)
        """
        if left_data.shape[0] < 5:  # Need minimum samples for CCA
            return np.nan  # Not enough data for CCA
            
        try:
            # Flatten spatial coordinates for CCA analysis
            left_features = left_data.reshape(left_data.shape[0], -1)
            right_features = right_data.reshape(right_data.shape[0], -1)
            
            # Apply CCA with single component
            cca = CCA(n_components=1)
            left_c, right_c = cca.fit_transform(left_features, right_features)
            
            # Compute canonical correlation
            correlation = np.corrcoef(left_c.flatten(), right_c.flatten())[0, 1]
            
            # Handle NaN cases
            if np.isnan(correlation):
                return np.nan  # Correlation computation failed
                
            return abs(correlation)  # Take absolute value

        except Exception as e:
            import warnings
            warnings.warn(f"CCA correlation computation failed: {e}", RuntimeWarning)
            return np.nan
    
    def analyze_frame(self, mocap_frame):
        """
        Analyze single frame of MoCap data for bilateral symmetry.

        Args:
            mocap_frame: (n_joints, 3) array of joint positions for one frame

        Returns:
            dict: Symmetry metrics for current frame
        """
        self.history.append(mocap_frame)
        history_length = len(self.history)

        if history_length < 10:  # Need minimum history for analysis
            return {
                'overall_symmetry': 0.0,
                'phase_sync': 0.0,
                'cca_correlation': 0.0,
                'joint_symmetries': {}
            }

        # ThreadSafeHistoryBuffer provides thread-safe get_array method
        history_array = self.history.get_array()  # (n_frames, n_joints, 3)
        
        joint_symmetries = {}
        symmetry_scores = []
        phase_scores = []
        cca_scores = []
        
        # Analyze each bilateral joint pair
        for left_idx, right_idx in self.joint_pairs:
            left_joint_data = history_array[:, left_idx, :]
            right_joint_data = history_array[:, right_idx, :]
            
            # Compute multiple symmetry metrics
            bsi = self._compute_bilateral_symmetry_index(left_joint_data, right_joint_data)

            # Use vertical movement for phase analysis (most relevant for gait)
            # Compute phase synchronization directly
            try:
                sig = np.column_stack([left_joint_data[:, 2], right_joint_data[:, 2]])
                phase_sync = compute_phase_synchronization(sig, self.filter_params)
            except Exception as e:
                warnings.warn(f"Phase symmetry computation failed: {e}", RuntimeWarning)
                phase_sync = np.nan
            
            cca_corr = self._compute_cca_correlation(left_joint_data, right_joint_data)
            
            joint_pair_name = f"joint_{left_idx}_{right_idx}"
            joint_symmetries[joint_pair_name] = {
                'bilateral_symmetry_index': bsi,
                'phase_synchronization': phase_sync,
                'cca_correlation': cca_corr
            }
            
            symmetry_scores.append(bsi)
            phase_scores.append(phase_sync)
            cca_scores.append(cca_corr)
        
        # Compute overall metrics
        overall_symmetry = np.mean(symmetry_scores) if symmetry_scores else 0.0
        overall_phase_sync = np.mean(phase_scores) if phase_scores else 0.0
        overall_cca = np.mean(cca_scores) if cca_scores else 0.0
        
        return {
            'overall_symmetry': overall_symmetry,
            'phase_sync': overall_phase_sync,
            'cca_correlation': overall_cca,
            'joint_symmetries': joint_symmetries
        }

    def __call__(self, mocap_frame):
        """
        Compute bilateral symmetry metrics for motion capture frame.

        This method provides a standardized API interface by delegating to analyze_frame.

        Args:
            mocap_frame: (n_joints, 3) array of joint positions for one frame

        Returns:
            dict: Symmetry metrics containing:
                - overall_symmetry: Overall bilateral symmetry score (0-1)
                - phase_sync: Phase synchronization value
                - cca_correlation: Canonical correlation coefficient
                - joint_symmetries: Per-joint-pair symmetry metrics
        """
        return self.analyze_frame(mocap_frame)


