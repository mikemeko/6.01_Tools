"""
Main constants.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from core.gui.constants import CONNECTOR_BOTTOM
from core.gui.constants import CONNECTOR_LEFT
from core.gui.constants import CONNECTOR_RIGHT
from core.gui.constants import CONNECTOR_TOP

# colors
ADDER_FILL = '#93E1D4'
ADDER_OUTLINE = 'black'
DELAY_FILL = '#93E1D4'
DELAY_OUTLINE = 'black'
GAIN_FILL = '#93E1D4'
GAIN_OUTLINE = 'black'
IO_FILL = '#BBB'
IO_OUTLINE = 'black'

# connector flags for system drawable components
ADDER_CONNECTORS = CONNECTOR_LEFT | CONNECTOR_RIGHT
DELAY_CONNECTORS = CONNECTOR_LEFT | CONNECTOR_RIGHT
GAIN_HORIZONTAL_CONNECTORS = CONNECTOR_LEFT | CONNECTOR_RIGHT
GAIN_VERTICAL_CONNECTORS = CONNECTOR_BOTTOM | CONNECTOR_TOP
X_CONNECTORS = CONNECTOR_RIGHT
Y_CONNECTORS = CONNECTOR_LEFT

# system drawable component constants
ADDER_RADIUS = 10
ADDER_SEGMENT_SIZE = 10
DELAY_SIZE = 40
GAIN_BASE= 40
GAIN_HEIGHT = 40
GAIN_DOWN_VERTICES = (0, 0, GAIN_BASE / 2, GAIN_HEIGHT, GAIN_BASE, 0)
GAIN_LEFT_VERTICES = (0, GAIN_BASE / 2, GAIN_HEIGHT, GAIN_BASE, GAIN_HEIGHT, 0)
GAIN_RIGHT_VERTICES = (0, 0, 0, GAIN_BASE, GAIN_HEIGHT, GAIN_BASE / 2)
GAIN_UP_VERTICES = (GAIN_BASE / 2, 0, 0, GAIN_HEIGHT, GAIN_BASE, GAIN_HEIGHT)
IO_PADDING = 40
IO_SIZE = 20

# text
APP_NAME = 'System Simulator'
DELAY_TEXT = 'R'
DEV_STAGE = 'Pre-alpha'
FILE_EXTENSION = '.sysim'
FR = 'FR' # frequency response
INIT_UI_HELP = 'Ctrl-click to delete.\nShift-click to rotate.'
PZD = 'PZD' # pole-zero diagram
USR = 'USR' # unit sample response

# regular expressions
RE_GAIN_VERTICES = r'\((\d+), (\d+), (\d+), (\d+), (\d+), (\d+)\)'
