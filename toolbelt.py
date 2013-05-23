from const import *
from io import log
import game

def get_bombs_for_player(player_id, bombs):
    return [bomb for bomb in bombs if bomb.player_id == player_id]

def get_possible_moves(loc, board, bombs):
    ret = [DIRECTIONS[dloc] for dloc in DIRECTIONS.iterkeys()
                    if(board.is_floor(loc + dloc) and not bomb_at(loc + dloc, bombs))]
    # in case standing on a bomb, pass is still a valid move
    if "pass" not in ret: ret.insert(0, "pass")
    return ret

def bomb_at(loc, bombs):
    return find(lambda bomb: bomb.loc == loc, bombs)
    
def get_best_move(player, state, ticks=25):
    safelist = get_safe_move(player.loc, state, ticks=ticks)
    
    if not safelist:
        return None
    best_moves = safelist[0]
    for moves in safelist[1:]:
        if len(moves) < len(best_moves):
            best_moves = moves       
    # safelist is mutable, clear it!
    del safelist[:]
    # log("Best moves (%s ticks): %s"%(ticks,best_moves))
    return best_moves[0] if best_moves else None

def get_safe_move(loc, state, safelist=[], move_history=[], deep=0, ticks=25):
    if deep < RECURSION_LIMIT:
        (board, players, bombs, previous_actions) = state
        possible_moves = get_possible_moves(loc, board, bombs)
        if move_history:
            try:
                prev_move = move_history[-1]
                possible_moves.remove(DIRECTIONS[-(RDIRECTIONS[prev_move])])
            except ValueError:
                pass
        for move in possible_moves:
            if deep > 0:
                if move == "pass": continue
            move_history_branch = move_history[:]
            move_history_branch.append(move)
            newloc = loc + RDIRECTIONS[move]
            if loc_is_safe(newloc, ticks):
                safelist.append(move_history_branch)
                # dont look any further if found quick route
                if len(move_history_branch) <= 2:
                    break
            # log("Deep: %s - calling get safe now with move history:\n %s"%(deep,move_history_branch))
            get_safe_move(newloc, state, safelist, move_history_branch[:], deep+1)
    
    return safelist
        
def loc_is_safe(loc, ticks=25):
    return not loc in get_current_round().get_blast_paths(ticks)

def get_player_with_id(player_id, players):
    return find(lambda player: player.id == player_id, players)
    
def get_me():
    return game.ME
    
def get_current_round():
    return game.CURRENT_ROUND

def find(pred, seq):
    return next((x for x in seq if pred(x)), None)
    
def AssureSafe(func):
    ''' Intelligent Safety Assurance System (I.S.A.S.)'''
    def wrapper(*args):
        ret = func(*args)
        me = get_me()
        if me.is_alive():
            if not check(ret, me):
                log("Wanted to return \""+ret+"\" - blocked by I.S.A.S.")
                # try to find best move for 3,2,1 turns ahead
                for i in reversed(range(1,4)):
                    best_move = get_best_move(me, args[1], ticks=i)
                    if check(best_move, me):
                        log("Alternative best move (%s ticks): %s"%(i, best_move))
                        return best_move
                log("No other option - prepare to die...")
        return ret
        
    def check(move, me):
        try:
            return loc_is_safe(me.loc + RDIRECTIONS[move], 1)
        except KeyError:
            return False
        
    return wrapper