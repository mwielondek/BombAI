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

            for bot in (bot for bot in alive_players if bot.id != game.PLAYER_ID):
                if bot.loc in line_of_sight(self.me.loc, board):
                    bots_in_sight = True
                    log("Bot %s in line of sight @ %s"%(bot.id,bot.loc))
                                        
                    # assume bot will place bomb
                    bomb_count = len([bomb for bomb in bombs if (bomb.player_id == bot.id and bomb.tick > 1)])
                    for _ in range(5-bomb_count):
                        mock_bombs.append(game.Bomb(bot.id, bot.loc.x, bot.loc.y, 11))

            # check scenario where all bots in
            # line of sight place bombs (next turn)
            _backup = get_current_round()
            mock_state = (board, alive_players, mock_bombs, previous_actions)
            # turn clock 1 tick ahead
            for bomb in mock_bombs:
                bomb.tick -= 1
            game.CURRENT_ROUND = game.Round(mock_state, 1337)
            best_move = get_best_move(self.me.loc, mock_state)
            log("** If bots place bombs -> best move: %s"%best_move)
            if best_move:
                ret = best_move
            else:
                log("Confronting one of the bots! Come at me bro!")
                ret = go_towards(self.me.loc, bot.loc)
            game.CURRENT_ROUND = _backup
            return (bots_in_sight, ret)
        
        def move():
            for move in possible_commands:
                if loc_is_safe(self.me.loc + RDIRECTIONS[move], traps=False):
                    return move
        
            # if no single move guarantees safety, look for closest safe spot
            best_move = get_best_move(self.me.loc, state)
            log("Calculated best move (25 ticks): %s"%best_move)
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
                return move()
            if bots_in_sight:
                # log("Assuming bots in sight will place bombs..")
                # TODO
                pass
            return "pass"
            
        # check if other bot in direct line of sight
        lnp = look_n_predict()
        if lnp:
            bots_in_sight = True
            log("LNP %s"%lnp[1])
            if lnp[1]: return lnp[1]
                
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