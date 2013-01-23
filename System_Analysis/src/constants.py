"""
Main constants.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from gui.constants import CONNECTOR_BOTTOM
from gui.constants import CONNECTOR_LEFT
from gui.constants import CONNECTOR_RIGHT
from gui.constants import CONNECTOR_TOP

# colors
ADDER_FILL = 'orange'
ADDER_OUTLINE = 'black'
DELAY_FILL = 'orange'
DELAY_OUTLINE = 'black'
GAIN_FILL = 'orange'
GAIN_OUTLINE = 'black'
WIRE_CONNECTOR_FILL = 'grey'
WIRE_CONNECTOR_OUTLINE = 'black'

# connector flags for drawable components
ADDER_CONNECTORS = CONNECTOR_BOTTOM | CONNECTOR_LEFT | CONNECTOR_RIGHT
DELAY_CONNECTORS = CONNECTOR_LEFT | CONNECTOR_RIGHT
GAIN_CONNECTORS = CONNECTOR_LEFT | CONNECTOR_RIGHT
WIRE_CONNECTOR_CONNECTORS = (CONNECTOR_BOTTOM | CONNECTOR_LEFT |
    CONNECTOR_RIGHT | CONNECTOR_TOP)

# drawable component constants
ADDER_RADIUS = 10
GAIN_VERTICES = (0, 0, 0, 40, 30, 20) # TODO(mikemeko): clarify
DELAY_BBOX = (0, 0, 40, 40) # TODO(mikemeko): clarify
WIRE_CONNECTOR_RADIUS = 10

# text
ADDER_TEXT = '+'
DELAY_TEXT = 'R'
