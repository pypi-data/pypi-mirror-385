from .gam_atom import GAM_Atom





from typing import Dict, Any, Optional, List, Tuple, Set, Union
import numpy as np
from dataclasses import dataclass, field
from enum import Enum
import json
from abc import ABC, abstractmethod
from scipy.spatial.distance import euclidean
from scipy.spatial.transform import Rotation
from collections import deque


# Physical constants
ATOMIC_MASS_UNIT = 1.66053906660e-27  # kg
BOHR_RADIUS = 5.29177210903e-11  # m
ELEMENTARY_CHARGE = 1.602176634e-19  # C

# Bond length reference data (in Angstroms)
REFERENCE_BOND_LENGTHS = {
    ('C', 'C'): {'1': 1.54, '2': 1.34, '3': 1.20},  # single, double, triple
    ('C', 'H'): {'1': 1.09},
    ('C', 'O'): {'1': 1.43, '2': 1.23},
    ('C', 'N'): {'1': 1.47, '2': 1.29, '3': 1.16},
    # Add more reference data as needed
}


REFERENCE_PERIODIC_TABLE_CONFIG={
    'H': {'number': 1, 'mass': 1.008, 'config': '1s1', 'radius': 0.53},
    'He': {'number': 2, 'mass': 4.003, 'config': '1s2', 'radius': 0.31},
    'Li': {'number': 3, 'mass': 6.941, 'config': '[He] 2s1', 'radius': 1.67},
    'Be': {'number': 4, 'mass': 9.012, 'config': '[He] 2s2', 'radius': 1.12},
    'B': {'number': 5, 'mass': 10.811, 'config': '[He] 2s2 2p1', 'radius': 0.85},
    'C': {'number': 6, 'mass': 12.011, 'config': '[He] 2s2 2p2', 'radius': 0.67},
    'N': {'number': 7, 'mass': 14.007, 'config': '[He] 2s2 2p3', 'radius': 0.56},
    'O': {'number': 8, 'mass': 15.999, 'config': '[He] 2s2 2p4', 'radius': 0.48},
    'F': {'number': 9, 'mass': 18.998, 'config': '[He] 2s2 2p5', 'radius': 0.42},
    'Ne': {'number': 10, 'mass': 20.180, 'config': '[He] 2s2 2p6', 'radius': 0.38},
    'Na': {'number': 11, 'mass': 22.990, 'config': '[Ne] 3s1', 'radius': 1.90},
    'Mg': {'number': 12, 'mass': 24.305, 'config': '[Ne] 3s2', 'radius': 1.45},
    'Al': {'number': 13, 'mass': 26.982, 'config': '[Ne] 3s2 3p1', 'radius': 1.18},
    'Si': {'number': 14, 'mass': 28.085, 'config': '[Ne] 3s2 3p2', 'radius': 1.11},
    'P': {'number': 15, 'mass': 30.974, 'config': '[Ne] 3s2 3p3', 'radius': 1.06},
    'S': {'number': 16, 'mass': 32.06, 'config': '[Ne] 3s2 3p4', 'radius': 1.02},
    'Cl': {'number': 17, 'mass': 35.453, 'config': '[Ne] 3s2 3p5', 'radius': 0.99},
    'Ar': {'number': 18, 'mass': 39.948, 'config': '[Ne] 3s2 3p6', 'radius': 0.95},
    'K': {'number': 19, 'mass': 39.098, 'config': '[Ar] 4s1', 'radius': 2.43},
    'Ca': {'number': 20, 'mass': 40.078, 'config': '[Ar] 4s2', 'radius': 1.94},
    'Sc': {'number': 21, 'mass': 44.956, 'config': '[Ar] 3d1 4s2', 'radius': 1.84},
    'Ti': {'number': 22, 'mass': 47.867, 'config': '[Ar] 3d2 4s2', 'radius': 1.76},
    'V': {'number': 23, 'mass': 50.942, 'config': '[Ar] 3d3 4s2', 'radius': 1.71},
    'Cr': {'number': 24, 'mass': 51.996, 'config': '[Ar] 3d5 4s1', 'radius': 1.66},
    'Mn': {'number': 25, 'mass': 54.938, 'config': '[Ar] 3d5 4s2', 'radius': 1.61},
    'Fe': {'number': 26, 'mass': 55.845, 'config': '[Ar] 3d6 4s2', 'radius': 1.56},
    'Co': {'number': 27, 'mass': 58.933, 'config': '[Ar] 3d7 4s2', 'radius': 1.52},
    'Ni': {'number': 28, 'mass': 58.693, 'config': '[Ar] 3d8 4s2', 'radius': 1.49},
    'Cu': {'number': 29, 'mass': 63.546, 'config': '[Ar] 3d10 4s1', 'radius': 1.45},
    'Zn': {'number': 30, 'mass': 65.38, 'config': '[Ar] 3d10 4s2', 'radius': 1.42},
    'Ga': {'number': 31, 'mass': 69.723, 'config': '[Ar] 3d10 4s2 4p1', 'radius': 1.36},
    'Ge': {'number': 32, 'mass': 72.630, 'config': '[Ar] 3d10 4s2 4p2', 'radius': 1.25},
    'As': {'number': 33, 'mass': 74.922, 'config': '[Ar] 3d10 4s2 4p3', 'radius': 1.19},
    'Se': {'number': 34, 'mass': 78.971, 'config': '[Ar] 3d10 4s2 4p4', 'radius': 1.16},
    'Br': {'number': 35, 'mass': 79.904, 'config': '[Ar] 3d10 4s2 4p5', 'radius': 1.14},
    'Kr': {'number': 36, 'mass': 83.798, 'config': '[Ar] 3d10 4s2 4p6', 'radius': 1.10}
}


REFERENCE_VALENCE_ELECTRONS = {
    # Period 1
    'H': 1, 'He': 2,
    # Period 2
    'Li': 1, 'Be': 2, 'B': 3, 'C': 4, 'N': 5, 'O': 6, 'F': 7, 'Ne': 8,
    # Period 3
    'Na': 1, 'Mg': 2, 'Al': 3, 'Si': 4, 'P': 5, 'S': 6, 'Cl': 7, 'Ar': 8,
    # Period 4 (main group)
    'K': 1, 'Ca': 2, 'Ga': 3, 'Ge': 4, 'As': 5, 'Se': 6, 'Br': 7, 'Kr': 8,
    # Period 5 (main group)
    'Rb': 1, 'Sr': 2, 'In': 3, 'Sn': 4, 'Sb': 5, 'Te': 6, 'I': 7, 'Xe': 8,
    # Period 6 (main group)
    'Cs': 1, 'Ba': 2, 'Tl': 3, 'Pb': 4, 'Bi': 5, 'Po': 6, 'At': 7, 'Rn': 8,
    # Period 7 (main group)
    'Fr': 1, 'Ra': 2,
    # Other common elements
    'Sc': 3, 'Ti': 4, 'V': 5, 'Cr': 6, 'Mn': 7, 'Fe': 8, 'Co': 9, 'Ni': 10,
    'Cu': 11, 'Zn': 12, 'Ag': 11, 'Cd': 12, 'Au': 11, 'Hg': 12
}


REFERENCE_PAULING_ELECTRONEGATIVITIES={
    'H': 2.20, 'He': 0.00, 'Li': 0.98, 'Be': 1.57, 'B': 2.04, 'C': 2.55,
    'N': 3.04, 'O': 3.44, 'F': 3.98, 'Ne': 0.00, 'Na': 0.93, 'Mg': 1.31,
    'Al': 1.61, 'Si': 1.90, 'P': 2.19, 'S': 2.58, 'Cl': 3.16, 'Ar': 0.00,
    'K': 0.82, 'Ca': 1.00, 'Sc': 1.36, 'Ti': 1.54, 'V': 1.63, 'Cr': 1.66,
    'Mn': 1.55, 'Fe': 1.83, 'Co': 1.88, 'Ni': 1.91, 'Cu': 1.90, 'Zn': 1.65,
    'Ga': 1.81, 'Ge': 2.01, 'As': 2.18, 'Se': 2.55, 'Br': 2.96, 'Kr': 3.00,
    'Rb': 0.82, 'Sr': 0.95, 'Y': 1.22, 'Zr': 1.33, 'Nb': 1.60, 'Mo': 2.16,
    'Tc': 1.90, 'Ru': 2.20, 'Rh': 2.28, 'Pd': 2.20, 'Ag': 1.93, 'Cd': 1.69,
    'In': 1.78, 'Sn': 1.96, 'Sb': 2.05, 'Te': 2.10, 'I': 2.66, 'Xe': 2.60,
    'Cs': 0.79, 'Ba': 0.89, 'La': 1.10, 'Hf': 1.30, 'Ta': 1.50, 'W': 2.36,
    'Re': 1.90, 'Os': 2.20, 'Ir': 2.20, 'Pt': 2.28, 'Au': 2.54, 'Hg': 2.00,
    'Tl': 1.62, 'Pb': 1.87, 'Bi': 2.02, 'Po': 2.00, 'At': 2.20, 'Rn': 2.20,
    'Fr': 0.70, 'Ra': 0.90, 'Ac': 1.10, 'Th': 1.30, 'Pa': 1.50, 'U': 1.38,
    'Np': 1.36, 'Pu': 1.28, 'Am': 1.13, 'Cm': 1.28, 'Bk': 1.30, 'Cf': 1.30,
    'Es': 1.30, 'Fm': 1.30, 'Md': 1.30, 'No': 1.30, 'Lr': 1.30
}

class ElectronicState(Enum):
    """Enumeration for electronic states of atoms."""
    GROUND_STATE = "ground"
    EXCITED_STATE = "excited"
    IONIZED = "ionized"

@dataclass
class AtomicOrbital:
    """Represents an atomic orbital with quantum numbers."""
    n: int  # Principal quantum number
    l: int  # Angular momentum quantum number
    m: int  # Magnetic quantum number
    s: float  # Spin quantum number
    occupation: float = 0.0  # Electron occupation number

class AtomicData:
    """Static class containing fundamental atomic data."""
    _periodic_table: Dict[str, Dict[str, Any]] =REFERENCE_PERIODIC_TABLE_CONFIG  

    @classmethod
    def get_atomic_data(cls, element: str) -> Dict[str, Any]:
        """Get atomic data for an element."""
        return cls._periodic_table.get(element, {})

class ForceField(ABC):
    """Abstract base class for force field implementations."""
    @abstractmethod
    def calculate_energy(self, atom: 'GAM_Atom', neighbors: List['GAM_Atom']) -> float:
        """Calculate the energy contribution of an atom."""
        pass




class GAM_Bond:
    """
    Advanced bond class for computational chemistry and molecular modeling applications.
    
    The GAM_Bond class represents covalent bonds between atoms within molecular systems
    and provides comprehensive functionality for structural analysis, geometric calculations,
    and bond property evaluation. It supports various bond orders, strain energy calculations,
    and advanced geometric transformations essential for molecular dynamics simulations
    and quantum chemistry computations.
    
    Attributes:
        id (int): Unique identifier for the bond within a molecular system.
        atom1_id (int): ID of the first atom in the bond.
        atom2_id (int): ID of the second atom in the bond.
        order (int): Bond order (1=single, 2=double, 3=triple).
        _length (Optional[float]): Cached bond length in Angstroms.
        _energy (Optional[float]): Cached bond energy in Joules.
        
    Examples:
        Basic bond creation:
        >>> bond = GAM_Bond(id=1, atom1_id=1, atom2_id=2, order=1)
        >>> print(f"Bond order: {bond.order}")
        Bond order: 1
        
        Bond length calculation:
        >>> atoms = {1: GAM_Atom(1, "C", 0.0, 0.0, 0.0), 
        ...           2: GAM_Atom(2, "C", 1.54, 0.0, 0.0)}
        >>> bond = GAM_Bond(1, 1, 2, 1)
        >>> length = bond.calculate_length(atoms)
        >>> print(f"Bond length: {length:.2f} Å")
        Bond length: 1.54 Å
        
        Bond validation:
        >>> is_reasonable = bond.is_reasonable_length(atoms)
        >>> print(f"Reasonable bond length: {is_reasonable}")
        Reasonable bond length: True
        
        Strain energy calculation:
        >>> strain_energy = bond.calculate_strain_energy(atoms)
        >>> print(f"Strain energy: {strain_energy:.3f} kcal/mol")
        Strain energy: 0.000 kcal/mol
        
    Notes:
        - Bond lengths are calculated in Angstroms.
        - Strain energies are calculated in kcal/mol using harmonic approximation.
        - Bond validation uses reference bond lengths with 20% tolerance.
        - All geometric calculations require access to the complete atom dictionary.
        
    Raises:
        ValueError: If fixed atom ID in rotation operations is not part of the bond.
        ValueError: If atoms associated with the bond do not exist in the provided dictionary.
        
    See Also:
        GAM_Atom: For individual atom representation and properties.
        GAM_Molecule: For complete molecular system management.
        REFERENCE_BOND_LENGTHS: For reference bond length data.
    """
    
    def __init__(self, id: int, atom1_id: int, atom2_id: int, order: int = 1):
        self.id = id
        self.atom1_id = atom1_id
        self.atom2_id = atom2_id
        self.order = order
        self._length: Optional[float] = None
        self._energy: Optional[float] = None

    @property
    def bond_vector(self, atoms: Dict[int, GAM_Atom]) -> np.ndarray:
        """Calculate the bond vector from atom1 to atom2."""
        atom1 = atoms[self.atom1_id]
        atom2 = atoms[self.atom2_id]
        return atom2.position - atom1.position

    def calculate_length(self, atoms: Dict[int, GAM_Atom]) -> float:
        """Calculate the bond length in Angstroms."""
        return np.linalg.norm(self.bond_vector(atoms))

    def is_reasonable_length(self, atoms: Dict[int, GAM_Atom]) -> bool:
        """
        Check if the bond length is reasonable based on reference data.
        
        Args:
            atoms: Dictionary mapping atom IDs to Atom objects
            
        Returns:
            bool: True if the bond length is within 20% of reference value
        """
        atom1 = atoms[self.atom1_id]
        atom2 = atoms[self.atom2_id]
        
        # Sort elements to match reference data format
        elements = tuple(sorted([atom1.element, atom2.element]))
        ref_lengths = REFERENCE_BOND_LENGTHS.get(elements, {})
        ref_length = ref_lengths.get(str(self.order))
        
        if ref_length is None:
            return True  # No reference data available
            
        actual_length = self.calculate_length(atoms)
        return abs(actual_length - ref_length) / ref_length < 0.2
    
    #maybe mroe reliable:
    def is_reasonable_length(self, atoms: Dict[int, GAM_Atom]) -> bool:
        """
        Check if the bond length is reasonable based on reference data.
        ...
        """
        atom1 = atoms[self.atom1_id]
        atom2 = atoms[self.atom2_id]

        elements = tuple(sorted([atom1.element, atom2.element]))
        ref_lengths = REFERENCE_BOND_LENGTHS.get(elements, {})
        # Corrected lookup to use integer key
        ref_length = ref_lengths.get(self.order)

        if ref_length is None:
            return True

        actual_length = self.calculate_length(atoms)
        return abs(actual_length - ref_length) / ref_length < 0.2




    def calculate_angle_with(self, other: 'GAM_Bond', atoms: Dict[int, GAM_Atom]) -> float:
        """
        Calculate angle between this bond and another bond.
        
        Args:
            other: Another Bond object
            atoms: Dictionary mapping atom IDs to Atom objects
            
        Returns:
            float: Angle in degrees between the bonds
        """
        v1 = self.bond_vector(atoms)
        v2 = other.bond_vector(atoms)
        cos_angle = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
        return np.degrees(np.arccos(np.clip(cos_angle, -1.0, 1.0)))

    def rotate_around_axis(self, 
                         axis: np.ndarray, 
                         angle_degrees: float,
                         atoms: Dict[int, GAM_Atom],
                         fixed_atom_id: Optional[int] = None) -> None:
        """
        Rotate the bond around an axis while keeping one atom fixed.
        
        Args:
            axis: Rotation axis
            angle_degrees: Rotation angle in degrees
            atoms: Dictionary mapping atom IDs to Atom objects
            fixed_atom_id: ID of the atom to keep fixed (defaults to atom1_id)
        """
        if fixed_atom_id is None:
            fixed_atom_id = self.atom1_id

        if fixed_atom_id not in {self.atom1_id, self.atom2_id}:
            raise ValueError(f"Fixed atom ID must be either {self.atom1_id} or {self.atom2_id}.")
            
        moving_atom_id = self.atom2_id if fixed_atom_id == self.atom1_id else self.atom1_id
        
        # Get the fixed atom's position as rotation center
        center = atoms[fixed_atom_id].position
        
        # Rotate the moving atom
        atoms[moving_atom_id].rotate_around_axis(axis, angle_degrees, center)

    def calculate_strain_energy(self, atoms: Dict[int, GAM_Atom]) -> float:
        """
        Calculate the strain energy of the bond based on deviation from ideal length.
        
        Args:
            atoms: Dictionary mapping atom IDs to Atom objects
            
        Returns:
            float: Strain energy in kcal/mol
        """
        atom1 = atoms[self.atom1_id]
        atom2 = atoms[self.atom2_id]
        
        elements = tuple(sorted([atom1.element, atom2.element]))
        ref_lengths = REFERENCE_BOND_LENGTHS.get(elements, {})
        ref_length = ref_lengths.get(str(self.order))
        
        if ref_length is None:
            return 0.0
            
        actual_length = self.calculate_length(atoms)
        # Simple harmonic approximation
        force_constant = 100.0  # kcal/mol/Å² (approximate)
        return 0.5 * force_constant * (actual_length - ref_length) ** 2
    
    def get_elements(self, atoms: Dict[int, 'GAM_Atom']) -> Tuple[str, str]:
        """
        Returns a tuple of the elements involved in the bond.

        Args:
            atoms: Dictionary mapping atom IDs to Atom objects.

        Returns:
            A sorted tuple of the elements (e.g., ('C', 'H')).
        """
        atom1 = atoms[self.atom1_id]
        atom2 = atoms[self.atom2_id]
        return tuple(sorted([atom1.element, atom2.element]))
    
    def get_bond_type(self, atoms: Dict[int, 'GAM_Atom']) -> str:
        """
        Returns a descriptive string for the bond type.

        Args:
            atoms: Dictionary mapping atom IDs to Atom objects.

        Returns:
            A string describing the bond (e.g., 'C-C single bond').
        """
        elements = self.get_elements(atoms)
        bond_order_map = {1: 'single', 2: 'double', 3: 'triple'}
        bond_type = bond_order_map.get(self.order, 'unspecified')
        return f"{elements[0]}-{elements[1]} {bond_type} bond"
    

    
    def is_aromatic(self, atoms: Dict[int, 'GAM_Atom']) -> bool:
        """
        Checks if the bond is likely part of an aromatic system.
        This is a simple heuristic based on bond order and element types.

        Args:
            atoms: Dictionary mapping atom IDs to Atom objects.

        Returns:
            True if the bond is aromatic, False otherwise.
        """
        if self.order == 1:
            elements = self.get_elements(atoms)
            # Aromatic bonds are often C-C bonds with an order of 1.5,
            # but in some representations, they are labeled as order 1.
            if elements == ('C', 'C'):
                # Check for a more subtle indicator of aromaticity, such as sp2 hybridization
                atom1 = atoms[self.atom1_id]
                atom2 = atoms[self.atom2_id]
                # A common heuristic is checking if both atoms have 3 neighbors
                if len(atom1._bonds) == 3 and len(atom2._bonds) == 3:
                    return True
        return False
    

    def calculate_dihedral_angle(self, atom3_id: int, atom4_id: int, atoms: Dict[int, 'GAM_Atom']) -> float:
        """
        Calculates the dihedral angle between this bond and a plane defined by
        the third and fourth atoms.

        Args:
            atom3_id: The ID of the third atom.
            atom4_id: The ID of the fourth atom.
            atoms: Dictionary mapping atom IDs to Atom objects.

        Returns:
            The dihedral angle in degrees.
        """
        atom1 = atoms[self.atom1_id]
        atom2 = atoms[self.atom2_id]
        atom3 = atoms[atom3_id]
        atom4 = atoms[atom4_id]

        b1 = atom1.position - atom2.position
        b2 = atom3.position - atom2.position
        b3 = atom4.position - atom3.position

        n1 = np.cross(b1, b2)
        n2 = np.cross(b2, b3)

        m1 = np.cross(n1, b2 / np.linalg.norm(b2))

        x = np.dot(n1, n2)
        y = np.dot(m1, n2)

        return np.degrees(np.arctan2(y, x))
    
    def calculate_angle_with_plane(self, plane_normal: np.ndarray, atoms: Dict[int, 'GAM_Atom']) -> float:
        """
        Calculates the angle between the bond vector and a user-defined plane.

        Args:
            plane_normal: The normal vector of the plane.
            atoms: Dictionary mapping atom IDs to Atom objects.

        Returns:
            The angle in degrees.
        """
        bond_vector = self.bond_vector(atoms)
        normal_vec = plane_normal / np.linalg.norm(plane_normal)
        
        # The angle between the vector and the normal of the plane
        cos_angle_to_normal = np.dot(bond_vector, normal_vec) / (np.linalg.norm(bond_vector))
        
        # The angle with the plane is 90 degrees minus the angle with the normal
        angle_with_plane_rad = np.pi / 2 - np.arccos(np.clip(cos_angle_to_normal, -1.0, 1.0))
        
        return np.degrees(angle_with_plane_rad)
    


    def to_dict(self) -> Dict[str, Any]:
        """
        Serializes the bond's data into a dictionary.
        
        Returns:
            A dictionary representation of the bond.
        """
        return {
            'id': self.id,
            'atom1_id': self.atom1_id,
            'atom2_id': self.atom2_id,
            'order': self.order
        }
    
    def get_atoms(self, atoms: Dict[int, 'GAM_Atom']) -> Tuple['GAM_Atom', 'GAM_Atom']:
        """
        Retrieves the two GAM_Atom objects connected by this bond.

        Args:
            atoms: Dictionary mapping atom IDs to Atom objects.

        Returns:
            A tuple containing the two GAM_Atom objects.
        """
        atom1 = atoms.get(self.atom1_id)
        atom2 = atoms.get(self.atom2_id)
        if not all([atom1, atom2]):
            raise ValueError("One or more atoms associated with this bond do not exist.")
        return atom1, atom2

    def get_neighboring_bonds(self, atoms: Dict[int, 'GAM_Atom']) -> List['GAM_Bond']:
        """
        Finds all other bonds that share an atom with this bond.

        Args:
            atoms: Dictionary mapping atom IDs to Atom objects.

        Returns:
            A list of GAM_Bond objects that are neighbors to this bond.
        """
        atom1, atom2 = self.get_atoms(atoms)
        neighboring_bonds = []
        for bond in atom1.get_bonds():
            if bond.id != self.id:
                neighboring_bonds.append(bond)
        for bond in atom2.get_bonds():
            if bond.id != self.id and bond not in neighboring_bonds:
                neighboring_bonds.append(bond)
        return neighboring_bonds

    

    def is_part_of_ring(self, atoms: Dict[int, 'GAM_Atom'], max_ring_size: int = 7) -> bool:
        """
        Checks if the bond is part of a closed ring structure using Breadth-First Search (BFS).
        ...
        """
        atom1, atom2 = self.get_atoms(atoms)
    
        # Use a more efficient deque for the queue
        queue = deque([(atom2, 1, {atom2.id})])  # (current_atom, path_length, visited_set)
    
        while queue:
            current_atom, path_length, visited = queue.popleft()
    
            if path_length >= max_ring_size:
                continue
    
            for bond in current_atom.get_bonds():
                if bond.id == self.id:
                    continue
    
                neighbor = atoms[bond.atom2_id if bond.atom1_id == current_atom.id else bond.atom1_id]
    
                if neighbor.id == atom1.id:
                    return True  # Found a path back to atom1, forming a ring
    
                if neighbor.id not in visited:
                    new_visited = visited.copy()
                    new_visited.add(neighbor.id)
                    queue.append((neighbor, path_length + 1, new_visited))
        return False
    


    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'GAM_Bond':
        """
        Reconstructs a GAM_Bond object from a dictionary.

        Args:
            data: A dictionary containing the bond's data.

        Returns:
            A new GAM_Bond object.
        """
        return cls(
            id=data['id'],
            atom1_id=data['atom1_id'],
            atom2_id=data['atom2_id'],
            order=data['order']
        )
    
    def to_json(self, filepath: str):
        """
        Saves the bond's data to a JSON file.
        
        Args:
            filepath: The path to the output JSON file.
        """
        with open(filepath, 'w') as f:
            json.dump(self.to_dict(), f, indent=4)  
    


    def __repr__(self) -> str:
        return f"Bond(id={self.id}, atom1_id={self.atom1_id}, atom2_id={self.atom2_id}, order={self.order})"
    
    
   