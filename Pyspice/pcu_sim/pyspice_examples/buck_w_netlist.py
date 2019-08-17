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
circuit.include(spice_library['buck_netlist'])
# Top level circuit annotated as "x1"
circuit.X(1,'buck_netlist', 'Vin', 'duty_cycle', 'period') 



# From Microchip WebSeminars - Buck Converter Design Example

Vin = 12@u_V
Vout = 5@u_V
ratio = Vout / Vin

frequency = 400@u_kHz
period = frequency.period
duty_cycle = ratio * period






#####
# Simulation parameters
#####

print()
simulator = circuit.simulator(temperature=25, nominal_temperature=25)
analysis = simulator.transient(step_time=period/300, end_time=period*150)


#####
# Plot
#####

figure = plt.figure(1, (10, 5))
axe = plt.subplot(111)

plot(analysis.out, axis=axe)
plot(analysis['source'], axis=axe)
# plot(analysis['source'] - analysis['out'], axis=axe)
# plot(analysis['gate'], axis=axe)
plt.axhline(y=float(Vout), color='red')
plt.legend(('Vout [V]', 'Vsource [V]'), loc=(.8,.8))
plt.grid()
plt.xlabel('t [s]')
plt.ylabel('[V]')

plt.tight_layout()
plt.show()

#f# save_figure('figure', 'buck-converter.png')

