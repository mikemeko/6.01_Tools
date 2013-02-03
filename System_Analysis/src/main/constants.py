"""
Main constants.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from gui.constants import CONNECTOR_BOTTOM
from gui.constants import CONNECTOR_LEFT
from gui.constants import CONNECTOR_RIGHT
from gui.constants import CONNECTOR_TOP

# colors
ADDER_FILL = '#EEE'
ADDER_OUTLINE = 'black'
DELAY_FILL = '#EEE'
DELAY_OUTLINE = 'black'
GAIN_FILL = '#EEE'
GAIN_OUTLINE = 'black'
IO_FILL = '#BBB'
IO_OUTLINE = 'black'
RUN_RECT_FILL = 'white'
RUN_RECT_OUTLINE = 'black'
RUN_TEXT_ACTIVE_FILL = 'red'
RUN_TEXT_FILL = 'black'

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
GAIN_DOWN_VERTICES = (0, 0, 20, 40, 40, 0) # pointing down
GAIN_LEFT_VERTICES = (0, 20, 40, 40, 40, 0) # pointing left
GAIN_RIGHT_VERTICES = (0, 0, 0, 40, 40, 20) # pointing right
GAIN_UP_VERTICES = (20, 0, 0, 40, 40, 40) # pointing up
IO_PADDING = 40
IO_SIZE = 20
RUN_RECT_SIZE = 40

# text
APP_NAME = 'System Analysis Simulator' # TODO(mikemeko): find better name :)
DELAY_TEXT = 'R'
DEV_STAGE = 'Pre-alpha'
INIT_UI_HELP = 'Ctrl-click to delete.\nShift-click to rotate.'
PZD = 'PZD' # pole-zero diagram
REQUEST_SAVE_MESSAGE = 'System has been changed, save first?'
REQUEST_SAVE_TITLE = 'Save?'
USR = 'USR' # unit sample response
