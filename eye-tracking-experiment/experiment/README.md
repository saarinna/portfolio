## Eye-tracking experiment scripts

Recorded data saved into the [data](data/) folder.

- [experiment_utils.py](experiment_utils.py/): This script imports core PsychoPy modules and the Tobii eye-tracking integration, sets up monitor and window parameters, and is called by the main experiment script [experiment.py](experiment.py/).
- [experiment.py](experiment.py/): The main script that runs the experiment. It handles the overall experiment flow, including stimulus presentation, response collection, eye-tracking integration, and data logging. It uses utility functions from [experiment_utils.py](experiment_utils.py/) to manage display and input.
- [practice.py](practice.py/): Identical to experiment.py with different set of stimuli (laajoki area). As a separate script to prevent to ensure dynamic and easy break between the practice and experiment during the actual experiment => experiment.py should be run only after the participant is ready to complete it.