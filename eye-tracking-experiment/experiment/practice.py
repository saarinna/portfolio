import pandas as pd
from psychopy import visual, monitors, core, data, event, gui
import numpy as np
import h5py
import os
import csv
from titta import Titta, helpers_tobii as helpers
from experiment_utils import (
    show_instruction,
    show_fixation,
    show_multiple_choice,
    show_fixed_stimulus
)

# -------------------------
# Participant ID GUI
# -------------------------
info = {'Participant ID': ''}
dlg = gui.DlgFromDict(dictionary=info, title='Practice Session')
if not dlg.OK:
    core.quit()
participant_id = info['Participant ID']
dummy_mode = (participant_id.lower() == 'dummy') # If 'dummy' is entered use dummy mode

# -------------------------
# Monitor, window, eye-tracker and timer set up
# -------------------------
MY_MONITOR = 'Dell7560' # Needs to be found at Psychopy monitor center
FULLSCREEN = True
SCREEN_RES = [1920, 1080] # Resolution in pixels
SCREEN_WIDTH = 53  # # Physical width in cm ///  53 x 30 cm, 24"
VIEWING_DIST = 75 # Viewing distance in cm
monitor_refresh_rate = 60 # Hz

# Create a Monitor object
mon = monitors.Monitor(MY_MONITOR)
mon.setWidth(SCREEN_WIDTH)
mon.setDistance(VIEWING_DIST)
mon.setSizePix(SCREEN_RES)

# Create main experiment window using monitor settings
win = visual.Window(monitor=mon, fullscr=FULLSCREEN, screen=1, size=SCREEN_RES, units='deg')

# Eye-tracker setup
et_name = 'Tobii Pro Fusion'
settings = Titta.get_defaults(et_name)
settings.FILENAME = f'practice_{participant_id}'
settings.N_CAL_TARGETS = 5
settings.DEBUG = False

# Connect to eye tracker
tracker = Titta.Connect(settings)
if dummy_mode:
    tracker.set_dummy_mode()
tracker.init()

experiment_clock = core.Clock() # For measuring total duration in seconds

# -------------------------
# Stimuli file names for Tasks A and B and correct answers
# -------------------------
STIMULI_DIR = os.path.join(os.getcwd(), 'stimuli')  # Absolute path to the 'stimuli' folder in the root directory

task_a_stimuli = [
    os.path.join(STIMULI_DIR, f) for f in [
        'laajoki2a.png', 'laajoki3a.png'
    ]
]

task_b_stimuli = [
    os.path.join(STIMULI_DIR, f) for f in [
        'laajoki1b.png', 'laajoki4b.png'
    ]
]

# Predefined correct answers
correct_answers = {
    'laajoki2a.png': 'B',
    'laajoki3a.png': 'A',
    'laajoki1b.png': 'B',
    'laajoki4b.png': 'C'
}

# -------------------------
# Create stimuli (ImageStim objects) and fixation point
# -------------------------
task_a_stimuli_images = [visual.ImageStim(win, image=filename, units='pix', pos=(0, 0)) for filename in task_a_stimuli] # Task A
task_b_stimuli_images = [visual.ImageStim(win, image=filename, units='pix', pos=(0, 0)) for filename in task_b_stimuli] # Task A
fixation_point = helpers.MyDot2(win) # Create fixation point

# -------------------------
# Instructions shown to the participant
# -------------------------
task_a_instructions = (
    "Select the point pair (A, B, C) with the greatest elevation difference.\n\n"
    "Press [SPACE] when you're ready to start task A."
)

task_change = (
    "Task A has now ended.\n\n"
    "Press [SPACE] when you're ready to see the instructions for Task B."
)

task_b_instructions = (
    "Select the bridge (A, B, or C) that is highest above the ground or the bottom of the water it crosses over, considering the lowest point beneath it.\n\n"
    "Press [SPACE] when you're ready to start task B."
)

# End of the experiment message
experiment_end = (
    "You are now done with the practice.\n\n"
    "You can leave the screen as it is.\n\n"
)

# -------------------------
# Calibration, instructions and other preparations
# -------------------------
tracker.calibrate(win) # Calibrate the eye-tracker
experiment_clock.reset() # Start recording time to track the whole experiment time
show_instruction(win, task_a_instructions) # Show instructions for task A

# Start recording if not in dummy mode
if not dummy_mode:
    tracker.start_recording(gaze=True, time_sync=True, eye_image=False,
                            notifications=True, external_signal=True, positioning=True)
    core.wait(0.5)

# Present fixation before starting Task A
for i in range(monitor_refresh_rate):
    fixation_point.draw()
    win.flip()

trial_log = [] # Create log trial info list

# -------------------------
# Present task A stimuli
# -------------------------
for stim in task_a_stimuli_images:
    show_fixation(win, fixation_point, monitor_refresh_rate, duration=0.5) # Show fixation point for 0.5 seconds
    # Show the stimulus for 60s and track its duration
    stimulus_duration = show_fixed_stimulus(win, stim, tracker, stimulus_duration=600, monitor_refresh_rate=monitor_refresh_rate, cooldown_time=2)
    # Present the multiple-choice screen and get the submitted answer
    answer = show_multiple_choice(win, monitor_refresh_rate)
    correct_answer = correct_answers.get(os.path.basename(stim.image), '') # Get the correct answer for the stimulus
    is_correct = 'correct' if answer == correct_answer else 'incorrect' # Check if given answer is correct
    tracker.send_message(f"Response sent: {answer} for stimulus {stim.image} (Stimulus Duration: {stimulus_duration:.2f}s)")
    trial_log.append({
        'filename': stim.image,
        'stimulus_duration': stimulus_duration,
        'response': answer,
        'correct_answer': correct_answer,
        'answer_correctness': is_correct
    })

# -------------------------
# Change to task B and show the instructions
# -------------------------
show_instruction(win, task_change) # Notify about task A ending
show_instruction(win, task_b_instructions) # Task B instructions

# -------------------------
# Present task B stimuli
# -------------------------
for stim in task_b_stimuli_images:
    show_fixation(win, fixation_point, monitor_refresh_rate, duration=0.5) # Show fixation point for 0.5 seconds
    # Show the stimulus for 60s and track its duration
    stimulus_duration = show_fixed_stimulus(win, stim, tracker, stimulus_duration=600, monitor_refresh_rate=monitor_refresh_rate, cooldown_time=2)
    # Present the multiple-choice screen and get the submitted answer
    answer = show_multiple_choice(win, monitor_refresh_rate)
    correct_answer = correct_answers.get(os.path.basename(stim.image), '') # Get the correct answer for the stimulus
    is_correct = 'correct' if answer == correct_answer else 'incorrect' # Check if given answer is correct
    tracker.send_message(f"Response sent: {answer} for stimulus {stim.image} (Stimulus Duration: {stimulus_duration:.2f}s)")
    trial_log.append({
        'filename': stim.image,
        'stimulus_duration': stimulus_duration,
        'response': answer,
        'correct_answer': correct_answer,
        'answer_correctness': is_correct
    })

# -------------------------
# Log total experiment duration and end session
# -------------------------
total_experiment_time = experiment_clock.getTime() # Total experiment time
tracker.send_message(f"Total experiment duration: {total_experiment_time:.2f}s")
show_instruction(win, experiment_end) # Show a screen telling that the experiment has ended
win.close() # Close the experiment window

# -------------------------
# Prepare data directory path
# -------------------------
data_dir = os.path.join('data', f'participant_{participant_id}')
os.makedirs(data_dir, exist_ok=True)  # Create the folder if it doesn't exist

# -------------------------
# Save trial log as CSV
# -------------------------
csv_filename = os.path.join(data_dir, f'practice_{participant_id}.csv')
csv_data = trial_log + [{
    'filename': 'Total Experiment Time',
    'stimulus_duration': total_experiment_time,
    'response': '',
    'correct_answer': '',
    'answer_correctness': ''
}]
with open(csv_filename, mode='w', newline='') as file:
    writer = csv.DictWriter(file, fieldnames=['filename', 'stimulus_duration', 'response', 'correct_answer', 'answer_correctness'])
    writer.writeheader()
    writer.writerows(csv_data)
print(f"Data saved to {csv_filename}")

# -------------------------
# Save eye-tracking data if not dummy mode
# -------------------------
if dummy_mode:
    print("Running in dummy mode. Eye-tracker not required.")
else:
    h5_filename = os.path.join(data_dir, f'practice_{participant_id}.h5')
    tracker.save_data(filename=h5_filename, append_version=False)
    print(f"Data saved as {h5_filename}")

    # Store trial-level metadata inside HDF5 file
    with h5py.File(h5_filename, 'a') as f:
        if 'stimuli' in f:
            del f['stimuli']  # Remove existing group if it exists (to avoid errors)
        trial_info_grp = f.create_group('stimuli')
        for i, trial in enumerate(trial_log):
            trial_grp = trial_info_grp.create_group(f'trial_{i+1}')
            for key, value in trial.items():
                trial_grp.attrs[key] = value

# -------------------------
# Load gaze data for post-experiment review
# -------------------------
if not dummy_mode:
    filename = f'{settings.FILENAME}.h5'
    with h5py.File(filename, "r") as f:
        keys = [key for key in f.keys()]
        print(f'HDF5 keys: {keys}')