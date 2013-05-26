from const import *
from io import log
import game, io

def go_towards(loc1, loc2):
    delta = loc2 - loc1
    possible_moves = []
    if delta.x > 0:
        possible_moves.append("right")
    elif delta.x < 0:
        possible_moves.append("left")
    if delta.y > 0:
        possible_moves.append("down")
    elif delta.y < 0:
        possible_moves.append("up")
    if possible_moves:
        return possible_moves[0]
    return "pass"
    

def get_bombs_for_player(player_id, bombs):
    return [bomb for bomb in bombs if bomb.player_id == player_id]

def get_possible_moves(loc, board, bombs):
    ret = [DIRECTIONS[dloc] for dloc in DIRECTIONS.iterkeys()
                    if(board.is_floor(loc + dloc) and not bomb_at(loc + dloc, bombs))]
    # in case standing on a bomb, pass is still a valid move
    if "pass" not in ret: ret.insert(0, "pass")
    return ret

def bomb_at(loc, bombs):
    return find(lambda bomb: bomb.loc == loc and not bomb.ghost, bombs)
    
def line_of_sight(loc, board, bombs=None):
    res = []
    for delta in range(1,board.width-loc.x+1):
        newloc = loc+Location(delta,0)
        if board.is_floor(newloc):
            res.append(newloc)
        else: break
    for delta in range(1,loc.x+1):
        newloc = loc+Location(-delta,0)
        if board.is_floor(newloc):
            res.append(newloc)
        else: break
    for delta in range(1,board.height-loc.y+1):
        newloc = loc+Location(0,delta)
        if board.is_floor(newloc):
            res.append(newloc)
        else: break
    for delta in range(1,loc.y+1):
        newloc = loc+Location(0,-delta)
        if board.is_floor(newloc):
            res.append(newloc)
        else: break
    # somebody stepping on your shoes also counts
    res.append(loc)
    return res

def is_trap(loc, board, bombs):
    return len(get_possible_moves(loc, board, bombs)) <= 2

def get_player_with_id(player_id, players):
    return find(lambda player: player.id == player_id, players)
    
def get_me():
    return game.ME
    
def get_current_round():
    return game.CURRENT_ROUND

def find(pred, seq):
    return next((x for x in seq if pred(x)), None)

shortest = RECURSION_LIMIT
def get_best_move(loc, state, ticks=DEFAULT_TICKS, allow_pass=True):
    # reset shortest
    global shortest
    for b00l in [True, False]:
        shortest = RECURSION_LIMIT
        safelist = get_safe_move(loc, state, ticks=ticks, traps=b00l, allow_pass=allow_pass)
        if safelist: break

    if not safelist:
        return None
        
    best_moves = safelist[0]
    for moves in safelist[1:]:
        if len(moves) < len(best_moves):
            best_moves = moves       
    log("Best move strategy (%s ticks): %s"%(ticks,best_moves))
    if not b00l: log("It's a trap! ... but what else am I gonna do")
    # safelist is mutable, clear it!
    del safelist[:]
    return best_moves[0] if best_moves else None

def get_safe_move(loc, state, safelist=[], move_history=[], deep=0, ticks=DEFAULT_TICKS, traps=False, allow_pass=True):
    global shortest
    # break if found short(est) strategy
    if safelist and len(safelist[-1])<=2:
        return
    
    if deep < RECURSION_LIMIT:
        (board, players, bombs, previous_actions) = state
        
        possible_moves = get_possible_moves(loc, board, bombs)
        if deep == 0 and not allow_pass:
            possible_moves.remove("pass")

        for move in possible_moves:
            newloc = loc + RDIRECTIONS[move]
            # check if wont blow up in the first place..
            if not loc_is_safe(newloc, deep+1, False):
                continue
            move_history_branch = move_history[:]
            move_history_branch.append(move)
            if loc_is_safe(newloc, ticks, traps=traps):
                safelist.append(move_history_branch[:])
                shortest = min(len(move_history_branch),shortest)
                # doesnt get much shorter than this!
                if shortest <= 2: break
                # dont go deeper, Jack
                continue
            if len(move_history_branch) < shortest:
                get_safe_move(newloc, state, safelist, move_history_branch[:], deep+1, ticks, traps)

    return safelist
    
def loc_is_safe(loc, ticks=DEFAULT_TICKS, progressive=True, traps=False):
    r = get_current_round()
    board = r.state[0]
    main = loc not in r.get_blast_paths(ticks, progressive) and board.is_floor(loc)
    if not traps:
        return main
    (board, alive_players, bombs, previous_actions) = r.state
    return main and not is_trap(loc, board, bombs)

def AssureSafe(func):
    ''' Intelligent Safety Assurance System (I.S.A.S.)'''
    def wrapper(*args, **kwargs):
        ret = func(*args, **kwargs)
        me = get_me()
        state = args[1]
        bombs = state[2]
        if me.is_alive():
            if not check(ret, me, bombs):
                log("Wanted to return \""+ret+"\" - blocked by I.S.A.S.")
                io.PREFIX = "* "
                # try to find best move for 3,2,1 turns ahead
                for i in reversed(range(1,4)):
                    best_move = get_best_move(me.loc, args[1], ticks=i)
                    # bombs = args[1][2]
                    # log("Bombs ISAS %s"%bombs)
                    # for bomb in bombs:
                    #     log("Ticks %s"%bomb.tick)
                    if check(best_move, me, bombs):
                        log("Alternative best move (%s ticks): %s"%(i, best_move))
                        io.PREFIX = ""
                        return best_move
                log("No other option - prepare to die...")
                io.PREFIX = ""
        return ret
        
    def check(move, me, bombs):
        if not move: return False
        newloc = me.loc + RDIRECTIONS[move]
        no_bomb = not bomb_at(newloc, bombs)
        # if already standing on the bomb it doesnt matter
        if move == "pass": no_bomb = True
        return loc_is_safe(newloc, 1) and no_bomb
        
    return wrapper