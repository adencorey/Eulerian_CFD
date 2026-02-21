# Eulerian Computational Fluid Dynamics

A Python-based fluid simulator demonstrating **incompressible,
isothermal, inviscid flow** using an Eulerian grid-based formulation.

The solver operates on a fixed spatial grid and evolves velocity fields
over time, with real-time visualisation.


## Built With

-   [Pygame](https://www.pygame.org/) -- Visualisation interface
-   [NumPy](https://numpy.org/) -- Numerical array operations
-   [Numba](https://numba.pydata.org/) -- JIT acceleration for performance
  

## Prerequisites

Install Python from the official website:

https://www.python.org/downloads/

> Recommended: Python 3.11 or later


## 1. Clone the Repository

Open Command Prompt (Windows) or Terminal (Mac/Linux):

``` bash
git clone https://github.com/adencorey/Eulerian_CFD.git
cd Eulerian_CFD
```

If Git is not installed, download the repository as a `.zip` from GitHub
and extract it. Then navigate to the folder:

``` bash
cd absolute/path/to/Eulerian_CFD
```


## 2. Create a Virtual Environment

Using a virtual environment isolates dependencies and simplifies removal
later.

### Windows

``` bash
python -m venv venv
venv\Scripts\activate
```

### Mac / Linux

``` bash
python3 -m venv venv
source venv/bin/activate
```

## 3. Install Dependencies

``` bash
pip install -r requirements.txt
```


## 4. Run the Simulation

Ensure you are inside the project directory:

``` bash
python -m cfd
```

On first run, Numba will compile optimised kernels. This may take a
short time.\
After compilation, the simulation window will launch.

------------------------------------------------------------------------

## Notes

-   Initial startup may take longer due to JIT compilation.
-   Performance scales with grid resolution; higher resolutions require
    more CPU time.

------------------------------------------------------------------------
