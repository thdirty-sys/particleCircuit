The TASEP circuit generator and simulator
=========================================

## Table of Contents

1. [Introduction](#introduction)
2. [Features](#features)
3. [Installation](#installation)
4. [Usage](#usage)

# Introduction

The Asymmetric Simple Exclusion Process (ASEP) is a Stochastic process,
first proposed by Frank Spitzer in his 1970 paper 'Interaction of Markov Processes', that models the motion
of particles over a one-dimensional space under some very basic rules which are typically summarised in the introduction to any paper on the topic.
Since then it has come to be described as the ”default stochastic model for
transport phenomena” (Horng-Tzer Yau, 2004).

This tool enables the user to draw their own circuit with customisable in/out rates, or to generate a random circuit, over which TASEP is simulated. Raw current data is recorded and graphs can be opened to observe stationarity and the unique, well-recorded properties of this process in open boundary conditions. Should be helpful for visualisation of the TASEP process.

# Features

## Draw
Users can draw their own custom circuits using an intuitive interface, enabling precise control over the simulation environment. Boundary transition rates can be set manually.

## Random Generation
Alternatively, they can choose to generate random circuits, providing a quick and diverse way to experiment with different configurations.

## Play
Once a circuit is set up, users can run detailed simulations, observing the evolution of particle flow over time.

## Analyse
After the simulation, the application provides graphing tools to visualize key metrics, such as the current over nodes.
<video width="720" height="405"><source src="./imgs/analyse_vid.mp4" type="video/mp4"><\video>

# Installation

**Confirmed successful runs on the following:**

- Operating Systems:
  - Windows 10
- Python versions:
  - 3.12.0
  
1. **Download and Install Python:**

   Ensure you have the last Python version  installed. If not, download and install it from Python's official website.

2. **Clone the repository or download manually:**

   ```bash
   git clone https://github.com/thdirty-sys/tasepC.git
   
   cd tasepC
   ```

5. **Set-up:**

   ```bash
   pip install .
   ```
   to initialise by setup.py, or
   
   ```bash
   pip install -r requirements.txt
   ```

## Usage

If properly installed, main.py in tasepC folder will run the application.
