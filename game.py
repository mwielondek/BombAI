from board import *

class Player(Positionable):
    def __init__(self, id, x, y):
        self.id = id
        super(Player, self).__init__(x, y)
        
class Bomb(Positionable):
    def __init__(self, player_id, x, y, tick):
        self.player_id = player_id
        self.tick = tick
        super(Bomb, self).__init__(x, y)
        
    def get_blast_wave(self, blast_range):
        wave = set()
        for delta in range(blast_range+1):
            for d in [delta,-delta]:
                wave.add(self.loc + Location(d,0))
                wave.add(self.loc + Location(0,d))      
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