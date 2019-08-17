'''
Python version 3.7
NGSpice version ngspice-30
Pyspice version 1.3.2
Scipy version 1.2.0
matplotlib version 3.0.3
'''
####################################################################################################

import matplotlib.pyplot as plt

####################################################################################################

import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()

####################################################################################################

from PySpice.Doc.ExampleTools import find_libraries
from PySpice.Probe.Plot import plot
from PySpice.Spice.Library import SpiceLibrary
from PySpice.Spice.Netlist import Circuit
from PySpice.Unit import *

####################################################################################################
# Stuff for model
from PySpice.Spice.NgSpice.Shared import NgSpiceShared

####################################################################################################

libraries_path = find_libraries()
spice_library = SpiceLibrary(libraries_path)

####################################################################################################

circuit = Circuit('Basic Switch')


circuit.PulseVoltageSource('pulse', 'sw_drive', circuit.gnd, 0@u_V, 10@u_V, 1@u_ms, 2@u_ms,)

circuit.V('input', 'input', circuit.gnd, 20@u_V)
circuit.R('load', circuit.gnd, 'sw_node', 5@u_Ohm)
circuit.VoltageControlledSwitch('input','sw_node','sw_drive',circuit.gnd,'sw1',model=None)



#####
# Simulation parameters
#####

# Parameters for basic simulation
simulator = circuit.simulator(temperature=25, nominal_temperature=25)
analysis = simulator.transient(step_time=0.1E-6, end_time=50E-3)



#####
# Plots
#####
NUMBER_PLOTS = '2'

#plots of circuit components
figure = plt.figure(1, (10, 5))
plot1 = plt.subplot(int(NUMBER_PLOTS+'11'))

# Plot of references
plot(analysis.sw_drive, color='r')

plt.grid()
plt.xlabel('t [s]')
plt.ylabel('[V]')
plt.legend(('Switch Drive',''), loc=(.05,.1))


plot2 = plt.subplot(int(NUMBER_PLOTS+'12'))

# Plot of sw drive
plot(analysis.sw_node, color='r')
plot((analysis.sw_node)/circuit['Rload'].resistance,color='b')
plt.grid()
plt.xlabel('t [s]')
plt.ylabel('[V]')
plt.legend(('Switch Output','Load Current'), loc=(.05,.1))



plt.tight_layout()
plt.show()