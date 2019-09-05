####################################################################################################

import matplotlib.pyplot as plt
import pandas as pd
import numpy as np

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
        #####
        # Section below actually needed for initialization.
        #####
        #clock inits
        self.clk_out_old = 0
        self.ana_time_old = 0.0
        self.time_filt = 0.0
        # voltage output inits
        self.clk_cycls = 0.0
        self.volts = 0.0
        
        # Load the csv data
        # CH1: PHA to B Volts CH2: ResCos CH3: ResSin CH4: PHB Current
        df = pd.read_csv('tek0015ALL.csv',header=0)
        self.data=pd.np.array(df[['CH3']])
        # print()
        # print(self.data[0:20])
        # print()
        
        # Data time step: 20ns, 20*10^-9
        # Want to change the sampled voltage every 20ns
        # That makes clock speed one edge ev 20ns, or 40ns period (2.5MHz)
        
        
    
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
            
            self.volts = self.data[int(self.clk_cycls)]
            self.clk_cycls+=1
            # print(self.clk_cycls, type(self.clk_cycls))
            
            
            
            
                
        ################### Outputs below go from Python to NGspice####################################################            
        if node == 'vsense':
            voltage[0]=self.volts
        elif node == 'vsense2':
            voltage[0]=self.volts
        
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
circuit = Circuit('Filter')




# Real analog stimuli from python code below:
circuit.V('sense', 'sense_net', circuit.gnd, 'dc 0 external')
circuit.V('sense2', 'sense_net_2', circuit.gnd, 'dc 0 external')


# Other NGspice circuit parameters for filter stage


# Cout = 22@u_uF
# ESR = 20@u_mOhm
# ESL = 0




# parameters on input to buck
# circuit.V('input', 'input', circuit.gnd, Vin)
# circuit.C('input', 'input', circuit.gnd, Cin)


circuit.C(1, 'esr', circuit.gnd, 22@u_uF) # , initial_condition=0@u_V
circuit.R(1, 'sense_net_2', 'esr', 10@u_Ohm)



# This clock is used for NGspice mixed signal simulation.
# The python code runs every clock edge, both positive and negative
# clock speed: 2.5MHz
# clock cycle length: 40ns
circuit.PulseVoltageSource('clk', 'clk', circuit.gnd, 0@u_V, 1@u_V, 20@u_ns, 40@u_ns)




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
analysis = simulator.transient(step_time=20E-9, end_time=1E-3)


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

plot(analysis.sense_net, axis=axe)
plot(analysis.esr, axis=axe)
# plot(analysis.gate_drive1_net, axis=axe)
# plot(analysis.source2/circuit['Rload_on'].resistance,axis=axe)
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