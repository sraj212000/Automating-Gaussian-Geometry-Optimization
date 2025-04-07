import pandas as pd
import os

# =========================
# Define Gaussian Input Template
# =========================
# This is a multi-line string template for Gaussian input (.com) files.
# The placeholders in curly braces {} will be filled with data from the script for each complex.
GAUSSIAN_TEMPLATE = """%mem=10000mb
%NProcShared=8
%LindaWorkers=1
%chk={chk_path}
#p opt ub3lyp/gen gfinput gfoldprint iop(3/124=3) pseudo=lanl2 scf=xqc

bs

{charge},{multiplicity}
{coordinates}

{basis_atoms} 0
6-31G*
****
{central_atom} 0
lanl2dz
****

"""

# =========================
# Function: read_xyz_file
# =========================
def read_xyz_file(xyz_path, central_atom):
    """
    Reads an XYZ file and extracts atomic coordinates.
    Also collects the unique atom types (except the central atom) for basis set specification.

    Parameters:
    xyz_path (str): Path to the XYZ file.
    central_atom (str): The symbol of the central atom (e.g., 'Fe', 'Co').

    Returns:
    str: Formatted string of atomic coordinates.
    str: Space-separated list of non-central atoms (used in the basis set block).
    """
    with open(xyz_path, "r") as f:
        lines = f.readlines()[2:]  # Skip first two lines: number of atoms and comment

    coordinates = []     # To store formatted atomic coordinates
    atom_symbols = set() # To store unique non-central atom types

    for line in lines:
        parts = line.split()
        if len(parts) >= 4:
            atom = parts[0]                       # Atom symbol, e.g., C, H, N
            x, y, z = map(float, parts[1:4])      # Coordinates as floats
            # Format each coordinate line properly
            coordinates.append(f"{atom:<2} {x:>12.6f} {y:>12.6f} {z:>12.6f}")
            # Collect unique non-central atoms for later basis set definition
            if atom != central_atom:
                atom_symbols.add(atom)

    # Join coordinates and atom list to return
    return "\n".join(coordinates), " ".join(sorted(atom_symbols))


# =========================
# Function: generate_gaussian_input
# =========================
def generate_gaussian_input(excel_path, base_chk_path):
    """
    Reads an Excel file containing molecular data and generates Gaussian input files.

    Parameters:
    excel_path (str): Path to the Excel file with the following columns:
                      Column 1: Path to .xyz file
                      Column 2: Charge of the molecule
                      Column 3: Multiplicity
                      Column 4: Central atom
    base_chk_path (str): Base directory where .chk files will be stored (used in Gaussian input).
    """
    df = pd.read_excel(excel_path)  # Load Excel sheet into a DataFrame

    # Iterate over each row (i.e., each molecule entry)
    for index, row in df.iterrows():
        xyz_path = row[0]         # Column 1: Path to .xyz file
        charge = row[1]           # Column 2: Charge
        multiplicity = row[2]     # Column 3: Multiplicity
        central_atom = row[3]     # Column 4: Central atom symbol (e.g., 'Fe')

        # Check if the XYZ file exists
        if not os.path.exists(xyz_path):
            print(f"Error: XYZ file not found - {xyz_path}")
            continue

        # Extract atomic coordinates and basis atoms
        coordinates, basis_atoms = read_xyz_file(xyz_path, central_atom)

        # Create the path for the Gaussian checkpoint (.chk) file
        chk_path = os.path.join(base_chk_path, os.path.basename(xyz_path).replace(".xyz", ".chk"))

        # Fill the Gaussian input template with specific molecule data
        gaussian_input = GAUSSIAN_TEMPLATE.format(
            chk_path=chk_path,
            charge=charge,
            multiplicity=multiplicity,
            coordinates=coordinates,
            central_atom=central_atom,
            basis_atoms=basis_atoms
        )

        # Define the output .com file path (same directory as .xyz)
        inp_path = xyz_path.replace(".xyz", ".com")

        # Write the generated Gaussian input content to file
        with open(inp_path, "w") as f:
            f.write(gaussian_input)

        # Notify the user
        print(f"Generated Gaussian input: {inp_path}")


# =========================
# Example usage
# =========================
# You can change these variables to point to your own Excel and checkpoint directory

excel_file = "data.xlsx"  # Excel file with molecular input information
base_chk_dir = "/home/msc3/opt_desgin/16new/"  # Directory to store .chk files

# Generate all input files by calling the main function
generate_gaussian_input(excel_file, base_chk_dir)
