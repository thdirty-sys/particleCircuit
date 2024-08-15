The TASEP circuit generator and simulator
=========================================

The Asymmetric Simple Exclusion Process (ASEP) is a Stochastic process,
first proposed by Frank Spitzer in his 1970 paper 'Interaction of Markov Processes', that models the motion
of particles over a one-dimensional space under some very basic rules which are typically summarised in the introduction to any paper on the topic.
Since then it has come to be described as the ”default stochastic model for
transport phenomena” (Horng-Tzer Yau, 2004. Law of the two dimensional asymmetric simple exclusion
process. Annals of mathematics). TASEP limits the movement of particles to one 'forwards' direction.

Using this tool, a 'circuit' can be randomly generated, as well as pathing between elements of the circuit such
that TASEP is appropriate with open-boundary conditions.

To use the program download the project and run 'dpgEnviron.py'. Within the code is an at-the-moment
defunct TASEP motor that does not involve the UI. Will be made operational soon.

This is a very primitive version. There are only a few rare bugs in random path generation.

Short-term goals
----------
- Make random generation customisable
- Complete TASEP loop without UI element for fast data collection
- Fix small bugs in path generation

Long-term goals
---------------
- Tools for handmade circuit crafting