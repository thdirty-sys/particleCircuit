The TASEP circuit generator and simulator
=========================================

## Table of Contents

1. [Introduction](#introduction)
2. [Installation](#installation)
4. [Configuration](#configuration)
5. [Usage](#usage)
6. [Documentation](#documentation)
7. [Troubleshooting](#troubleshooting)
8. [Conclusion](#conclusion)
9. [Contributors](#contributors)
10. [License](#license)
11. [Disclaimer](#disclaimer)

# Introduction

The Asymmetric Simple Exclusion Process (ASEP) is a Stochastic process,
first proposed by Frank Spitzer in his 1970 paper 'Interaction of Markov Processes', that models the motion
of particles over a one-dimensional space under some very basic rules which are typically summarised in the introduction to any paper on the topic.
Since then it has come to be described as the ”default stochastic model for
transport phenomena” (Horng-Tzer Yau, 2004).

This tool enables the user to draw their own circuit with customisable in/out rates, or to generate a random circuit, over which TASEP is simulated. Raw current data is recorded and graphs can be opened to observe stationarity and the unique, well-recorded properties of this process in open boundary conditions. Should be helpful for visualisation of the TASEP process.

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
   
Short-term goals
----------
- Make random generation customisable
- Complete TASEP loop without UI element for fast data collection
- Fix small bugs in path generation
- Options for the colour-blind
- Fill out needed commenting

Long-term goals
---------------
- Tools for handmade circuit crafting

Notes
---
- In the current version too much of the code is uncommented
- There are no actual 'paths' in the code, just co-ordinates pointing to other, sometimes several, co-ordinates.
  While most-likely faster for look-ups, it often leads to a confusion of conditions for sticking to the right path
- Random path generation is limited to the finite-sized grid of the UI, and favours visibility over
  breadth of generation.
- As of now, main.py does nothing

DEMO:  https://streamable.com/efikq5 
