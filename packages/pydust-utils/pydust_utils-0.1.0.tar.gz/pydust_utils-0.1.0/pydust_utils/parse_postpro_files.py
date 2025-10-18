"""
Post-Processing File Parsers
=============================

This module provides parsers for various DUST post-processing output files.
Each parser returns a structured dataclass containing the parsed data.

Available parsers:
    - :func:`read_sectional`: Parse sectional aerodynamic loads
    - :func:`read_probes`: Parse velocity probe data
    - :func:`read_chordwise`: Parse chordwise distribution data
    - :func:`read_integral`: Parse integral loads
    - :func:`read_hinge`: Parse hinge loads

Data Structures:
    - :class:`SectionalData`: Container for sectional loads
    - :class:`ProbesData`: Container for probe velocities
    - :class:`ChordwiseData`: Container for chordwise distributions
    - :class:`IntegralData`: Container for integral loads
    - :class:`HingeData`: Container for hinge loads
"""

import re
import pandas as pd
import numpy as np
from dataclasses import dataclass 

@dataclass
class SectionalData:
    """Structure for sectional aerodynamic data.
    
    Attributes
    ----------
    sec : np.ndarray
        Sectional load data with shape (n_time, n_sec)
    time : np.ndarray
        Time values with shape (n_time,)
    y_cen : np.ndarray
        Spanwise center positions with shape (n_sec,)
    """
    sec: np.ndarray
    time: np.ndarray
    y_cen: np.ndarray

@dataclass
class ProbesData:
    """Structure for probe velocity data.
    
    Attributes
    ----------
    locations : np.ndarray
        Probe spatial coordinates with shape (n_probes, 3)
    time : np.ndarray
        Time values with shape (n_time,)
    velocities : np.ndarray
        Velocity components at each probe with shape (n_time, n_probes, 3)
    """
    locations: np.ndarray
    time: np.ndarray
    velocities: np.ndarray

@dataclass
class ChordwiseData:
    """Structure for chordwise distribution data.
    
    Attributes
    ----------
    x_ref : np.ndarray
        Chordwise reference x-coordinates with shape (n_chord,)
    z_ref : np.ndarray
        Chordwise reference z-coordinates with shape (n_chord,)
    chord_data : np.ndarray
        Chordwise distribution values with shape (n_time, n_chord)
    time : np.ndarray
        Time values with shape (n_time,)
    spanwise_location : float
        Spanwise location where chordwise data is extracted
    chord_length : float
        Local chord length at the spanwise location
    """
    x_ref: np.ndarray
    z_ref: np.ndarray
    chord_data: np.ndarray
    time: np.ndarray
    spanwise_location: float
    chord_length: float

@dataclass
class IntegralData:
    """Structure for integral loads data.
    
    Attributes
    ----------
    forces : np.ndarray
        Force components (Fx, Fy, Fz) with shape (n_time, 3)
    moments : np.ndarray
        Moment components (Mx, My, Mz) with shape (n_time, 3)
    time : np.ndarray
        Time values with shape (n_time,)
    """
    forces: np.ndarray
    moments: np.ndarray
    time: np.ndarray

@dataclass
class HingeData:
    """Structure for hinge loads data.
    
    Attributes
    ----------
    forces : np.ndarray
        Force components (Fx, Fy, Fz) with shape (n_time, 3)
    moments : np.ndarray
        Moment components (Mx, My, Mz) with shape (n_time, 3)
    time : np.ndarray
        Time values with shape (n_time,)
    """
    forces: np.ndarray
    moments: np.ndarray
    time: np.ndarray

def read_sectional(filename):
    """Parse sectional aerodynamic loads from DUST output file.
    
    Reads a DUST sectional loads file containing time-varying aerodynamic
    loads distributed along the span.
    
    Parameters
    ----------
    filename : str or Path
        Path to the sectional loads output file
    
    Returns
    -------
    SectionalData
        Structured data containing sectional loads, time history, and
        spanwise positions
        
    Raises
    ------
    ValueError
        If file format is incorrect or required metadata is missing
    FileNotFoundError
        If the specified file does not exist
        
    Examples
    --------
    >>> data = read_sectional('sectional_loads.dat')
    >>> print(data.sec.shape)
    (1000, 20)  # 1000 time steps, 20 spanwise sections
    >>> print(data.time[0])
    0.0
    >>> print(data.y_cen)
    [0.1 0.2 0.3 ... 1.8 1.9 2.0]
    
    Notes
    -----
    The file format expects:
    - Header line with n_sec and n_time metadata
    - Three lines containing y_cen, y_span, and chord data
    - Time series data in column-major order
    """
    
    # Initialize variables
    n_sec, n_time = None, None
    # Reading the file to process line by line
    with open(filename, 'r') as file:
        lines = file.readlines()

    # Extracting n_sec and n_time from the header line
    for line in lines:
        if line.startswith('# n_sec'):
            match = re.search(r"# n_sec\s*:\s*(\d+)\s*;\s*n_time\s*:\s*(\d+)", line)
            if match:
                n_sec = int(match.group(1))
                n_time = int(match.group(2))
            else:
                raise ValueError("The line format is incorrect or n_sec and n_time are missing.")
            break

    # Parsing the data starting from the "y_cen, y_span, chord" line
    data_start_index = lines.index(next(l for l in lines if 'y_cen' in l)) + 1
    data_lines = [line for line in lines[data_start_index:] if not line.startswith('#')]

    # Creating a DataFrame for the first 3 lines of data
    df = pd.DataFrame(
        np.array([list(map(float, line.split())) for line in data_lines[:3]]).T,
        columns=['y_cen', 'y_span', 'chord']
    )

    data_lines = data_lines[3:] # Remove the first 3 lines from the data list to process the remaining data 

    # Create a DataFrame for the remaining data: they are a matrix of shape (n_time, time + n_sec + 9 + 3)
    data = np.array([list(map(float, line.split())) for line in data_lines]) 
    data = data.reshape(n_time, -1, order='F') # Reshape the data to (n_time, n_sec + 12)
    # delete the last 12 columns
    data = data[:, :-12] # Remove the last 12 columns   
    columns = ['time'] + [f'sec_{i}' for i in range(n_sec)] 
    df_data = pd.DataFrame(data, columns=columns) # Create a DataFrame for the data  

    # convert into np array of dimension (n_time, n_sec) 
    sec = df_data.iloc[:, 1:].values # Extract the sectional data
    time = df_data['time'].values # Extract the time data 
    y_cen = df['y_cen'].values # Extract the y_cen data

    return SectionalData(
        sec=sec, 
        time=time, 
        y_cen=y_cen
    )


def read_probes(filename):
    """Parse velocity probe data from DUST output file.
    
    Reads a DUST velocity probe file containing time-varying velocity
    measurements at fixed spatial locations.
    
    Parameters
    ----------
    filename : str or Path
        Path to the probe velocity output file
    
    Returns
    -------
    ProbesData
        Structured data containing probe locations, time history, and
        velocity components
        
    Raises
    ------
    ValueError
        If file format is incorrect or required metadata is missing
    FileNotFoundError
        If the specified file does not exist
        
    Examples
    --------
    >>> data = read_probes('probes_velocity.dat')
    >>> print(data.locations.shape)
    (10, 3)  # 10 probes with (x, y, z) coordinates
    >>> print(data.velocities.shape)
    (1000, 10, 3)  # 1000 time steps, 10 probes, 3 velocity components
    >>> print(data.velocities[0, 0, :])
    [1.2, 0.1, 0.05]  # (u, v, w) at first probe, first time step
    
    Notes
    -----
    The file format expects:
    - Header line with number of probes
    - Three lines containing x, y, z coordinates of probes
    - Header line with n_time
    - Time series data with time followed by velocity components
    """
    # Initialize variables
    n_probes, n_time = None, None
    # Reading the file to process line by line
    with open(filename, 'r') as file:
        lines = file.readlines()

    for line in lines:  
        if line.startswith(' # N. of point probes:'):
            match = re.search(r"(\d+)$", line) 
            line_probe = line   
            if match:
                n_probes = int(match.group(1))
            else:
                raise ValueError("The line format is incorrect or n_probes is missing.")
        elif line.startswith('# n_time:'): 
            match = re.search(r"(\d+)$", line)
            line_time = line 
            if match:
                n_time = int(match.group(1))
            else:
                raise ValueError("The line format is incorrect or n_time is missing.")
            break
    
    # Parsing probe location 
    probe_locations = []
    locations = np.zeros((3, n_probes)) 
    for i in range(3):
        probe_line = lines[lines.index(line_probe) + i + 1]
        probe_locations.append(list(map(float, probe_line.split())))
        locations = np.array(probe_locations).T
    
    # Parsing the time series data 
    probe_velocities = []

    time = np.zeros(n_time) 
    velocities = np.zeros((n_time, n_probes, 3)) 
    for i in range(n_time): 
        time_line = lines[lines.index(line_time) + i + 2]
        probe_velocities.append(list(map(float, time_line.split()))) 
        time[i] = probe_velocities[i][0] 
        velocities[i,:,:] = np.array(probe_velocities)[:, 1:].reshape(-1, 3) 
    
    return ProbesData(
        locations=locations, 
        time=time, 
        velocities=velocities
    )


def read_chordwise(filename):
    """Parse chordwise distribution data from DUST output file.
    
    Reads a DUST chordwise distribution file containing time-varying
    aerodynamic quantities distributed along the chord at a specific
    spanwise location.
    
    Parameters
    ----------
    filename : str or Path
        Path to the chordwise distribution output file
    
    Returns
    -------
    ChordwiseData
        Structured data containing chordwise reference coordinates,
        distribution values, time history, and metadata
        
    Raises
    ------
    ValueError
        If file format is incorrect, required metadata is missing, or
        data dimensions are inconsistent
    FileNotFoundError
        If the specified file does not exist
        
    Examples
    --------
    >>> data = read_chordwise('chordwise_cp.dat')
    >>> print(data.spanwise_location)
    0.75
    >>> print(data.chord_length)
    1.0
    >>> print(data.x_ref.shape)
    (50,)  # 50 chordwise points
    >>> print(data.chord_data.shape)
    (1000, 50)  # 1000 time steps, 50 chordwise points
    
    Notes
    -----
    The file format expects:
    - Header line with spanwise_location and chord_length
    - Header line with n_chord and n_time
    - Two data lines containing x_ref and z_ref coordinates
    - Time series data with time followed by chordwise values
    """
    
    # Initialize variables
    n_chord, n_time = None, None
    spanwise_location, chord_length = None, None
    
    # Reading the file to process line by line
    with open(filename, 'r') as file:
        lines = file.readlines()
    
    # Extracting metadata from header lines
    for line in lines:
        if 'spanwise_location' in line and 'chord_length' in line:
            match = re.search(r'spanwise_location:\s*([\d.eE+-]+)\s*;\s*chord_length:\s*([\d.eE+-]+)', line)
            if match:
                spanwise_location = float(match.group(1))
                chord_length = float(match.group(2))
        
        elif 'n_chord' in line and 'n_time' in line:
            match = re.search(r"n_chord\s*:\s*(\d+)\s*;\s*n_time\s*:\s*(\d+)", line)
            if match:
                n_chord = int(match.group(1))
                n_time = int(match.group(2))
    
    if n_chord is None or n_time is None:
        raise ValueError("Could not find n_chord and n_time in file metadata")
    
    # Find non-comment data lines (skip empty lines and comment lines)
    data_lines = []
    for line in lines:
        stripped = line.strip()
        if stripped and not stripped.startswith('#'):
            data_lines.append(stripped)
    
    if len(data_lines) < 2 + n_time:
        raise ValueError(f"Not enough data lines. Expected {2 + n_time}, got {len(data_lines)}")
    
    # The first two non-comment lines should be x_ref and z_ref
    x_ref = np.array(list(map(float, data_lines[0].split())))
    z_ref = np.array(list(map(float, data_lines[1].split())))
    
    # Verify dimensions
    if len(x_ref) != n_chord or len(z_ref) != n_chord:
        raise ValueError(f"Expected {n_chord} chord points but got x_ref:{len(x_ref)}, z_ref:{len(z_ref)}")
    
    # The remaining lines are time series data
    time_series_lines = data_lines[2:2 + n_time]
    
    # Create array for time series data: shape (n_time, time + n_chord)
    data = np.array([list(map(float, line.split())) for line in time_series_lines])
    
    # Extract time and chordwise data
    time = data[:, 0]
    chord_data = data[:, 1:1 + n_chord] 

    # Return as namedtuple or similar structure
    return ChordwiseData(
        x_ref=x_ref, 
        z_ref=z_ref, 
        chord_data=chord_data, 
        time=time, 
        spanwise_location=spanwise_location, 
        chord_length=chord_length
    )

def read_integral(filename):
    """Parse integral loads from DUST output file.
    
    Reads a DUST integral loads file containing time-varying total
    forces and moments acting on the body.
    
    Parameters
    ----------
    filename : str or Path
        Path to the integral loads output file
    
    Returns
    -------
    IntegralData
        Structured data containing forces, moments, and time history
        
    Raises
    ------
    ValueError
        If file cannot be parsed or has incorrect format
    FileNotFoundError
        If the specified file does not exist
        
    Examples
    --------
    >>> data = read_integral('integral_loads.dat')
    >>> print(data.forces.shape)
    (1000, 3)  # 1000 time steps, (Fx, Fy, Fz)
    >>> print(data.moments.shape)
    (1000, 3)  # 1000 time steps, (Mx, My, Mz)
    >>> lift = data.forces[:, 2]  # Extract lift force (Fz)
    
    Notes
    -----
    The file format expects:
    - 4 header lines (skipped during reading)
    - Data columns: time, Fx, Fy, Fz, Mx, My, Mz
    """

    loads = np.loadtxt(filename, skiprows=4) 
    
    time = loads[:, 0]
    forces = loads[:, 1:4]
    moments = loads[:, 4:7]

    return IntegralData(
            forces=forces, 
            moments=moments, 
            time=time
        )

def read_hinge(filename):
    """Parse hinge loads from DUST output file.
    
    Reads a DUST hinge loads file containing time-varying forces and
    moments at control surface hinges.
    
    Parameters
    ----------
    filename : str or Path
        Path to the hinge loads output file
    
    Returns
    -------
    HingeData
        Structured data containing hinge forces, moments, and time history
        
    Raises
    ------
    ValueError
        If file cannot be parsed or has incorrect format
    FileNotFoundError
        If the specified file does not exist
        
    Examples
    --------
    >>> data = read_hinge('hinge_loads.dat')
    >>> print(data.forces.shape)
    (1000, 3)  # 1000 time steps, (Fx, Fy, Fz)
    >>> print(data.moments.shape)
    (1000, 3)  # 1000 time steps, (Mx, My, Mz)
    >>> hinge_moment = data.moments[:, 1]  # Extract My hinge moment
    
    Notes
    -----
    The file format expects:
    - 4 header lines (skipped during reading)
    - Data columns: time, Fx, Fy, Fz, Mx, My, Mz
    """

    hinges = np.loadtxt(filename, skiprows=4) 
    time = hinges[:, 0]
    forces = hinges[:, 1:4]
    moments = hinges[:, 4:7] 

    return HingeData(
        forces=forces, 
        moments=moments, 
        time=time
    )