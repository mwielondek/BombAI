from board import *

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
        
    def get_blast_paths(self, ticks=25):
        if ticks not in self.blast_paths:
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
                if bomb.tick <= ticks:
                    blast_paths.update([blast for blast in bomb.get_blast_wave(bomb.blast_range)])
            self.blast_paths[ticks] = blast_paths
        return self.blast_paths[ticks]