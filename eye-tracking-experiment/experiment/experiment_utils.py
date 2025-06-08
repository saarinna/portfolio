from psychopy import visual, monitors, core, data, event, gui
from titta import Titta, helpers_tobii as helpers
import time 

# -------------------------
# Monitor and Window Setup
# -------------------------
MY_MONITOR = 'Dell7560' # Needs to be found at Psychopy monitor center
FULLSCREEN = True
SCREEN_RES = [1920, 1080] # Resolution in pixels
SCREEN_WIDTH = 52  # # Physical width in cm ///  53 x 30 cm, 24"
VIEWING_DIST = 75 # Viewing distance in cm
monitor_refresh_rate = 60 # Refresh rate in Hz

# Create a Monitor object
mon = monitors.Monitor(MY_MONITOR)
mon.setWidth(SCREEN_WIDTH)
mon.setDistance(VIEWING_DIST)
mon.setSizePix(SCREEN_RES)

# Create main experiment window using monitor setting
win = visual.Window(monitor=mon, fullscr=FULLSCREEN, screen=1, size=SCREEN_RES, units='deg')

# -------------------------
# Functions
# -------------------------
def block_input_for_cooldown(cooldown_time=2):
    """
    Blocks all input for a cooldown period (default: 2s). During this time, all key presses are ignored except the 'escape' key, which
    immediately terminates the experiment. Continuously checks for key presses.

    Parameters:
    - cooldown_time: Duration in seconds to block input.
    """
    # Initialize a countdown timer with the specified cooldown duration
    cooldown_timer = core.CountdownTimer(cooldown_time)

    # Loop until the cooldown timer reaches zero
    while cooldown_timer.getTime() > 0:
        keys = event.getKeys() # Check for any key presses
        # If 'escape' is detected, terminate the experiment immediately
        if 'escape' in keys:
            print("Experiment terminated by user during cooldown.")
            core.quit()
        core.wait(0.01) # Short wait to prevent CPU overuse
        
def show_instruction(win, instruction_text, cooldown_time=2):
    """
    Displays an instruction text on the screen and waits for the user to press space to proceed, blocking any key input during an initial cooldown period.

    Parameters:
    - win: PsychoPy window where stimuli are drawn.
    - instruction_text: String containing the instruction message to display.
    - cooldown_time: Time in seconds to block user input before accepting keypress (default 2 seconds).
    """
    # Create a TextStim object to display the instruction text
    instruction_display = visual.TextStim(
        win, 
        text=instruction_text, 
        height=0.08, 
        color='white', 
        units='norm', 
        pos=(0, 0))
    
    # Draw the instruction text to the window and show it
    instruction_display.draw()
    win.flip()

    # Block any keyboard input during the cooldown period to avoid accidental consecutive key presses
    block_input_for_cooldown(cooldown_time=cooldown_time) 

    # Wait until the user presses the spacebar to proceed
    keys = event.waitKeys(keyList=['space']) # Allows the user to proceed after cooldown period
    return keys # Return the keys pressed (spacebar confirmation)

def show_fixation(win, fixation_point, monitor_refresh_rate, duration=0.5):
    """
    Displays a fixation point on the screen for a fixed duration.

    - win: PsychoPy window where stimuli are drawn.
    - fixation_point: PsychoPy visual stimulus object representing the fixation
    - monitor_refresh_rate: The refresh rate of the monitor (frames per second).
    - duration: How long to show the fixation point, in seconds (default 0.5 seconds).
    """
    # Loop through each frame and draw the fixation point, then update the window
    for _ in range(int(duration * monitor_refresh_rate)):
        fixation_point.draw() # Draw the fixation stimulus
        win.flip() # Flip the window buffer to display the fixation
        
def show_multiple_choice(win, monitor_refresh_rate, options=['A', 'B', 'C']):
    """
    Displays a multiple choice screen with 3 clickable boxes labeled with given options (default A, B, C).
    User selects an option by clicking the mouse on a box and confirms by pressing the spacebar.
    Returns the selected answer as a string.

    Parameters:
    - win: PsychoPy window where stimuli are drawn.
    - monitor_refresh_rate: The refresh rate of the monitor (frames per second).
    - options: List of option labels to display (default ['A', 'B', 'C']).
    """
    win.setMouseVisible(True) # Make mouse cursor visible during multiple choice
    
    # Instruction text shown above the options
    question_text = (
        "Please select the correct answer by left-clicking the mouse.\n\n"
        "Once you have selected your answer, press [SPACE] to confirm and proceed to the next stimulus."
    )
    
    # Create the question prompt text stimulus, positioned near top center
    question = visual.TextStim(win, text=question_text, height=0.1, color='white', units='norm', pos=(0, 0.5))
    
    box_positions = [(-0.5, -0.3), (0, -0.3), (0.5, -0.3)]  # 3 boxes centered horizontally
    box_size = (0.3, 0.2)  # Fixed size for each box
    box_color = 'gray'  # Color of the boxes

    # Create option boxes
    boxes = [
        visual.Rect(win, width=box_size[0], height=box_size[1],
                    fillColor=box_color, lineColor='black', pos=pos, units='norm')
        for pos in box_positions
    ]

    # Create option labels
    labels = [
        visual.TextStim(win, text=opt, height=0.08,
                        color='black', units='norm', pos=pos)
        for opt, pos in zip(options, box_positions)
    ]
    
    # Track mouse
    mouse = event.Mouse(win=win)
    event.clearEvents() # Clear previous events to avoid accidental inputs

    selected_index = None # Track which option is currently selected

    # Allow experiment termination by pressing escape
    while True:
        if 'escape' in event.getKeys(keyList=['escape']):
            print("Experiment terminated by user.")
            win.close()
            core.quit()
        question.draw() # Show the question

        # Draw all boxes and labels, highlight selected or hovered box
        for i, (box, label) in enumerate(zip(boxes, labels)):
            if selected_index == i:
                box.fillColor = 'yellow' # Highlight selected box
            elif box.contains(mouse):
                box.fillColor = 'gray' # Hover effect
            else:
                box.fillColor = box_color # Default box color

            box.draw() # Draw option boxes
            label.draw() # Draw the option labels

        win.flip() # Update the window to show changes

        # Detect click
        if mouse.getPressed()[0]:  # Left click
            # Check if click was inside any box; if yes, select that option
            for i, box in enumerate(boxes):
                if box.contains(mouse):
                    selected_index = i

        # Check for spacebar press to confirm selection
        keys = event.getKeys()
        if 'space' in keys and selected_index is not None:
            win.setMouseVisible(False) # Hide mouse cursor before exiting
            return options[selected_index] # Return chosen option label
        
        # Wait for one monitor refresh cycle before next loop iteration
        core.wait(1 / monitor_refresh_rate)

def show_fixed_stimulus(win, stimulus, tracker, stimulus_duration=60, monitor_refresh_rate=60, cooldown_time=2):
    """
    Displays a visual stimulus on the window for a fixed duration (in seconds) or until the user presses the spacebar.
    Initial spacebar inputs are blocked for a cooldown period right after stimulus onset to avoid accidental early termination.
    Returns the actual duration the stimulus was presented.

    Parameters:
    - win: The PsychoPy window where the stimulus is drawn.
    - stimulus: The stimulus object to display (assumed to have a .draw() method and .image attribute).
    - tracker: An object used to log event messages (e.g., stimulus onset and offset).
    - stimulus_duration: Duration (in seconds) to display the stimulus if spacebar isn't pressed.
    - monitor_refresh_rate: The refresh rate of the monitor (frames per second).
    - cooldown_time: Time (in seconds) after stimulus onset during which spacebar input is ignored.
    """
    stim_clock = core.Clock() # Timer to measure how long stimulus is displayed
    stim_clock.reset() # Reset timer to zero at stimulus onset

    total_frames = int(stimulus_duration * monitor_refresh_rate) # Calculate number of frames to display stimulus
    
    for frame in range(total_frames):
        stimulus.draw() # Draw the stimulus on the window buffer
        win.flip() # Flip the window buffer to update display (show stimulus)

        if frame == 0:
            # Send event message marking stimulus onset, using stimulus image name
            tracker.send_message("onset_" + stimulus.image)
            # Block input for cooldown_time seconds to prevent accidental key presses at onset
            block_input_for_cooldown(cooldown_time=cooldown_time)  # <-- block input after stimulus is shown

        keys = event.getKeys(keyList=['space', 'escape']) # Check for space or escape key presses

        if 'escape' in keys:
            # If escape pressed, terminate experiment immediately
            print("Experiment terminated by user during stimulus presentation.")
            win.close()
            core.quit()
        elif 'space' in keys:
            # If space pressed after cooldown, exit stimulus presentation early
            break

    elapsed_time = stim_clock.getTime() # Get actual time stimulus was displayed
    tracker.send_message("offset_" + stimulus.image) # Log stimulus offset event
    return elapsed_time # Return stimulus presentation duration