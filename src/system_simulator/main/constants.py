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
ADDER_MARK = 'Adder'
APP_NAME = 'System Simulator'
DELAY_MARK = 'Delay'
DELAY_TEXT = 'R'
DEV_STAGE = 'Pre-alpha'
FILE_EXTENSION = '.sysim'
GAIN_MARK = 'Gain'
INIT_UI_HELP = 'Ctrl-click to delete.\nShift-click to rotate.'
IO_MARK = 'IO'
OPEN_FILE_TITLE = 'Open file ...'
PZD = 'PZD' # pole-zero diagram
REQUEST_SAVE_MESSAGE = 'System has been changed, save first?'
REQUEST_SAVE_TITLE = 'Save?'
SAVE_AS_TITLE = 'Save file as ...'
USR = 'USR' # unit sample response
WIRE_CONNECTOR_MARK = 'Wire connector'
WIRE_MARK = 'Wire'

# regular expressions
RE_GAIN_VERTICES = r'\((\d+), (\d+), (\d+), (\d+), (\d+), (\d+)\)'
RE_INT = r'(\d+)'
RE_INT_PAIR = r'\((\d+), (\d+)\)'
