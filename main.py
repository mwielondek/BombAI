#!/usr/bin/python
from BombAI import *

# TODO: Create greatest robot ever programmed
class Robot(object):
    def __init__(self, my_id, max_turns):
        self.my_id = my_id

    def play_round(self, state):
        (board, alive_players, bombs, previous_actions) = state
        self.me = get_player_with_id(self.my_id, alive_players)
        
        # get possible commands and put pass first
        possible_commands = get_possible_moves(self.me, board, bombs)
        pc = possible_commands
        possible_commands.insert(0, pc.pop(pc.index("pass")))
        del pc
        
        # dont place out bombs.. yet.
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
        
        # else just make a move, except pass
        return possible_commands[random.randint(1, len(possible_commands) - 1)]

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