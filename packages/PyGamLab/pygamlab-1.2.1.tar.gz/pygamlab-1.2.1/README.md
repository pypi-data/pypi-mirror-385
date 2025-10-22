
<h1 align="center">PyGamLab</h1>


<p align="center">
  <img src="https://github.com/APMaii/pygamlab/blob/main/pics/python_logo_final.png" alt="PyGamLab Logo" width="450"/>
</p>




<p align="center"> <i>PyGamLab is a scientific Python library developed for researchers, engineers, and students who need access to powerful tools for nanostructure generation, alloy design, material data exploration, and AI-driven analysis. The package is designed with simplicity, clarity, and usability in mind.</i> </p>


---

## 📌 Overview

**PyGAMLab** stands for *Python GAMLAb tools*, a collection of scientific tools and functions developed at the **GAMLab (Graphene and Advanced Material Laboratory)** by **Ali Pilehvar Meibody** under the supervision of **Prof. Malek Naderi** at  **Amirkabir University of Technology (AUT)**.

- **Main Author:** Ali Pilehvar Meibody  
- **Supervisor:** Prof. Malek Naderi
- **Co Author:**  Danial Nekoonam
- **Contributor**  Shokoofeh Karimi
- **Affiliation:** GAMLab, Amirkabir University of Technology (AUT)

---

## 📦 Modules  

**PyGAMLab** is composed of several core scientific modules, each designed to address a specific domain of materials modeling, nanoscience, and data-driven discovery.  

---

### 🧱 `Structure`  

The **Structure** module is the foundation of PyGAMLab, providing advanced tools to **generate, manipulate, and analyze nanoscale and bulk materials**.  

**Key Features:**  
- Generate **0D (clusters, nanoparticles)**, **1D (nanowires, nanotubes)**, and **2D (nanosheets, thin films)** structures, as well as **bulk crystals**.  
- Automated builders for **nanoclusters, nanotubes, and supercells**.  
- Perform geometric operations such as **rotation, translation, scaling, merging, slicing**, and **symmetry analysis**.  
- Comprehensive **I/O support**: read, write, and convert structures in formats like `.cif`, `.xyz`, `.pdb`, `.vasp`, `.json`, and more.  
- Direct integration with the **ASE (Atomic Simulation Environment)** via built-in converters.  

---

### 🎨 `GAMVis` (GAM Visualizer)  

**GAMVis** is the internal visualization engine of PyGAMLab — an interactive and high-performance visualizer for atomic and molecular structures.  

**Capabilities:**  
- Real-time 2D and 3D visualization of **molecules, nanostructures, and crystal lattices**.  
- Graphical representation of **bonds, surfaces, and charge distributions**.  
- Export of rendered structures and animations.  
- Ideal for publication-quality figures and teaching demonstrations.  

---
### 🤖 `Nano_AI`  

**Nano_AI** integrates machine learning into materials research, providing tools for **automatic model training**, **fine-tuning**, and **prediction**.  

**Highlights:**  
- Automated ML workflows for regression, classification, and clustering.  
- Access to over **120 pre-trained machine learning models** trained on nanomaterials datasets.  
- Easy fine-tuning and inference on user-provided data.  
- Includes property predictors for band gap, formation energy, hardness, and more.  
- Built-in tools for data splitting, validation, and model evaluation.  


---

### 🧬 `DB_Explorer`  

The **DB_Explorer** module provides seamless access to multiple **materials databases**, allowing users to retrieve both structural and property data from leading open repositories.  

**Supported Databases:**  
- **Materials Project (MP)**  
- **AFLOW**  
- **JARVIS**  
- **Crystallography Open Database (COD)**  

**Available Data:**  
- Mechanical, electronic, and thermodynamic properties  
- Structural and crystallographic information  
- Chemical composition and symmetry details  

A universal parent class, **`GAM_Explorer`**, synchronizes and unifies data from all sources, enabling consistent data retrieval and cross-database comparison.  

---

### 📊 `Data_Analysis`  

The **Data_Analysis** module offers advanced tools for **data preprocessing, analysis, and scientific visualization**.  

**Main Features:**  
- Read and preprocess data from files or DataFrames.  
- Perform filtering, normalization, and feature extraction.  
- Generate publication-ready graphs (line, scatter, histogram, heatmap, etc.).  
- Support for **68+ experimental analysis tools**, including NMR, XPS, XRD, UV-Vis, and Raman spectroscopy.  
- Includes scientific constants, unit converters, and mathematical utilities for laboratory and computational work.  


### 🔹 ` Constants.py`
This module includes a comprehensive set of scientific constants used in physics, chemistry, and engineering.

Examples:
- Planck's constant
- Boltzmann constant
- Speed of light
- Universal gas constant
- Density of Metals
- Tm of Metals
- And many more...

---

### 🔹 `Convertors.py`
Contains unit conversion functions that follow the format:  
`FirstUnit_To_SecondUnit()`

Examples:
- `Kelvin_To_Celsius(k)`
- `Celsius_To_Kelvin(c)`
- `Meter_To_Foot(m)`
- ...and many more standard conversions used in science and engineering.

---

### 🔹 `Functions.py`
This module provides a wide collection of **scientific formulas and functional tools** commonly used in engineering applications.

Examples:
- Thermodynamics equations
- Mechanical stress and strain calculations
- Fluid dynamics formulas
- General utility functions


---

## 📦 Requirements

To use **PyGamLab**, make sure you have the following Python packages installed:

- `numpy`
- `pandas`
- `scipy`
- `matplotlib`
- `seaborn`
- `scikit-learn`
- `json`
- `scipy`
- `ase`
- `plotly`
- `PyQt5`

You can install all dependencies using:

```bash
pip install numpy pandas scipy matplotlib seaborn scikit-learn json scipy ase plotly PyQt5
```



---

## 🚀 Installation

To install PyGAMLab via pip:

```bash
pip install pygamlab
```

or

```bash
git clone https://github.com/APMaii/pygamlab.git
```

---

## 📖 Usage Example

```python
import PyGamLab


import PyGamLab.Constants as gamcn
import PyGamLab.Convertos as gamcv
import PyGamLab.Functions as gamfunc
import PyGamLab.Data_Analysis as gamdat



#--------------Constants-----------------------

print(gamcn.melting_point_of_Cu)
print(gamcn.melting_point_of_Al)
print(gamcn.Fe_Tm_Alpha)
print(gamcn.Fe_Tm_Gama)

print(gamcn.Boltzmann_Constant)
print(gamcn.Faraday_Constant)


#----------Converters------------------------

print(gamcv.Kelvin_to_Celcius(300))           # Convert 300 K to °C
print(gamcv.Coulomb_To_Electron_volt(1))      # Convert 1 Coulomb to eV
print(gamcv.Angstrom_To_Milimeter(1))         # Convert 1 Å to mm
print(gamcv.Bar_To_Pascal(1))                 # Convert 1 bar to Pascal

#-----------Functions------------------------

# Gibb's Free Energy: G = H0 - T*S0
H0 = 100  # Enthalpy in kJ/mol
T = 298   # Temperature in Kelvin
S0 = 0.2  # Entropy in kJ/mol·K
print(gamfunc.Gibs_free_energy(H0, T, S0))


# Electrical Resistance: R = V / I
voltage = 10         # in Volts
current = 2          # in Amperes
print(gamfunc.Electrical_Resistance(voltage, current))

# Hall-Petch Relationship: σ = σ0 + k / √d
d_grain = 0.01       # Grain diameter in mm
sigma0 = 150         # Friction stress in MPa
k = 0.5              # Strengthening coefficient in MPa·mm^0.5
print(gamfunc.Hall_Petch(d_grain, sigma0, k))

#-----------Data_Analysis--------------------
import pandas as pd

df= pd.read_csv('/users/apm/....../data.csv')
gamdat.Stress_Strain1(df, 'PLOT')
my_uts=gamdat.Stress_Strain1(df, 'UTS')


data=pd.read_csv('/users/apm/....../data.csv')
my_max=gamdat.Xrd_Analysis(data,'max intensity')
gamdat.Xrd_Analysis(data,'scatter plot')
gamdat.Xrd_Analysis(data,'line graph')
```

---
## 📚 Documentation

For detailed documentation, please visit the official [PyGamLab Documentation](https://apmaii.github.io/pygamlab/index.html).




---

## Structure
```
pygamlab/
├── __init__.py
├── Constants.py
├── Convertors.py
├── Functions.py
├── Data_Analysis.py
└── contributers.md

```



---
## 🤝 Contributing

**Contributions** are welcome! Here's how to get started:

Fork the repository.
Create your feature branch 

```bash
git checkout -b feature/my-feature
```
Commit your changes 
```bash
git commit -am 'Add some feature'
```
Push to the branch 
```bash
git push origin feature/my-feature
```
Create a new Pull Request.
Please make sure to update tests as appropriate and follow PEP8 guidelines.



---
## 📄 License

This project is licensed under the MIT License — see the LICENSE.txt file for details



---

## 🙏 Acknowledgements

This project is part of the scientific research activities at **GAMLab (Generalized Applied Mechanics Laboratory)**  at **Amirkabir University of Technology (AUT)**.

Special thanks to:

- **Prof. Malek Naderi** – For his guidance, mentorship, and continuous support.
- **Ali Pilehvar Meibody** – Main developer and author of PyGamLab.
- **Danial Nekoonam** –  Co-Author of PyGamLab.
- **Shokoofeh Karimi** - For her Contribution of verify and testing most functions 
- **GAMLab Research Group** – For providing a collaborative and innovative environment.
- **Hossein Behjoo** – For his guidance in taking the AI courses and his creative work in the development of the logo.

We would also like to thank **all the students who participated in the GAMLab AI course** and contributed to the growth and feedback of this project. Their names are proudly listed in the [contributors.md](contributors.md) file.

This project was made possible thanks to the powerful Python open-source ecosystem:  
`NumPy`, `SciPy`, `Pandas`, `Matplotlib`, `Seaborn`, `Scikit-learn`, and many more.

---






