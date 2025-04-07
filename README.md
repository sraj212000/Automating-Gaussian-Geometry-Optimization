# Automating-Gaussian-Geometry-Optimization

## Introduction

Geometry optimization is a fundamental step in quantum chemical simulations, aiming to find the lowest energy structure of a molecule by adjusting atomic positions. It helps ensure that further calculations, such as frequency analysis or electronic structure studies, are performed on a stable configuration. **Gaussian** is one of the most widely used computational chemistry packages for this purpose, capable of optimizing molecular geometries using various methods (e.g., HF, DFT, MP2).

This repository provides a streamlined pipeline to automate the generation of Gaussian input files and the execution of geometry optimization jobs on a computational server.

---

## Step 1: Create the Gaussian Input File

Use the Python script **`Gaussian_opt_input.py`** to generate the `.gjf` input file needed for geometry optimization.

[Gaussian_opt_input.py](./Gaussian_opt_input.py)

This script takes molecular coordinates and other job parameters to prepare a valid Gaussian input file formatted for geometry optimization.

---

## Step 2: Run the Gaussian Job on a Server

Once the input file is generated, use the **`Gaussian_Run.py`** script to automatically submit and manage the job on a server with Gaussian installed.

This script ensures smooth execution of your optimization job, handles queuing (if applicable), and captures the output for analysis.

---

Feel free to clone, modify, or extend this workflow based on your project requirements. Contributions and improvements are welcome!
