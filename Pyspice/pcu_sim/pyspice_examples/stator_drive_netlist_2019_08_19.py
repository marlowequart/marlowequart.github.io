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
        if node == 'vgate_drivehs':
            voltage[0]=self.gate_drivehs
        elif node == 'vgate_drivels':
            voltage[0]=self.gate_drivels          
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
circuit = Circuit('Stator Drive')


circuit.include(spice_library['stator_drive_netlist'])
# Top level circuit annotated as "x1"
circuit.X(1,'stator_drive_netlist', 'vin_p', 'vin_m', 'sw_node', 'hs_drive', 'ls_drive', 'sin_ref', 'tri_ref', 'N023', 'N025') 


# analog stimulus that goes nowhere below; just used to probe Python "net" inside digital controller

# Real analog stimuli below:
# ~ circuit.V('gate_drivehs', 'gate_drivehs_net', circuit.gnd, 'dc 0 external')
# ~ circuit.V('gate_drivels', 'gate_drivels_net', circuit.gnd, 'dc 0 external')


# Create input voltage to send to netlist
Vinput=100@u_V
circuit.V('input_p', 'vin_p', circuit.gnd, Vinput)
circuit.V('input_m', circuit.gnd, 'vin_m', Vinput)

'''
# Supply input parameters
# ~ circuit.V('input_p', 'input_p_out', circuit.gnd, 100@u_V) # use just this line for more stable source
circuit.V('input_p', 'input_p_net', circuit.gnd, 100@u_V)
circuit.R('input_p', 'input_p_net', 'input_p_net_R', 5@u_mOhm)
circuit.L('input_p', 'input_p_net_R', 'input_p_out', 50@u_nH)


# ~ circuit.V('input_m', circuit.gnd, 'input_m_out', 100@u_V) # use just this line for more stable source
circuit.V('input_m', circuit.gnd, 'input_m_net', 100@u_V)
circuit.R('input_m', 'input_m_net', 'input_m_net_R', 5@u_mOhm)
circuit.L('input_m', 'input_m_net_R', 'input_m_out', 50@u_nH)

# Supply cables input parameters
circuit.R('in_cable_p', 'input_p_out', 'in_p_cable_L', 10@u_mOhm)
circuit.L('in_cable_p', 'in_p_cable_L', '_pALE_p', 10@u_nH)

circuit.R('in_cable_m', 'input_m_out', 'in_m_cable_L', 10@u_mOhm)
circuit.L('in_cable_m', 'in_m_cable_L', '_mALE_p', 10@u_nH)


#ALE caps
circuit.R('_pALE_fuse', '_pALE_p', '_pfuse_m', 5@u_mOhm)
circuit.L('_pALE_ESL', '_pfuse_m', '_pALE_ESR', 500@u_nH)
circuit.R('_pALE_ESR', '_pALE_ESR', '_pALE_CAP', 100@u_mOhm)
circuit.C('_pALE', '_pALE_CAP', circuit.gnd, 10000@u_uF)

circuit.R('_mALE_fuse', '_mALE_p', '_mfuse_m', 5@u_mOhm)
circuit.L('_mALE_ESL', '_mfuse_m', '_mALE_ESR', 500@u_nH)
circuit.R('_mALE_ESR', '_mALE_ESR', '_mALE_CAP', 100@u_mOhm)
circuit.C('_mALE', '_mALE_CAP', circuit.gnd, 10000@u_uF)

# fuses to Hbridge parameters
circuit.R('hfuse_p', '_pALE_p', '_pfuseESL', 5@u_mOhm)
circuit.L('hfuse_p', '_pfuseESL', '_pfilm_p', 50@u_nH)

circuit.R('hfuse_m', '_mALE_p', '_mfuseESL', 5@u_mOhm)
circuit.L('hfuse_m', '_mfuseESL', '_mfilm_p', 50@u_nH)


#Film caps
circuit.R('_pfilm_ESR', '_pfilm_p', '_pfilm_CAP', 1@u_mOhm)
circuit.C('_pfilm', '_pfilm_CAP', circuit.gnd, 100@u_uF)

circuit.R('_mfilm_ESR', '_mfilm_p', '_mfilm_CAP', 1@u_mOhm)
circuit.C('_mfilm', '_mfilm_CAP', circuit.gnd, 100@u_uF)


# Hbridge Switches
# nchannel mosfet from +VPWR to switchnode
circuit.X('Qhs', 'irf150', '_pfilm_p', 'nchan_sw_drive_hs', 'sw_node')
# A more simple MOSFET option (no model, discrete parts)
# ~ circuit.R('hs_esr', '_pfilm_p', 'hs_fet', 15@u_mOhm)
# ~ circuit.X('Dhs', '1N5822', 'sw_node', '_pfilm_p')
# ~ circuit.VoltageControlledSwitch(input_plus='nchan_sw_drive_hs',input_minus='sw_node',output_plus='hs_fet',output_minus='sw_node',name='switchhs',model=None)
# resistor to drive nch fet, drive comes from controller
circuit.R('hs_drive', 'nchan_sw_drive_hs', 'ls_res1', 1@u_Ohm)


# nchannel mosfet from switchnode to -VPWR
circuit.X('Qls', 'irf150', 'sw_node', 'nchan_sw_drive_ls', '_mfilm_p')
# A more simple MOSFET option (no model, discrete parts)
# ~ circuit.R('ls_esr', 'sw_node', 'ls_fet', 15@u_mOhm)
# ~ circuit.X('Dls', '1N5822', '_mfilm_p', 'sw_node')
# ~ circuit.VoltageControlledSwitch(input_plus='nchan_sw_drive_ls',input_minus='_mfilm_p',output_plus='ls_fet',output_minus='_mfilm_p',name='switchls',model=None)
# resistor to drive nch fet, drive comes from controller
circuit.R('ls_drive', 'nchan_sw_drive_ls', 'ls_res2', 1@u_Ohm)




# consider using voltage controlled switch model
# ~ circuit.BJT(1, 4, 2, 3, model='bjt') # Q is mapped to BJT !
# ~ circuit.model('bjt', 'npn', bf=80, cjc=pico(5), rb=100)



#dummy voltage source so simulation will run
# ~ circuit.PulseVoltageSource('clk_hs', 'gate_drive_hs_net', circuit.gnd, 0@u_V, 10@u_V, 75@u_us, 100@u_us)
# ~ circuit.PulseVoltageSource('clk_ls', 'gate_drive_ls_net', circuit.gnd, 0@u_V, 10@u_V, 25@u_us, 100@u_us,75@u_us)



# Load
circuit.R('load_esr', 'sw_node', 'load_l', 70@u_mOhm)
circuit.L('load', 'load_l', circuit.gnd, 70@u_uH)

'''


# Simple controller comparing reference to triangle
# circuit.PulseVoltageSource('name', n1, n2, v_low, v_high, t_high, t_period, t_delay,t_rise,t_fall)
circuit.PulseVoltageSource('triangle', 'tri_ref', circuit.gnd, 0@u_V, 10@u_V, 0.1@u_us, 50@u_us, 0@u_s, 25@u_us,25@u_us)
circuit.SinusoidalVoltageSource('reference', 'sin_ref', circuit.gnd, amplitude=4.9@u_V, offset=5@u_V, frequency=400@u_Hz)
# circuit.VoltageControlledSwitch(input_plus='sin_ref',input_minus='tri_ref',output_minus='ls_res1',output_plus='test_out1',name='switch1',model=None)

'''
#switch implementation comparators to drive mosfets
# high side comparator. Output to drive HS mosfet is referenced to SW Node
circuit.V('testing1', 'test_out1', 'sw_node', 10@u_V)
circuit.VoltageControlledSwitch(input_plus='sin_ref',input_minus='tri_ref',output_minus='ls_res1',output_plus='test_out1',name='switch11',model=None)
circuit.R('gate_res1', 'ls_res1', 'sw_node', 10@u_Ohm)

# low side comparator. Output to drive LS mosfet is referenced to -VPWR
circuit.V('testing2', 'test_out2', '_mfilm_p', 10@u_V)
circuit.VoltageControlledSwitch(input_plus='tri_ref',input_minus='sin_ref',output_minus='ls_res2',output_plus='test_out2',name='switch12',model=None)
circuit.R('gate_res2', 'ls_res2', '_mfilm_p', 10@u_Ohm)


#Switch implementation only using voltage controlled switch
# ~ circuit.VoltageControlledSwitch(input_plus='sin_ref',input_minus='tri_ref',output_minus='sw_node',output_plus='_pfilm_p',name='switch11',model='SW')
# ~ circuit.VoltageControlledSwitch(input_plus='tri_ref',input_minus='sin_ref',output_minus='_mfilm_p',output_plus='sw_node',name='switch12',model='SW')
# ~ circuit.model('SW','SW', Ron=.002@u_Ohm, Roff=1@u_MOhm, Vt=3.0@u_V)

# ~ circuit.BehavioralSource('gate_drive_hs_net1',circuit.gnd,'hs_gate1',voltage_expression='V(sin_ref) + V(tri_ref)')
# ~ circuit.BehavioralSource('gate_drive_hs_net1',circuit.gnd,'hs_gate1',voltage_expression='if(V(sin_ref) > V(tri_ref),10,0)')
# ~ circuit.BehavioralSource('ls_gate','gate_drive_ls_net',if(V(sin_ref)>V(tri_ref),0@u_V,10@u_V))





# resistor from p-channel gate to Vin to bring pchan gate back to Vin when off
# ~ circuit.R('pgate', 'input', 'p_gate_drive', 1@u_Ohm)
# nchannel mosfet to pull pchannel gate to ground to turn it on
# ~ circuit.X('Q3', 'irf150', 'p_gate_drive', 'nchan_sw_drive', circuit.gnd)
# resistor to drive nch fet, drive comes from controller
# ~ circuit.R('pgate_nch', 'nchan_sw_drive', 'gate_drive1_net', 1@u_Ohm)


'''



# Voltage Feedback for controller
# ~ circuit.R(2, 'out', 'v_sns', 10@u_kOhm)
# ~ circuit.R(3, 'v_sns', circuit.gnd, 10@u_kOhm)


# This clock is used for NGspice mixed signal simulation.
# The python code runs every clock edge, both positive and negative
# clock speed: 20MHz
# clock cycle length: 50ns
# ~ circuit.PulseVoltageSource('clk', 'clk', circuit.gnd, 0@u_V, 1@u_V, 0.05@u_us, 0.1@u_us)
# circuit.R(4, 'gate_drive1', circuit.gnd, 10@u_kOhm)



#####
# Simulation parameters
#####
# Python block input constants
# ~ amplitude = 10@u_V

# Call the MyNgSpiceShared
# ~ ngspice_shared = MyNgSpiceShared(amplitude=amplitude, send_data=True)

# ~ simulator = circuit.simulator(temperature=25, nominal_temperature=25,simulator='ngspice-shared',ngspice_shared=ngspice_shared)


# record 10ms of data from t=30ms to t=40ms
# ~ analysis = simulator.transient(step_time=.05E-6, end_time=40ms, )


# Run a simple simulation on the basic circuit
# triangle wave is 50us, 10 samples gives min time step 5us
print()
simulator = circuit.simulator(temperature=25, nominal_temperature=25)
# simulator.options(reltol=1000E-6, chgtol=1E-14, abstol=1E-12, gmin=1E-12, vntol=1E-6, rseries=0, trtol=7, rshunt=1E12, xmu=0.5, maxord=2, itl3=4, itl4=10, itl5=5000) #NgSpice defaults (similar to LTspice)
# simulator.options(reltol=1E-3, chgtol=1E-13, abstol=1E-11, gmin=1E-12, vntol=1E-5, rseries=10E-6, trtol=7, rshunt=1.0E12, xmu=0.5, maxord=6, itl3=8, itl4=20, itl5=0)
# simulator.options(reltol=1E-3, chgtol=1E-13, abstol=1E-11, gmin=1E-12, vntol=1E-5, rseries=10E-6, trtol=7, rshunt=1.0E12, xmu=0.5, maxord=6, itl4=20)
simulator.initial_condition(sw_node=0, tri_ref=0)
# ~ analysis = simulator.transient(step_time=5E-6, start_time=20E-3, end_time=30E-3,max_time=10000E-6, use_initial_condition=True)
analysis = simulator.transient(step_time=.005E-6, start_time=5E-3, end_time=7.5E-3, use_initial_condition=True)



# ~ simulator = circuit.simulator(temperature=25, nominal_temperature=25)
# ~ analysis = simulator.transient(step_time=period/300, end_time=period*150)

# ~ analysis = simulator.transient(step_time=.05E-6, end_time=40E-3, start_time=30E-3)

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
NUMBER_PLOTS = '2'

#plots of circuit components
figure = plt.figure(1, (10, 5))
plot1 = plt.subplot(int(NUMBER_PLOTS+'11'))

plot(analysis.N023)
# plot(analysis.N025)
# plot(analysis.N101)
plt.legend(('hs_drive [V]', 'ls_drive [V]','N101 [V]'), loc=(.8,.8))

plt.grid()
plt.xlabel('t [s]')
plt.ylabel('[V]')



plot2 = plt.subplot(int(NUMBER_PLOTS+'12'))

plot(analysis.sw_node)
# plot(analysis.tri_ref)
plt.legend(('Switch Node',''), loc=(.05,.1))

plt.grid()
plt.xlabel('t [s]')
plt.ylabel('[V]')


'''
plot3 = plt.subplot(int(NUMBER_PLOTS+'13'))

# ~ plot(analysis.input_p_net)
# ~ plot(analysis.input_m_net)
plot(analysis.sw_node)
plt.grid()
plt.xlabel('t [s]')
plt.ylabel('[V]')

plt.legend(('Switch Node',''), loc=(.05,.1))


plot4 = plt.subplot(int(NUMBER_PLOTS+'14'))
# Plot load current
plot((analysis.sw_node-analysis.load_l)/circuit['Rload_esr'].resistance)
plt.grid()
plt.xlabel('t [s]')
plt.ylabel('[A]')
plt.legend(('Load Current',''), loc=(.05,.1))
'''

plt.tight_layout()
plt.show()

