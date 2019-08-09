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
        #filter inits
        self.inz2 = 0.0 
        self.inz1 = 0.0
        self.midz2 = 0.0
        self.midz1 = 0.0
        self.outz2 = 0.0
        self.outz1 = 0.0
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
        
        # print()
        # print('clk_out= '+str(round(self.clk_out))+', clk_out_old= '+str(round(self.clk_out_old))+', time= '+str(round(time,7))+', time_filt= '+str(round(self.time_filt,7)))
        if (round(self.clk_out) != round(self.clk_out_old)) and (time != self.time_filt):
            self.time_filt = time #Need time stamp to avoid executing this code redundantly
            self.clk_out_old = self.clk_out #Need state of clk to know when it next changes
            
            # duty_raw = g_angle*(pot_bip-trgt_bip) #Raw duty cycle is simply gain times actual minus target angle.
            # duty = min(abs(duty_raw),1) #Clip raw duty to get duty
            
            self.clk_cycls+=1
            # print()
            # print('clk_cycls= '+str(self.clk_cycls))
            
            
            # PWM output stage
            # duty cycle = 0.2
            # buck fsw=200k, period=5us
            # switch period is 5us
            # sw_period = 0.000005
            # This if statement runs on every positive and negative edge.
            # clock period: 1000ns
            # new clock edge every: 500ns
            # clock edge speed: 2MHz
            # number of clock edges per switching period: 100
            self.dc_pct = 50 # 20% duty cycle
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
            

            ################################################################
            """ 
            Elliptic filter below for current limit loop to supress the 18.3kHz (min) resonance of the first LC in the output filter.
            See Elliptic_62k5Hz_4th_500mdB_15kHz.py for details.  Topology is Direct Form 1.
            """
            '''
            b10 = 0.1795978
            b11 = 0.25263921
            b12 = 0.1795978
            a10 = 1.
            a11 = -0.39029624
            a12 = 0.25226106
            b20 = 1.
            b21 = 0.35147428
            b22 = 1.
            a20 = 1.
            a21 =-0.06669631
            a22 = 0.83470697
    
            mid_filt = ovr_i_pz*b10 + self.inz1*b11 + self.inz2*b12 - self.midz1*a11 - self.midz2*a12
            out_filt = mid_filt*b20 + self.midz1*b21 + self.midz2*b22 - self.outz1*a21 - self.outz2*a22
            self.inz2 = self.inz1  
            self.inz1 = ovr_i_pz
            self.midz2 = self.midz1
            self.midz1 = mid_filt
            self.outz2 = self.outz1
            self.outz1 = out_filt
            '''
            ########################### END of elliptic filter##############
            
            # duty = min(self.outz1, duty)   # cannot use out_filt here (it's not remembered)
            # if self.i_pol == -1:
                # d_scaled = self.outz1 # no feed forward needed for reverse current regulation; better to use full bus voltage (not 22V max). Also need to override positional loop (use self.outz1 instead of duty here); active high instead of just open-drain output for outz1 when regulating reverse current.
            # else:
                # d_scaled = min(max(0, duty*22/self.p_28v_out), 1) # feed-forward of Vbus
            
            # scale the duty cycle to the drive voltage
            self.gate_drive1=self._amplitude*self.duty
            # print(duty, gate_drive1)
                
        ################### Outputs below go from Python to NGspice####################################################            
        if node == 'vgate_drive1':
            voltage[0]=self.gate_drive1
        # elif node == 'vb':
            # voltage[0]=self.vb_val          
        # elif node == 'vc':
            # voltage[0]=self.vc_val
        
        # Dummy outputs below are just for probing.  They are no-connects in NGspice    
        elif node == 'filt_out': # this can be used to probe various "nets" inside the Python (not NGspice)
            voltage[0]=self.outz1 #output of elliptic filter
            
        # send the data
        # self.send_data(self, number_of_vectors=2,ngspice_id=ngspice_id)
        return 0
        
            
    ############################################## 
    # NGspice data sent to Python

    # def send_data(self):
    def send_data(self, actual_vector_values, number_of_vectors, ngspice_id):
        self.clk_out = actual_vector_values['clk'].real
        self.v_sns = actual_vector_values['v_sns'].real
        # self.gate_drive1_out = actual_vector_values['gate_drive1'].real
        #~ self.idt_in_1 = actual_vector_values['x1.xx1.xx5.xx2.xx7.idt_in'].real  # example of probing a net in the hierarchy
        return 0



##########
# NGspice block
##########
circuit = Circuit('Buck Converter')

circuit.include(spice_library['1N5822']) # Schottky diode
circuit.include(spice_library['irf150'])