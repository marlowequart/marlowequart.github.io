"""
Designed 4th order Elliptic filter with pyFDAx tool.
Open file CurrentLimitFilter_pyfdax.npz with pyfdax from terminal.
This script takes those parameters and produces a series of second-order filters.

Need at least 15.7dB attenuation at 18.3kHz to bring 
resonance back down to unity gain, given g_ovr_I=470 
and UGBW of 1.5kHz.  Using a 4th order IIR elliptic filter, 
0.5dB passband ripple and Fc(-0.5dB)=
15kHz allows for increasing the gain and UGBW by a 
factor of 2*1.414=4.24 at 60 deg PM. Note that the 
low-side skirt of the 18.3kHz resonance must be checked 
for attenuation as  well as the peak. 
Fs=62.5kHz will alias 125kHz resonance of second LC 
to DC, but at 40dB down, so this should not be a problem.  
See PySpice for implementation.
"""

from scipy import signal
import matplotlib.pyplot as plt
import numpy as np
import math
fs = 1.0E6 / 16
fc = 15.0E3
sos = signal.iirfilter(N=4, Wn=fc/(fs/2), rp=0.5, rs=25, btype='low', analog= False, ftype='ellip', output='sos')
print('sos_digital = ', sos)
w, h = signal.sosfreqz(sos)
plt.semilogx(w/math.pi*fs/2.0/1000.0, 20 * np.log10(abs(h)))
plt.xlim(1,50)
plt.ylim(-80,1)
plt.xlabel('Frequency [kHz]')
plt.ylabel('Amplitude response [dB]')
plt.grid()

anafilt = signal.iirfilter(N=4, Wn=fc/(fs/2), rp=0.5, rs=25, btype='low', analog= True, ftype='ellip', output='sos')
print('sos_analog = ', sos)
w, h = signal.sosfreqz(sos)
plt.semilogx(w/math.pi*fs/2.0/1000.0, 20 * np.log10(abs(h)))

plt.show()

x = signal.unit_impulse(700)

y_sos = signal.sosfilt(sos, x)

plt.plot(y_sos, 'k', label='SOS')
plt.legend(loc='best')
plt.show()
