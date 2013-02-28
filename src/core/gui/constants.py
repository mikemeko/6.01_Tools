"""
GUI constants.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

# colors
BOARD_BACKGROUND_COLOR = 'white'
BOARD_MARKER_LINE_COLOR = '#DDD'
CONNECTOR_EMPTY_COLOR = 'white'
CONNECTOR_COLOR = '#BBB'
MESSAGE_ERROR_COLOR = '#FD7279'
MESSAGE_INFO_COLOR = '#95EE6B'
MESSAGE_WARNING_COLOR = '#FFD640'
PALETTE_BACKGROUND_COLOR = '#BBB'
RUN_RECT_FILL = 'white'
RUN_RECT_OUTLINE = 'black'
RUN_TEXT_ACTIVE_FILL = 'red'
RUN_TEXT_FILL = 'black'
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
MESSAGE_WIDTH = 300
MESSAGE_HEIGHT = 40
MESSAGE_PADDING = 10
MESSAGE_TEXT_WIDTH = 260
PALETTE_WIDTH = 600
PALETTE_HEIGHT = 60
PALETTE_PADDING = 10
RUN_RECT_SIZE = 40
WIRE_ARROW_LENGTH = 10
WIRE_WIDTH = 2

# duration constants
MESSAGE_ERROR_DURATION = 5 # seconds
MESSAGE_INFO_DURATION = 3 # seconds
MESSAGE_WARNING_DURATION = 4 # seconds

# key-press flags
CTRL_DOWN =  2**0
SHIFT_DOWN = 2**1

# tags
CONNECTOR_TAG = 'connector_tag'
DRAG_TAG = 'drag_tag'
ROTATE_TAG = 'rotate_tag'

# debug options
DISPLAY_WIRE_LABELS = True
