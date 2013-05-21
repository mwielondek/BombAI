#!/usr/bin/python
from game import *
from robot import Robot
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
    counter = 0
    while state:
        counter += 1
        log("Round %s"%counter)
        command = robot.play_round(state)
        write_command(command)
        state = read_state(height, player_count)
        
if __name__ == "__main__":
    run()