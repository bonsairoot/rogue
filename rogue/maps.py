class Tile:
    # a tile of the map and its properties
    def __init__(self, blocked, block_sight=None):
        self.blocked = blocked

        # by default, if a tile is blocked, it also blocks sight
        if block_sight is None:
            block_sight = blocked
        self.block_sight = block_sight


class Rect:
    # a rectangle on the map. used to characterize a room.
    def __init__(self, x, y, w, h):
        self.x1 = x
        self.y1 = y
        self.x2 = x + w
        self.y2 = y + h


class Map(list):

    def __init__(self, height, width):
        list.__init__(self, [[Tile(True) for y in range(height)] for x in range(width)])
        self.create_standard_map()

    def create_room(self, room):
        # go through the tiles in the rectangle and make them passable
        for x in range(room.x1 + 1, room.x2):
            for y in range(room.y1 + 1, room.y2):
                self[x][y].blocked = False
                self[x][y].block_sight = False

    def create_standard_map(self):
        # create two rooms
        room1 = Rect(20, 15, 10, 15)
        room2 = Rect(50, 15, 10, 15)
        self.create_room(room1)
        self.create_room(room2)

        self.spawn_x = 25
        self.spawn_y = 23
