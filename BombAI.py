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
               Location( 0,  1) : COMMAND_DOWN }
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
            for d in [delta,-delta]:
                wave.add(self.loc + Location(d,0))
                wave.add(self.loc + Location(0,d))      
        return wave
        
    def __eq__(self, other):
        return (self.x,self.y) == (other.x,other.y)
        
    def __hash__(self):
        return hash((self.x,self.y))

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

def get_possible_moves(loc, board, bombs):
    return [DIRECTIONS[dloc] for dloc in DIRECTIONS.iterkeys()
                if(board.is_floor(loc + dloc) and not bomb_at(loc + dloc, bombs))]

def bomb_at(loc, bombs):
    return find(lambda bomb: bomb.loc == loc, bombs)
    
# def get_free_tiles(board, bombs):
#     tiles = set()
#     for y,row in enumerate(board.board):
#         for x,_ in enumerate(row):
#             loc = Location(x,y)
#             if(board.is_floor(loc) and not bomb_at(loc, bombs)):
#                 tiles.add(loc)
#     
#     return tiles
#     
# def get_closest(x, list):
#     closest = None
#     for loc in list:
#         log(len(x-loc))
#     return closest
    
def get_best_move(player, board, bombs, blast_paths):
    pc = get_possible_moves(player.loc, board, bombs)
    safelist = get_safe_move((board, bombs, blast_paths), player.loc, pc)
    log(safelist)
    
    if not safelist:
        return None
        
    best_move = safelist[0]
    for moves in safelist:
        if len(moves) < len(best_move):
            best_move = moves
    del safelist[:]
    return best_move

def get_safe_move(comp, loc, possible_moves, safelist=[], move_history=[], deep=0):
    if deep < 7:
        (board, bombs, blast_paths) = comp
        for move in possible_moves:
            move_history_branch = move_history[:]
            newloc = loc + RDIRECTIONS[move]
            move_history_branch.append(move)
            if loc_is_safe(newloc, blast_paths):
                log("Appending safelist with %s"%move_history_branch)
                safelist.append(move_history_branch)
                if len(move_history_branch) <= 2:
                    log("breaking")
                    break
            pc = get_possible_moves(newloc, board, bombs)
            try:
                pc.remove(DIRECTIONS[-(RDIRECTIONS[move])])
            except ValueError:
                pass
            log("Deep: %s - calling get safe now with move history:\n %s"%(deep,move_history_branch))
            get_safe_move(comp, newloc, pc, safelist, move_history_branch, deep+1)
    
    return safelist
        
def loc_is_safe(loc, blast_paths):
    return not loc in blast_paths

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