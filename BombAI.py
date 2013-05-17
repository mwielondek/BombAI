from sys import stdin, stdout, stderr
from BoardTools import Location, Positionable
import random

COMMAND_LEFT  = "left"
COMMAND_RIGHT = "right"
COMMAND_UP    = "up"
COMMAND_DOWN  = "down"
COMMAND_PASS  = "pass"

DIRECTIONS = { Location(-1,  0) : COMMAND_LEFT,
               Location( 1,  0) : COMMAND_RIGHT,
               Location( 0, -1) : COMMAND_UP,
               Location( 0,  1) : COMMAND_DOWN,
               Location( 0,  0) : COMMAND_PASS }
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

class Player(Positionable):
    def __init__(self, id, x, y):
        self.id = id
        super(Player, self).__init__(x, y)
        
class Bomb(Positionable):
    def __init__(self, player_id, x, y, tick):
        self.player_id = player_id
        self.tick = tick
        super(Bomb, self).__init__(x, y)
        
    def get_blast_wave(self, blast_range):
        wave = set()
        for delta in range(blast_range+1):
            wave.add((self.x+delta,self.y))
            wave.add((self.x-delta,self.y))
            wave.add((self.x,self.y+delta))
            wave.add((self.x,self.y-delta))
        return wave

class Board(object):
    def __init__(self, board):
        self.board = board

    def tile_at(self, loc):
        (x,y) = loc
        if((y >= 0) and (y < len(self.board)) and (x >= 0) and (x < len(self.board[y]))):
            return self.board[y][x]

        return TILE_OUT_OF_BOUNDS

    def is_floor(self, loc):
        return self.tile_at(loc) == TILE_FLOOR

class Action(object):
    def __init__(self, player_id, action_string):
        self.player_id = int(player_id)
        try:
            self.action = int(action_string)
            self.is_bomb = True
        except ValueError:
            self.action = action_string
            self.is_bomb = False
class Robot(object):
    def __init__(self, my_id, max_turns):
        self.my_id = my_id

    def play_round(self, state):
        pass
       
def get_bombs_for_player(player_id, bombs):
    return [bomb for bomb in bombs if bomb.player_id == player_id]

def get_possible_moves(player, board, bombs):
    ploc = player.get_loc()
    return [DIRECTIONS[dloc] for dloc in DIRECTIONS.iterkeys()
                if(board.is_floor(ploc + dloc) and not bomb_at(ploc + dloc, bombs))]

def bomb_at(loc, bombs):
    return find(lambda bomb: bomb.get_loc() == loc, bombs)

def get_player_with_id(player_id, players):
    return find(lambda player: player.id == player_id, players)

def find(pred, seq):
    return next((x for x in seq if pred(x)), None)

def readline():
    in_data = stdin.readline() 
    log("in: %s"%in_data)
    return in_data

def read_int():
    return int(readline())

def read_tuple():
    return readline().split()

def read_int_tuple():
    return [int(x) for x in read_tuple()]

def read_list():
    return list(readline().rstrip())

def eof_detected(seq):
    return not all(seq)

def read_state(height, player_count):
    board_list = [read_list() for _ in range(height)]
    if eof_detected(board_list):
        return None

    board = Board(board_list)

    alive_count   = read_int()
    alive_players = [Player(*read_int_tuple()) for _ in range(alive_count)]
    
    bomb_count = read_int()
    bombs      = [Bomb(*read_int_tuple()) for _ in range(bomb_count)]
    
    previous_actions = [Action(*read_tuple()) for _ in range(player_count)]

    return (board, alive_players, bombs, previous_actions)

def log(message):
    print >> stderr, str(message).rstrip()

def write_command(command):
    command_str = str(command)
    log("out: %s"%command_str)
    print >> stdout, command_str
    stdout.flush()

def read_initial_data():
    return [read_int() for _ in range(5)]