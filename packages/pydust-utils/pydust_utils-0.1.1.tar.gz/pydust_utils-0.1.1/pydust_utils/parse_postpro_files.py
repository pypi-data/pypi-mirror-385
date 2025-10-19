"""Parse DUST post-processing output files.

This module provides functions to read and parse various DUST output files
including sectional loads, probe data, chordwise distributions, integral loads,
and hinge loads.
"""

from typing import Optional, Union
from dataclasses import dataclass
import numpy as np
import pandas as pd
from numpy.typing import NDArray

__all__ = [
    'SectionalData',
    'ProbesData',
    'ChordwiseData',
    'IntegralData',
    'HingeData',
    'read_sectional',
    'read_probes',
    'read_chordwise',
    'read_integral',
    'read_hinge',
]


@dataclass
class SectionalData:
    """Container for sectional loads data.
    
    Attributes:
        time: Time values array (n_time,)
        y_cen: Spanwise center locations array (n_sections,)
        sec: Sectional data array (n_time, n_sections)
    """
    time: NDArray[np.floating]
    y_cen: NDArray[np.floating]
    sec: NDArray[np.floating]


@dataclass
class ProbesData:
    """Container for probe data.
    
    Attributes:
        time: Time values array (n_time,)
        x: X coordinates array (n_probes,)
        y: Y coordinates array (n_probes,)
        z: Z coordinates array (n_probes,)
        data: Probe data array (n_time, n_probes)
    """
    time: NDArray[np.floating]
    x: NDArray[np.floating]
    y: NDArray[np.floating]
    z: NDArray[np.floating]
    data: NDArray[np.floating]


@dataclass
class ChordwiseData:
    """Container for chordwise distribution data.
    
    Attributes:
        time: Time values array (n_time,)
        y_cen: Spanwise center locations array (n_sections,)
        x_cen: Chordwise center locations array (n_chord,)
        chord: Chordwise data array (n_time, n_sections, n_chord)
    """
    time: NDArray[np.floating]
    y_cen: NDArray[np.floating]
    x_cen: NDArray[np.floating]
    chord: NDArray[np.floating]


@dataclass
class IntegralData:
    """Container for integral loads data.
    
    Attributes:
        time: Time values array (n_time,)
        forces: Forces array (n_time, 3) - [Fx, Fy, Fz]
        moments: Moments array (n_time, 3) - [Mx, My, Mz]
    """
    time: NDArray[np.floating]
    forces: NDArray[np.floating]
    moments: NDArray[np.floating]


@dataclass
class HingeData:
    """Container for hinge loads data.
    
    Attributes:
        time: Time values array (n_time,)
        forces: Hinge forces array (n_time, n_hinges)
        moments: Hinge moments array (n_time, n_hinges)
    """
    time: NDArray[np.floating]
    forces: NDArray[np.floating]
    moments: NDArray[np.floating]


def read_sectional(filename: str) -> SectionalData:
    """Read sectional loads data from DUST output file.
    
    Args:
        filename: Path to sectional loads file
        
    Returns:
        SectionalData object containing time, y_cen, and sec arrays
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file format is invalid
        
    Example:
        >>> data = read_sectional('sectional_loads.dat')
        >>> print(f"Time steps: {len(data.time)}")
        >>> print(f"Sections: {len(data.y_cen)}")
    """
    import re
    
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
    except FileNotFoundError:
        raise FileNotFoundError(f"Sectional loads file not found: {filename}")
    except Exception as e:
        raise ValueError(f"Error reading sectional loads file: {e}")
    
    # Extract n_sec and n_time from header
    n_sec, n_time = None, None
    for line in lines:
        if line.startswith('# n_sec'):
            match = re.search(r"# n_sec\s*:\s*(\d+)\s*;\s*n_time\s*:\s*(\d+)", line)
            if match:
                n_sec = int(match.group(1))
                n_time = int(match.group(2))
                break
    
    if n_sec is None or n_time is None:
        raise ValueError(f"Could not find n_sec and n_time in file header: {filename}")
    
    # Find data start (after y_cen, y_span, chord line)
    data_start_index = next(i for i, l in enumerate(lines) if 'y_cen' in l) + 1
    data_lines = [line for line in lines[data_start_index:] if not line.startswith('#')]
    
    # Parse first 3 lines: y_cen, y_span, chord
    y_cen = np.array(data_lines[0].split(), dtype=np.float64)
    # y_span = np.array(data_lines[1].split(), dtype=np.float64)  # Not used
    # chord = np.array(data_lines[2].split(), dtype=np.float64)  # Not used
    
    # Parse remaining data: time + sectional loads
    data_raw = []
    for line in data_lines[3:]:
        data_raw.append(list(map(float, line.split())))
    
    data = np.array(data_raw)
    # Reshape to (n_time, n_sec + 13) where 13 = 1 (time) + 9 (ref_mat) + 3 (ref_off)
    data = data.reshape(n_time, -1, order='F')
    
    # Extract time and sectional data (remove last 12 columns which are ref_mat and ref_off)
    time = data[:, 0]
    sec = data[:, 1:n_sec+1]
    
    return SectionalData(
        time=np.asarray(time, dtype=np.float64),
        y_cen=np.asarray(y_cen, dtype=np.float64),
        sec=np.asarray(sec, dtype=np.float64)
    )


def read_probes(filename: str) -> ProbesData:
    """Read probe data from DUST output file.
    
    Args:
        filename: Path to probes file
        
    Returns:
        ProbesData object containing time, coordinates, and data arrays
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file format is invalid
        
    Example:
        >>> data = read_probes('probes_velocity.dat')
        >>> print(f"Probes: {len(data.x)}")
        >>> print(f"Time steps: {len(data.time)}")
    """
    import re
    
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
    except FileNotFoundError:
        raise FileNotFoundError(f"Probes file not found: {filename}")
    except Exception as e:
        raise ValueError(f"Error reading probes file: {e}")
    
    # Extract n_probes and n_time from headers
    n_probes, n_time = None, None
    line_probe, line_time = None, None
    
    for i, line in enumerate(lines):
        if line.startswith(' # N. of point probes:'):
            match = re.search(r"(\d+)$", line)
            if match:
                n_probes = int(match.group(1))
                line_probe = i
        elif line.startswith('# n_time:'):
            match = re.search(r"(\d+)$", line)
            if match:
                n_time = int(match.group(1))
                line_time = i
                break
    
    if n_probes is None or n_time is None or line_probe is None or line_time is None:
        raise ValueError(f"Could not find n_probes and n_time in file header: {filename}")
    
    # Parse probe locations (3 lines: x, y, z coordinates)
    locations = np.zeros((3, n_probes))
    for i in range(3):
        probe_line = lines[line_probe + i + 1]
        locations[i, :] = np.array(probe_line.split(), dtype=np.float64)
    
    x, y, z = locations[0, :], locations[1, :], locations[2, :]
    
    # Parse time series data
    time = np.zeros(n_time)
    velocities = np.zeros((n_time, n_probes, 3))
    
    for i in range(n_time):
        time_line = lines[line_time + i + 2]
        values = np.array(time_line.split(), dtype=np.float64)
        time[i] = values[0]
        velocities[i, :, :] = values[1:].reshape(n_probes, 3)
    
    return ProbesData(
        time=np.asarray(time, dtype=np.float64),
        x=np.asarray(x, dtype=np.float64),
        y=np.asarray(y, dtype=np.float64),
        z=np.asarray(z, dtype=np.float64),
        data=np.asarray(velocities, dtype=np.float64)
    )


def read_chordwise(filename: str) -> ChordwiseData:
    """Read chordwise distribution data from DUST output file.
    
    Args:
        filename: Path to chordwise data file
        
    Returns:
        ChordwiseData object containing time, y_cen, x_cen, and chord arrays
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file format is invalid
        
    Example:
        >>> data = read_chordwise('chordwise_cp.dat')
        >>> print(f"Sections: {len(data.y_cen)}")
        >>> print(f"Chordwise points: {len(data.x_cen)}")
    """
    import re
    
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
    except FileNotFoundError:
        raise FileNotFoundError(f"Chordwise data file not found: {filename}")
    except Exception as e:
        raise ValueError(f"Error reading chordwise data file: {e}")
    
    # Extract n_chord and n_time from header
    n_chord, n_time = None, None
    for line in lines:
        if line.startswith('# n_chord'):
            match = re.search(r"# n_chord\s*:\s*(\d+)\s*;\s*n_time\s*:\s*(\d+)", line)
            if match:
                n_chord = int(match.group(1))
                n_time = int(match.group(2))
                break
    
    if n_chord is None or n_time is None:
        raise ValueError(f"Could not find n_chord and n_time in file header: {filename}")
    
    # Find data start (after x_chord, z_chord line)
    data_start_index = next(i for i, l in enumerate(lines) if 'x_chord' in l) + 1
    data_lines = [line for line in lines[data_start_index:] if not line.startswith('#')]
    
    # Parse first 2 lines: x_chord, z_chord coordinates
    x_cen = np.array(data_lines[0].split(), dtype=np.float64)
    # z_chord = np.array(data_lines[1].split(), dtype=np.float64)  # Not used
    
    # Parse time series data: time + Cp values
    time = np.zeros(n_time)
    chord = np.zeros((n_time, n_chord))
    
    for i in range(n_time):
        time_line = data_lines[2 + i]
        values = np.array(time_line.split(), dtype=np.float64)
        time[i] = values[0]
        chord[i, :] = values[1:n_chord+1]
    
    # For single spanwise location, y_cen is extracted from header
    y_cen = np.array([0.0])  # Placeholder, actual value in header
    for line in lines:
        if 'spanwise_location' in line:
            match = re.search(r"spanwise_location:\s*([\d.]+)", line)
            if match:
                y_cen = np.array([float(match.group(1))])
                break
    
    return ChordwiseData(
        time=np.asarray(time, dtype=np.float64),
        y_cen=np.asarray(y_cen, dtype=np.float64),
        x_cen=np.asarray(x_cen, dtype=np.float64),
        chord=np.asarray(chord[:, :, np.newaxis], dtype=np.float64).transpose(0, 2, 1)  # Shape: (n_time, 1, n_chord)
    )


def read_integral(filename: str) -> IntegralData:
    """Read integral loads data from DUST output file.
    
    Args:
        filename: Path to integral loads file
        
    Returns:
        IntegralData object containing time, forces, and moments arrays
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file format is invalid
        
    Example:
        >>> data = read_integral('integral_loads.dat')
        >>> print(f"Max lift: {data.forces[:, 2].max()}")
        >>> print(f"Drag: {data.forces[:, 0]}")
    """
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
    except FileNotFoundError:
        raise FileNotFoundError(f"Integral loads file not found: {filename}")
    except Exception as e:
        raise ValueError(f"Error reading integral loads file: {e}")
    
    # Skip comment lines and empty lines
    data_lines = [line for line in lines if not line.strip().startswith('#') and line.strip()]
    
    if not data_lines:
        raise ValueError(f"Integral loads file has no data: {filename}")
    
    # Parse data: time, Fx, Fy, Fz, Mx, My, Mz, ref_mat(9), ref_off(3)
    data_list = []
    for line in data_lines:
        try:
            values = list(map(float, line.split()))
            data_list.append(values)
        except ValueError:
            # Skip lines that can't be parsed as floats
            continue
    
    data: NDArray[np.floating] = np.array(data_list, dtype=np.float64)
    
    # Extract columns: time, forces (Fx, Fy, Fz), moments (Mx, My, Mz)
    # Ignore ref_mat and ref_off (last 12 columns)
    time = data[:, 0]
    forces = data[:, 1:4]  # Fx, Fy, Fz
    moments = data[:, 4:7]  # Mx, My, Mz
    
    return IntegralData(
        time=np.asarray(time, dtype=np.float64),
        forces=np.asarray(forces, dtype=np.float64),
        moments=np.asarray(moments, dtype=np.float64)
    )


def read_hinge(filename: str) -> HingeData:
    """Read hinge loads data from DUST output file.
    
    Args:
        filename: Path to hinge loads file
        
    Returns:
        HingeData object containing time, hinge_id, forces, and moments arrays
        
    Raises:
        FileNotFoundError: If file doesn't exist
        ValueError: If file format is invalid
        
    Example:
        >>> data = read_hinge('hinge_loads.dat')
        >>> print(f"Hinges: {len(data.hinge_id)}")
        >>> print(f"Hinge moments: {data.moments}")
    """
    try:
        with open(filename, 'r') as file:
            lines = file.readlines()
    except FileNotFoundError:
        raise FileNotFoundError(f"Hinge loads file not found: {filename}")
    except Exception as e:
        raise ValueError(f"Error reading hinge loads file: {e}")
    
    # Skip comment lines and empty lines
    data_lines = [line for line in lines if not line.strip().startswith('#') and line.strip()]
    
    if not data_lines:
        raise ValueError(f"Hinge loads file has no data: {filename}")
    
    # Parse data: time, Fv, Fh, Fn, Mv, Mh, Mn, axis_mat(9), node_hinge(3)
    data_list = []
    for line in data_lines:
        try:
            values = list(map(float, line.split()))
            data_list.append(values)
        except ValueError:
            # Skip lines that can't be parsed as floats
            continue
    
    data: NDArray[np.floating] = np.array(data_list, dtype=np.float64)
    
    # Extract columns: time, forces (Fv, Fh, Fn), moments (Mv, Mh, Mn)
    # Ignore axis_mat and node_hinge (last 12 columns)
    time = data[:, 0]
    forces = data[:, 1:4]  # Fv, Fh, Fn
    moments = data[:, 4:7]  # Mv, Mh, Mn

    return HingeData(
        time=np.asarray(time, dtype=np.float64),
        forces=np.asarray(forces, dtype=np.float64),
        moments=np.asarray(moments, dtype=np.float64)
    )