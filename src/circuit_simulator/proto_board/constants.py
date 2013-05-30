"""
Proto board constants.
"""

__author__ = 'mikemeko@mit.edu (Michael Mekonnen)'

from circuit_simulator.main.constants import POT_ALPHA_FILL

# gui constants
N_PIN_CONNECTOR_FILL = '#999'
N_PIN_CONNECTOR_OUTLINE = 'black'
OP_AMP_BODY_COLOR = '#999'
OP_AMP_DOT_COLOR = '#CCC'
OP_AMP_DOT_OFFSET = 6
OP_AMP_DOT_RADIUS = 4
POT_CIRCLE_FILL = '#EEE'
POT_CIRCLE_RADIUS = 8
POT_FILL = POT_ALPHA_FILL
POT_OUTLINE = 'black'
RESISTOR_INNER_COLOR = '#777'
RESISTOR_OUTER_COLOR = '#5DCFC3'

# dimension constants
PROTO_BOARD_HEIGHT = 14 # should be even
PROTO_BOARD_MIDDLE = (PROTO_BOARD_HEIGHT - 1) / 2.
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
# vertical separations
NUM_ROWS_PER_VERTICAL_SEPARATION = 2

# wire constants
ALLOW_PIECE_CROSSINGS = False
ALLOW_WIRE_CROSSINGS = True # of opposite orientation, no wire crossings of
                            #     same orientation are allowed

# circuit piece placement constants
CIRCUIT_PIECE_SEPARATION = 2

# whether to treat resistors as components or wires
RESISTORS_AS_COMPONENTS = True
