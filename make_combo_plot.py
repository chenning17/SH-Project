import matplotlib.pyplot as plt
import numpy as np

# Open the file and read in the data
filein = open("combo_data.txt","r")
lines = filein.readlines( )
filein.close()

# Read in two columns of data separately
lit_volt = []
mask_volt = []
for line in lines:
    line = line.strip()
    cols = line.split()
    lit_volt.append(float(cols[0]))
    mask_volt.append(float(cols[1]))
 
corr = np.corrcoef(lit_volt, mask_volt)[0, 1]
print "correlation coefficient is: ", corr
 
#plot crosstalk voltage data of ch1 (illuminated) against ch2 (masked)
plt.figure(1)
plt.scatter(lit_volt, mask_volt)
#plt.plot(lit_volt, mask_volt)
plt.xlabel('x values, illuminated channel')
plt.ylabel('y values, masked channel')
plt.title('masked channel voltage vs illuminated channel voltage')
plt.xlim([-60,0])
plt.ylim([-60,0])
plt.grid(True)
plt.text(-30, -50, "correlation coefficient is: "+ str(corr))
plt.savefig('join_combo_crosstalk.png')

#variable to calculate percent of crosstalk
percent_cross = []
for k in range(len(mask_volt)):
    percent_cross.append((mask_volt[k]/lit_volt[k])*100)
#plot crosstalk percentage values of data against ch1 (illuminated) max voltage values
plt.figure(2)
plt.scatter(lit_volt, percent_cross)
#plt.plot(lit_volt, mask_volt)
plt.xlabel('x values, illuminated channel')
plt.ylabel('y values, percentage of crosstalk measured')
plt.title('percentage crosstalk vs illuminated channel voltage')
plt.xlim([-60,0])
plt.ylim([0,100])
plt.grid(True)
plt.text(-30, 10, "correlation coefficient is: "+ str(corr))
plt.savefig('Join_combo_percent_crosstalk.png')

plt.show()