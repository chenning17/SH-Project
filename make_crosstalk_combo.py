# BEFORE USE: change line 291 to where file to append data to is located
### use this as command for program: "python make_crosstalk.py 2600_00_LED_ON_C1 2600_00_LED_OFF_C1 2600_00_LED_ON_C2 2600_00_LED_OFF_C2"
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
import sys
import scipy.fftpack
from matplotlib import rcParams, style
import os.path
style.use('seaborn-muted')
rcParams.update({'font.size': 12})
rcParams['figure.figsize'] = 12, 12
rcParams['xtick.labelsize'] = 16
rcParams['ytick.labelsize'] = 16


# Take filename from terminal input.
data_name     = sys.argv[1]  #ch1 LED ON input file
data_ped_name = sys.argv[2]  #ch1 LED OFF input file  , ch1 / first two inputs must be illuminated channel
data_name2     = sys.argv[3] #ch2 LED ON input file
data_ped_name2 = sys.argv[4] #ch2 LED OFF input file  , ch2 / last two inputs must be masked channel

# Match with pickle_data        #TODO: make this automatic
n_samples = 402
frameSize = 10.05e-8  # Not actually used in the analysis currently, but can be useful to know

data           = pd.read_pickle(data_name + '.pkl')
data_ped       = pd.read_pickle(data_ped_name + '.pkl')
data2           = pd.read_pickle(data_name2 + '.pkl')            #values with '2' after are ch2 values
data_ped2       = pd.read_pickle(data_ped_name2 + '.pkl')

charge_subset = []
resistance = 50
dt = (data['time'][1] - data['time'][0])/1e9 # to get back to seconds
# V = IR => I = V/R; Q = int_t0^t1 I dt = int_t0^t1 V/R dt => Q = sum(V/R *Delta t)

dt2 = (data2['time'][1] - data2['time'][0])/1e9 # to get back to seconds
# V = IR => I = V/R; Q = int_t0^t1 I dt = int_t0^t1 V/R dt => Q = sum(V/R *Delta t)

n_events = len(data)/n_samples
n_events2 = len(data2)/n_samples

print data_name, data_ped_name
print "time interval:", dt
print "number of events:", n_events

print data_name2, data_ped_name2
print "time interval:", dt2
print "number of events:", n_events2

# This part would only be used if we wanted to define some range of integration (by default we just take everything)
low_offset = 0
high_offset = 0
# Let's make some assumptions about the rise-time
rise_time = 1e-9 #seconds
rise_time_in_samples = int(rise_time/dt)
fall_time = 4e-9 #seconds
fall_time_in_samples = int(fall_time/dt)

# Define range of integration
filterTimeRange = True
lower_time = 60.
upper_time = 80.

if filterTimeRange:
    data = data[(np.abs(data.filtered_voltage)<100) & (data.time > lower_time) & (data.time < upper_time)]
    data_ped = data_ped[(np.abs(data_ped.filtered_voltage)<100) & (data_ped.time > lower_time) & (data_ped.time < upper_time)]
    data2 = data2[(np.abs(data2.filtered_voltage)<100) & (data2.time > lower_time) & (data2.time < upper_time)]
    data_ped2 = data_ped2[(np.abs(data_ped2.filtered_voltage)<100) & (data_ped2.time > lower_time) & (data_ped2.time < upper_time)]
else:
    data = data[(np.abs(data.filtered_voltage)<100)]
    data_ped = data_ped[(np.abs(data_ped.filtered_voltage)<100)]
    data2 = data2[(np.abs(data2.filtered_voltage)<100)]
    data_ped2 = data_ped2[(np.abs(data_ped2.filtered_voltage)<100)]

# Shift baseline to zero
mean_ped_voltage = data_ped.filtered_voltage.mean()
print "Offset all voltages by the average baseline voltage of the pedestal:", mean_ped_voltage
data_ped.voltage          = data_ped.voltage - mean_ped_voltage
data_ped.filtered_voltage = data_ped.filtered_voltage - mean_ped_voltage
data.voltage              = data    .voltage - mean_ped_voltage
data.filtered_voltage     = data    .filtered_voltage - mean_ped_voltage

# Shift baseline to zero
mean_ped_voltage2 = data_ped2.filtered_voltage.mean()
print "Offset all voltages by the average baseline voltage of the pedestal:", mean_ped_voltage2
data_ped2.voltage          = data_ped2.voltage - mean_ped_voltage2
data_ped2.filtered_voltage = data_ped2.filtered_voltage - mean_ped_voltage2
data2.voltage              = data2    .voltage - mean_ped_voltage2
data2.filtered_voltage     = data2    .filtered_voltage - mean_ped_voltage2


# Apply Time Over Threshold Filter
############number to change to get rid of low counts#
voltage_threshold = -5.                            # units of this are volts or time not sure
###################################################### 
     
min_TOT = data[(data.filtered_voltage < voltage_threshold)].groupby(['eventID']).time.min()
max_TOT = data[(data.filtered_voltage < voltage_threshold)].groupby(['eventID']).time.max()
diff = (max_TOT - min_TOT) > 0.7 # 700ps
diff = diff[diff] # only select the events where the above condition is true

min_TOT2 = data2[(data2.filtered_voltage < voltage_threshold)].groupby(['eventID']).time.min()
max_TOT2 = data2[(data2.filtered_voltage < voltage_threshold)].groupby(['eventID']).time.max()
diff2 = (max_TOT2 - min_TOT2) > 0.7 # 700ps
diff2 = diff2[diff2] # only select the events where the above condition is true

print "Number of good pulses below threshold (-2 mV) is: diff, data : ", len(diff), len(data)
print "Number of good pulses below threshold (-2 mV) is: diff, data : ", len(diff2), len(data2)

# Group the data into events (i.e., separate triggers)
# Only keep events without spikes where there is some DAQ error due to large signals cut by the scope
spikes      = data     [(data     .voltage > 10)].groupby(['eventID']).eventID.min()
spikes_ped  = data_ped [(data_ped .voltage > 10)].groupby(['eventID']).eventID.min()

# Group the data into events (i.e., separate triggers)
# Only keep events without spikes where there is some DAQ error due to large signals cut by the scope
spikes2      = data2     [(data2     .voltage > 10)].groupby(['eventID']).eventID.min()
spikes_ped2  = data_ped2 [(data_ped2 .voltage > 10)].groupby(['eventID']).eventID.min()

#data to remove vertically   -> change number to change cut off point, counts above -5v are currently rejected
temp_height_data   = data     [(data     .voltage < -5)].groupby(['eventID']).eventID.min()   
temp_height_data_ped  = data_ped [(data_ped .voltage < -5)].groupby(['eventID']).eventID.min()

#data to remove vertically   -> change number to change cut off point, counts above -5v are currently rejected
temp_height_data2   = data2     [(data2     .voltage < -5)].groupby(['eventID']).eventID.min()   
temp_height_data_ped2  = data_ped2 [(data_ped2 .voltage < -5)].groupby(['eventID']).eventID.min()

#~ means not so make this data everything expect the data identified to not be used
data_spikes_removed_andHeight      = data     [~data     .eventID.isin(spikes.index) &        data     .eventID.isin(temp_height_data.index)]            
data_ped_spikes_removed_andHeight  = data_ped [~data_ped .eventID.isin(spikes_ped.index)&     data     .eventID.isin(temp_height_data_ped.index)]

print len(data_spikes_removed_andHeight.groupby(['eventID']))

#~ means not so make this data everything expect the data identified to not be used
data_spikes_removed_andHeight2      = data2     [~data2     .eventID.isin(spikes2.index) &        data2     .eventID.isin(temp_height_data2.index)]            
data_ped_spikes_removed_andHeight2  = data_ped2 [~data_ped2 .eventID.isin(spikes_ped2.index)&     data2     .eventID.isin(temp_height_data_ped2.index)]

print len(data_spikes_removed_andHeight2.groupby(['eventID']))


grouped_data      = data_spikes_removed_andHeight     .groupby(['eventID'])
grouped_data_ped  = data_ped_spikes_removed_andHeight .groupby(['eventID'])
grouped_data2      = data_spikes_removed_andHeight2     .groupby(['eventID'])
grouped_data_ped2  = data_ped_spikes_removed_andHeight2 .groupby(['eventID'])

print "Number of events after removing large voltage spikes", len(grouped_data)
print "Number of events after removing large voltage spikes", len(grouped_data2)


#height_data      = temp_height_data.groupby(['eventID'])
#height_data_ped  = temp_height_data_ped.groupby(['eventID'])


# Plot the time position and voltage of the max voltage in each event
fig, axes = plt.subplots(nrows=1, ncols=2, figsize=(12, 6), sharey = True)                          #
max_voltages     = data    .loc[grouped_data    .filtered_voltage.idxmin()]                         #
max_voltages_ped = data_ped.loc[grouped_data_ped.filtered_voltage.idxmin()]                         #
max_voltages    .plot(kind='scatter',x='time',y='filtered_voltage', title = '',  ax = axes[0])      #
max_voltages_ped.plot(kind='scatter',x='time',y='filtered_voltage', title = '', ax = axes[1])       #
axes[0].set_xlabel("time [ns]", fontsize = 20)                                                      #
axes[1].set_xlabel("time [ns]", fontsize = 20)                                                      #
axes[0].set_ylabel("filtered voltage [mV]", fontsize = 20)                                          #
axes[0].set_ylabel("")                                                                              #
fig.savefig('plots/' + sys.argv[1] + '_' + sys.argv[2] + '_max_voltage_vs_time-5.png')                #
print "number of max voltages", len(max_voltages)  

# Plot the time position and voltage of the max voltage in each event
fig2, axes2 = plt.subplots(nrows=1, ncols=2, figsize=(12, 6), sharey = True)                          #
max_voltages2     = data2    .loc[grouped_data2    .filtered_voltage.idxmin()]                         #
max_voltages_ped2 = data_ped2.loc[grouped_data_ped2.filtered_voltage.idxmin()]                         #
max_voltages2    .plot(kind='scatter',x='time',y='filtered_voltage', title = '',  ax = axes2[0])      #
max_voltages_ped2.plot(kind='scatter',x='time',y='filtered_voltage', title = '', ax = axes2[1])       #
axes2[0].set_xlabel("time [ns]", fontsize = 20)                                                      #
axes2[1].set_xlabel("time [ns]", fontsize = 20)                                                      #
axes2[0].set_ylabel("filtered voltage [mV]", fontsize = 20)                                          #
axes2[0].set_ylabel("")                                                                              #
fig2.savefig('plots/' + sys.argv[3] + '_' + sys.argv[4] + '_max_voltage_vs_time-5.png')                #
print "number of max voltages", len(max_voltages2)  


lit_volt =[]
mask_volt = []


cross_ch1 = data.loc[grouped_data.filtered_voltage.idxmin()]
cross_ch2 = data2.loc[grouped_data2.filtered_voltage.idxmin()]

for i in range(len(cross_ch2)):
    
    for j in range(len(cross_ch1)):
        if(int(cross_ch1.iloc[j]['eventID']) == int(cross_ch2.iloc[i]['eventID'])):
            #temp1.append(cross_ch1.get_value(i, 'filtered_voltage'))
            #temp2.append(cross_ch2.get_value(i, 'filtered_voltage'))
            
            print "wayhay " , i
            lit_volt.append(cross_ch1.iloc[j]['filtered_voltage'])
            mask_volt.append(cross_ch2.iloc[i]['filtered_voltage'])
            
            print "cross_ch1 = " , cross_ch1.iloc[j]['eventID'],cross_ch1.iloc[j]['filtered_voltage'], j
            print "cross_ch2 = " , cross_ch2.iloc[i]['eventID'],cross_ch2.iloc[i]['filtered_voltage'], i
            
#calculates the pearson correlation: http://stackoverflow.com/questions/3949226/calculating-pearson-correlation-and-significance-in-python
#https://en.wikipedia.org/wiki/Pearson_product-moment_correlation_coefficient
corr = np.corrcoef(lit_volt, mask_volt)[0, 1]
print "correlation coefficient is: ", corr
            
#plot crosstalk voltage data of ch1 (illuminated) against ch2 (masked)
plt.figure(3)
plt.scatter(lit_volt, mask_volt)
#plt.plot(lit_volt, mask_volt)
plt.xlabel('x values, illuminated channel')
plt.ylabel('y values, masked channel')
plt.title('masked channel voltage vs illuminated channel voltage')
plt.xlim([-60,0])
plt.ylim([-60,0])
plt.grid(True)
plt.text(-30, -50, "correlation coefficient is: "+ str(corr))
plt.savefig('plots/' + 'crosstalk_' + data_name + '_' + data_name2 + '.png')
#plt.show()


#variable to calculate percent of crosstalk
percent_cross = []
for k in range(len(mask_volt)):
    percent_cross.append((mask_volt[k]/lit_volt[k])*100)
#plot crosstalk percentage values of data against ch1 (illuminated) max voltage values
plt.figure(4)
plt.scatter(lit_volt, percent_cross)
#plt.plot(lit_volt, mask_volt)
plt.xlabel('x values, illuminated channel')
plt.ylabel('y values, percentage of crosstalk measured')
plt.title('percentage crosstalk vs illuminated channel voltage')
plt.xlim([-60,0])
plt.ylim([0,100])
plt.grid(True)
plt.text(-30, 10, "correlation coefficient is: "+ str(corr))
plt.savefig('plots/' + 'percent_crosstalk_' + data_name + '_' + data_name2 + '.png')
#plt.show()

#variable to calculate sum of both channel readings
tot_volt = []
for k in range(len(mask_volt)):
    tot_volt.append(mask_volt[k]+lit_volt[k])        

#plot crosstalk percentage values of data against ch1 (illuminated) max voltage values
plt.figure(5)
plt.scatter(lit_volt, tot_volt)
#plt.plot(lit_volt, mask_volt)
plt.xlabel('voltage of channel 1 [v]')
plt.ylabel('total voltage of two channels combined [v]')
plt.title('combined channel voltage vs channel 1 voltage')
plt.xlim([-70,0])
plt.ylim([-100,0])
plt.grid(True)
#plt.text(-30, 10, "correlation coefficient is: "+ str(corr))
plt.savefig('plots/' + 'combined_volt_ch1' + data_name + '_' + data_name2 + '.png')     
    

#plot crosstalk percentage values of data against ch1 (illuminated) max voltage values
plt.figure(6)
plt.scatter(mask_volt, tot_volt)
#plt.plot(lit_volt, mask_volt)
plt.xlabel('voltage of channel 2 [v]')
plt.ylabel('total voltage of two channels combined [v]')
plt.title('combined channel voltage vs channel 2 voltage')
plt.xlim([-70,0])
plt.ylim([-100,0])
plt.grid(True)
#plt.text(-30, 10, "correlation coefficient is: "+ str(corr))
plt.savefig('plots/' + 'combined_volt_ch2' + data_name + '_' + data_name2 + '.png')     


#plot crosstalk percentage values of data against ch1 (illuminated) max voltage values
plt.figure(7)
plt.hist(tot_volt, bins = 100)
#plt.plot(lit_volt, mask_volt)
plt.xlabel('total voltage of two channels combined [v]')
plt.ylabel('number of counts of measurement')
plt.title('counts vs combined channel voltage')
#plt.xlim([-60,0])
#plt.ylim([0,100])
#plt.grid(True)
#plt.text(-30, 10, "correlation coefficient is: "+ str(corr))
plt.savefig('plots/' + 'combined_volt_hist' + data_name + '_' + data_name2 + '.png')        
#plt.show()



#must be updated to where the file you want to append data to is located
save_path = '--------where the file is saved ------'

name_of_file = 'combo_data'

completeName = os.path.join(save_path, name_of_file+".txt")         

file1 = open(completeName, "a")

for l in range(len(mask_volt)):
    file1.write(str(lit_volt[l]) +" "+ str(mask_volt[l]) + "\n")

file1.close()

