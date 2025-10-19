"""Tests for parse_postpro_files module."""

import os
import pytest
import numpy as np
from pathlib import Path
from pydust_utils import postpro

# Define test data folder path
TEST_DATA_FOLDER = Path(__file__).parent / 'dat_files'


# ============================================================================
# Sectional Data Tests
# ============================================================================

class TestSectional:
    """Test suite for sectional data parsing."""
    
    @pytest.mark.skipif(
        not (TEST_DATA_FOLDER / 'test_sectional.dat').exists(),
        reason="Test sectional data file not available"
    )
    def test_read_sectional_basic(self):
        """Test that sectional data is read correctly."""
        filepath = TEST_DATA_FOLDER / 'test_sectional.dat'
        data = postpro.read_sectional(str(filepath))
        
        # Check attributes exist
        assert hasattr(data, 'time')
        assert hasattr(data, 'y_cen')
        assert hasattr(data, 'sec')
        
        # Check types
        assert isinstance(data.time, np.ndarray)
        assert isinstance(data.y_cen, np.ndarray)
        assert isinstance(data.sec, np.ndarray)
        
        # Check shapes are consistent
        assert len(data.time) > 0
        assert len(data.y_cen) > 0
        assert data.sec.shape == (len(data.time), len(data.y_cen))
        
        # Check dtypes
        assert data.time.dtype == np.float64
        assert data.y_cen.dtype == np.float64
        assert data.sec.dtype == np.float64
        
        # Validate actual values from file
        # First data point
        assert np.isclose(data.time[0], 0.134875134875135)
        assert np.isclose(data.y_cen[0], 0.0394014258346759)
        assert np.isclose(data.sec[0, 0], 2.44598700980664)
        # Last data point
        assert np.isclose(data.time[-1], 0.149875149875150)
        assert np.isclose(data.sec[-1, -1], 16.7119091697773)
    
    @pytest.mark.skipif(
        not (TEST_DATA_FOLDER / 'test_sectional.dat').exists(),
        reason="Test sectional data file not available"
    )
    def test_sectional_data_structure(self):
        """Test sectional data structure and values."""
        filepath = TEST_DATA_FOLDER / 'test_sectional.dat'
        data = postpro.read_sectional(str(filepath))
        
        # Time should be monotonically increasing
        assert np.all(np.diff(data.time) >= 0)
        
        # No NaN values
        assert not np.any(np.isnan(data.time))
        assert not np.any(np.isnan(data.y_cen))
        assert not np.any(np.isnan(data.sec))
        
        # All finite values
        assert np.all(np.isfinite(data.time))
        assert np.all(np.isfinite(data.y_cen))
        assert np.all(np.isfinite(data.sec))
    
    def test_sectional_file_not_found(self):
        """Test that FileNotFoundError is raised for missing file."""
        with pytest.raises(FileNotFoundError, match="not found"):
            postpro.read_sectional('nonexistent_file.dat')


# ============================================================================
# Probes Data Tests
# ============================================================================

class TestProbes:
    """Test suite for probe data parsing."""
    
    @pytest.mark.skipif(
        not (TEST_DATA_FOLDER / 'test_probes.dat').exists(),
        reason="Test probes data file not available"
    )
    def test_read_probes_basic(self):
        """Test that probe data is read correctly."""
        filepath = TEST_DATA_FOLDER / 'test_probes.dat'
        data = postpro.read_probes(str(filepath))
        
        # Check attributes exist
        assert hasattr(data, 'time')
        assert hasattr(data, 'x')
        assert hasattr(data, 'y')
        assert hasattr(data, 'z')
        assert hasattr(data, 'data')
        
        # Check types
        assert isinstance(data.time, np.ndarray)
        assert isinstance(data.x, np.ndarray)
        assert isinstance(data.y, np.ndarray)
        assert isinstance(data.z, np.ndarray)
        assert isinstance(data.data, np.ndarray)
        
        # Check shapes are consistent
        n_probes = len(data.x)
        assert len(data.y) == n_probes
        assert len(data.z) == n_probes
        assert data.data.shape[1] == n_probes
        assert data.data.shape[0] == len(data.time)
        
        # Check dtypes
        assert data.time.dtype == np.float64
        assert data.x.dtype == np.float64
        assert data.y.dtype == np.float64
        assert data.z.dtype == np.float64
        assert data.data.dtype == np.float64
        
        # Validate actual values from file
        # First probe coordinates
        assert np.isclose(data.x[0], 0.0)
        assert np.isclose(data.y[0], 0.0)
        assert np.isclose(data.z[0], -0.04)
        # Last probe coordinates  
        assert np.isclose(data.x[-1], 0.24)
        assert np.isclose(data.y[-1], 0.0)
        assert np.isclose(data.z[-1], -0.04)
        # First velocity data (ux, uy, uz for first probe)
        assert np.isclose(data.data[0, 0, 0], 0.0665431505933723)
        assert np.isclose(data.data[0, 0, 1], 0.0387543743481059)
        assert np.isclose(data.data[0, 0, 2], -4.38143731625720)
        # Last velocity data (uz for last probe)
        assert np.isclose(data.data[0, -1, 2], 1.58313648730237)
    
    @pytest.mark.skipif(
        not (TEST_DATA_FOLDER / 'test_probes.dat').exists(),
        reason="Test probes data file not available"
    )
    def test_probes_coordinates(self):
        """Test that probe coordinates are valid."""
        filepath = TEST_DATA_FOLDER / 'test_probes.dat'
        data = postpro.read_probes(str(filepath))
        
        # Coordinates should be finite
        assert np.all(np.isfinite(data.x))
        assert np.all(np.isfinite(data.y))
        assert np.all(np.isfinite(data.z))
        
        # Data should be finite
        assert np.all(np.isfinite(data.data))
        
        # Time should be monotonically increasing
        assert np.all(np.diff(data.time) >= 0)
    
    def test_probes_file_not_found(self):
        """Test that FileNotFoundError is raised for missing file."""
        with pytest.raises(FileNotFoundError, match="not found"):
            postpro.read_probes('nonexistent_file.dat')


# ============================================================================
# Chordwise Data Tests
# ============================================================================

class TestChordwise:
    """Test suite for chordwise data parsing."""
    
    @pytest.mark.skipif(
        not (TEST_DATA_FOLDER / 'test_chordwise.dat').exists(),
        reason="Test chordwise data file not available"
    )
    def test_read_chordwise_basic(self):
        """Test that chordwise data is read correctly."""
        filepath = TEST_DATA_FOLDER / 'test_chordwise.dat'
        data = postpro.read_chordwise(str(filepath))
        
        # Check attributes exist
        assert hasattr(data, 'time')
        assert hasattr(data, 'y_cen')
        assert hasattr(data, 'x_cen')
        assert hasattr(data, 'chord')
        
        # Check types
        assert isinstance(data.time, np.ndarray)
        assert isinstance(data.y_cen, np.ndarray)
        assert isinstance(data.x_cen, np.ndarray)
        assert isinstance(data.chord, np.ndarray)
        
        # Check shapes are consistent
        n_time = len(data.time)
        n_sections = len(data.y_cen)
        n_chord = len(data.x_cen)
        assert data.chord.shape == (n_time, n_sections, n_chord)
        
        # Check dtypes
        assert data.time.dtype == np.float64
        assert data.y_cen.dtype == np.float64
        assert data.x_cen.dtype == np.float64
        assert data.chord.dtype == np.float64
        
        # Validate actual values from file
        # First data point
        assert np.isclose(data.time[0], 0.0)
        assert np.isclose(data.y_cen[0], 3.0)
        assert np.isclose(data.x_cen[0], 1.47099806716085)
        assert np.isclose(data.chord[0, 0, 0], -0.654328469076783)
        # Last data point
        assert np.isclose(data.time[-1], 0.99)
        assert np.isclose(data.chord[-1, 0, -1], 0.145193138173354)
    
    @pytest.mark.skipif(
        not (TEST_DATA_FOLDER / 'test_chordwise.dat').exists(),
        reason="Test chordwise data file not available"
    )
    def test_chordwise_data_validity(self):
        """Test that chordwise data is valid."""
        filepath = TEST_DATA_FOLDER / 'test_chordwise.dat'
        data = postpro.read_chordwise(str(filepath))
        
        # All values should be finite
        assert np.all(np.isfinite(data.time))
        assert np.all(np.isfinite(data.y_cen))
        assert np.all(np.isfinite(data.x_cen))
        assert np.all(np.isfinite(data.chord))
        
        # Time should be monotonically increasing
        assert np.all(np.diff(data.time) >= 0)
        
        # Chordwise locations exist and have reasonable length
        assert len(data.x_cen) > 0
        # Note: x_cen doesn't need to be monotonic - it represents airfoil coordinates
        # which go from leading edge to trailing edge and back
    
    def test_chordwise_file_not_found(self):
        """Test that FileNotFoundError is raised for missing file."""
        with pytest.raises(FileNotFoundError, match="not found"):
            postpro.read_chordwise('nonexistent_file.dat')


# ============================================================================
# Integral Loads Tests
# ============================================================================

class TestIntegral:
    """Test suite for integral loads parsing."""
    
    @pytest.mark.skipif(
        not (TEST_DATA_FOLDER / 'test_integral.dat').exists(),
        reason="Test integral data file not available"
    )
    def test_read_integral_basic(self):
        """Test that integral loads are read correctly."""
        filepath = TEST_DATA_FOLDER / 'test_integral.dat'
        data = postpro.read_integral(str(filepath))
        
        # Check attributes exist
        assert hasattr(data, 'time')
        assert hasattr(data, 'forces')
        assert hasattr(data, 'moments')
        
        # Check types
        assert isinstance(data.time, np.ndarray)
        assert isinstance(data.forces, np.ndarray)
        assert isinstance(data.moments, np.ndarray)
        
        # Check shapes
        n_time = len(data.time)
        assert data.forces.shape == (n_time, 3)  # Fx, Fy, Fz
        assert data.moments.shape == (n_time, 3)  # Mx, My, Mz
        
        # Check dtypes
        assert data.time.dtype == np.float64
        assert data.forces.dtype == np.float64
        assert data.moments.dtype == np.float64
        
        # Validate actual values from file
        # First data point
        assert np.isclose(data.time[0], 0.0)
        assert np.isclose(data.forces[0, 2], 106.588508666019)  # Fz
        assert np.isclose(data.moments[0, 2], -4.65363050774746)  # Mz
        # Last data point
        assert np.isclose(data.time[-1], 0.149875149875150)
        assert np.isclose(data.forces[-1, 0], 0.0249620681505069)  # Fx
        assert np.isclose(data.moments[-1, 2], -0.826769689114582)  # Mz
    
    @pytest.mark.skipif(
        not (TEST_DATA_FOLDER / 'test_integral.dat').exists(),
        reason="Test integral data file not available"
    )
    def test_integral_data_validity(self):
        """Test that integral load values are valid."""
        filepath = TEST_DATA_FOLDER / 'test_integral.dat'
        data = postpro.read_integral(str(filepath))
        
        # All values should be finite
        assert np.all(np.isfinite(data.time))
        assert np.all(np.isfinite(data.forces))
        assert np.all(np.isfinite(data.moments))
        
        # Time should be monotonically increasing
        assert np.all(np.diff(data.time) >= 0)
        
        # Forces and moments should have reasonable magnitudes (not all zeros)
        assert not np.allclose(data.forces, 0.0) or not np.allclose(data.moments, 0.0)
    
    def test_integral_file_not_found(self):
        """Test that FileNotFoundError is raised for missing file."""
        with pytest.raises(FileNotFoundError, match="not found"):
            postpro.read_integral('nonexistent_file.dat')


# ============================================================================
# Hinge Loads Tests
# ============================================================================

class TestHinge:
    """Test suite for hinge loads parsing."""
    
    @pytest.mark.skipif(
        not (TEST_DATA_FOLDER / 'test_hinge.dat').exists(),
        reason="Test hinge data file not available"
    )
    def test_read_hinge_basic(self):
        """Test that hinge loads are read correctly."""
        filepath = TEST_DATA_FOLDER / 'test_hinge.dat'
        data = postpro.read_hinge(str(filepath))
        
        # Check attributes exist
        assert hasattr(data, 'time')
        assert hasattr(data, 'forces') 
        assert hasattr(data, 'moments')
        
        # Check types
        assert isinstance(data.time, np.ndarray)
        assert isinstance(data.forces, np.ndarray)
        assert isinstance(data.moments, np.ndarray)
        
        # Check shapes are consistent
        n_time = len(data.time)
        assert data.forces.shape == (n_time, 3) # Fv, Fh, Fn
        assert data.moments.shape == (n_time, 3) # Mv, Mh, Mn
        
        # Check dtypes
        assert data.time.dtype == np.float64
        assert data.forces.dtype == np.float64
        assert data.moments.dtype == np.float64
        
        # Validate actual values from file
        # First data point
        assert np.isclose(data.time[0], 0.0)
        assert np.isclose(data.forces[0, 0], 64.5413801417535)  # Fv
        assert np.isclose(data.moments[0, 2], -63.9090751301546)  # Mn
        # Last data point
        assert np.isclose(data.time[-1], 0.99)
        assert np.isclose(data.forces[-1, 0], 5.75911234279239)  # Fv
        assert np.isclose(data.moments[-1, 2], -5.70829615266029)  # Mn
    
    @pytest.mark.skipif(
        not (TEST_DATA_FOLDER / 'test_hinge.dat').exists(),
        reason="Test hinge data file not available"
    )
    def test_hinge_data_validity(self):
        """Test that hinge load values are valid."""
        filepath = TEST_DATA_FOLDER / 'test_hinge.dat'
        data = postpro.read_hinge(str(filepath))
        
        # All values should be finite
        assert np.all(np.isfinite(data.time))
        assert np.all(np.isfinite(data.forces))
        assert np.all(np.isfinite(data.moments))
        
        # Time should be monotonically increasing
        assert np.all(np.diff(data.time) >= 0)

    def test_hinge_file_not_found(self):
        """Test that FileNotFoundError is raised for missing file."""
        with pytest.raises(FileNotFoundError, match="not found"):
            postpro.read_hinge('nonexistent_file.dat')


# ============================================================================
# Integration Tests
# ============================================================================

class TestIntegration:
    """Integration tests using real data files."""
    
    @pytest.mark.skipif(
        not (TEST_DATA_FOLDER / 'test_sectional.dat').exists(),
        reason="Test sectional data file not available"
    )
    def test_sectional_workflow(self):
        """Test complete sectional data analysis workflow."""
        filepath = TEST_DATA_FOLDER / 'test_sectional.dat'
        data = postpro.read_sectional(str(filepath))
        
        # Perform typical analysis operations
        mean_loads = np.mean(data.sec, axis=0)
        max_loads = np.max(data.sec, axis=0)
        
        assert len(mean_loads) == len(data.y_cen)
        assert len(max_loads) == len(data.y_cen)
        assert np.all(max_loads >= mean_loads)
    
    @pytest.mark.skipif(
        not (TEST_DATA_FOLDER / 'test_integral.dat').exists(),
        reason="Test integral data file not available"
    )
    def test_integral_workflow(self):
        """Test complete integral loads analysis workflow."""
        filepath = TEST_DATA_FOLDER / 'test_integral.dat'
        data = postpro.read_integral(str(filepath))
        
        # Calculate typical aerodynamic metrics
        mean_lift = np.mean(data.forces[:, 2])  # Fz
        max_lift = np.max(data.forces[:, 2])
        mean_drag = np.mean(data.forces[:, 0])  # Fx
        
        # Check that calculations work
        assert np.isfinite(mean_lift)
        assert np.isfinite(max_lift)
        assert np.isfinite(mean_drag)


# ============================================================================
# Error Handling Tests
# ============================================================================

class TestErrorHandling:
    """Test error handling for various edge cases."""
    
    def test_empty_filename(self):
        """Test handling of empty filename."""
        with pytest.raises(FileNotFoundError):
            postpro.read_sectional('')
    
    def test_invalid_file_type(self):
        """Test handling of invalid file types."""
        # Create a non-existent file path
        with pytest.raises(FileNotFoundError):
            postpro.read_sectional('test.invalid')
    
    def test_sectional_malformed_header(self, tmp_path):
        """Test handling of malformed sectional file header."""
        test_file = tmp_path / "malformed_sectional.dat"
        test_file.write_text("# This is a file without proper header\n0.0 1.0 2.0\n")
        
        with pytest.raises(ValueError, match="Could not find n_sec and n_time"):
            postpro.read_sectional(str(test_file))
    
    def test_probes_malformed_header(self, tmp_path):
        """Test handling of malformed probes file header."""
        test_file = tmp_path / "malformed_probes.dat"
        test_file.write_text("# This is a file without proper header\n0.0 1.0 2.0\n")
        
        with pytest.raises(ValueError, match="Could not find n_probes and n_time"):
            postpro.read_probes(str(test_file))
    
    def test_chordwise_malformed_header(self, tmp_path):
        """Test handling of malformed chordwise file header."""
        test_file = tmp_path / "malformed_chordwise.dat"
        test_file.write_text("# This is a file without proper header\n0.0 1.0 2.0\n")
        
        with pytest.raises(ValueError, match="Could not find n_chord and n_time"):
            postpro.read_chordwise(str(test_file))
    
    def test_integral_empty_data(self, tmp_path):
        """Test handling of integral file with only comments."""
        test_file = tmp_path / "empty_integral.dat"
        test_file.write_text("# Header\n# More comments\n# No actual data\n")
        
        with pytest.raises(ValueError, match="has no data"):
            postpro.read_integral(str(test_file))
    
    def test_hinge_empty_data(self, tmp_path):
        """Test handling of hinge file with only comments."""
        test_file = tmp_path / "empty_hinge.dat"
        test_file.write_text("# Header\n# More comments\n# No actual data\n")
        
        with pytest.raises(ValueError, match="has no data"):
            postpro.read_hinge(str(test_file))
    
    def test_integral_with_invalid_lines(self, tmp_path):
        """Test handling of integral file with some invalid data lines."""
        test_file = tmp_path / "mixed_integral.dat"
        # Mix valid and invalid lines
        test_file.write_text(
            "# Header\n"
            "0.0 1.0 2.0 3.0 4.0 5.0 6.0 1.0 0.0 0.0 0.0 1.0 0.0 0.0 0.0 1.0 0.0 0.0 0.0\n"
            "invalid line with text\n"
            "0.1 1.1 2.1 3.1 4.1 5.1 6.1 1.0 0.0 0.0 0.0 1.0 0.0 0.0 0.0 1.0 0.0 0.0 0.0\n"
        )
        
        # Should skip invalid line and parse valid ones
        data = postpro.read_integral(str(test_file))
        assert len(data.time) == 2  # Only 2 valid lines
    
    def test_hinge_with_invalid_lines(self, tmp_path):
        """Test handling of hinge file with some invalid data lines."""
        test_file = tmp_path / "mixed_hinge.dat"
        # Mix valid and invalid lines
        test_file.write_text(
            "# Header\n"
            "0.0 1.0 2.0 3.0 4.0 5.0 6.0 1.0 0.0 0.0 0.0 1.0 0.0 0.0 0.0 1.0 0.5 2.0 0.0\n"
            "bad data here\n"
            "0.1 1.1 2.1 3.1 4.1 5.1 6.1 1.0 0.0 0.0 0.0 1.0 0.0 0.0 0.0 1.0 0.5 2.0 0.0\n"
        )
        
        # Should skip invalid line and parse valid ones
        data = postpro.read_hinge(str(test_file))
        assert len(data.time) == 2  # Only 2 valid lines
    
    def test_sectional_permission_error(self, tmp_path, monkeypatch):
        """Test handling of generic exceptions when reading sectional file."""
        test_file = tmp_path / "test.dat"
        test_file.write_text("dummy")
        
        def mock_open(*args, **kwargs):
            raise PermissionError("Permission denied")
        
        monkeypatch.setattr("builtins.open", mock_open)
        
        with pytest.raises(ValueError, match="Error reading sectional loads file"):
            postpro.read_sectional(str(test_file))
    
    def test_probes_permission_error(self, tmp_path, monkeypatch):
        """Test handling of generic exceptions when reading probes file."""
        test_file = tmp_path / "test.dat"
        test_file.write_text("dummy")
        
        def mock_open(*args, **kwargs):
            raise PermissionError("Permission denied")
        
        monkeypatch.setattr("builtins.open", mock_open)
        
        with pytest.raises(ValueError, match="Error reading probes file"):
            postpro.read_probes(str(test_file))
    
    def test_chordwise_permission_error(self, tmp_path, monkeypatch):
        """Test handling of generic exceptions when reading chordwise file."""
        test_file = tmp_path / "test.dat"
        test_file.write_text("dummy")
        
        def mock_open(*args, **kwargs):
            raise PermissionError("Permission denied")
        
        monkeypatch.setattr("builtins.open", mock_open)
        
        with pytest.raises(ValueError, match="Error reading chordwise data file"):
            postpro.read_chordwise(str(test_file))
    
    def test_integral_permission_error(self, tmp_path, monkeypatch):
        """Test handling of generic exceptions when reading integral file."""
        test_file = tmp_path / "test.dat"
        test_file.write_text("dummy")
        
        def mock_open(*args, **kwargs):
            raise PermissionError("Permission denied")
        
        monkeypatch.setattr("builtins.open", mock_open)
        
        with pytest.raises(ValueError, match="Error reading integral loads file"):
            postpro.read_integral(str(test_file))
    
    def test_hinge_permission_error(self, tmp_path, monkeypatch):
        """Test handling of generic exceptions when reading hinge file."""
        test_file = tmp_path / "test.dat"
        test_file.write_text("dummy")
        
        def mock_open(*args, **kwargs):
            raise PermissionError("Permission denied")
        
        monkeypatch.setattr("builtins.open", mock_open)
        
        with pytest.raises(ValueError, match="Error reading hinge loads file"):
            postpro.read_hinge(str(test_file))


if __name__ == '__main__':
    pytest.main([__file__, '-v'])