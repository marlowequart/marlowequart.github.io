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

'''
8/12/19
I need to get this switch working right with a basic mosfet

'''

'''
class MyNgSpiceShared(NgSpiceShared):


    def __init__(self, amplitude, frequency, **kwargs):

        super().__init__(**kwargs)

        # self._amplitude = amplitude
        # self._pulsation = float(frequency.pulsation)
		
		self.pwm_input = 0.0


    def get_vsrc_data(self, voltage, time, node, ngspice_id):
        self._logger.debug('ngspice_id-{} get_vsrc_data @{} node {}'.format(ngspice_id, time, node))
        voltage[0] = self._amplitude * math.sin(self._pulsation * time)
		
		
        if self.pwm_input > 2.0:
			self.v_drain_output = 
		
		
		################### Outputs below go from Python to NGspice####################################################            
        if node == 'vgate_drive1':
            voltage[0]=self.gate_drive1
        # elif node == 'vb':
            # voltage[0]=self.vb_val          
        # elif node == 'vc':
            # voltage[0]=self.vc_val
        
        # Dummy outputs below are just for probing.  They are no-connects in NGspice    
        # elif node == 'vdc_pct_out': # this can be used to probe various "nets" inside the Python (not NGspice)
            # voltage[0]=self.dc_pct #output of elliptic filter
            
        # send the data
        # self.send_data(self, number_of_vectors=2,ngspice_id=ngspice_id)
        return 0


    # def get_isrc_data(self, current, time, node, ngspice_id):
        # self._logger.debug('ngspice_id-{} get_isrc_data @{} node {}'.format(ngspice_id, time, node))
        # current[0] = 1.
        # return 0
		
		
    ############################################## 
    # NGspice data sent to Python

    # def send_data(self):
    def send_data(self, actual_vector_values, number_of_vectors, ngspice_id):
        # self.clk_out = actual_vector_values['clk'].real
        self.pwm_input = actual_vector_values['hs_res_out'].real
		self.v_source_input = actual_vector_values['sw_node'].real
		# self.v_drain_input = actual_vector_values[circuit.gnd].real
        # self.gate_drive1_out = actual_vector_values['gate_drive1'].real
        #~ self.idt_in_1 = actual_vector_values['x1.xx1.xx5.xx2.xx7.idt_in'].real  # example of probing a net in the hierarchy
        return 0
'''
		

circuit = Circuit('Load Switch')

sw_model='''
.model SW SW(Ron=10 Roff=1Meg Vt=3.0)
'''
ngspice.load_circuit(sw_model)

# mos_model='''
# .model MyMOSFET NMOS(KP=.001)
# '''
# ngspice.load_circuit(mos_model)

# circuit.include(spice_library['irf150'])
# circuit.include(spice_library['1N5822'])
# circuit.include(spice_library['mq100'])
# circuit.include(spice_library['IXKK85N60C'])

# Input Source
circuit.V('input', 'input', circuit.gnd, 20@u_V)
# Load parameters
# circuit.R('load', 'sw_node', 'load_L', 70@u_mOhm)
# circuit.L('load', 'load_L', circuit.gnd, 70@u_uH)



# Simple controller comparing reference to triangle
# circuit.PulseVoltageSource('name', n1, n2, v_low, v_high, t_high, t_period, t_delay,t_rise,t_fall)
circuit.PulseVoltageSource('triangle', 'tri_ref', circuit.gnd, 0@u_V, 10@u_V, 0.1@u_us, 50@u_us, 0@u_s, 25@u_us,25@u_us)
circuit.SinusoidalVoltageSource('reference', 'sin_ref', circuit.gnd, amplitude=4.9@u_V, offset=5@u_V, frequency=400@u_Hz)


# high side comparator. Output to drive HS mosfet is referenced to circuit.gnd
circuit.V('drive_hs', 'drive_hs', circuit.gnd, 20@u_V)
circuit.VoltageControlledSwitch(input_plus='sin_ref',input_minus='tri_ref',output_minus='hs_res_out',output_plus='drive_hs',name='switch11',model=None)
circuit.R('gate_res_hs', 'hs_res_out', 'sw_drive', 1@u_Ohm)
circuit.R('pulldown', 'hs_res_out', circuit.gnd, 100@u_Ohm)	#pulldown to keep sw_drive reasonable

# low side comparator. Output to drive LS mosfet is referenced to -VPWR
# circuit.V('testing2', 'test_out2', '_mfilm_p', 10@u_V)
# circuit.VoltageControlledSwitch(input_plus='tri_ref',input_minus='sin_ref',output_minus='ls_res2',output_plus='test_out2',name='switch12',model=None)
# circuit.R('gate_res2', 'ls_res2', '_mfilm_p', 10@u_Ohm)


# Using mosfet for load switch
# circuit.X('Qls', 'irf150', 'sw_node', 'hs_res_out', circuit.gnd)
# circuit.X('Qls', 'IXKK85N60C', 'sw_node', 'hs_res_out', circuit.gnd)
# circuit.X('D1', '1N5822', 'sw_node','input')
# circuit.X('Qls', 'irf150', 'sw_node', 'sw_drive', circuit.gnd)


# using basic switch in python loop
# circuit.V('drain_output', 'sw_node', circuit.gnd, 'dc 0 external')




# Load parameters
# circuit.R('load', 'input', 'load_L', 100@u_mOhm)
# circuit.L('load', 'load_L', 'sw_node', 70@u_uH)

circuit.R('load', circuit.gnd, 'sw_node', 1@u_Ohm)

# circuit.PulseVoltageSource('name', n1, n2, v_low, v_high, t_high, t_period, t_delay,t_rise,t_fall)
# circuit.PulseVoltageSource('pulse', 'sw_drive', circuit.gnd, 0@u_V, 10@u_V, 1@u_s, 1@u_s, 100@u_us)



# This switch is implemented using the model called out in sw_model above
# circuit.S(n1,n2,cntrl_sw+,cntrl_sw-,sw_model)
# circuit.S(circuit.gnd,'sw_node',circuit.gnd,'hs_res_out',sw_model)


# Here is a way to implement a switch without including the netlist like above
# circuit.VoltageControlledSwitch(sw_high_node, sw_low_node, drive_high, drive_low, 'name', model=None)
# circuit.VoltageControlledSwitch(input_plus='sw_node',input_minus=circuit.gnd,output_plus='sw_drive',output_minus=circuit.gnd,name='sw1',model=None)
# circuit.VoltageControlledSwitch('sw_drive',circuit.gnd,'sw_node',circuit.gnd,'sw1',model=sw_model)
circuit.VoltageControlledSwitch('input','sw_node','sw_drive',circuit.gnd,'sw1',model=None)


#####
# Simulation parameters
#####

# Parameters for basic simulation
simulator = circuit.simulator(temperature=25, nominal_temperature=25)
# # period is 2.5us, 300 datapoints per switch period, 150 switch periods captured
analysis = simulator.transient(step_time=0.1E-6, end_time=5E-3)


# Parameters for using python loop
# Call the MyNgSpiceShared
# ngspice_shared = MyNgSpiceShared(amplitude=amplitude, send_data=True)
# simulator = circuit.simulator(temperature=25, nominal_temperature=25,simulator='ngspice-shared',ngspice_shared=ngspice_shared)

# simulator.initial_condition(clk=0)
# step time is 0.1us, 100 datapoints per clock switch period, and 25 datapoints per buck switch period
# Total of 150 clock cycles measured and 1200 buck switch cycles
# analysis = simulator.transient(step_time=0.1E-6, end_time=5E-3)


#####
# Plot
#####
NUMBER_PLOTS = '3'

#plots of circuit components
figure = plt.figure(1, (10, 5))
plot1 = plt.subplot(int(NUMBER_PLOTS+'11'))

# Plot of references
plot(analysis.tri_ref, color='r')
plot(analysis.sin_ref, color='b')
plt.grid()
plt.xlabel('t [s]')
plt.ylabel('[V]')
plt.legend(('Triangle Reference','Sin Reference'), loc=(.05,.1))


plot2 = plt.subplot(int(NUMBER_PLOTS+'12'))

# Plot of sw drive
plot(analysis.sw_drive, color='r')
plt.grid()
plt.xlabel('t [s]')
plt.ylabel('[V]')
plt.legend(('Switch Drive',''), loc=(.05,.1))

plot3 = plt.subplot(int(NUMBER_PLOTS+'13'))
# ax2 = plot3.twinx()
# Plot of load voltage/current
plot(analysis.sw_node, color='r')
plot((analysis.sw_node)/circuit['Rload'].resistance,color='b')
plt.grid()
plt.xlabel('t [s]')
plt.ylabel('[V]')
plt.legend(('Switch Node','Load Current'), loc=(.05,.1))

plt.tight_layout()
plt.show()
