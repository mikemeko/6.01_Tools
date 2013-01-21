"""
Constants.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

# TODO(mikemeko): alphabetize

# colors
BOARD_BACKGROUND_COLOR = 'white'
BOARD_MARKER_COLOR = 'grey'
CONNECTOR_COLOR = 'grey'
PALETTE_BACKGROUND_COLOR = '#DDDDDD'
WIRE_COLOR = 'grey'
WIRE_ILLEGAL_COLOR = 'red'

# connector flags
CONNECTOR_BOTTOM = 2**0
CONNECTOR_LEFT =   2**1
CONNECTOR_RIGHT =  2**2
CONNECTOR_TOP =    2**3

# size constants
BOARD_WIDTH = 600
BOARD_HEIGHT = 400
BOARD_MARKER_SEPARATION = 10
BOARD_MARKER_RADIUS = 1
CONNECTOR_RADIUS = 2
PALETTE_WIDTH = 600
PALETTE_HEIGHT = 60
PALETTE_PADDING = 10
WIRE_WIDTH = 2

# tags
CONNECTOR_TAG = 'connector_tag'
DRAG_TAG = 'drag_tag'
