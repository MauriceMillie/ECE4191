Checklist:





\- ~~check nominal voltages in the schematic of all nodes just in case~~



\- **add voltage feedback to both the hil model and the code (make it so that voltage changes how discharging or charging is weighted)**



\- ~~FIX NOMINAL VOLTAGE DICT IN CONTROLLER CODE!!! (FORGOT TO MAKE IT SO THAT ONE OF THE NODES HAS NOMINAL VOLTAGE 277V OR SOMETHING, LOOK AT MODULE 1 FOR EXACT VALUE)~~



\- ~~Make sure the battery hardware limits are changed (by resolving that set of simultaneous equations and then changing the scalings accordingly) to be grid overvoltage is at nominal+3% and grid undervoltage is at nominal-3% (rather than +/- 5% which is what it is currently)~~



\- ADD IN THE THING THAT LOOKS AT THE VOLTAGES AFTER THE MPC OUTPUTS THEM AND THEN APPLIES THE GRID LIMIT THING ONTO PBAT SO THAT THE CONTROLLER STATE REFLECTS WHAT IS HAPPENING ON HARDWARE. (make it consider bat limits as +/-3% not +/-5%)



\- Create a no batt emu integrated version and a batt emu version



\- make it so that the controller records both the hil soc and the bat emu soc for comparison



\- ~~consider finding a way to make the hil plots able to display more than 600 sec? or see if the signal analyzer thing takes all the data including the stuff outside the 600 seconds?~~



\- ~~complete meetiing minutes for week 10~~



\- ~~ENSURE THAT QREF IS SET TO ZERO FOR ALL NODES~~



\- <b>~~make it so that the stuff is no longer aggregated for mpc then disagregated, make it so that mpc runs separately for every single node individually.~~</b> **(hopefully)**



\- <b>~~Finish forecasting (both ML training and implementation to the script. the script will then need to have weather data input)~~</b> **Half done kinda. might need to finish implementing it on Friday**



**- CLEAN UP ALL CODE AND MAKE SURE THAT IT LOOKS GOOD ENOUGH TO SUBMIT/SHOW OFF!!!**



**- GATHER LOTS OF DATA SHOWING THE PERFORMANCE OF ALL THE DIFFERENT PARTS OF THE SYSTEM STUFF LIKE:**

&#x09;**- SHOW THAT THE NODE 632 ACTIVE POWER = THE GRID ACTIVE POWER OF ALL OTHER NODES**

&#x09;**- SHOW THAT VOLTAGES DONT VIOLATE LIMITS**

&#x09;**- SHOW THAT THE FORECAST IS SOMEWHAT ACCURATE. WHETHER OR NOT IT SATISFIES OUR REQUIREMENTS DEPENDS A LITTLE ON HOW WE CAN BEND THE RULES. IF YOU LOOK AT THE 	  MODEL EVALUATION RESULTS OR THE TXT/MD FILE THAT HAS SOME PERFORMANCE RESULTS WHEN CREATED. YOU COULD POSSIBLY MAKE AN ARGUMENT THAT OUR MODEL WORKS GREAT 	  ON THE AVERAGE DATA BUT PERFORMS WORSE ON THIS EXACT TEST WEEK BECAUSE IT HAS A BIG OUTLIER IN IT**

&#x09;**- truthfully im not super sure wat to do about the pv model. it doesn't rlly satisfy the requirements we set of it in the proposal doc i dont thinkkkk. we set 	  some pretty tough to hit limits in there. I assume that when averaged over a long time, the pv model is pretty accurate but the data i am giving it is not 	  really enough for it to predict stuff like cloud cover.**



**- FINISH THE PRESENTATION!!!!!!!**





Note1: for the voltage feedback, it will be used both somewhere in the mpc for attempts at optimization (either as a constraint of some sort or as a value that modifies the objective function weightings), as well as after the mpc to enforce the hard limits that are set by the battery hardware).



Note2: you might need to change the number of regs that are created in the schematic initialisation script or something. You will need to figure out how many voltages you have to measure and then you will need to increase it by that many (make sure u increase the right ones, the ones where soc is defined regs 3000 and 3001)





NOMINAL VOLTAGES AND THEIR BOUNDS:

MOST NODES: LOWER=, NOMINAL=, UPPER=

NODE 634: LOWER=, NOMINAL=, UPPER=



