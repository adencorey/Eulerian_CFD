#  Eulerian Computational Fluid Dynamics

A simple Python fluid simulator that demonstrates incompressible, isothermal and inviscid flow using an **Eulerian grid-baseed method**.

Built with:
-  [Pygame](https://www.pygame.org/)
-  [NumPy](https://numpy.org/)
-  [Numba](https://numba.pydata.org/).


## Prerequisites

Make sure Python is installed on your computer. You can download it from the official website:

[Download Python](https://www.python.org/downloads/)

> Recommended: Python 3.11 or later


## 1. Clone the repository

Open Command Prompt (Windows) or Terminal (Mac / Linux) and paste the following. This downloads all the necessary files into your computer.
```
git clone https://github.com/adencorey/Eulerian_CFD.git
cd Eulerian_CFD
```

If you don't have Git installed, you can also download the .zip files in GitHub and extract it. Then paste the following, replacing the path with the absolute path to the folder.
```
cd absolute/path/to/Eulerian_CFD
```

## 2. Create virtual environment

This downloads all dependencies into a folder, so uninstalling is easier.

#### Windows
```
python -m venv venv
venv\Scripts\activate
```

####  Mac / Linux
```
python3 -m venv venv
source venv/bin/activate
```
###  Install dependencies
```
pip install -r requirements.txt
```

##  3. Running the program

Make sure you are in the program directory first.
```
python -m cfd
```
Wait for a few minutes to compile all the algorithms, then an interface should appear.

