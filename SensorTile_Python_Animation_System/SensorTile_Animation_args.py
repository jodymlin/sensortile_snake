#!/usr/bin/python

import datetime as dt

import matplotlib; matplotlib.use("TkAgg")

import matplotlib.pyplot as plt

import matplotlib.animation as animation

import numpy as np

import SensorTile_Serial

import sys





#  Serial setup according to command line arguments

python_version = sys.version[0]

if len(sys.argv) != 2:

    print ("Wrong Number of Arguments!")

    print ("Please use format: python SensorTile_Animation_args.py SerialAddress")

else:

    address = sys.argv[1]

    if python_version == "2":

        python3 = False

    else:

        python3 = True



baud_rate = 9600

timeout = 2



# Create figure for plotting

fig = plt.figure()

ax1 = fig.add_subplot(211)

plt.title('SensorTile Project')

ax2 = fig.add_subplot(212)

ax1.set(ylabel='X Tilt ')

ax2.set(ylabel='Y Tilt ')



# plot parameters

x_len = 200

x_range = [-500, 500]

y_range = [-500, 500]

xs = list(range(0, 200))

tx = [0] * x_len

ty = [0] * x_len



ax1.set_ylim(x_range)

line1, = ax1.plot(xs, tx, animated=True)

ax2.set_ylim(y_range)

line2, = ax2.plot(xs, ty, animated=True)



# serial initialization

sensortile = SensorTile_Serial.serial_SensorTile(address, baud_rate, timeout, python3)

sensortile.init_connection()



# This function is called periodically from FuncAnimation

# def animate(i, xs, ys):

def animate(i, tx, ty):



    # get displacement, acceleration

    tilt_x_list, tilt_y_list = sensortile.collect_data()



    # Add dis and accel to lists

    tx.extend(tilt_x_list)

    ty.extend(tilt_y_list)



    # Limit x and y lists to 200 samples - 2s 

    tx = tx[-x_len:]

    ty = ty[-x_len:]



    # Draw dis and accel lists

    line1.set_ydata(tx)

    line2.set_ydata(ty)



    return line1, line2,





# Set up plot to call animate() function periodically

# interval = 10ms

ani = animation.FuncAnimation(fig, animate, fargs=(tx, ty,), interval=3, blit=True)

plt.show()



# shutdown the system after closing the plot

sensortile.close_connection()