These programs are used to analyse crosstalk data from an MCP-PMT.

    'make_crosstalk.py' produces plots of voltage from the illuminated channel vs voltage from the masked channel.
    A plot of the crosstalk expressed as a percentage value of the voltage read on the illuminated channel is also made.

    'make_crosstalk_between.py' is used for measurements where the mask is placed inbetween two adjacent channels. It produces 
    the same outputs as 'make_crosstalk.py', however it also plots a histogram of the total voltage of the two channels combined.

    'make_charge_spec.py' is the same idea as 'make_crosstalk.py' however instead of plotting the voltages of each channel against one 
    another it converts these to the amount of charge collected.
    The outputted plot appears to be identical to that made using the voltages (but having undergone a reflection in both axes).

    'make_crosstalk_combo.py' is used to output and combine all of the crosstalk data into one file that can be plotted on the same graph.

    'make_combo_plot.py' is used in conjunction with the previous script to plot the graph of the collected crosstalk data contained in the file.

The correct format for the commands in order to run the scripts are as follows:

    python make_crosstalk.py 2600_00_LED_ON_C1 2600_00_LED_OFF_C1 2600_00_LED_ON_C2 2600_00_LED_OFF_C2
    python make_crosstalk_between.py 2600_00_LED_ON_C1 2600_00_LED_OFF_C1 2600_00_LED_ON_C2 2600_00_LED_OFF_C2
    python make_charge_spec.py 2600_00_LED_ON_C1 2600_00_LED_OFF_C1 2600_00_LED_ON_C2 2600_00_LED_OFF_C2
    python make_crosstalk_combo.py 2600_00_LED_ON_C1 2600_00_LED_OFF_C1 2600_00_LED_ON_C2 2600_00_LED_OFF_C2
    python make_combo_plot.py
    
These programs are modified versions of and should be used in conjunction with those of G. Cowan found online at: https://github.com/gcowan/hyperk/tree/1/lappd/spectra