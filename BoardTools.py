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
    
    def __repr__(self):
        return "%s: %s"%(self.__class__.__name__, "(%s,%s)"%(self.x, self.y))
    
    def get_loc(self):
        return Location(self.x, self.y)