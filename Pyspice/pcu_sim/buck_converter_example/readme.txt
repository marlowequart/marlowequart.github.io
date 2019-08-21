Readme:

buck_basic.py:
A basic buck converter example found on the web at:
https://pyspice.fabrice-salvaire.fr/examples/switched-power-supplies/buck-converter.html

buck_w_netlist.py:
This takes the basic buck converter and puts the circuit components in a netlist (found in libararies file) called buck_netlist_simple.lib.  The point of this example is to show how to call a spice netlist from a .lib file. Included in the .lib file are some pointers for converting from LTSpice netlist to a netlist compatible with PySpice.

buck_nofdbk_mcu_cntrl.py:
This example is meant to show how a basic buck converter can be operated open loop using the interface between the PySpice schematic and a microcontroller block coded in python. This example is built on in the next example.

buck_zdomain.py:
This example is designed to show a closed loop controlled buck converter using zdomain controls in the python code block.



the libraries folder contains both the buck converter netlist for the example above as well as the necessary models for running the other examples.