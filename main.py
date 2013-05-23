#!/usr/bin/python
import game, time
from robot import Robot
from toolbelt import get_player_with_id
from io import *

def run():
    log("Starting robot")
    initial_data = read_initial_data()
    log("Initial data: %s"%initial_data)
    (player_id, player_count, max_turns, width, height) = initial_data

    # import time
    # random.seed(time.time() * (player_id + 1))
    
    robot = Robot(player_id, max_turns)
    state = read_state(height, player_count)
    game.PLAYER_ID = player_id
    game.ME = get_player_with_id(player_id, state[1])
    counter = 0
    while state:
        start = time.time()
        game.CURRENT_ROUND = game.Round(state, counter)
        me = get_player_with_id(player_id, state[1])
        game.ME = me if me else game.ME
        command = robot.play_round(state)
        exectime = time.time() - start
        log("Execution time: %s s"%exectime)
        if exectime > 1:
            log("Timed out.")
            break
        write_command(command)
        counter += 1
        log("--"*20+"\nRound %s"%counter)
        state = read_state(height, player_count)

        
if __name__ == "__main__":
    run()