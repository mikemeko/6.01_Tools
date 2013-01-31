"""
Main constants.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from gui.constants import CONNECTOR_LEFT
from gui.constants import CONNECTOR_RIGHT

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
GAIN_CONNECTORS = CONNECTOR_LEFT | CONNECTOR_RIGHT
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
PZD = 'PZD' # pole-zero diagram
USR = 'USR' # unit sample response
