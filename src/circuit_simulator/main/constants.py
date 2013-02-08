"""
Main constants.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from core.gui.constants import CONNECTOR_LEFT
from core.gui.constants import CONNECTOR_RIGHT

# colors
NEGATIVE_COLOR = 'blue'
PIN_OUTLINE = 'black'
PIN_TEXT_COLOR = 'white'
POSITIVE_COLOR = 'red'

# connector flags for circuit drawable components
PIN_RIGHT_CONNECTORS = CONNECTOR_RIGHT
RESISTOR_HORIZONTAL_CONNECTORS = CONNECTOR_LEFT | CONNECTOR_RIGHT

# circuit drawable component constants
PIN_HORIZONTAL_HEIGHT = 20
PIN_HORIZONTAL_WIDTH = 40
POWER = 10 # volts
RESISTOR_HORIZONTAL_HEIGHT = 20
RESISTOR_HORIZONTAL_WIDTH = 40
RESISTOR_NUM_ZIG_ZAGS = 5
RESISTOR_TEXT_PADDING = 10

# text
APP_NAME = 'Circuit Simulator'
DEV_STAGE = 'Pre-alpha'
GROUND = 'gnd'
