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
        # current_round = get_current_round()
        
        if not self.me.is_alive():
            log("Fatal Error: Dead :( ... fatal, haha, get it?")
            return "break"
            
        log("My position: %s"%self.me.loc)
        
        # get possible commands
        possible_commands = get_possible_moves(self.me.loc, board, bombs)
        log("Possible commands: %s"%possible_commands)
        
        ret = ''
        # Rule 1: defend your ass
        ret = self.defend(state, possible_commands)
        
        # Rule 2: if no need to defend, attack!
        if not ret:
            log("Attack mode activated. Prepare to die bitchez.")
            ret = self.attack(state, possible_commands)
        elif ret == "pass":
            log("Tried returning \"pass\". Why not see if we can attack meanwhile?")
            ret = self.attack(state, possible_commands)
        return ret if ret else "pass"
        
    def attack(self, state, possible_commands, force=False):
        # do no checks, just do it!
        if force:
            return BOMB_MIN_TICK
        
        (board, alive_players, bombs, previous_actions) = state
        if not (len(get_bombs_for_player(self.my_id, bombs)) < BOMB_MAX_PER_PLAYER):
            log("Cannot place more bombs.. :( Fuucking buullshit!")
            return
        
        # Check if other bots around
        for bot in (bot for bot in alive_players if bot.id != game.PLAYER_ID):
            l = abs(self.me.loc - bot)
            d = l.x + l.y
            if d > ATTACK_DISTANCE:
                log("Other bots too far away to be wasting bombs..")
                try:
                    prev_action = get_prev_action_for_player(self.my_id, previous_actions).action
                    possible_commands.remove((DIRECTIONS[-(RDIRECTIONS[prev_action])]))
                except:
                    pass
                ret = possible_commands.pop()
                if ret == "pass": ret = possible_commands.pop()
                return ret
        
        # Now place bomb, but first check if not kamikaze move
        mock_bombs = bombs[:]
        mock_state = (board, alive_players, mock_bombs, previous_actions)
        # pushing clock 1 tick ahead
        for bomb in mock_bombs:
            bomb.tick -= 1
        _backup = get_current_round()
        for bomb_tick in range(BOMB_MIN_TICK+5, BOMB_MAX_TICK+1, 10):
            mock_bombs.append(game.Bomb(self.my_id, self.me.loc.x, self.me.loc.y, bomb_tick))
            game.CURRENT_ROUND = game.Round(mock_state, 1337)
            best_move = get_best_move(self.me.loc, mock_state)
            log("** If I'd place a bomb -> best move: %s"%best_move)
        
            if best_move:
                log("Placing bomb with %s ticks"%bomb_tick)
                return bomb_tick
        
        game.CURRENT_ROUND = _backup
        log("Can't place bomb without killing myself.")
        return
        
        
    def defend(self, state, possible_commands):
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
        
            # else PANIC! Haha, jk. No but seriously, auto-destruct.
            log("No safe moves! Self-destruct sequence initiated...")
            return self.attack(0, 0, force=True)
        
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
                
            return
                
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