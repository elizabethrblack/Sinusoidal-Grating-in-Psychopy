from psychopy import visual, core, event, gui, data, logging
from psychopy.hardware import brainproducts
import numpy as np
import serial.tools.list_ports
import random, os, sys, serial, time, threading
ports = serial.tools.list_ports.comports()
from psychopy.misc import fromFile
import os

for port, desc, hwid in sorted(ports):
    print("{}: {} [{}]".format(port, desc, hwid))
port=serial.Serial('COM7', 2000000)
time.sleep(5)

Connected = True


PulseWidth = 0.01

def ReadThread(port):
    """Thread function to read data from the serial port."""
    global Connected
    while Connected:
        if port.inWaiting() > 0:
            try:
                data = ord(port.read(1))
                print(f"0x{data:X}")
            except Exception as e:
                print(f"Error reading from port: {e}")



thread = threading.Thread(target=ReadThread, args=(port,))
thread.daemon = True
thread.start()

# Set the port to an initial state
port.write([0x00])

info = {'Subject Number': '', 'Handedness': ['Left', 'Right', 'Ambidextrous']}
dlg = gui.DlgFromDict(info, title="Participant Information")
if dlg.OK:
    subject_number = info['Subject Number']
    handedness = info['Handedness']
else:
    core.quit()


expName = 'grating_experiment'
expInfo = {'participant': subject_number, 'session': '001'}
filename = f'data/{expInfo["participant"]}_{expName}_{expInfo["session"]}.csv'


conditions = [
    {'spatial_frequency': 0.5, 'size': 2},
    {'spatial_frequency': 1, 'size': 2},
    {'spatial_frequency': 2, 'size': 2},
    {'spatial_frequency': 4, 'size': 2},
    {'spatial_frequency': 8, 'size': 2},
]

trials = data.TrialHandler(
    conditions, nReps=1, method='random', dataTypes=['spatial_frequency', 'size']
)
win = visual.Window(
    size=[1680, 1050],
    units="deg",
    fullscr=True,
    color=[-1, -1, -1],
    monitor='Stim'# Update based on monitor
)
trigger_codes = {
    "g_fr_1":1,
    "g_fr_2":2,
    "g_fr_3":3,
    "g_fr_4":4,
    "g_fr_5":5,
    

  
}
welcome_text = visual.TextStim(win=win, text="Welcome to the experiment! Please keep your eyes fixated on the center of the screen.", height=1.2, color=[1, 1, 1])
welcome_text.draw()
win.flip()
core.wait(5)

fixation_duration_s = 5
stim_duration_s = 7
reversal_interval = 3.5

grating_size =[6,6]
text_height = 1.0
for trial in trials:
    sf = trial['spatial_frequency']
    stim_size = trial['size']

   
    fixation_text = visual.TextStim(win=win, text="+", height=text_height, color=[1, 1, 1])
    fixation_text.draw()
    win.flip()
    core.wait(fixation_duration_s)

    
    grating = visual.GratingStim(
        win=win,
        size=grating_size,  
        units="deg",
        sf=sf,
        mask='circle'
    )

port.write([0x01])
time.sleep(PulseWidth)
port.write([0x00])

clock = core.Clock()
phase_direction = 1
last_reversal_time = 0

while clock.getTime() < stim_duration_s:
        current_time = clock.getTime()

        
        if current_time - last_reversal_time >= reversal_interval:
            phase_direction *= -1
            last_reversal_time = current_time

        grating.phase += phase_direction * 0.05
        grating.draw()
        win.flip()
trials.addData('spatial_frequency', sf)
trials.addData('stimulus_size', stim_size)


if not os.path.exists('data'):
    os.makedirs('data')
trials.saveAsWideText(filename)

connected = False
thread.join(1.0)
port.close()
win.close()
core.quit()

win.close()
core.quit()
