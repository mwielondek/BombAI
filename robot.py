from toolbelt import *
from io import log
import game

# TODO: Create greatest robot ever programmed
class Robot(object):
    def __init__(self, my_id, max_turns):
        self.my_id = my_id
    
    @AssureSafe
    def play_round(self, state):
        (board, alive_players, bombs, previous_actions) = state
        self.me = get_me()
        current_round = get_current_round()
        
        if not self.me.is_alive():
            log("Fatal Error: Dead :( // fatal, haha, get it?")
            return "break"
            
        log("My position: %s"%self.me.loc)
        
        # get possible commands
        possible_commands = get_possible_moves(self.me.loc, board, bombs)
        log("Possible commands: %s"%possible_commands)
        
        # Rule 1: defend your ass
        defend_state = (board, bombs, possible_commands)
        return self.defend(defend_state, current_round)
        
    def defend(self, state, current_round):
        (board, bombs, possible_commands) = state
        
        if not bombs:
            log("No bombs. No stress.")
            return "pass"
        
        bombs.sort(key=lambda bomb: bomb.x)
        log("Bombs at %s"%bombs)
        # log("Blast paths for next turn %s"%current_round.get_blast_paths(1))

        if loc_is_safe(self.me.loc):
            log("Not in blast path, chillax.")
            return "pass"
        
        log("In blast path, run Forrest!")
        for move in possible_commands:
            if loc_is_safe(self.me.loc + RDIRECTIONS[move]):
                return move
        
        # if no single move guarantees safety, look for closest safe spot
        best_move = get_best_move(self.me, current_round.state)
        log("Calculated best move (25 ticks): %s"%best_move)
        if best_move:
            return best_move
        
        # check for closest safe spot but for less turns ahead
        for i in reversed(range(1,6)):
            best_move = get_best_move(self.me, current_round.state, i)
            log("Calculated best move (%s ticks): %s"%(i, best_move))
            if best_move:
                return best_move
        
        # else fall back to randomness, except pass
        log("Robot Panic! Choosing move at random.")
        import random
        if possible_commands:
            return possible_commands[random.randint(0, len(possible_commands) - 1)]
        return "pass"