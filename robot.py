from toolbelt import *
from io import log
import game, io

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
            log("Fatal Error: Dead :( ... fatal, haha, get it?")
            return "break"
            
        log("My position: %s"%self.me.loc)
        
        # get possible commands
        possible_commands = get_possible_moves(self.me.loc, board, bombs)
        log("Possible commands: %s"%possible_commands)
        
        # Rule 1: defend your ass
        return self.defend(state, current_round, possible_commands)
        
    def defend(self, state, current_round, possible_commands):
        (board, alive_players, bombs, previous_actions) = state
        bots_in_sight = False
        
        def look_n_predict(presumptive=False):            
            ret = ''
            bots_in_sight = False
            mock_bombs = bombs[:]
            
            _line_of_sight = line_of_sight(self.me.loc, board)
            for bot in (bot for bot in alive_players if bot.id != game.PLAYER_ID):
                if bot.loc in _line_of_sight:
                    bots_in_sight = True
                    log("Bot %s in line of sight @ %s"%(bot.id,bot.loc))
                                        
                    # assume bot will place bomb
                    bomb_count = len([bomb for bomb in bombs if (bomb.player_id == bot.id and bomb.tick > 1)])
                    for _ in range(5-bomb_count):
                        b = game.Bomb(bot.id, bot.loc.x, bot.loc.y, DEFAULT_TICKS)
                        b.ghost = True
                        mock_bombs.append(b)

            if bots_in_sight:
                _backup = get_current_round()
                mock_state = (board, alive_players, mock_bombs, previous_actions)
                game.CURRENT_ROUND = game.Round(mock_state, 1337)
                best_move = get_best_move(self.me.loc, mock_state)
                log("** If bots place bombs -> best move: %s"%best_move)
                ret = best_move
                game.CURRENT_ROUND = _backup
            
            return (bots_in_sight, ret)
        
        def move(possible_commands=possible_commands, allow_pass=True):
            for move in possible_commands:
                if loc_is_safe(self.me.loc + RDIRECTIONS[move], traps=False):
                    return move
        
            # if no single move guarantees safety, look for closest safe spot
            best_move = get_best_move(self.me.loc, state, allow_pass=allow_pass)
            log("Calculated best move (%s ticks): %s"%(DEFAULT_TICKS, best_move))
            if best_move:
                return best_move
        
            # check for closest safe spot but for less turns ahead
            for i in reversed(range(1,6)):
                best_move = get_best_move(self.me.loc, state, i)
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
                pc = possible_commands[:]
                pc.remove("pass")
                return move(pc, False)
            
            # check if other bot in direct line of sight
            # and predict best move if bot places bomb
            lnp = look_n_predict()
            if lnp and lnp[1]: return lnp[1]
                
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