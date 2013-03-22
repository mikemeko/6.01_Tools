"""
Proto board constants.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

# gui constants
OP_AMP_BODY_COLOR = '#999'
OP_AMP_DOT_COLOR = '#CCC'
OP_AMP_DOT_OFFSET = 6
OP_AMP_DOT_RADIUS = 4
RESISTOR_INNER_COLOR = '#777'
RESISTOR_OUTER_COLOR = '#5DCFC3'

# dimension constants
PROTO_BOARD_HEIGHT = 14 # should be even
PROTO_BOARD_WIDTH = 63

# structure constants
COLUMNS = set(xrange(PROTO_BOARD_WIDTH))
ROWS = set(xrange(PROTO_BOARD_HEIGHT))
BODY_BOTTOM_ROWS = set(r for r in xrange(PROTO_BOARD_HEIGHT / 2,
    PROTO_BOARD_HEIGHT - 2))
BODY_TOP_ROWS = set(r for r in xrange(2, PROTO_BOARD_HEIGHT / 2))
BODY_ROWS = BODY_BOTTOM_ROWS | BODY_TOP_ROWS
BODY_LEGAL_COLUMNS = COLUMNS
RAIL_ILLEGAL_COLUMNS = set([0, PROTO_BOARD_WIDTH - 1]) | set(6 * i + 1 for i in
    xrange(PROTO_BOARD_WIDTH / 6 + 1))
RAIL_LEGAL_COLUMNS = COLUMNS - RAIL_ILLEGAL_COLUMNS
RAIL_ROWS = set([0, 1, PROTO_BOARD_HEIGHT - 2, PROTO_BOARD_HEIGHT - 1])
# default power and ground rails
POWER_RAIL = PROTO_BOARD_HEIGHT - 1
GROUND_RAIL = PROTO_BOARD_HEIGHT - 2

# wire constants
MAYBE_ALLOW_CROSSING_WIRES = False
WIRE_LENGTH_LIMIT = 5

# debugging
DEBUG_SHOW_COST =        2 ** 0
DEBUG_SHOW_PROFILE =     2 ** 1
DEBUG_SHOW_PROTO_BOARD = 2 ** 2
DEBUG = DEBUG_SHOW_COST
