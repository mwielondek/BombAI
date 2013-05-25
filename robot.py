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
        return self.defend(state, current_round, possible_commands)
        
    def defend(self, state, current_round, possible_commands):
        (board, alive_players, bombs, previous_actions) = state
        
        # ep = get_escape_paths(self.me.loc, state)
        # ep2 = [moveset[0] for moveset in ep]
        # antal = len(set(ep2))
        # log("Antal utvagar: %s"%antal)
        
        # check if other bot in direct line of sight'
        for bot in alive_players:
            print bot
        
        def move():
            for move in possible_commands:
                if loc_is_safe(self.me.loc + RDIRECTIONS[move], traps=False):
                    log("from here%s"%move)
                    return move
        
            # if no single move guarantees safety, look for closest safe spot
            best_move = get_best_move(self.me, state)
            log("Calculated best move (25 ticks): %s"%best_move)
            if best_move:
                return best_move
        
            # check for closest safe spot but for less turns ahead
            for i in reversed(range(1,6)):
                best_move = get_best_move(self.me, state, i)
                log("Calculated best move (%s ticks): %s"%(i, best_move))
                if best_move:
                    return best_move
        
            # else fall back to randomness, except pass
            log("Robot Panic! Choosing move at random.")
            import random
            if possible_commands:
                return possible_commands[random.randint(0, len(possible_commands) - 1)]
        
        def passive_defence():
            # check if trapped
            if not loc_is_safe(self.me.loc, 1, False, True):
                log("Threat level low, but I seem trapped!")
                return move()
            # check if 'kinda' trapped - how many escape paths do I have?
            # log("=GEP: %s"%get_escape_paths(self.me.loc, state))
            # if len(get_escape_paths()) <= 2:
            #     log("TOO LITTLE ESCPAE PODS OMAOMAMAOGM")
            # else chillax
            return "pass"
                
        if not bombs:
            log("No bombs. No stress.")
            return passive_defence()
        
        bombs.sort(key=lambda bomb: bomb.x)
        log("Bombs at %s"%bombs)
        # log("Blast paths for next turn %s"%current_round.get_blast_paths(1))

        if loc_is_safe(self.me.loc):
            log("Not in blast path, chillax.")
            return passive_defence()
        
        # else (is in blastpath) move
        log("In blast path, run Forrest!")
        return move()
        
        return "pass"