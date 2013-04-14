"""
Main constants.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from core.gui.constants import CONNECTOR_LEFT
from core.gui.constants import CONNECTOR_RIGHT

# colors
N_PIN_CONNECTOR_FILL = '#EEE'
N_PIN_CONNECTOR_OUTLINE = 'black'
NEGATIVE_COLOR = '#1531AE'
OP_AMP_FILL = '#EEE'
OP_AMP_OUTLINE = 'black'
PIN_OUTLINE = 'black'
PIN_TEXT_COLOR = 'white'
POSITIVE_COLOR = '#EF002A'
POT_ALPHA_EMPTY_FILL = '#EEE'
POT_ALPHA_FILL = '#3AAACF'
POT_ALPHA_OUTLINE = '#888'
RESISTOR_FILL = 'white'
RESISTOR_OUTLINE = 'grey'

# connector flags for circuit drawable components
PIN_RIGHT_CONNECTORS = CONNECTOR_RIGHT
RESISTOR_HORIZONTAL_CONNECTORS = CONNECTOR_LEFT | CONNECTOR_RIGHT

# circuit drawable component constants
DIRECTION_UP    = 0
DIRECTION_RIGHT = 1
DIRECTION_DOWN  = 2
DIRECTION_LEFT  = 3
N_PIN_CONNECTOR_PER_CONNECTOR = 10
N_PIN_CONNECTOR_TEXT_SIZE = 70
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
PALETTE_HEIGHT = 80
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

# text
APP_NAME = 'Circuit Simulator'
DEV_STAGE = 'Pre-alpha'
FILE_EXTENSION = '.circsim'
GROUND = 'gnd'
OPEN_POT_SIGNAL_FILE_TITLE = 'Open pot signal file ...'
POT_ALPHA_TEXT = u'\u03B1'
POT_SIGNAL_FILE_EXTENSION = '.potsig'
POT_SIGNAL_FILE_TYPE = 'Pot Signal File'
POWER = 'pwr'
PROBE_MINUS = '-p'
PROBE_PLUS = '+p'
PROTO_BOARD = 'PB'
SIMULATE = 'SIM'

# regular expressions
RE_OP_AMP_VERTICES = r'\((\d+), (\d+), (\d+), (\d+), (\d+), (\d+)\)'
