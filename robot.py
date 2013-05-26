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
        
        def look_n_predict():
            for bot in (bot for bot in alive_players if bot.id != game.PLAYER_ID):
                if bot.loc in line_of_sight(self.me.loc, board):
                    log("Bot %s in line of sight @ %s"%(bot.id,bot.loc))
                    # check if in potential blast range (max 7)
                    bomb_count = len([bomb for bomb in bombs if bomb.player_id == bot.id])
                    delta = bot.loc  - self.me.loc
                    delta = abs(delta.x) if delta.x != 0 else abs(delta.y)
                    if bomb_count >= 5 or delta > 7-bomb_count:
                        log("Bot not dangerous.")
                        continue
                    # assume bot will place bomb
                    mock_bombs = bombs[:]
                    for _ in range(5-bomb_count):
                        mock_bombs.append(game.Bomb(bot.id, bot.loc.x, bot.loc.y, 5))
                    # how would you play now? will I be stuck?
                    log("What would happen?!")
                    io.PREFIX = "* "
                    mock_state = (board, alive_players, mock_bombs, previous_actions)
                    _backup = get_current_round()
                    game.CURRENT_ROUND = game.Round(mock_state, 123)
                    gem = get_best_move(self.me, mock_state)
                    log("Mock best move: %s"%gem)
                    game.CURRENT_ROUND = _backup
                
                    if not gem: # we're in trouble.
                        log("We would be in trouble. Confronting the bot!")
                        io.PREFIX = ""
                        return go_towards(self.me.loc, bot.loc)
                    io.PREFIX = ""
        
        def move():
            for move in possible_commands:
                if loc_is_safe(self.me.loc + RDIRECTIONS[move], traps=False):
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
            
        # check if other bot in direct line of sight
        lnp = look_n_predict()
        if lnp: return lnp
                
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