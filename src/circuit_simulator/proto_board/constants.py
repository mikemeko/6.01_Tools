"""
Proto board constants.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

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

# wire constants
WIRE_LENGTH_LIMIT = 10

# heuristic constants
MAYBE_ALLOW_CROSSING_WIRES = False
CROSSING_WIRE_PENALTY = 10
