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

libraries_path = find_libraries()
spice_library = SpiceLibrary(libraries_path)
print('libraries_path = '+libraries_path)

####################################################################################################
import datetime
sim_start_time = datetime.datetime.now()
print()
print('Simulation Start Time =', sim_start_time)
print()
####################################################################################################


#?# circuit_macros('buck-converter.m4')

circuit = Circuit('Buck Converter')

# Note that PySpice will parse ALL *.lib in the directory, even if they are not included, so keep extra .libs out
# the directory where the .lib files are called from is specified in 'libraries_path' (line 327 above)
circuit.include(spice_library['buck_netlist_simple'])
# Top level circuit annotated as "x1"
circuit.X(1,'buck_netlist_simple', 'vin', 'gate_drive', 'output_v', 'sw_node') 


Vin = 12@u_V
# Vout = 6@u_V
# ratio = Vout / Vin

# frequency = 400@u_kHz
# period = 2.5@u_us
# duty_cycle = 1.25@u_us



# Create input voltage to send to netlist
circuit.V('input', 'vin', circuit.gnd, Vin)


#####
# Simulation parameters
#####
period = 2.5@u_us
print()

simulator = circuit.simulator(temperature=25, nominal_temperature=25)
simulator.initial_condition(output_v=0)
analysis = simulator.transient(step_time=period/300, end_time=period*300)


#####
# Plot
#####

figure = plt.figure(1, (10, 5))
axe = plt.subplot(111)

# plot(analysis.sw_node, axis=axe)
plot(analysis.output_v, axis=axe)
# plot current
# plot(analysis.output_v/5, axis=axe)

plt.legend(('Vout [V]', 'Iout [A]'), loc=(.8,.8))
plt.grid()
plt.xlabel('t [s]')
plt.ylabel('[V]')

plt.tight_layout()
plt.show()

#f# save_figure('figure', 'buck-converter.png')

