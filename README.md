Analysis of data collected by SR2017 team HRS relating to a potential power board overcurrent problem.

Log 1
=====

Turn function drives motors with `power` of 20 for 11.888ms/° when θ < 25°, and `power` of 40 for 5.944ms/° otherwise.

Turn on line 20 of 19.2°. Run for 228ms. There are 176 lines of IV samples, giving a sample rate of 772Hz.

Turn on line 205 of 19.2°. Run for 228ms. There are 180 lines of IV samples, giving a sample rate of 789Hz.

Turn on line 391 of 19.2°. Run for 228ms. 182 lines. 798Hz.

Turn on line 579 of 19.2°. Run for 228ms. 184 lines. 807Hz.

Turn on line 769 of 19.2°. Run for 228ms. 181 lines. 794Hz.

Turn on line 956 of 19.2°. Run for 228ms. 181 lines. 794Hz.

Turn on line 1143 of 19.2°. Run for 228ms. 181 lines. 794Hz.

Turn on line 1329 of 19.2°. Run for 228ms. 182 lines. 798Hz.

Turn on line 1517 of 19.2°. Run for 228ms. 180 lines. 789Hz.

Turn on line 1703 of 3.95°. Run for 47.0ms. 38 lines. 809Hz.

Turn on line 1751 of 86.6°. Run for 515ms. 408 lines. 792Hz.

At line 2162 the robot moves forwards. First with `power` of 42 for 20ms (16 lines, 800Hz), then with `power` of 60 for 117ms. The power board trips after 98 lines of IV samples. Assuming a sample rate of ~800Hz it would appear that 123ms elapsed. However, there are IV samples printed during the 117ms of `power` = 60 and for 40ms after the `power` has been set to 0. Based upon the number of IV samples printed, the robot was 6ms into the 40ms end period. Approximately the last 5 lines were during the end period. Out of the last 5 samples printed, the fifth to last was probably the last in the while loop, the 4th to last was probably the single sample that is taken outside of the loop prior to setting the `power` to 0 and the remaining three were probably taken in the end period loop.

The last two samples before the power board tripped are very interesting. The penultimate one shows 0.0A, which is very unusual considering that the kit as a whole draws some current, so one would never expect it to read 0. The final one shows 1309.9A, which is clearly false. I suspect that when the motor power is set from 60 to 0 the stored energy (in the rotating mass) results in the net current from the battery becoming negative - the motor board is temporarily charing the battery. I don't know how the power board firmware will handle this negative current measurement.

Looking at the power board firmware it's covered in unsigned integers, so I highly doubt it handles negative currents. The power board uses an INA219. It returns the voltage across the shunt resistor as a two's compliment signed integer with the LSB = 10µV. The shunt resistor is 500µΩ, so drops 500µV/A. This means that 1 LSB of the INA219 register value represents 20mA. The firmware multiplies the register value by 20 to give a current in mA. If the register value were to become negative then, by interpreting it as an unsigned integer, it would appear that the current is (65535 * 20) = 1310.7A (for the smallest measured negative value). This is suspiciously similar to the 1309.9A value logged. Working back, this would correspond with a register value of 65495. As a two's compliment 16 bit integer this is actually -41. From the scaling factor of 20, this represents a current of -820mA.

Even though it's possible to detect and work around this problem in the sr-robot python library, the power board uses the measured battery current to determine if there is too much current being drawn. It has an IRR filter which, rather fortunately, results in there being a small delay between the negative current condition and it deciding to bomb out. This small delay is what has allowed the python to query the current and print it to the log. Had this not been present, tracking the problem down from a log file would have been pretty much impossible.
