"""
Designed 4th order Elliptic filter

This script generates the zdomain coefficients for the buck controller

successfully implemented 2p2z typ3 III error amp analog controller with following parameters:
Origin pole
pole1: 15915 Hz
pole2: 31831 Hz
zero1: 338 Hz
zero2: 795 Hz

Digital Filter:
(See SLUA622 from TI)
Want to use IIR filter to have both poles and zeros
two zero, two pole filter: d[n]=b0*e[n]+b1*e[n-1]+b2*e[n-2]-a1*d[n-1]-a2*d[n-2]
where e is error amp input and d is error amp output


See PySmath.pice for implementation.
"""

from scipy import signal
import matplotlib.pyplot as plt
from numpy import *
import math


import control



##------------------------------------
## Error Amp
##------------------------------------
'''
#Type-3 E.A. iuts
R1=200000.
R2=100000.
R3=5000.
C1=4.7*10**-9
C2=100.*10**-12
C3=1.*10**-9

nsamps=100000
df=10.

n_range=arange(1,nsamps+1)
freq=[]
for i in range(1,nsamps+1):
    freq.append(n_range[i-1]*df)

Zi=[]
Zf=[]
tx=[]
ea_trans=[]
ea_phase=[]
op_amp=[]
op_amp_trans=[]

for i in range(0,nsamps):
	# Type III tx func
	Zi.append(((2.j*math.pi*freq[i])*R3*R1*C3+R1)/((2.j*math.pi*freq[i])*(C3*R3+C3*R1)+1))
	Zf.append(((2.j*math.pi*freq[i])*R2*C1+1)/((2.j*math.pi*freq[i])**2*R2*C1*C2+(2.j*math.pi*freq[i])*(C2+C1)))
	tx.append(Zf[i]/Zi[i])
	
	ea_trans.append(linalg.norm(tx[i]))
	ea_phase.append((angle(tx[i])*180/math.pi)+180)
	if (ea_phase[i]>180):
		ea_phase[i]=ea_phase[i]-360
		
##------------------------------------
## Plot Error Amp Response
##------------------------------------

fig=plt.figure(0)
ax1=fig.add_subplot(111)
line1=ax1.semilogx(freq, 20*log10(ea_trans),color='b',label='Error Amp tx func')
ax2=ax1.twinx()
line3=ax2.plot(freq,ea_phase,color='r',label='Phase Margin')
lines=line1+line3
labels=[y.get_label() for y in lines]
ax1.legend(lines,labels,loc=0)
ax1.minorticks_on
ax1.grid(True, which='both')
ax1.set_yticks(arange(-100,120,20))
ax2.set_yticks(arange(-200,240,40))
ax1.set_ylabel('Magnitude (dB)')
ax1.set_xlabel('Frequency')
ax1.set_title('Error Amp Response')
plt.show()

'''
##------------------------------------
## Digital Filter
##------------------------------------
# fsamp of 20MHz and 100k samps gives total dt of: 


fsamp=6000
Kdc=15
wr=3275
wp=12500
Q=1500

b = [0.07967, 0.1135, 0.0796]
a = [1, -0.8285, 0.3]

b0=Kdc*(wp/(2*fsamp+wp))*((2*fsamp/(wr*wr))+1/(wr*Q)+1/(2*fsamp))
b1=Kdc*(wp/(2*fsamp+wp))*((-4*fsamp/(wr*wr))+1/fsamp)
b2=Kdc*(wp/(2*fsamp+wp))*((2*fsamp/(wr*wr))-1/(wr*Q)+1/(2*fsamp))
a1=-4*fsamp/(2*fsamp+wp)
a2=-wp*((2*fsamp-wp)/(2*fsamp+wp))
print('b0='+str(b0))
print('b1='+str(b1))
print('b2='+str(b2))
print('a1='+str(a1))
print('a2='+str(a2))


# Coefficients generated from C2000 software 1/21/17
# b0=4.17
# b1=-5.91
# b2=1.94
# a0=1
# a1=0.8285
# a2=0.1714


# b=[b0,b1,b2]
# a=[1,a1,a2]

# w, h = signal.freqz(b,a)

# nsamps=100000
# df=10.
# Fs=2*df*nsamps
#create freq
# n_range=arange(1,nsamps+1)
# freq=[]
# h=[]
# for i in range(1,nsamps+1):
	# freq.append(n_range[i-1]*df)
	
	# f0=i*df
	# z=exp(2j*math.pi*f0/Fs)
	# num=b0+b1/z+b2/z**2
	# den=a0+a1/z+a2/z**2
	# h.append(abs(num/den))


##------------------------------------
## Plot Digital Filter Response
##------------------------------------

# plt.semilogx(freq, 20 * log10(h))
# plt.xlabel('Frequency [kHz]')
# plt.ylabel('Amplitude response [dB]')
# plt.grid()
# plt.show()









# online example

b = [0.0976, 0.1952, 0.0976]
a = [1, -0.9429, -0.3334]

# b0=0.007967
# b1=-0.01135
# b2=0.00796
# a0=1
# a1=-0.7804
# a2=2743.9
# my coeffs
# b = [0.07967, 0.1135, 0.0796]
# a = [1, -0.8285, 0.3]

Fs = 4000
N = 1000  # number of frequency points
df = (Fs/2) / N  # distance between two frequency points


H = zeros(N)
for n in range(N):
    f0 = n*df
    z = exp(2j*pi*f0/Fs)

    num = b[0] + b[1]/z + b[2]/z**2
    denom = a[0] + a[1]/z + a[2]/z**2
    H[n]=abs(num/denom)

# Now just do the plotting
f = arange(0,Fs/2,df)
plt.plot(f, 20*log10(H))
# plt.ylim((-30,5))
plt.grid(True)
plt.show()
