"""
Proto board constants.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

# dimension constants
PROTO_BOARD_HEIGHT = 14 # should be even
PROTO_BOARD_WIDTH = 62

# structure constants
BOTTOM_SECTION = set(r for r in xrange(PROTO_BOARD_HEIGHT / 2,
    PROTO_BOARD_HEIGHT - 2))
TOP_SECTION = set(r for r in xrange(2, PROTO_BOARD_HEIGHT / 2))

# wire constants
WIRE_LENGTH_LIMIT = 5
