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
    
    robot = Robot(player_id, max_turns)
    state = read_state(height, player_count)
    game.PLAYER_ID = player_id
    game.ME = get_player_with_id(player_id, state[1])
    counter = 0
    longest_calc = (0,0)
    while state:
        start = time.time()
        game.CURRENT_ROUND = game.Round(state, counter)
        me = get_player_with_id(player_id, state[1])
        game.ME = me if me else game.ME
        command = robot.play_round(state)
        # if dead robot returns 'break'
        if command == "break":
            break
        exectime = time.time() - start
        longest_calc = [longest_calc,(exectime,counter)][exectime>longest_calc[0]]
        log("Execution time: %s s"%exectime)
        if exectime > 1:
            log("Timed out.")
            # break
        write_command(command)
        counter += 1
        log(("--"*8+"Round %s"+"--"*8)%counter)
        state = read_state(height, player_count)

    log("Longest exec: %s"%str(longest_calc))
        
if __name__ == "__main__":
    run()