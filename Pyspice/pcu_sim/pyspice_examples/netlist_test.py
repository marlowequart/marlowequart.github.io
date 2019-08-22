####################################################################################################

# import matplotlib.pyplot as plt

####################################################################################################

import PySpice.Logging.Logging as Logging
logger = Logging.setup_logging()

####################################################################################################

# from PySpice.Doc.ExampleTools import find_libraries
# from PySpice.Probe.Plot import plot
# from PySpice.Spice.Library import SpiceLibrary
# from PySpice.Spice.Netlist import Circuit
# from PySpice.Unit import *

####################################################################################################
# Stuff for model
from PySpice.Spice.NgSpice.Shared import NgSpiceShared

####################################################################################################

# libraries_path = find_libraries()
# spice_library = SpiceLibrary(libraries_path)

####################################################################################################
import datetime
sim_start_time = datetime.datetime.now()
print()
print('Simulation Start Time =', sim_start_time)
print()
####################################################################################################

ngspice = NgSpiceShared.new_instance()

print(ngspice.exec_command('version -f'))
# print(ngspice.exec_command('print all'))
# print(ngspice.exec_command('devhelp'))
# print(ngspice.exec_command('devhelp resistor'))

circuit = '''
.title Voltage Multiplier

.SUBCKT 1N4148 1 2
*
R1 1 2 5.827E+9
D1 1 2 1N4148
*
.MODEL 1N4148 D
+ IS = 4.352E-9
+ N = 1.906
+ BV = 110
+ IBV = 0.0001
+ RS = 0.6458
+ CJO = 7.048E-13
+ VJ = 0.869
+ M = 0.03
+ FC = 0.5
+ TT = 3.48E-9
.ENDS

Vinput in 0 DC 0V AC SIN(0V 10V 50Hz 0s 0Hz)
C0 in 1 1mF
X0 1 0 1N4148
C1 0 2 1mF
X1 2 1 1N4148
C2 1 3 1mF
X2 3 2 1N4148
C3 2 4 1mF
X3 4 3 1N4148
C4 3 5 1mF
X4 5 4 1N4148
R1 5 6 1MegOhm
.options TEMP = 25°C
.options TNOM = 25°C
.options filetype = binary
.options NOINIT
.ic
.tran 0.0001s 0.4s 0s
.end
'''

ngspice.load_circuit(circuit)

# print(ngspice.show('c3'))
# print(ngspice.showmod('c3'))

ngspice.run()
# print('Plots:', ngspice.plot_names)

# print(ngspice.ressource_usage())
# print(ngspice.status())

plot = ngspice.plot(simulation=None, plot_name=ngspice.last_plot)
print(plot)


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