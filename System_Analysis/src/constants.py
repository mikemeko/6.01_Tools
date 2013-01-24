"""
Main constants.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from gui.constants import CONNECTOR_BOTTOM
from gui.constants import CONNECTOR_LEFT
from gui.constants import CONNECTOR_RIGHT

# colors
ADDER_FILL = '#5ED1BA'
ADDER_OUTLINE = 'black'
DELAY_FILL = '#5ED1BA'
DELAY_OUTLINE = 'black'
GAIN_FILL = '#5ED1BA'
GAIN_OUTLINE = 'black'
IO_FILL = '#5ED1BA'
IO_OUTLINE = 'black'

# connector flags for drawable components
ADDER_CONNECTORS = CONNECTOR_BOTTOM | CONNECTOR_LEFT | CONNECTOR_RIGHT
DELAY_CONNECTORS = CONNECTOR_LEFT | CONNECTOR_RIGHT
GAIN_CONNECTORS = CONNECTOR_LEFT | CONNECTOR_RIGHT
X_CONNECTORS = CONNECTOR_RIGHT
Y_CONNECTORS = CONNECTOR_LEFT

# drawable component constants
ADDER_RADIUS = 10
DELAY_SIZE = 40
GAIN_LEFT_VERTICES = (0, 20, 30, 0, 30, 40)
GAIN_RIGHT_VERTICES = (0, 0, 0, 40, 30, 20)
IO_SIZE = 40
IO_PADDING = 40

# text
ADDER_TEXT = '+'
DELAY_TEXT = 'R'
