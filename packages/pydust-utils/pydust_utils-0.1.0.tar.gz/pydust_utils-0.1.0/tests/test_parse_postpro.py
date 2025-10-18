import os
import pytest
import numpy as np
from pydust_utils import (
    read_probes,
    read_sectional,
    read_chordwise,
    read_integral,
    read_hinge
)

# Define test data folder path
TEST_DATA_FOLDER = os.path.join(os.path.dirname(__file__), 'dat_files')

class TestProbes:
    """Test suite for probe data parsing"""
    
    def test_read_probes(self):
        """Test that probe data is read correctly"""
        probe_data = read_probes(os.path.join(TEST_DATA_FOLDER, 'test_probes.dat'))
        
        # Check that data structures exist
        assert probe_data.locations is not None
        assert probe_data.time is not None
        assert probe_data.velocities is not None
        
        # Check shapes
        n_probes = probe_data.locations.shape[0]
        n_time = len(probe_data.time)
        
        assert probe_data.locations.shape == (n_probes, 3)
        assert probe_data.velocities.shape == (n_time, n_probes, 3)
        
    def test_probe_data_types(self):
        """Test that probe data has correct types"""
        probe_data = read_probes(os.path.join(TEST_DATA_FOLDER, 'test_probes.dat'))
        
        assert isinstance(probe_data.locations, np.ndarray)
        assert isinstance(probe_data.time, np.ndarray)
        assert isinstance(probe_data.velocities, np.ndarray)


class TestSectional:
    """Test suite for sectional data parsing"""
    
    @pytest.mark.skipif(
        not os.path.exists(os.path.join(TEST_DATA_FOLDER, 'test_sectional.dat')),
        reason="Test sectional data file not available"
    )
    def test_read_sectional(self):
        """Test that sectional data is read correctly"""
        sectional_data = read_sectional(os.path.join(TEST_DATA_FOLDER, 'test_sectional.dat'))
        
        assert sectional_data.sec is not None
        assert sectional_data.time is not None
        assert sectional_data.y_cen is not None
        
        n_sec = len(sectional_data.y_cen)
        n_time = len(sectional_data.time)
        
        assert sectional_data.sec.shape == (n_time, n_sec)


class TestChordwise:
    """Test suite for chordwise data parsing"""
    
    @pytest.mark.skipif(
        not os.path.exists(os.path.join(TEST_DATA_FOLDER, 'test_chordwise.dat')),
        reason="Test chordwise data file not available"
    )
    def test_read_chordwise(self):
        """Test that chordwise data is read correctly"""
        chord_data = read_chordwise(os.path.join(TEST_DATA_FOLDER, 'test_chordwise.dat'))
        
        assert chord_data.x_ref is not None
        assert chord_data.z_ref is not None
        assert chord_data.chord_data is not None
        assert chord_data.time is not None
        
        n_chord = len(chord_data.x_ref)
        n_time = len(chord_data.time)
        
        assert len(chord_data.z_ref) == n_chord
        assert chord_data.chord_data.shape == (n_time, n_chord)


class TestIntegral:
    """Test suite for integral loads parsing"""
    
    @pytest.mark.skipif(
        not os.path.exists(os.path.join(TEST_DATA_FOLDER, 'test_integral.dat')),
        reason="Test integral data file not available"
    )
    def test_read_integral(self):
        """Test that integral loads are read correctly"""
        integral_data = read_integral(os.path.join(TEST_DATA_FOLDER, 'test_integral.dat'))
        
        assert integral_data.forces is not None
        assert integral_data.moments is not None
        assert integral_data.time is not None
        
        n_time = len(integral_data.time)
        
        assert integral_data.forces.shape == (n_time, 3)
        assert integral_data.moments.shape == (n_time, 3)


class TestHinge:
    """Test suite for hinge loads parsing"""
    
    @pytest.mark.skipif(
        not os.path.exists(os.path.join(TEST_DATA_FOLDER, 'test_hinge.dat')),
        reason="Test hinge data file not available"
    )
    def test_read_hinge(self):
        """Test that hinge loads are read correctly"""
        hinge_data = read_hinge(os.path.join(TEST_DATA_FOLDER, 'test_hinge.dat'))
        
        assert hinge_data.forces is not None
        assert hinge_data.moments is not None
        assert hinge_data.time is not None
        
        n_time = len(hinge_data.time)
        
        assert hinge_data.forces.shape == (n_time, 3)
        assert hinge_data.moments.shape == (n_time, 3)


if __name__ == '__main__':
    pytest.main([__file__, '-v'])