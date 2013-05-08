"""
Circuit simulator constants.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

# op amp constants
OP_AMP_K = 1000000000

# head constants
HEAD_POT_INIT_ALPHA = 0.5
HEAD_POT_RESISTANCE = 10 # TODO(mikemeko): verify this with measurements

# motor constants
MOTOR_B_LOADED = 0.0045
MOTOR_B_UNLOADED = 0.0006
MOTOR_INIT_ANGLE = 0
MOTOR_INIT_SPEED = 0
MOTOR_J = 0.00132
MOTOR_KB = 0.495
MOTOR_KT = 0.323
MOTOR_RESISTANCE = 5.26

# photodetector constants
PHOTODETECTOR_K = 5e-7 # TODO(mikemeko): verify this with measurements

# sampling constants
NUM_SAMPLES = 120
T = 0.01 # sampling periond

# debugging
DEBUG = True
