import numpy as np 
from datetime import datetime, timezone 

def _compute_end_tangents(sections):
        tangents = np.array([
            [sections[1].dx - sections[0].dx, sections[1].dy - sections[0].dy, sections[1].dz - sections[0].dz],
            [sections[-1].dx - sections[-2].dx, sections[-1].dy - sections[-2].dy, sections[-1].dz - sections[-2].dz]
        ])
        norms = np.linalg.norm(tangents, axis=1)
        norms[norms == 0] = 1.0  # avoid division by zero
        tangents = tangents / norms[:, np.newaxis]
        return tangents[0], tangents[1] 

def write_pointwise_mesh(filename, sections, config):

    with open(filename, "w") as file: 
        file.write(f"! {config['title']}\n") 
        timestamp = datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S UTC")
        file.write(f"! generated = {timestamp}\n")
        file.write(f"mesh_file_type = pointwise\n")
        file.write(f"el_type = {config['el_type']}\n\n")

        file.write(f"! Chord-wise settings\n")
        file.write(f"nelem_chord = {config['nelem_chord']}\n")
        file.write(f"type_chord = {config['type_chord']}\n")
        file.write(f"reference_chord_fraction = {config['reference_chord_fraction']}\n")
        file.write(f"y_fountain = {config['y_fountain']}\n\n")

        n_points = len(sections)
        for i, section in enumerate(sections):
            file.write("point = {\n")
            file.write(f"  id = {str(i + 1)}\n")
            file.write(f"  coordinates = (/{section.dx}, {section.dy}, {section.dz}/)\n")
            file.write(f"  airfoil = {section.airfoil}.dat\n")
            file.write(f"  airfoil_table = {section.airfoil_table}.c81\n") 
            file.write(f"  chord = {section.chord}\n")
            file.write(f"  twist = {section.twist}\n")
            file.write(f"  section_normal = referenceLine\n")
            file.write("}\n\n")

        file.write("line = {\n")
        file.write(f"  type = Spline\n")
        file.write(f"  end_points = (/1, {n_points}/)\n") 
        file.write(f"  nelems = {config['nelem_span']}\n") 
        file.write(f"  type_span = {config['type_span']}\n") 
        # Handle geoseries parameters 
        if config['type_span'] == "geoseries":  
            file.write(f"  r_ob = {config['r_ob']}\n") 
            file.write(f"  r_ib = {config['r_ib']}\n") 
            file.write(f"  y_refinement = {config['y_refinement']}\n") 
        elif config['type_span'] == "geoseries_ob": 
            file.write(f"  r_ob = {config['r_ob']}\n") 
        elif config['type_span'] == "geoseries_ib": 
            file.write(f"  r_ib = {config['r_ib']}\n")  
        
        tang1, tang2 = _compute_end_tangents(sections)
        tang1_x, tang1_y, tang1_z = tang1
        tang2_x, tang2_y, tang2_z = tang2
        
        file.write(f"  tangent_vec1 = (/{tang1_x}, {tang1_y}, {tang1_z}/)\n")
        file.write(f"  tangent_vec2 = (/{tang2_x}, {tang2_y}, {tang2_z}/)\n") 
        file.write(f"  tension = 0.0\n")
        file.write(f"  bias = 0.0\n")
        file.write("}\n\n") 

def write_parametric_mesh(filename, sections, config):
    pass  # To be implemented in the future 