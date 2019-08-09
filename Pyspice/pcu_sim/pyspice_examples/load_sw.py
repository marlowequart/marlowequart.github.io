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
ngspice = NgSpiceShared.new_instance()

####################################################################################################

libraries_path = find_libraries()
spice_library = SpiceLibrary(libraries_path)

####################################################################################################
import datetime
sim_start_time = datetime.datetime.now()
print()
print('Simulation Start Time =', sim_start_time)
print()
####################################################################################################




circuit = Circuit('Load Switch')

# sw_model='''
# .model SW SW(Ron=1 Roff=1Meg Vt=3.0)
# '''
# ngspice.load_circuit(sw_model)




period = 2.5@u_us



# circuit.PulseVoltageSource('name', n1, n2, v_low, v_high, t_high, t_period, t_delay,t_rise,t_fall)
circuit.PulseVoltageSource('pulse', 'sw_drive', circuit.gnd, 0@u_V, 10@u_V, 1@u_s, 1@u_s, 100@u_us)

#circuit.V('name', n1, n2, v)
circuit.V('out', 'Vout', circuit.gnd, 10@u_V)
circuit.R(1,'r_top', circuit.gnd,10@u_Ohm)

# This switch is implemented using the model called out in sw_model above
# circuit.S(n1,n2,cntrl_sw+,cntrl_sw-,sw_model)
# circuit.S('Vout','r_top','sw_drive',circuit.gnd,sw_model)


# Here is a way to implement a switch without including the netlist like above
# circuit.VoltageControlledSwitch(sw_high_node, sw_low_node, drive_high, drive_low, 'name', model=None)
circuit.VoltageControlledSwitch('Vout','r_top','sw_drive',circuit.gnd,'sw1',model=None)


#####
# Simulation parameters
#####

simulator = circuit.simulator(temperature=25, nominal_temperature=25)

# period is 2.5us, 300 datapoints per switch period, 150 switch periods captured
analysis = simulator.transient(step_time=period/300, end_time=period*150)


#####
# Plot
#####

figure = plt.figure(1, (10, 5))
axe = plt.subplot(111)

plot(analysis.sw_drive, axis=axe)
# plot(analysis.clock, axis=axe)
# plot(analysis['source'], axis=axe)

#Plot load resistor current
plot(analysis.r_top/circuit['R1'].resistance,axis=axe)

plt.grid()
plt.xlabel('t [s]')
plt.ylabel('[V]')

plt.tight_layout()
plt.show()
