from board import Location
from collections import OrderedDict

COMMAND_LEFT  = "left"
COMMAND_RIGHT = "right"
COMMAND_UP    = "up"
COMMAND_DOWN  = "down"
COMMAND_PASS  = "pass"

DIRECTIONS = OrderedDict((
                        (Location( 0,  0), COMMAND_PASS),
                        (Location(-1,  0), COMMAND_LEFT),
                        (Location( 1,  0), COMMAND_RIGHT),
                        (Location( 0, -1), COMMAND_UP),
                        (Location( 0,  1), COMMAND_DOWN)
                        ))

# reversed-lookup directions        
RDIRECTIONS = dict((v,k) for (k,v) in DIRECTIONS.items())

STATUS_DEAD = "out"

TILE_WALL          = '#'
TILE_FLOOR         = '.'
TILE_FORCE_FIELD   = '+'
TILE_OUT_OF_BOUNDS = ' '

BOMB_MAX_PER_PLAYER = 5
BOMB_MAX_TICK       = 25
BOMB_MIN_TICK       = 5

RECURSION_LIMIT = 6
DEFAULT_TICKS = 10