"""
Proto board visualization constants.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from circuit_simulator.proto_board.constants import PROTO_BOARD_HEIGHT
from circuit_simulator.proto_board.constants import PROTO_BOARD_WIDTH

# color
BACKGROUND_COLOR = 'white'
CONNECTOR_COLOR = 'grey'
WIRE_COLOR = 'orange'
WIRE_OUTLINE = 'black'

# size
CONNECTOR_SIZE = 4
CONNECTOR_SPACING = 8
VERTICAL_SEPARATION = 30
PADDING = 30
HEIGHT = (PROTO_BOARD_HEIGHT * CONNECTOR_SIZE + (PROTO_BOARD_HEIGHT - 4) *
    CONNECTOR_SPACING + 3 * VERTICAL_SEPARATION + 2 * PADDING)
WIDTH = (PROTO_BOARD_WIDTH * CONNECTOR_SIZE + (PROTO_BOARD_WIDTH - 1) *
    CONNECTOR_SPACING + 2 * PADDING)

# text
WINDOW_TITLE = 'Proto board'
