"""Build mesh configuration files for DUST simulations.

This module provides functions to write pointwise and parametric mesh files
in the format expected by the DUST solver.
"""

from typing import List, Any, TextIO, Optional, Callable
from dataclasses import dataclass, field
from datetime import datetime, timezone
import numpy as np

__all__ = [
    'Point',
    'Line',
    'Section',
    'Region',
    'MeshConfig',
    'PointwiseMesh',
    'ParametricMesh',
    'write_pointwise_mesh',
    'write_parametric_mesh',
]


# Dataclass definitions for better type safety and validation
@dataclass
class Point:
    """Mesh point with geometric and aerodynamic properties.

    Attributes:
        x, y, z: Cartesian coordinates
        chord: Local chord length
        twist: Local twist angle (degrees)
        airfoil: Airfoil section name (without .dat extension)
        airfoil_table: Airfoil aerodynamic table name (without .c81 extension)
    """
    x: float
    y: float
    z: float
    chord: float
    twist: float
    airfoil: str
    airfoil_table: str = ""


@dataclass
class Line:
    """Line definition for pointwise mesh.
    Attributes:
        type: Line type ('spline' or 'straight')
        idx_start: Starting point index (1-based)
        idx_end: Ending point index (1-based)
        nelem_span: Number of elements along span
        type_span: Spanwise discretization type
        tension: Spline tension parameter (spline only)
        bias: Spline bias parameter (spline only)
        r_ob: Outer boundary ratio for geoseries
        r_ib: Inner boundary ratio for geoseries
        r_hi: High refinement ratio for geoseries
        y_refinement: Refinement location for geoseries
    """
    type: str
    idx_start: int
    idx_end: int
    nelem_span: int
    type_span: str
    tension: float = 0.0
    bias: float = 0.0
    r_ob: Optional[float] = None
    r_ib: Optional[float] = None
    r_hi: Optional[float] = None
    y_refinement: Optional[float] = None
    def __post_init__(self):
        """Validate line type."""
        if self.type not in ('spline', 'straight'):
            raise ValueError(f"Line type must be 'spline' or 'straight', got '{self.type}'")


@dataclass
class Section:
    """Section definition for parametric mesh.
    Attributes:
        chord: Section chord length
        twist: Section twist angle (degrees)
        airfoil: Airfoil section name (without .dat extension)
        airfoil_table: Airfoil aerodynamic table name (without .c81 extension)
    """
    chord: float
    twist: float
    airfoil: str
    airfoil_table: str = ""


@dataclass
class Region:
    """Region definition for parametric mesh.
    Attributes:
        span: Region span length
        sweep: Sweep angle (degrees)
        dihed: Dihedral angle (degrees)
        nelem_span: Number of elements along span
        type_span: Spanwise discretization type
        r_ob: Outer boundary ratio for geoseries
        r_ib: Inner boundary ratio for geoseries
        y_refinement: Refinement location for geoseries
    """
    span: float
    sweep: float
    dihed: float
    nelem_span: int
    type_span: str
    r_ob: Optional[float] = None
    r_ib: Optional[float] = None
    y_refinement: Optional[float] = None


@dataclass
class MeshConfig:
    """Mesh configuration parameters.
    Required attributes:
        title: Mesh title/description
        el_type: Element type ('l' for lifting-line, 'v' for vortex-lattice, 'p' for panel)
        nelem_chord: Number of chordwise elements
        type_chord: Chordwise discretization type
        reference_chord_fraction: Reference chord fraction (typically 0.25)
    Optional attributes:
        airfoil_table_correction: Use airfoil table correction (for 'v' elements)
        mesh_symmetry: Enable symmetry plane
        mesh_mirror: Enable mirror plane
        y_fountain: Fountain height parameter
        symmetry_point: Point on symmetry plane [x, y, z]
        symmetry_normal: Normal vector to symmetry plane [nx, ny, nz]
        mirror_point: Point on mirror plane [x, y, z]
        mirror_normal: Normal vector to mirror plane [nx, ny, nz]
        r_ob: Outer boundary ratio for geoseries
        r_ib: Inner boundary ratio for geoseries
        r_hi: High refinement ratio for geoseries
        y_refinement: Refinement location for geoseries
    """
    title: str
    el_type: str
    nelem_chord: int
    type_chord: str
    reference_chord_fraction: float
    # Optional fields with defaults
    airfoil_table_correction: bool = False
    mesh_symmetry: bool = False
    mesh_mirror: bool = False
    y_fountain: Optional[float] = None
    symmetry_point: list[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    symmetry_normal: list[float] = field(default_factory=lambda: [0.0, 1.0, 0.0])
    mirror_point: list[float] = field(default_factory=lambda: [0.0, 0.0, 0.0])
    mirror_normal: list[float] = field(default_factory=lambda: [1.0, 0.0, 0.0])
    r_ob: Optional[float] = None
    r_ib: Optional[float] = None
    r_hi: Optional[float] = None
    y_refinement: Optional[float] = None

    def __post_init__(self):
        """Validate configuration parameters."""
        if self.el_type not in ('l', 'v', 'p'):
            raise ValueError(f"el_type must be 'l', 'v', or 'p', got '{self.el_type}'")
        if self.nelem_chord <= 0:
            raise ValueError(f"nelem_chord must be positive, got {self.nelem_chord}")
        if not 0.0 <= self.reference_chord_fraction <= 1.0:
            raise ValueError(
                f"reference_chord_fraction must be in [0, 1], got {self.reference_chord_fraction}"
            )


@dataclass
class PointwiseMesh:
    """Container for pointwise mesh data with validation.
    This class groups related mesh data and validates it upon creation.
    It provides a convenient interface for creating and writing meshes.
    Attributes:
        config: Mesh configuration
        points: List of mesh points
        lines: List of connecting lines
    Example:
        >>> config = MeshConfig('Wing', 'v', 20, 'uniform', 0.25)
        >>> points = [Point(0, 0, 0, 1.0, 0, 'naca0012')]
        >>> lines = [Line('straight', 1, 2, 10, 'uniform')]
        >>> mesh = PointwiseMesh(config, points, lines)
        >>> mesh.write('wing.in')
    """
    config: MeshConfig
    points: list[Point]
    lines: list[Line]

    def __post_init__(self):
        """Validate mesh data upon creation."""
        if not self.points:
            raise ValueError("Points list cannot be empty")
        if not self.lines:
            raise ValueError("Lines list cannot be empty")

        # Validate line indices reference existing points
        for i, line in enumerate(self.lines):
            if line.idx_start < 1 or line.idx_end > len(self.points):
                raise IndexError(
                    f"Line {i+1} indices ({line.idx_start}, {line.idx_end}) "
                    f"are out of bounds (valid: 1-{len(self.points)})"
                )

        # Validate airfoil tables if needed
        if _is_airfoil_table_needed(self.config):
            for i, point in enumerate(self.points):
                if not point.airfoil_table:
                    raise ValueError(
                        f"Point {i+1} is missing airfoil_table "
                        f"(required for el_type='{self.config.el_type}')"
                    )

    def write(self, filename: str) -> None:
        """Write mesh to file.

        Args:
            filename: Output file path

        Raises:
            IOError: If file cannot be written

        Example:
            >>> mesh.write('wing.in')
        """
        write_pointwise_mesh(filename, self.points, self.lines, self.config)

    def __repr__(self) -> str:
        """String representation of mesh."""
        return (
            f"PointwiseMesh(title='{self.config.title}', "
            f"n_points={len(self.points)}, n_lines={len(self.lines)})"
        )


@dataclass
class ParametricMesh:
    """Container for parametric mesh data with validation.

    This class groups related mesh data and validates it upon creation.
    It provides a convenient interface for creating and writing meshes.

    Attributes:
        config: Mesh configuration
        sections: List of wing sections (n+1 sections for n regions)
        regions: List of regions connecting sections (n regions)

    Example:
        >>> config = MeshConfig('Wing', 'v', 20, 'uniform', 0.25)
        >>> sections = [Section(1.0, 0, 'naca0012'), Section(0.8, 5, 'naca0012')]
        >>> regions = [Region(5.0, 10.0, 0.0, 10, 'uniform')]
        >>> mesh = ParametricMesh(config, sections, regions)
        >>> mesh.write('wing.in')
    """
    config: MeshConfig
    sections: list[Section]
    regions: list[Region]

    def __post_init__(self):
        """Validate mesh data upon creation."""
        if not self.sections:
            raise ValueError("Sections list cannot be empty")
        if not self.regions:
            raise ValueError("Regions list cannot be empty")

        # Validate section-region count relationship
        if len(self.sections) != len(self.regions) + 1:
            raise ValueError(
                f"Expected {len(self.regions) + 1} sections for {len(self.regions)} regions, "
                f"got {len(self.sections)} sections"
            )

        # Validate airfoil tables if needed
        if _is_airfoil_table_needed(self.config):
            for i, section in enumerate(self.sections):
                if not section.airfoil_table:
                    raise ValueError(
                        f"Section {i+1} is missing airfoil_table "
                        f"(required for el_type='{self.config.el_type}')"
                    )

    def write(self, filename: str) -> None:
        """Write mesh to file.

        Args:
            filename: Output file path

        Raises:
            IOError: If file cannot be written

        Example:
            >>> mesh.write('wing.in')
        """
        write_parametric_mesh(filename, self.sections, self.regions, self.config)
    def __repr__(self) -> str:
        """String representation of mesh."""
        return (
            f"ParametricMesh(title='{self.config.title}', "
            f"n_sections={len(self.sections)}, n_regions={len(self.regions)})"
        )


def _get_timestamp(file: TextIO) -> None:
    """Write UTC timestamp to mesh file.

    Args:
        file: Output file handle
    """
    now = datetime.now(timezone.utc)
    timestamp = now.strftime("%Y-%m-%d %H:%M:%S %Z")
    file.write(f"! generated = {timestamp}\n")


def _is_airfoil_table_needed(config: MeshConfig) -> bool:
    """Check if airfoil table files are needed based on element type.
    Args:
        config: Mesh configuration
    Returns:
        True if airfoil tables are required
    """
    return (config.el_type == 'l' or
            (config.el_type == 'v' and config.airfoil_table_correction))


def _write_chordwise_settings(config: MeshConfig, file: TextIO) -> None:
    """Write chordwise mesh settings to file.

    Args:
        config: Mesh configuration
        file: Output file handle
    """
    file.write("! Chord-wise settings\n")
    file.write(f"nelem_chord = {config.nelem_chord}\n")
    file.write(f"type_chord = {config.type_chord}\n")
    file.write(f"reference_chord_fraction = {config.reference_chord_fraction}\n\n")

    # Handle geoseries parameters
    if config.type_chord == 'geoseries': 
        file.write(f"r_ob = {config.r_ob}\n")
        file.write(f"r_ib = {config.r_ib}\n")
        file.write(f"y_refinement = {config.y_refinement}\n")
    elif config.type_chord == 'geoseries_ob':
        file.write(f"r_ob = {config.r_ob}\n")
    elif config.type_chord == 'geoseries_ib':
        file.write(f"r_ib = {config.r_ib}\n")
    elif config.type_chord == 'geoseries_hi':
        file.write(f"r_hi = {config.r_hi}\n")


def _write_spanwise_settings(config: Any, file: TextIO) -> None:
    """Write spanwise mesh settings to file.

    Args:
        config: Configuration object (MeshConfig, Line, or Region)
        file: Output file handle
    """
    file.write(f"nelem_span = {config.nelem_span}\n")
    file.write(f"type_span = {config.type_span}\n")

    # Handle geoseries parameters
    if config.type_span == 'geoseries':
        file.write(f"r_ob = {config.r_ob}\n")
        file.write(f"r_ib = {config.r_ib}\n")
        file.write(f"y_refinement = {config.y_refinement}\n")
    elif config.type_span == 'geoseries_ob':
        file.write(f"r_ob = {config.r_ob}\n")
    elif config.type_span == 'geoseries_ib':
        file.write(f"r_ib = {config.r_ib}\n")

    file.write("\n")


def _write_symmetry(config: MeshConfig, file: TextIO) -> None:
    """Write symmetry plane settings to file.

    Args:
        config: Mesh configuration
        file: Output file handle
    """
    file.write("! Symmetry settings\n")
    file.write("mesh_symmetry = T\n")
    sym_pt = config.symmetry_point
    sym_norm = config.symmetry_normal
    file.write(f"symmetry_point = (/ {sym_pt[0]:.1f}, {sym_pt[1]:.1f}, {sym_pt[2]:.1f} /)\n")
    file.write(f"symmetry_normal = (/ {sym_norm[0]:.1f}, {sym_norm[1]:.1f}, {sym_norm[2]:.1f} /)\n\n")


def _write_mirror(config: MeshConfig, file: TextIO) -> None:
    """Write mirror plane settings to file.

    Args:
        config: Mesh configuration
        file: Output file handle
    """
    file.write("! Mirror settings\n")
    file.write("mesh_mirror = T\n")
    mir_pt = config.mirror_point
    mir_norm = config.mirror_normal
    file.write(f"mirror_point = (/ {mir_pt[0]:.1f}, {mir_pt[1]:.1f}, {mir_pt[2]:.1f} /)\n")
    file.write(f"mirror_normal = (/ {mir_norm[0]:.1f}, {mir_norm[1]:.1f}, {mir_norm[2]:.1f} /)\n\n")


def _write_point(config: MeshConfig, point: Point, idx: int, file: TextIO) -> None:
    """Write a single point definition to file.

    Args:
        config: Mesh configuration
        point: Point object
        idx: Zero-based index of the point
        file: Output file handle
    """
    file.write("point = {\n")
    file.write(f"  id = {idx + 1}\n")
    file.write(f"  coordinates = (/{point.x}, {point.y}, {point.z}/)\n")
    file.write(f"  chord = {point.chord}\n")
    file.write(f"  twist = {point.twist}\n")
    file.write(f"  airfoil = {point.airfoil}.dat\n")

    if _is_airfoil_table_needed(config):
        if not point.airfoil_table:
            raise ValueError(
                f"Point {idx+1} is missing airfoil_table "
                f"(required for el_type='{config.el_type}')"
            )
        file.write(f"  airfoil_table = {point.airfoil_table}.c81\n")

    file.write("  section_normal = referenceLine\n")
    file.write("}\n\n")


def _write_straight(line: Line, points: list[Point], file: TextIO) -> None:
    """Write a straight line definition to file.

    Args:
        line: Line object
        points: List of point objects
        file: Output file handle

    Raises:
        IndexError: If line indices are out of bounds
    """
    # Validate bounds
    if line.idx_start < 1 or line.idx_end > len(points):
        raise IndexError(
            f"Line indices ({line.idx_start}, {line.idx_end}) "
            f"are out of bounds (valid: 1-{len(points)})"
        )

    file.write("line = {\n")
    file.write("  type = Straight\n")
    file.write(f"  end_points = (/{line.idx_start}, {line.idx_end}/)\n")
    _write_spanwise_settings(line, file)
    file.write("}\n\n")


def _write_spline(line: Line, points: list[Point], file: TextIO) -> None:
    """Write a spline line definition to file.

    Args:
        line: Line object
        points: List of point objects
        file: Output file handle

    Raises:
        IndexError: If line indices are out of bounds
    """
    # Validate bounds
    if line.idx_start < 1 or line.idx_end > len(points):
        raise IndexError(
            f"Line indices ({line.idx_start}, {line.idx_end}) "
            f"are out of bounds (valid: 1-{len(points)})"
        )

    file.write("line = {\n")
    file.write("  type = Spline\n")
    file.write(f"  end_points = (/{line.idx_start}, {line.idx_end}/)\n")
    file.write(f"  tension = {line.tension}\n")
    file.write(f"  bias = {line.bias}\n")
    _write_spanwise_settings(line, file)
    _write_end_tangents(line, points, file)
    file.write("}\n\n")


def _write_end_tangents(line: Line, points: list[Point], file: TextIO) -> None:
    """Calculate and write tangent vectors at line endpoints.

    Tangents are computed using forward/backward finite differences and normalized.

    Args:
        line: Line object
        points: List of point objects
        file: Output file handle

    Raises:
        IndexError: If tangent calculation would go out of bounds
    """
    pt_start = line.idx_start - 1  # Convert to 0-based index
    pt_end = line.idx_end - 1

    # Bounds checking
    if pt_start < 0 or pt_end >= len(points):
        raise IndexError(
            f"Invalid line indices: start={line.idx_start}, end={line.idx_end} "
            f"(valid: 1-{len(points)})"
        )

    if pt_start + 1 >= len(points):
        raise IndexError(
            f"Cannot calculate start tangent: need point at index {line.idx_start+1} "
            f"(have 1-{len(points)})"
        )

    if pt_end - 1 < 0:
        raise IndexError(
            f"Cannot calculate end tangent: need point at index {line.idx_end-1} "
            f"(have 1-{len(points)})"
        )

    # Calculate tangents using finite differences
    start_tangent = np.array([
        points[pt_start + 1].x - points[pt_start].x,
        points[pt_start + 1].y - points[pt_start].y,
        points[pt_start + 1].z - points[pt_start].z
    ])
    end_tangent = np.array([
        points[pt_end].x - points[pt_end - 1].x,
        points[pt_end].y - points[pt_end - 1].y,
        points[pt_end].z - points[pt_end - 1].z
    ])

    tangents = np.array([start_tangent, end_tangent])

    # Normalize tangents (prevent division by zero)
    norms = np.linalg.norm(tangents, axis=1)
    norms[norms == 0] = 1.0
    tangents = tangents / norms[:, np.newaxis]

    # Write tangents to file
    file.write(f"  tangent_vec1 = (/{tangents[0, 0]}, {tangents[0, 1]}, {tangents[0, 2]}/)\n")
    file.write(f"  tangent_vec2 = (/{tangents[1, 0]}, {tangents[1, 1]}, {tangents[1, 2]}/)\n")


def _write_section(section: Section, idx: int, config: MeshConfig, file: TextIO) -> None:
    """Write a section definition to file.

    Args:
        section: Section object
        idx: Zero-based section index
        config: Mesh configuration
        file: Output file handle
    """
    file.write(f"! Section {idx + 1}\n")
    file.write(f"chord = {section.chord}\n")
    file.write(f"twist = {section.twist}\n")
    file.write(f"airfoil = {section.airfoil}\n")

    if _is_airfoil_table_needed(config):
        if not section.airfoil_table:
            raise ValueError(
                f"Section {idx+1} is missing airfoil_table "
                f"(required for el_type='{config.el_type}')"
            )
        file.write(f"airfoil_table = {section.airfoil_table}\n")

    file.write("\n")


def _write_region(region: Region, idx: int, file: TextIO) -> None:
    """Write a region definition to file.

    Args:
        region: Region object
        idx: Zero-based region index
        file: Output file handle
    """
    file.write(f"! Region {idx + 1}\n")
    file.write(f"span = {region.span}\n")
    file.write(f"sweep = {region.sweep}\n")
    file.write(f"dihed = {region.dihed}\n")
    _write_spanwise_settings(region, file)


def write_pointwise_mesh(filename: str, points: list[Point], lines: list[Line],
                         config: MeshConfig) -> None:
    """Write a pointwise mesh configuration file for DUST.

    Args:
        filename: Output file path
        points: List of Point objects
        lines: List of Line objects
        config: MeshConfig object

    Raises:
        ValueError: If inputs are invalid
        IOError: If file cannot be written
        IndexError: If line indices reference non-existent points

    Example:
        >>> from pydust_utils import Point, Line, MeshConfig, write_pointwise_mesh
        >>>
        >>> config = MeshConfig(
        ...     title='Wing Mesh',
        ...     el_type='v',
        ...     nelem_chord=20,
        ...     type_chord='uniform',
        ...     reference_chord_fraction=0.25
        ... )
        >>>
        >>> points = [
        ...     Point(0.0, 0.0, 0.0, 1.0, 0.0, 'naca0012', 'naca0012'),
        ...     Point(1.0, 0.0, 0.0, 1.0, 0.0, 'naca0012', 'naca0012')
        ... ]
        >>>
        >>> lines = [
        ...     Line('straight', 1, 2, 10, 'uniform')
        ... ]
        >>>
        >>> write_pointwise_mesh('mesh.in', points, lines, config)
    """
    # Validate inputs
    if not points:
        raise ValueError("Points list cannot be empty")
    if not lines:
        raise ValueError("Lines list cannot be empty")

    try:
        with open(filename, "w") as file:
            file.write(f"! {config.title}\n")
            _get_timestamp(file)

            file.write("mesh_file_type = pointwise\n")
            file.write(f"el_type = {config.el_type}\n\n")

            # Handle airfoil table correction for 'v' elements
            if config.el_type == 'v' and config.airfoil_table_correction:
                file.write("airfoil_table_correction = T\n\n")

            _write_chordwise_settings(config, file)

            # Optional parameters (symmetry, mirror, y_fountain)
            if config.mesh_symmetry:
                _write_symmetry(config, file)
            if config.mesh_mirror:
                _write_mirror(config, file)
            if config.y_fountain:
                file.write(f"y_fountain = {config.y_fountain}\n\n")

            # Write points 
            for idx, point in enumerate(points):
                _write_point(config, point, idx, file)

            # Write lines
            for line in lines:
                if line.type == 'spline':
                    _write_spline(line, points, file)
                elif line.type == 'straight':
                    _write_straight(line, points, file)

    except OSError as e:
        raise OSError(f"Failed to write mesh file {filename}: {e}") from e


def write_parametric_mesh(filename: str, sections: list[Section],
                          regions: list[Region], config: MeshConfig) -> None:
    """Write a parametric mesh configuration file for DUST.

    Args:
        filename: Output file path
        sections: List of Section objects
        regions: List of Region objects
        config: MeshConfig object

    Raises:
        ValueError: If inputs are invalid
        OSError: If file cannot be written

    Example:
        >>> from pydust_utils import Section, Region, MeshConfig, write_parametric_mesh
        >>>
        >>> config = MeshConfig(
        ...     title='Wing Mesh',
        ...     el_type='v',
        ...     nelem_chord=20,
        ...     type_chord='uniform',
        ...     reference_chord_fraction=0.25
        ... )
        >>>
        >>> sections = [
        ...     Section(1.0, 0.0, 'naca0012', 'naca0012'),
        ...     Section(0.8, 5.0, 'naca0012', 'naca0012')
        ... ]
        >>>
        >>> regions = [
        ...     Region(5.0, 10.0, 0.0, 10, 'uniform')
        ... ]
        >>>
        >>> write_parametric_mesh('mesh.in', sections, regions, config)
    """
    # Validate inputs
    if not sections:
        raise ValueError("Sections list cannot be empty")
    if not regions:
        raise ValueError("Regions list cannot be empty")
    if len(sections) != len(regions) + 1:
        raise ValueError(
            f"Expected {len(regions) + 1} sections for {len(regions)} regions, "
            f"got {len(sections)} sections"
        )

    try:
        with open(filename, "w") as file:
            file.write(f"! {config.title}\n")
            _get_timestamp(file)

            file.write("mesh_file_type = parametric\n")
            file.write(f"el_type = {config.el_type}\n\n")

            # Handle airfoil table correction for 'v' elements
            if config.el_type == 'v' and config.airfoil_table_correction:
                file.write("airfoil_table_correction = T\n\n")

            _write_chordwise_settings(config, file)

            # Optional parameters (symmetry, mirror, y_fountain)
            if config.mesh_symmetry:
                _write_symmetry(config, file)
            if config.mesh_mirror:
                _write_mirror(config, file)
            if config.y_fountain:
                file.write(f"y_fountain = {config.y_fountain}\n\n")

            # Write sections and regions
            for idx, (section, region) in enumerate(zip(sections, regions)):
                _write_section(section, idx, config, file)
                _write_region(region, idx, file)

            # Write final section (no region after it)
            _write_section(sections[-1], len(regions), config, file)

    except OSError as e:
        raise OSError(f"Failed to write mesh file {filename}: {e}") from e
