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

##########
# Python code block
##########
class MyNgSpiceShared(NgSpiceShared):

    ##############################################

    def __init__(self, g_ovr_i, g_angle, gear_rat, deg_range, i_lim, pz_cap, pz_rbig, pz_rsmall, vdd_hall, **kwargs):
        super().__init__(**kwargs)
        # Section below needed only to prevent harmless "AttributeError: 'MyNgSpiceShared' object has no attribute 'clk_out'"
        #messages at beginning of run
        self.clk_out = 0
    
	#########
	# the def get_vsrc_data function provides digital signals from the python block to the ngspice block
	#########
    def get_vsrc_data(self, voltage, time, node, ngspice_id):
        self._logger.debug('ngspice_id-{} get_vsrc_data @{} node {}'.format(ngspice_id, time, node))
        
		#####
		# Debugging aid shows timestep deltas (not just time stamps) when non-zero, and in RED when negative
		#####
        timestep = time - self.ana_time_old
        if timestep > 0:
            print('Timestep = ', time - self.ana_time_old)
        if timestep < 0:
            print('\033[1;31mTimestep = ', time - self.ana_time_old, '\033[1;31m  ************************************************************************************************************************') 
        self.ana_time_old = time # END debugging aid
        
		
		# This "if" statement evaluated once for each node for each NgSpice timestep; for speed,
		# the calculations following this conditional are only executed once per dig_timestep.
        if (round(self.clk_out) != round(self.clk_out_old)) and (time != self.time_filt):
            self.time_filt = time #Need time stamp to avoid executing this code redundantly
            self.clk_out_old = self.clk_out #Need state of clk to know when it next changes
		    
            duty_raw = g_angle*(pot_bip-trgt_bip) #Raw duty cycle is simply gain times actual minus target angle.
            duty = min(abs(duty_raw),1) #Clip raw duty to get duty

            ################################################################
            """ 
            Elliptic filter below for current limit loop to supress the 18.3kHz (min) resonance of the first LC in the output filter.
            See Elliptic_62k5Hz_4th_500mdB_15kHz.py for details.  Topology is Direct Form 1.
            """
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
            ########################### END of elliptic filter##############
			
            duty = min(self.outz1, duty)   # cannot use out_filt here (it's not remembered)
            if self.i_pol == -1:
                d_scaled = self.outz1 # no feed forward needed for reverse current regulation; better to use full bus voltage (not 22V max). Also need to override positional loop (use self.outz1 instead of duty here); active high instead of just open-drain output for outz1 when regulating reverse current.
            else:
                d_scaled = min(max(0, duty*22/self.p_28v_out), 1) # feed-forward of Vbus
				
				
			################### Outputs below go from Python to NGspice####################################################            
			if node == 'va':
				voltage[0]=self.va_val
			elif node == 'vb':
				voltage[0]=self.vb_val          
			elif node == 'vc':
				voltage[0]=self.vc_val
			# Dummy outputs below are just for probing.  They are no-connects in NGspice    
			elif node == 'vi_limit': # this can be used to probe various "nets" inside the Python (not NGspice)
				voltage[0]=self.outz1 #output of elliptic filter
			elif node == 'vdrv_dir': # this can be used to probe various "nets" inside the Python (not NGspice)
				voltage[0]=self.drv_dir 
			elif node == 'vi_pol': # this can be used to probe various "nets" inside the Python (not NGspice)
				voltage[0]=self.i_pol_smooth 
			elif node == 'vi_cmpst': # this can be used to probe various "nets" inside the Python (not NGspice)
				voltage[0]=self.i_cmpst             
							
			return 0
			
			
		############################################## 
		# NGspice data sent to Python

		def send_data(self, actual_vector_values, number_of_vectors, ngspice_id):
            self.v_sns = actual_vector_values['v_sns'].real
			self.clk_out = actual_vector_values['clk'].real
			#~ self.idt_in_1 = actual_vector_values['x1.xx1.xx5.xx2.xx7.idt_in'].real  # example of probing a net in the hierarchy
			return 0



##########
# NGspice block
##########
circuit = Circuit('Buck Converter')

circuit.include(spice_library['1N5822']) # Schottky diode
circuit.include(spice_library['irf150'])


# Define the switch model for use in step load section
sw_model='''
.model SW SW(Ron=0.002 Roff=1Meg Vt=3.0)
'''
ngspice.load_circuit(sw_model)


# Other NGspice circuit parameters for buck stage
Vin = 28@u_V
Vout = 5@u_V
ratio = Vout / Vin

Rload = 3@u_Ohm

frequency = 400@u_kHz
period = 2.5@u_us
duty_cycle = ratio * period

# Actual buck fsw=150kHz, 6.66us




L = 150@u_uH
RL = 100@u_mOhm

Cout = 22@u_uF
ESR = 20@u_mOhm
ESL = 0

ESR_in = 120@u_mOhm
Cin = 10@u_uF

# 8/6/19 what is the purpose of .canonise()?
# L = L.canonise()
# Cout = Cout.canonise()
# Cin = Cin.canonise()


# parameters on input to buck
circuit.V('in', 'in', circuit.gnd, Vin)
circuit.C('in', 'in', circuit.gnd, Cin)

# Fixme: out drop from 12V to 4V
# circuit.VCS('switch', 'gate', circuit.gnd, 'in', 'source', model='Switch', initial_state='off')
# circuit.PulseVoltageSource('pulse', 'gate', circuit.gnd, 0@u_V, Vin, duty_cycle, period)
# circuit.model('Switch', 'SW', ron=1@u_mÎ©, roff=10@u_MÎ©)

# Fixme: Vgate => Vout ???
circuit.X('Q', 'irf150', 'in', 'gate', 'source')
# circuit.PulseVoltageSource('pulse', 'gate', 'source', 0@u_V, Vin, duty_cycle, period)
circuit.R('gate', 'gate', 'clock', 1@u_Ohm)
circuit.PulseVoltageSource('pulse', 'clock', circuit.gnd, 0@u_V, 2.*Vin, duty_cycle, period)


circuit.X('D', '1N5822', circuit.gnd, 'source')
circuit.L(1, 'source', 1, L)
circuit.R('L', 1, 'out', RL)
circuit.C(1, 'out', circuit.gnd, Cout) # , initial_condition=0@u_V
circuit.R('load', 'out', circuit.gnd, Rload)


# Voltage Feedback for controller
circuit.R(2, 'out', 'v_sns', 10@u_kOhm)
circuit.R(3, 'v_sns', circuit.gnd, 10@u_kOhm)

# This clock is used for NGspice mixed signal simulation.
circuit.PulseVoltageSource('ng_clk', 'clk', circuit.gnd, 0@u_V, 1@u_V, 10@u_us, 20@u_us)



#####
# Add a step load
#####
# circuit.PulseVoltageSource('name', n1, n2, v_low, v_high, t_high, t_period, t_delay,t_rise,t_fall)
circuit.PulseVoltageSource('load_sw', 'sw_drive', circuit.gnd, 0@u_V, 10@u_V, 1@u_s,1@u_s,300@u_us,10@u_ns)
circuit.R(1,'r_top', circuit.gnd,Rload)
# circuit.S(n1,n2,cntrl_sw+,cntrl_sw-,sw_model)
circuit.S('out','r_top','sw_drive',circuit.gnd,sw_model)



#####
# Simulation parameters
#####

simulator = circuit.simulator(temperature=25, nominal_temperature=25)

# step time is 0.1us, 100 datapoints per clock switch period, and 25 datapoints per buck switch period
# Total of 150 clock cycles measured and 1200 buck switch cycles
analysis = simulator.transient(step_time=.1E-6, end_time=150*20E-6)


#####
# Plotting
#####
'''
#plots of circuit components
figure = plt.figure(1, (10, 5))
axe = plt.subplot(111)

plot(analysis.out, axis=axe)
plot(analysis['source'], axis=axe)
plot(analysis.sw_drive, axis=axe)
# plot(analysis['source'] - analysis['out'], axis=axe)
# plot(analysis['gate'], axis=axe)
plt.axhline(y=float(Vout), color='red')
plt.legend(('Vout [V]', 'Vsource [V]'), loc=(.8,.8))
plt.grid()
plt.xlabel('t [s]')
plt.ylabel('[V]')

plt.tight_layout()
plt.show()
'''
# plots of mcu internal signals

figure = plt.figure(2, (10, 5))
axe = plt.subplot(111)

plot(analysis.clk, axis=axe)
# plot(analysis.r_top, axis=axe)
# plot(analysis['source'], axis=axe)

plt.grid()
plt.xlabel('t [s]')
plt.ylabel('[V]')

plt.tight_layout()
plt.show()
