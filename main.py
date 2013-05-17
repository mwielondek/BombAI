#!/usr/bin/python
from sys import stdin, stdout, stderr
import random

COMMAND_LEFT  = "left"
COMMAND_RIGHT = "right"
COMMAND_UP    = "up"
COMMAND_DOWN  = "down"
COMMAND_PASS  = "pass"

DIRECTIONS = { (-1,  0) : COMMAND_LEFT,
               ( 1,  0) : COMMAND_RIGHT,
               ( 0, -1) : COMMAND_UP,
               ( 0,  1) : COMMAND_DOWN,
               ( 0,  0) : COMMAND_PASS }
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

class BoardObject(object):
    def __init__(self):
        pass
    
    def __repr__(self):
        return "%s: %s"%(self.__class__.__name__, "(%s,%s)"%(self.x, self.y))
        
    def get_coord_tuple(self):
        return "(%s,%s)"%(self.x, self.y)

class Player(BoardObject):
    def __init__(self, id, x, y):
        self.id = id
        self.x = x
        self.y = y
        
class Bomb(BoardObject):
    def __init__(self, player_id, x, y, tick):
        self.player_id = player_id
        self.x = x
        self.y = y
        self.tick = tick
    
    # bombs at the same loc are treated equal
    def __eq__(self, other):
        return (self.x,self.y) == (other.x,other.y)
        
    def __hash__(self):
        return hash((self.x,self.y))
        
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

    def tile_at(self, x, y):
        if((y >= 0) and (y < len(self.board)) and (x >= 0) and (x < len(self.board[y]))):
            return self.board[y][x]

        return TILE_OUT_OF_BOUNDS

    def is_floor(self, x, y):
        return self.tile_at(x, y) == TILE_FLOOR

# TODO: Create greatest robot ever programmed
class Robot(object):
    def __init__(self, my_id, max_turns):
        self.my_id = my_id

    def play_round(self, state):
        (board, alive_players, bombs, previous_actions) = state
        self.me = get_player_with_id(self.my_id, alive_players)

        possible_commands = []
        possible_commands.extend(get_possible_moves(self.me, board, bombs))
        
        # dont place out bombs
        # if(len(get_bombs_for_player(self.my_id, bombs)) < BOMB_MAX_PER_PLAYER):
        #     possible_commands.append(random.randint(BOMB_MIN_TICK, BOMB_MAX_TICK))

        log("Possible commands: %s"%possible_commands)
        # random fjantom
        # possible_commands[random.randint(0, len(possible_commands) - 1)]
        
        # Rule 1: defend your ass
        defend_state = (bombs, possible_commands)
        return self.defend(defend_state)
        
    def defend(self, state):
        (bombs, possible_commands) = state
        log(possible_commands)
        
        if not bombs:
            log("No bombs. Stop running Forest!")
            return "pass"
        
        bombs.sort(key=lambda bomb: bomb.x)
        log("Defending. Bombs at %s"%bombs)
        
        
        blast_paths = set()
        # if dupl. bombs
        multi = True if len(set(bombs)) != len(bombs) else False
        for bomb in set(bombs):
            # calc range
            count = [1,len([dupl for dupl in bombs if dupl == bomb])][multi]
            blast_range = 2 + count
            
            # collect blast paths
            [blast_paths.add(blast) for blast in bomb.get_blast_wave(blast_range)]
        
        for move in possible_commands:
            if not (self.me.x+RDIRECTIONS[move][0], self.me.y+RDIRECTIONS[move][1]) in blast_paths:
                return move
        
        # else just make a move
        return possible_commands[random.randint(0, len(possible_commands) - 1)]
        

class Action(object):
    def __init__(self, player_id, action_string):
        self.player_id = int(player_id)
        try:
            self.action = int(action_string)
            self.is_bomb = True
        except ValueError:
            self.action = action_string
            self.is_bomb = False
        
       
def get_bombs_for_player(player_id, bombs):
    return [bomb for bomb in bombs if bomb.player_id == player_id]

def get_possible_moves(player, board, bombs):
    (x, y) = (player.x, player.y)
    return [DIRECTIONS[(dx, dy)] for (dx, dy) in DIRECTIONS.iterkeys()
                if(board.is_floor(x + dx, y + dy) and not bomb_at(x + dx, y + dy, bombs))]

def bomb_at(x, y, bombs):
    return find(lambda bomb: (bomb.x, bomb.y) == (x, y), bombs)

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
    
def run():
    log("Starting robot")
    initial_data = read_initial_data()
    log("Initial data: %s"%initial_data)
    (player_id, player_count, max_turns, width, height) = initial_data

    import time
    random.seed(time.time() * (player_id + 1))

    robot = Robot(player_id, max_turns)
    state = read_state(height, player_count)
    while state:
        command = robot.play_round(state)
        write_command(command)
        state = read_state(height, player_count)


if __name__ == "__main__":
    run()
