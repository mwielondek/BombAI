from board import *
from const import DEFAULT_TICKS

CURRENT_ROUND = None
PLAYER_ID = -1
ME = None

class Player(Positionable):
    def __init__(self, id, x, y):
        self.id = id
        super(Player, self).__init__(x, y)
        
    def __eq__(self, other):
        return self.id == other.id
        
    def is_alive(self):
        return self in CURRENT_ROUND.state[1]
        
class Bomb(Positionable):
    def __init__(self, player_id, x, y, tick):
        self.player_id = player_id
        self.tick = tick
        self.ghost = False
        super(Bomb, self).__init__(x, y)
        
    def get_blast_wave(self, blast_range):
        wave = set()
        board = CURRENT_ROUND.state[0]
        for delta in range(blast_range+1):
            newloc = self.loc + Location(delta,0)
            wave.add(newloc)
            if not board.is_floor(newloc):
                break
        for delta in range(blast_range+1):
            newloc = self.loc + Location(-delta,0)
            wave.add(newloc)
            if not board.is_floor(newloc):
                break
        for delta in range(blast_range+1):
            newloc = self.loc + Location(0,delta)
            wave.add(newloc)
            if not board.is_floor(newloc):
                break
        for delta in range(blast_range+1):
            newloc = self.loc + Location(0,-delta)
            wave.add(newloc)
            if not board.is_floor(newloc):
                break
        return wave
        
    def __eq__(self, other):
        return (self.x,self.y) == (other.x,other.y)
        
    def __hash__(self):
        return hash((self.x,self.y))

class Action(object):
    def __init__(self, player_id, action_string):
        self.player_id = int(player_id)
        try:
            self.action = int(action_string)
            self.is_bomb = True
        except ValueError:
            self.action = action_string
            self.is_bomb = False
            
class Round(object):
    def __init__(self, state, nr):
        # (board, alive_players, bombs, previous_actions) = state
        self.state = state
        self.blast_paths = {}
        for n in range(1,DEFAULT_TICKS+1):
            self.get_blast_paths(n,False)
        
    def get_blast_paths(self, ticks=DEFAULT_TICKS, progressive=True):
        def calc():
            bombs = self.state[2]
            blast_paths = set()
            # if dupl. bombs
            multi = True if len(set(bombs)) != len(bombs) else False
            for bomb in bombs:
                # calc range
                count = [1,len([dupl for dupl in bombs if dupl == bomb])][multi]
                bomb.blast_range = 2 + count
                # account for chain reactions
                for other in bombs:
                    if other in bomb.get_blast_wave(bomb.blast_range):
                        other.tick = min(other.tick, bomb.tick)
            for bomb in set(bombs):
                # collect blast paths
                if bomb.tick == ticks:
                    blast_paths.update([blast for blast in bomb.get_blast_wave(bomb.blast_range)])
            return blast_paths
        
        def collect(ticks):
            l = set()
            try:
                _from, _to = ticks
            except TypeError:
                _from, _to = 1, ticks
            for n in range(_from,_to+1):
                l |= self.blast_paths[n]
            return l
        
        if progressive:
            if ticks == DEFAULT_TICKS:
                if "progDefault" not in self.blast_paths:                
                    self.blast_paths["progDefault"] = collect(DEFAULT_TICKS)
                return self.blast_paths["progDefault"]
            return collect(ticks)
            
        if ticks not in self.blast_paths:
            self.blast_paths[ticks] = calc()
        return self.blast_paths[ticks]