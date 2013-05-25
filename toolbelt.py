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
    
def loc_is_safe(loc, ticks=25, progressive=True):
    return loc not in get_current_round().get_blast_paths(ticks, progressive)

def get_player_with_id(player_id, players):
    return find(lambda player: player.id == player_id, players)
    
def get_me():
    return game.ME
    
def get_current_round():
    return game.CURRENT_ROUND

def find(pred, seq):
    return next((x for x in seq if pred(x)), None)    

shortest = RECURSION_LIMIT    
def get_best_move(player, state, ticks=25):
    # reset shortest
    global shortest
    shortest = RECURSION_LIMIT
    safelist = get_safe_move(player.loc, state, ticks=ticks)

    if not safelist:
        return None
        
    best_moves = safelist[0]
    for moves in safelist[1:]:
        if len(moves) < len(best_moves):
            best_moves = moves       
    log("Best moves (%s ticks): %s"%(ticks,best_moves))
    # safelist is mutable, clear it!
    del safelist[:]
    return best_moves[0] if best_moves else None

def get_safe_move(loc, state, safelist=[], move_history=[], deep=0, ticks=25):
    global shortest
    # break if found short(est) strategy
    if safelist and len(safelist[-1])<=2:
        return
    
    if deep < RECURSION_LIMIT:
        (board, players, bombs, previous_actions) = state
        
        possible_moves = get_possible_moves(loc, board, bombs)

        for move in possible_moves:
            newloc = loc + RDIRECTIONS[move]
            # check if wont blow up in the first place..
            if not loc_is_safe(newloc, deep+1, False):
                continue
            move_history_branch = move_history[:]
            move_history_branch.append(move)
            if loc_is_safe(newloc, ticks):
                log("mhb %s"%move_history_branch)
                safelist.append(move_history_branch[:])
                shortest = min(len(move_history_branch),shortest)
                # doesnt get much shorter than this!
                if shortest <= 2: break
                # dont go deeper, Jack
                continue
            if len(move_history_branch) < shortest:
                get_safe_move(newloc, state, safelist, move_history_branch[:], deep+1)
    
    return safelist

def AssureSafe(func):
    ''' Intelligent Safety Assurance System (I.S.A.S.)'''
    def wrapper(*args, **kwargs):
        ret = func(*args, **kwargs)
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