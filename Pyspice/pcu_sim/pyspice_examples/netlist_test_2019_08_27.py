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
import datetime
sim_start_time = datetime.datetime.now()
print()
print('Simulation Start Time =', sim_start_time)
print()
####################################################################################################

##########
# NGspice block
##########
circuit = Circuit('Stator Drive')


circuit.include(spice_library['test_netlist'])
# Top level circuit annotated as "x1"
circuit.X(1,'test_netlist', 'gate_drive1', 'sw_node_hs1', 'gate_drive2', 'sw_node_hs2', 'gate_drive3', 'sw_node_hs3', 'sin_ref', 'tri_ref')


# Create input voltage to send to netlist
# Vinput=100@u_V
# circuit.V('input_p', 'vin_p', circuit.gnd, Vinput)
# circuit.V('input_m', circuit.gnd, 'vin_m', Vinput)


# Simple controller comparing reference to triangle
# circuit.PulseVoltageSource('name', n1, n2, v_low, v_high, t_high, t_period, t_delay,t_rise,t_fall)
circuit.PulseVoltageSource('triangle', 'tri_ref', circuit.gnd, 0@u_V, 10@u_V, 0.1@u_us, 50@u_us, 0@u_s, 25@u_us,25@u_us)
circuit.SinusoidalVoltageSource('reference', 'sin_ref', circuit.gnd, amplitude=4.9@u_V, offset=5@u_V, frequency=400@u_Hz)


# Run a simple simulation on the basic circuit
# triangle wave is 50us, 10 samples gives min time step 5us
print()
simulator = circuit.simulator(temperature=25, nominal_temperature=25)
# simulator.options(reltol=1000E-6, chgtol=1E-14, abstol=1E-12, gmin=1E-12, vntol=1E-6, rseries=0, trtol=7, rshunt=1E12, xmu=0.5, maxord=2, itl3=4, itl4=10, itl5=5000) #NgSpice defaults (similar to LTspice)
# simulator.options(reltol=1E-3, chgtol=1E-13, abstol=1E-11, gmin=1E-12, vntol=1E-5, rseries=10E-6, trtol=7, rshunt=1.0E12, xmu=0.5, maxord=6, itl3=8, itl4=20, itl5=0)
# simulator.options(reltol=1E-3, chgtol=1E-13, abstol=1E-11, gmin=1E-12, vntol=1E-5, rseries=10E-6, trtol=7, rshunt=1.0E12, xmu=0.5, maxord=6, itl4=20)
simulator.initial_condition(sw_node_hs1=0, tri_ref=0)
# ~ analysis = simulator.transient(step_time=5E-6, start_time=20E-3, end_time=30E-3,max_time=10000E-6, use_initial_condition=True)
analysis = simulator.transient(step_time=.005E-6, start_time=1E-3, end_time=3.5E-3, use_initial_condition=True)


# Print the time to run simulation
sim_end_time = datetime.datetime.now()
print()
print('Simulation End Time =', sim_end_time)
elapsed = sim_end_time - sim_start_time
print('Total Simulation Time =', elapsed)
print()

'''

figure = plt.figure(1, (10, 5))
axe = plt.subplot(111)

# plot(analysis.vin_p, axis=axe)
# plot(analysis.vin_m, axis=axe)
# plt.legend(('Vin plus [V]', 'Vin minus [V]'), loc=(.8,.8))

plot(analysis.hs_drive, axis=axe)
plot(analysis.ls_drive, axis=axe)
plt.legend(('hs_drive [V]', 'ls_drive [V]'), loc=(.8,.8))

# plot current
# plot(analysis.output_v/5, axis=axe)

# plt.legend(('hs_drive [V]', 'ls_drive [V]'), loc=(.8,.8))
plt.grid()
plt.xlabel('t [s]')
plt.ylabel('[V]')

plt.tight_layout()
plt.show()
'''

NUMBER_PLOTS = '6'

#plots of circuit components
figure = plt.figure(1, (10, 5))
plot1 = plt.subplot(int(NUMBER_PLOTS+'11'))

plot(analysis.gate_drive1)
# plot(analysis.N025)
# plot(analysis.N101)
plt.legend(('gate drive 1 [V]', '',''), loc=(.8,.8))

plt.grid()
plt.xlabel('t [s]')
plt.ylabel('[V]')



plot2 = plt.subplot(int(NUMBER_PLOTS+'12'))

plot(analysis.sw_node_hs1)
# plot(analysis.tri_ref)
plt.legend(('Switch Node 1',''), loc=(.05,.1))

plt.grid()
plt.xlabel('t [s]')
plt.ylabel('[V]')



plot3 = plt.subplot(int(NUMBER_PLOTS+'13'))

# ~ plot(analysis.input_p_net)
# ~ plot(analysis.input_m_net)
plot(analysis.gate_drive2)
plt.grid()
plt.xlabel('t [s]')
plt.ylabel('[V]')

plt.legend(('gate drive 2',''), loc=(.05,.1))


plot4 = plt.subplot(int(NUMBER_PLOTS+'14'))
# Plot load current
plot(analysis.sw_node_hs2)
# plot((analysis.sw_node-analysis.load_l)/circuit['Rload_esr'].resistance)
plt.grid()
plt.xlabel('t [s]')
plt.ylabel('[V]')
plt.legend(('sw node 2',''), loc=(.05,.1))

plot5 = plt.subplot(int(NUMBER_PLOTS+'15'))

# ~ plot(analysis.input_p_net)
# ~ plot(analysis.input_m_net)
plot(analysis.gate_drive3)
plt.grid()
plt.xlabel('t [s]')
plt.ylabel('[V]')

plt.legend(('gate drive 3',''), loc=(.05,.1))


plot6 = plt.subplot(int(NUMBER_PLOTS+'16'))
# Plot load current
plot(analysis.sw_node_hs3)
# plot((analysis.sw_node-analysis.load_l)/circuit['Rload_esr'].resistance)
plt.grid()
plt.xlabel('t [s]')
plt.ylabel('[V]')
plt.legend(('sw node 3',''), loc=(.05,.1))


plt.tight_layout()
plt.show()

