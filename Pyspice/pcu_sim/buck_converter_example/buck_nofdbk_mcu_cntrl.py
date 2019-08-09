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
# Python code block
##########
class MyNgSpiceShared(NgSpiceShared):


    def __init__(self, amplitude, **kwargs):
        super().__init__(**kwargs)
        self._amplitude = amplitude
        # Section below needed only to prevent harmless "AttributeError: 'MyNgSpiceShared' object has no attribute 'clk_out'"
        #messages at beginning of run
        self.clk_out = 0
        self.gate_drive1 = 0
        #####
        # Section below actually needed for initialization.
        #####
        #clock inits
        self.clk_out_old = 0
        self.ana_time_old = 0.0
        self.time_filt = 0.0
        #PWM inits
        self.clk_cycls = 0.0
        self.dc_pct = 0.0
        self.i = 0.0
        self.duty = 0.0
        
    
    #########
    # the def get_vsrc_data function provides digital signals from the python block to the ngspice block
    #########
    def get_vsrc_data(self, voltage, time, node, ngspice_id):
        self._logger.debug('ngspice_id-{} get_vsrc_data @{} node {}'.format(ngspice_id, time, node))
        
        #####
        # Debugging aid shows timestep deltas (not just time stamps) when non-zero, and in RED when negative
        #####
        timestep = time - self.ana_time_old
        '''
        if timestep > 0:
            print('Timestep = ', time - self.ana_time_old)
        if timestep < 0:
            print('\033[1;31mTimestep = ', time - self.ana_time_old, '\033[1;31m  ************************************************************************************************************************') 
        '''
        self.ana_time_old = time # END debugging aid
        
        
        # the calculations following this conditional are only executed once per dig_timestep.
        # This runs on every positive and negative clock edge
        
        if (round(self.clk_out) != round(self.clk_out_old)) and (time != self.time_filt):
            self.time_filt = time #Need time stamp to avoid executing this code redundantly
            self.clk_out_old = self.clk_out #Need state of clk to know when it next changes
            
            
            self.clk_cycls+=1
            
            
            # PWM output stage
            # duty cycle = 0.17
            # buck fsw=200k, period=5us
            # switch period is 5us
            # sw_period = 0.000005
            # This if statement runs on every positive and negative edge.
            # clock period: 100ns
            # new clock edge every: 50ns
            # clock edge speed: 20MHz
            # number of clock edges per switching period: 100
            self.dc_pct = 17 # 17% duty cycle
            self.i += 1
            # if self.i < self.dc_pct:
                # print('duty high')
            if self.i >= self.dc_pct:
                self.duty = 0
                # print('duty low')
            if self.i >= 100:
                self.i=0
                self.duty = 1
                # print('duty high')
            

                        
            # scale the duty cycle to the drive voltage
            self.gate_drive1=self._amplitude*self.duty
                
        ################### Outputs below go from Python to NGspice####################################################            
        if node == 'vgate_drive1':
            voltage[0]=self.gate_drive1
        
        # Dummy outputs below are just for probing.  They are no-connects in NGspice    
            
        return 0
        
            
    ############################################## 
    # NGspice data sent to Python

    def send_data(self, actual_vector_values, number_of_vectors, ngspice_id):
        self.clk_out = actual_vector_values['clk'].real
        return 0



##########
# NGspice block
##########
circuit = Circuit('Buck Converter')

circuit.include(spice_library['1N5822']) # Schottky diode
# nch mosfet for pulling pch gate to ground
circuit.include(spice_library['irf150'])
# pch mosfet for driving buck output
circuit.include(spice_library['DMG4435SSS'])




# Real analog stimuli below:
circuit.V('gate_drive1', 'gate_drive1_net', circuit.gnd, 'dc 0 external')


# Other NGspice circuit parameters for buck stage
Vin = 28@u_V
Vout = 5@u_V
Rload = 3@u_Ohm

L = 150@u_uH
RL = 100@u_mOhm

Cout = 22@u_uF
ESR = 20@u_mOhm
ESL = 0

ESR_in = 120@u_mOhm
Cin = 10@u_uF


# parameters on input to buck
circuit.V('input', 'input', circuit.gnd, Vin)
circuit.C('input', 'input', circuit.gnd, Cin)

#####
# Buck switch
#####
# p-channel buck switch
circuit.X('Q', 'DMG4435SSS', 'pch_drain', 'p_gate_drive', 'input')

# resistor from p-channel gate to Vin to bring pchan gate back to Vin when off
circuit.R('pgate', 'input', 'p_gate_drive', 1@u_Ohm)
# nchannel mosfet to pull pchannel gate to ground to turn it on
circuit.X('Q3', 'irf150', 'p_gate_drive', 'nchan_sw_drive', circuit.gnd)
# resistor to drive nch fet, drive comes from controller
circuit.R('pgate_nch', 'nchan_sw_drive', 'gate_drive1_net', 1@u_Ohm)


#####
# Buck LC output and diode
#####
circuit.X('D', '1N5822', circuit.gnd, 'pch_drain')
circuit.L(1, 'pch_drain', 1, L)
circuit.R('L', 1, 'out', RL)
circuit.C(1, 'out', circuit.gnd, Cout) # , initial_condition=0@u_V
circuit.R('load', 'out', circuit.gnd, Rload)



# This clock is used for NGspice mixed signal simulation.
# The python code runs every clock edge, both positive and negative
# clock speed: 20MHz
# clock cycle length: 50ns
circuit.PulseVoltageSource('clk', 'clk', circuit.gnd, 0@u_V, 1@u_V, 0.05@u_us, 0.1@u_us)


#####
# Add a step load
#####
# ~ circuit.PulseVoltageSource('name', n1, n2, v_low, v_high, t_high, t_period, t_delay,t_rise,t_fall)
circuit.PulseVoltageSource('load_sw', 'gate_drive2', circuit.gnd, 0@u_V, 10@u_V, 1@u_s,1@u_s,0.8@u_ms,10@u_ns)

# load switch
circuit.X('Q2', 'irf150', 'out', 'gate2', 'source2')
circuit.R('gate2', 'gate2', 'gate_drive2', 1@u_Ohm)
circuit.R('load_on','source2', circuit.gnd,Rload)

#####
# Simulation parameters
#####
# Python block input constants
amplitude = 10@u_V

# Call the MyNgSpiceShared
ngspice_shared = MyNgSpiceShared(amplitude=amplitude, send_data=True)

simulator = circuit.simulator(temperature=25, nominal_temperature=25,simulator='ngspice-shared',ngspice_shared=ngspice_shared)

simulator.initial_condition(clk=0)
# step time is 0.1us, 100 datapoints per clock switch period, and 25 datapoints per buck switch period
# Total of 150 clock cycles measured and 1200 buck switch cycles
analysis = simulator.transient(step_time=.05E-6, end_time=100*20E-6)


# Print the time to run simulation
sim_end_time = datetime.datetime.now()
print()
print('Simulation End Time =', sim_end_time)
elapsed = sim_end_time - sim_start_time
print('Total Simulation Time =', elapsed)
print()

#####
# Plotting
#####

#plots of circuit components
figure = plt.figure(1, (10, 5))
axe = plt.subplot(111)

plot(analysis.out, axis=axe)
# plot(analysis.gate_drive1_net, axis=axe)
plot(analysis.source2/circuit['Rload_on'].resistance,axis=axe)
plt.axhline(y=float(Vout), color='red')
plt.grid()
plt.xlabel('t [s]')
plt.ylabel('[V]')

plt.tight_layout()
plt.show()

# plots of mcu internal signals
'''
figure = plt.figure(2, (10, 5))
axe = plt.subplot(111)

plot(analysis.clk, axis=axe)
plot(analysis.gate_drive1_net, axis=axe)

plt.grid()
plt.xlabel('t [s]')
plt.ylabel('[V]')

plt.tight_layout()
plt.show()
'''