Offline Land Model Testbed (OLMT)
Contact:  Dan Ricciuto (ricciutodm@ornl.gov)

OLMT is a set of python scripts designed to automate offline land model (ELM and CLM/CTSM) simulations at single sites, groups of sites, user-defined regions or global scales.
It will automatically create, build and submit the 3 cases needed for a full land model BGC simulation:
ad spinup:     Accelerated decomposition spinup (Thornton and Rosenbloom, 2005)
final spinup:  Final spinup to equilibrate carbon and nutrient pools
transient:     1850-present day simulation with transient CO2, land use, climate, etc.

This utility will automatically create surface and domain files using an existing global file at the specified resolution (default:  hcru_hcru).
