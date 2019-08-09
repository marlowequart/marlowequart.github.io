import control
import matplotlib.pyplot as plt

# import control.TransferFunction as tf


##------------------------------------
## pole zero map of analog ea
##------------------------------------
#Type-3 E.A. inputs
R1=200000.
R2=100000.
R3=5000.
C1=4.7*10**-9
C2=100.*10**-12
C3=1.*10**-9

num_s2_coeff=R2*C1*(R1+R3)*C3
num_s1_coeff=R2*C1+(R1+R3)*C3
num_s0_coeff=1
den_s4_coeff=(R1*(C1+C2)*R3*C3)*(R1*R2*C1*C2)
den_s3_coeff=R1*(C1+C2)*((R1*(C1+C2)*R3*C3)+(R1*R2*C1*C2))
den_s2_coeff=R1*R1*(C1+C2)*(C1+C2)
den_s1_coeff=0
den_s0_coeff=0

num=[num_s2_coeff,num_s1_coeff,num_s0_coeff]
den=[den_s4_coeff,den_s3_coeff,den_s2_coeff,den_s1_coeff,den_s0_coeff]


tfx = control.tf(num,den)

w,mag,phase=tfx.bode()

# print(tfx.pole())
# control.matlab.pzmap(tfx)
# plt.show()

#print bode plot
# want to plot from 10Hz to 1MHz
nsamps=100000
df=10.
#create freq
n_range=arange(1,nsamps+1)
freq=[]
for i in range(1,nsamps+1):
    freq.append(n_range[i-1]*df)
