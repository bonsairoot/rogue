class Tile:
    #a tile of the map and its properties
    def __init__(self, blocked, block_sight = None):
        self.blocked = blocked

        #by default, if a tile is blocked, it also blocks sight
        if block_sight is None: block_sight = blocked
        self.block_sight = block_sight

def make_map(height,width):
    #fill map with "unblocked" tiles
    my_map = [[Tile(False) for y in range(height)] for x in range(width)]

    #place two pillars to test the map
    my_map[30][22].blocked = True
    my_map[30][22].block_sight = True
    my_map[50][22].blocked = True
    my_map[50][22].block_sight = True

    return my_map
