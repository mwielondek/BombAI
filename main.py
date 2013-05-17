#!/usr/bin/python
from BombAI import *

# TODO: Create greatest robot ever programmed
class Robot(object):
    def __init__(self, my_id, max_turns):
        self.my_id = my_id

    def play_round(self, state):
        (board, alive_players, bombs, previous_actions) = state
        self.me = get_player_with_id(self.my_id, alive_players)
        
        # get possible commands
        possible_commands = get_possible_moves(self.me.loc, board, bombs)
        
        # dont place out bombs.. yet.
        # if(len(get_bombs_for_player(self.my_id, bombs)) < BOMB_MAX_PER_PLAYER):
        #     possible_commands.append(random.randint(BOMB_MIN_TICK, BOMB_MAX_TICK))

        log("Possible commands: %s"%possible_commands)
        # random fjantom
        # possible_commands[random.randint(0, len(possible_commands) - 1)]
        
        # Rule 1: defend your ass
        defend_state = (board, bombs, possible_commands)
        return self.defend(defend_state)
        
    def defend(self, state):
        (board, bombs, possible_commands) = state
        
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
        
        if not self.me.loc in blast_paths:
            log("Not in blast path, chillax.")
            return "pass"
        
        for move in possible_commands:
            if not self.me.loc + RDIRECTIONS[move] in blast_paths:
                return move
        
        # if no single move guarantees safety, look for closest safe spot
        best_move = get_best_move(self.me, board, bombs, blast_paths)
        log("best escape strategy: %s"%best_move)
        
        # make the first move
        if best_move:
            return best_move[0]
        
        # else fall back to randomness, except pass
        log("RoboPanick! Choosing move at random.")
        if possible_commands:
            return possible_commands[random.randint(0, len(possible_commands) - 1)]
        return "pass"

def run():
    log("Starting robot")
    initial_data = read_initial_data()
    log("Initial data: %s"%initial_data)
    (player_id, player_count, max_turns, width, height) = initial_data

    import time
    random.seed(time.time() * (player_id + 1))

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