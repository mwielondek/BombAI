class Board(object):
    def __init__(self, board):
        self.board = board

    def tile_at(self, loc):
        from const import TILE_OUT_OF_BOUNDS
        (x,y) = loc
        if((y >= 0) and (y < len(self.board)) and (x >= 0) and (x < len(self.board[y]))):
            return self.board[y][x]

        return TILE_OUT_OF_BOUNDS

    def is_floor(self, loc):
        from const import TILE_FLOOR
        return self.tile_at(loc) == TILE_FLOOR

class Location(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        
    def __repr__(self):
        return "(%s,%s)"%(self.x, self.y)
        
    def __add__(self, other):
        return Location(self.x+other.x, self.y+other.y)
        
    def __sub__(self, other):
        return Location(self.x-other.x, self.y-other.y)
        
    def __len__(self):
        return abs(self.x)+abs(self.y)
        
    def __neg__(self):
        return Location(-self.x,-self.y)
        
    def __getitem__(self, key):
        return [self.x, self.y][key]
        
    def __eq__(self, other):
        return (self.x,self.y) == (other.x,other.y)
        
    def __hash__(self):
        return hash((self.x,self.y))
        
class Positionable(object):
    def __init__(self, x, y):
        self.x = x
        self.y = y
        self.loc = Location(x,y)
    
    def __repr__(self):
        return "%s: %s"%(self.__class__.__name__, "(%s,%s)"%(self.x, self.y))