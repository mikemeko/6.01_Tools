"""
GUI constants.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

# colors
BOARD_BACKGROUND_COLOR = 'white'
BOARD_MARKER_LINE_COLOR = '#DDD'
CONNECTOR_COLOR = '#777'
MESSAGE_ERROR_COLOR = 'red' # TODO(mikemeko)
MESSAGE_INFO_COLOR = 'green' # TODO(mikemeko)
MESSAGE_WARNING_COLOR = 'yellow' # TODO(mikemeko)
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

# message types
ERROR = 0
INFO = 1
WARNING = 2

# sides of the palette on which items are added
LEFT = 0
RIGHT = 1

# size constants
BOARD_WIDTH = 600
BOARD_HEIGHT = 400
BOARD_GRID_SEPARATION = 10
CONNECTOR_RADIUS = 2
MESSAGE_WIDTH = 400
MESSAGE_HEIGHT = 40
MESSAGE_PADDING = 10
MESSAGE_TEXT_WIDTH = 260
PALETTE_WIDTH = 600
PALETTE_HEIGHT = 60
PALETTE_PADDING = 10
WIRE_ARROW_LENGTH = 10
WIRE_WIDTH = 2

# duration constants
MESSAGE_INFO_DURATION = 2 # seconds

# tags
CONNECTOR_TAG = 'connector_tag'
DRAG_TAG = 'drag_tag'
