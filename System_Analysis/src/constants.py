"""
Main constants.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from gui.constants import CONNECTOR_LEFT
from gui.constants import CONNECTOR_RIGHT

# colors
ADDER_FILL = '#FFB873'
ADDER_OUTLINE = 'black'
DELAY_FILL = '#FFB873'
DELAY_OUTLINE = 'black'
GAIN_FILL = '#FFB873'
GAIN_OUTLINE = 'black'
IO_FILL = 'yellow'
IO_OUTLINE = 'black'
RUN_RECT_OUTLINE = 'black'
RUN_RECT_FILL = 'white'

# connector flags for drawable components
ADDER_CONNECTORS = CONNECTOR_LEFT | CONNECTOR_RIGHT
DELAY_CONNECTORS = CONNECTOR_LEFT | CONNECTOR_RIGHT
GAIN_CONNECTORS = CONNECTOR_LEFT | CONNECTOR_RIGHT
X_CONNECTORS = CONNECTOR_RIGHT
Y_CONNECTORS = CONNECTOR_LEFT

# drawable component constants
ADDER_RADIUS = 10
ADDER_SEGMENT_SIZE = 10
DELAY_SIZE = 40
GAIN_LEFT_VERTICES = (0, 20, 40, 0, 40, 40)
GAIN_RIGHT_VERTICES = (0, 0, 0, 40, 40, 20)
IO_SIZE = 20
IO_PADDING = 40
RUN_RECT_SIZE = 40

# text
APP_NAME = 'System Analysis Simulator' # TODO(mikemeko): better name
DELAY_TEXT = 'R'
DEV_STAGE = 'Pre-alpha'
PZD = 'PZR' # pole-zero diagram
USR = 'USR' # unit sample response
