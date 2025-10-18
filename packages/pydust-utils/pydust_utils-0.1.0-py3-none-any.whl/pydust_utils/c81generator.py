import os 
import aerosandbox as asb
from neuralfoil import get_aero_from_airfoil
from pathlib import Path
import numpy as np
import matplotlib.pyplot as plt

class Airfoil:
    def __init__(self, name, mach, aoa, re, CL, CD, CM): 
        self.name = name
        self.mach = mach
        self.aoa = aoa 
        self.re = re
        self.CL = CL
        self.CD = CD
        self.CM = CM 

    
    def generate_c81_file(self, mbdynformat=False, pathout="c81tables"):
        mach_fmt = '{:7.2f}'
        coef_fmt = '{:7.3f}'
        aoa_fmt = '{:7.1f}'

        def format_matrix(matrix, mach, aoa):
            text = f"{'':7}"  # Indent for the Mach numbers
            for j in range(matrix.shape[0]):
                if j > 0 and j % 9 == 0:
                    text += '\n' + ' ' * 7  # Newline with indent
                text += mach_fmt.format(mach[j])
            text += '\n'

            for k in range(matrix.shape[1]):
                text += aoa_fmt.format(aoa[k])  # Add AoA row
                for j in range(matrix.shape[0]):
                    if j > 0 and j % 9 == 0:
                        text += '\n' + ' ' * 7  # Newline with indent
                    text += coef_fmt.format(matrix[j, k])
                text += '\n'
            return text 
        
        def format_matrix_dust(matrix, mach, aoa):
            text = f"{'':7}"  # Indent for the Mach numbers
            for j in range(matrix.shape[0]):
                text += mach_fmt.format(mach[j])
            text += '\n'

            for k in range(matrix.shape[1]):
                text += aoa_fmt.format(aoa[k])  # Add AoA row
                for j in range(matrix.shape[0]):
                    text += coef_fmt.format(matrix[j, k])
                text += '\n'
            return text 

        # Header generation
        if mbdynformat: 
            post_fix = "mbdyn" 
            header = f"{self.name:30}"  # Name
            header += f"{self.CL.shape[0]:02}{self.CL.shape[1]:02}"  # Ma and AoA for CL
            header += f"{self.CD.shape[0]:02}{self.CD.shape[1]:02}"  # Ma and AoA for CD
            header += f"{self.CM.shape[0]:02}{self.CM.shape[1]:02}"  # Ma and AoA for CM
            header += '\n'

            # Generate text for each matrix
            text = header
            text += format_matrix(self.CL, self.mach, self.aoa)
            text += format_matrix(self.CD, self.mach, self.aoa)
            text += format_matrix(self.CM, self.mach, self.aoa)
        else:  
            post_fix = "dust"
            header = "1 0 0\n"
            header += "0 1\n"
            header += "0.158 0.158\n"
            header += "COMMENT#1\n"
            header += f"{self.re}    0.200\n"
            header += ' ' 
            header += f"{self.CL.shape[0]:02}{self.CL.shape[1]:02}"  # Ma and AoA for CL
            header += f"{self.CD.shape[0]:02}{self.CD.shape[1]:02}"  # Ma and AoA for CD
            header += f"{self.CM.shape[0]:02}{self.CM.shape[1]:02}"  # Ma and AoA for CM
            header += '\n'

            # Generate text for each matrix
            text = header
            text += format_matrix_dust(self.CL, self.mach, self.aoa)
            text += format_matrix_dust(self.CD, self.mach, self.aoa)
            text += format_matrix_dust(self.CM, self.mach, self.aoa)
        # Write to file
        output_folder = Path(pathout)
        output_folder.mkdir(exist_ok=True) 
        self.filename = f"{self.name}_{post_fix}_Re_{int(self.re)}" 
        with open(os.path.join(output_folder, f"{self.filename}.c81"), 'w') as f:
            f.write(text)

    def plot_c81_table(self, lims=(-30, 30), pathout="c81plots", save_fig=True):
        # generate a plot of the c81 table for all mach numbers 
        fig, ax = plt.subplots(1, 3, figsize=(21, 7))
        fig.suptitle(f"C81 Table for {self.name} at Re={int(self.re)}")
        for i, coef in enumerate(['CL', 'CD', 'CM']):
            ax[i].set_title(coef)
            for j, m in enumerate(self.mach):
                ax[i].plot(self.aoa, self.__dict__[coef][j, :], label=f"Mach {m:.2f}")
                ax[i].set_xlabel("AoA [deg]")
                ax[i].set_xlim(lims) 
            if i == 2:
                ax[i].legend()
                ax[i].grid(True)

        if save_fig:
            output_folder = Path(pathout)
            output_folder.mkdir(exist_ok=True)
            plt.savefig(f"{output_folder}/{self.name}_Re_{int(self.re)}.png")

def generate_airfoil_data(file_name, pathprofile, reynolds):

    af = asb.Airfoil(name=file_name, coordinates=Path(pathprofile) / f"{file_name}.dat").to_kulfan_airfoil() 
    alphas_nf = np.concatenate((np.arange(-180, -23, 6), np.arange(-22, 23, 1), np.arange(24, 181, 6)))
    
    mach = np.linspace(0.0, 0.90, 10)

    ab_aero = {
        'CL': [],
        'CD': [],
        'CM': []
    }

    for m in mach:
        aero = af.get_aero_from_neuralfoil(
            alpha=alphas_nf,
            Re=reynolds,
            mach=m,
            model_size="xxxlarge"
        )
        ab_aero['CL'].append(aero['CL'])
        ab_aero['CD'].append(aero['CD'])
        ab_aero['CM'].append(aero['CM'])

    ab_aero['CL'] = np.array(ab_aero['CL'])
    ab_aero['CD'] = np.array(ab_aero['CD'])
    ab_aero['CM'] = np.array(ab_aero['CM'])

    airfoil = Airfoil(name=file_name, 
                        aoa=alphas_nf,
                        mach=mach,
                        re=reynolds, 
                        CL=ab_aero['CL'],
                        CD=ab_aero['CD'],
                        CM=ab_aero['CM'])
    return airfoil