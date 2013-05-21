from const import *
from io import log

def get_bombs_for_player(player_id, bombs):
    return [bomb for bomb in bombs if bomb.player_id == player_id]

def get_possible_moves(loc, board, bombs):
    return [DIRECTIONS[dloc] for dloc in DIRECTIONS.iterkeys()
                if(board.is_floor(loc + dloc) and not bomb_at(loc + dloc, bombs))]

def bomb_at(loc, bombs):
    return find(lambda bomb: bomb.loc == loc, bombs)
    
# def get_free_tiles(board, bombs):
#     tiles = set()
#     for y,row in enumerate(board.board):
#         for x,_ in enumerate(row):
#             loc = Location(x,y)
#             if(board.is_floor(loc) and not bomb_at(loc, bombs)):
#                 tiles.add(loc)
#     
#     return tiles
#     
# def get_closest(x, list):
#     closest = None
#     for loc in list:
#         log(len(x-loc))
#     return closest
    
def get_best_move(player, board, bombs, blast_paths):
    pc = get_possible_moves(player.loc, board, bombs)
    safelist = get_safe_move((board, bombs, blast_paths), player.loc, pc)
    log(safelist)
    
    if not safelist:
        return None
        
    best_move = safelist[0]
    for moves in safelist:
        if len(moves) < len(best_move):
            best_move = moves
    del safelist[:]
    return best_move

def get_safe_move(comp, loc, possible_moves, safelist=[], move_history=[], deep=0):
    if deep < 7:
        (board, bombs, blast_paths) = comp
        for move in possible_moves:
            move_history_branch = move_history[:]
            newloc = loc + RDIRECTIONS[move]
            move_history_branch.append(move)
            if loc_is_safe(newloc, blast_paths):
                log("Appending safelist with %s"%move_history_branch)
                safelist.append(move_history_branch)
                if len(move_history_branch) <= 2:
                    log("breaking")
                    break
            pc = get_possible_moves(newloc, board, bombs)
            try:
                pc.remove(DIRECTIONS[-(RDIRECTIONS[move])])
            except ValueError:
                pass
            log("Deep: %s - calling get safe now with move history:\n %s"%(deep,move_history_branch))
            get_safe_move(comp, newloc, pc, safelist, move_history_branch, deep+1)
    
    return safelist
        
def loc_is_safe(loc, blast_paths):
    return not loc in blast_paths

def get_player_with_id(player_id, players):
    return find(lambda player: player.id == player_id, players)

def find(pred, seq):
    return next((x for x in seq if pred(x)), None)