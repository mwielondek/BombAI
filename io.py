from sys import stdin, stdout, stderr
from board import Board
from game import *

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