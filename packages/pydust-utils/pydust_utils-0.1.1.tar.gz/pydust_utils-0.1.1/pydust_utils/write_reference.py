import numpy as np 
import re 
# Function to write configuration to a file
def write_reference_file(filename, alpha):
    # Define parameters
    config = {
        "reference_tag": "Elliptical",
        "parent_tag": 0,
        "origin": [0.0, 0.0, 0.0],
        "orientation": [
            [np.cos(alpha), 0.0, -np.sin(alpha)],
            [0.0,           1.0,            0.0],
            [np.sin(alpha), 0.0,  np.cos(alpha)]
        ],
        "multiple": False,
        "moving": False
    }
    with open(filename, "w") as file:
        file.write(f"! Rotation matrix: of {alpha*180/np.pi} deg\n")
        file.write(f"reference_tag = {config['reference_tag']}\n")
        file.write(f"parent_tag = {config['parent_tag']}\n")
        file.write(f"origin = (/ {config['origin'][0]:.8f}, {config['origin'][1]:.8f}, {config['origin'][2]:.8f} /)\n")
        # Write orientation matrix
        orientation_str = "orientation = (/ "
        for row in config['orientation']:
            orientation_str += ", ".join([f"{value:.8f}" for value in row]) + ", "
        orientation_str = orientation_str.rstrip(', ')  # Remove trailing comma
        orientation_str += " /)\n"
        file.write(orientation_str)
        
        file.write(f"multiple = {'T' if config['multiple'] else 'F'}\n")
        file.write(f"moving = {'T' if config['moving'] else 'F'}\n")

def substitute_string_in_file(file_path, pattern, new_value):
    # Read the content of the file
    with open(file_path, "r") as file:
        file_content = file.read()

    # Substitute the old string with the new string
    modified_content = re.sub(pattern, r"\1" + new_value, file_content)

    # Write the modified content back to the file
    with open(file_path, "w") as file:
        file.write(modified_content)