"""
GUI constants.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

# colors
BOARD_BACKGROUND_COLOR = 'white'
BOARD_MARKER_LINE_COLOR = '#DDD'
CONNECTOR_COLOR = '#777'
PALETTE_BACKGROUND_COLOR = '#BBB'
WIRE_COLOR = '#777'
WIRE_CONNECTOR_FILL = 'grey'
WIRE_CONNECTOR_OUTLINE = 'black'

# connector flags
CONNECTOR_BOTTOM = 2**0
CONNECTOR_CENTER = 2**1
CONNECTOR_LEFT =   2**2
CONNECTOR_RIGHT =  2**3
CONNECTOR_TOP =    2**4

# size constants
BOARD_WIDTH = 600
BOARD_HEIGHT = 400
BOARD_GRID_SEPARATION = 10
CONNECTOR_RADIUS = 3
PALETTE_WIDTH = 600
PALETTE_HEIGHT = 60
PALETTE_PADDING = 10
WIRE_ARROW_LENGTH = 10
WIRE_WIDTH = 2

# tags
CONNECTOR_TAG = 'connector_tag'
DRAG_TAG = 'drag_tag'
