"""
Main constants.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from circuit_simulator.simulation.constants import NUM_SAMPLES
from circuit_simulator.simulation.constants import T

# colors
LAMP_BOX_COLOR = 'white'
LAMP_COLOR = 'yellow'
LAMP_EMPTY_COLOR = '#DDD'
MOTOR_FILL = '#666'
MOTOR_POT_FILL = '#666'
N_PIN_CONNECTOR_FILL = '#EEE'
N_PIN_CONNECTOR_OUTLINE = 'black'
NEGATIVE_COLOR = '#1531AE'
OP_AMP_FILL = '#EEE'
OP_AMP_OUTLINE = 'black'
PHOTORESISTORS_FILL = '#666'
PIN_OUTLINE = 'black'
PIN_TEXT_COLOR = 'white'
POSITIVE_COLOR = '#EF002A'
POT_ALPHA_EMPTY_FILL = '#EEE'
POT_ALPHA_FILL = '#3AAACF'
POT_ALPHA_OUTLINE = '#888'
RESISTOR_FILL = 'white'
RESISTOR_OUTLINE = 'grey'
ROBOT_PIN_FILL = '#666'

# circuit drawable component constants
DIRECTION_UP    = 0
DIRECTION_RIGHT = 1
DIRECTION_DOWN  = 2
DIRECTION_LEFT  = 3
LAMP_BOX_PADDING = 3
LAMP_BOX_SIZE = 12
LAMP_RADIUS = 4
MOTOR_SIZE = 60
MOTOR_POT_SIZE = 60
N_PIN_CONNECTOR_PER_CONNECTOR = 10
N_PIN_CONNECTOR_TEXT_SIZE = 60
OP_AMP_BASE = 60
OP_AMP_HEIGHT = 60
OP_AMP_DOWN_VERTICES = (0, 0, OP_AMP_BASE / 2, OP_AMP_HEIGHT, OP_AMP_BASE, 0)
OP_AMP_LEFT_VERTICES = (0, OP_AMP_BASE / 2, OP_AMP_HEIGHT, OP_AMP_BASE,
    OP_AMP_HEIGHT, 0)
OP_AMP_RIGHT_VERTICES = (0, 0, 0, OP_AMP_BASE, OP_AMP_HEIGHT, OP_AMP_BASE / 2)
OP_AMP_UP_VERTICES = (OP_AMP_BASE / 2, 0, 0, OP_AMP_HEIGHT, OP_AMP_BASE,
    OP_AMP_HEIGHT)
OP_AMP_CONNECTOR_PADDING = 20
OP_AMP_SIGN_PADDING = 10
PHOTORESISTORS_SIZE = 60
PIN_HORIZONTAL_HEIGHT = 20
PIN_HORIZONTAL_WIDTH = 40
POT_ALPHA_WIDTH = 12
POT_ALPHA_HEIGHT = 12
POWER_VOLTS = 10
PROBE_SIZE = 20
PROBE_INIT_PADDING = 10
RESISTOR_HORIZONTAL_HEIGHT = 20
RESISTOR_HORIZONTAL_WIDTH = 40
RESISTOR_NUM_ZIG_ZAGS = 5
RESISTOR_TEXT_PADDING = 10
ROBOT_PIN_SIZE = 60

# text
APP_NAME = 'Circuit Simulator'
DEV_STAGE = 'Pre-alpha'
FILE_EXTENSION = '.circsim'
GROUND = 'gnd'
LAMP_SIGNAL_FILE_EXTENSION = '.lampsig'
LAMP_SIGNAL_FILE_TYPE = 'Lamp Signal File'
OPEN_LAMP_SIGNAL_FILE_TITLE = 'Open lamp signal file ...'
OPEN_POT_SIGNAL_FILE_TITLE = 'Open pot signal file ...'
POT_ALPHA_TEXT = u'\u03B1'
POT_SIGNAL_FILE_EXTENSION = '.potsig'
POT_SIGNAL_FILE_TYPE = 'Pot Signal File'
POWER = 'pwr'
PROBE_MINUS = '-p'
PROBE_PLUS = '+p'
PROTO_BOARD = 'PB'
SIMULATE = 'SIM'

# window constants
BOARD_WIDTH = 800
BOARD_HEIGHT = 500
PALETTE_HEIGHT = 100

# connector piece disabled pins
DISABLED_PINS_HEAD_CONNECTOR = ()
DISABLED_PINS_MOTOR_CONNECTOR = (1, 2, 3, 4)
DISABLED_PINS_ROBOT_CONNECTOR = (1, 3, 5, 6, 7, 8)

# plotter constants
T_SAMPLES = [(n * T) for n in xrange(NUM_SAMPLES)]

# way to represent connectors
SCHEMATIC_CONNECTOR_DRAWABLES = True

# regular expressions
RE_OP_AMP_VERTICES = r'\((\d+), (\d+), (\d+), (\d+), (\d+), (\d+)\)'
