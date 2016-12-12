from random import randint
from gameobject import GameObject
import colors

ROOM_MAX_SIZE = 10
ROOM_MIN_SIZE = 6
MAX_ROOMS = 30
MAX_ROOM_MONSTERS = 3


class Tile:
    # a tile of the map and its properties
    def __init__(self, blocked, block_sight=None):
        self.blocked = blocked
        self.explored = False

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

    def center(self):
        center_x = (self.x1 + self.x2) // 2
        center_y = (self.y1 + self.y2) // 2
        return (center_x, center_y)

    def intersect(self, other):
        # returns true if this rectangle intersects with another one
        return (self.x1 <= other.x2 and self.x2 >= other.x1 and
                self.y1 <= other.y2 and self.y2 >= other.y1)


class Map(list):

    def __init__(self, height, width):
        list.__init__(self, [[Tile(True) for y in range(height)] for x in range(width)])
        self.width = width
        self.height = height
        self.rooms = []
        self.create_standard_map()

    def create_room(self, room):
        # go through the tiles in the rectangle and make them passable
        for x in range(room.x1 + 1, room.x2):
            for y in range(room.y1 + 1, room.y2):
                self[x][y].blocked = False
                self[x][y].block_sight = False

    def create_standard_map(self):
        num_rooms = 0

        for r in range(MAX_ROOMS):
            # random width and height
            w = randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)
            h = randint(ROOM_MIN_SIZE, ROOM_MAX_SIZE)
            # random position without going out of the boundaries of the map
            x = randint(0, self.width-w-1)
            y = randint(0, self.height-h-1)

            # "Rect" class makes rectangles easier to work with
            new_room = Rect(x, y, w, h)

            # run through the other rooms and see if they intersect with this one
            failed = False
            for other_room in self.rooms:
                if new_room.intersect(other_room):
                    failed = True
                    break

            if not failed:
                # this means there are no intersections, so this room is valid

                # "paint" it to the map's tiles
                self.create_room(new_room)

                # center coordinates of new room, will be useful later
                (new_x, new_y) = new_room.center()

                if num_rooms == 0:
                    # this is the first room, where the player starts at
                    self.spawn_x = new_x
                    self.spawn_y = new_y

                else:
                    # all rooms after the first:
                    # connect it to the previous room with a tunnel

                    # center coordinates of previous room
                    (prev_x, prev_y) = self.rooms[num_rooms-1].center()

                    # draw a coin (random number that is either 0 or 1)
                    if randint(0, 1):
                        # first move horizontally, then vertically
                        self.create_h_tunnel(prev_x, new_x, prev_y)
                        self.create_v_tunnel(prev_y, new_y, new_x)
                    else:
                        # first move vertically, then horizontally
                        self.create_v_tunnel(prev_y, new_y, prev_x)
                        self.create_h_tunnel(prev_x, new_x, new_y)

                # finally, append the new room to the list
                self.rooms.append(new_room)
                num_rooms += 1

    def create_h_tunnel(self, x1, x2, y):
        for x in range(min(x1, x2), max(x1, x2) + 1):
            self[x][y].blocked = False
            self[x][y].block_sight = False

    def create_v_tunnel(self, y1, y2, x):
        # vertical tunnel
        for y in range(min(y1, y2), max(y1, y2) + 1):
            self[x][y].blocked = False
            self[x][y].block_sight = False

    def is_visible_tile(self, x, y):
        if x >= self.width or x < 0:
            return False
        elif y >= self.height or y < 0:
            return False
        elif self[x][y].blocked:
            return False
        elif self[x][y].block_sight:
            return False
        else:
            return True

    def populate(self,objects):
        for room in self.rooms:
            num_monsters = randint(0, MAX_ROOM_MONSTERS)
            for i in range(num_monsters):
                # choose random spot for this monster
                x = randint(room.x1+1, room.x2-1)
                y = randint(room.y1+1, room.y2-1)

                if not self.is_blocked(x, y, objects):
                    if randint(0, 100) < 80:  #80% chance of getting an orc
                        # create an orc
                        monster = GameObject(x, y, 'o', "orc", colors.desaturated_green, blocks=True)
                    else:
                        # create a troll
                        monster = GameObject(x, y, 'T', "troll", colors.darker_green, blocks=True)

                    objects.append(monster)

    def is_blocked(self, x, y, objects):
        # first test the map tile
        if self[x][y].blocked:
            return True

        # now check for any blocking objects
        for obj in objects:
            if obj.blocks and obj.x == x and obj.y == y:
                return True

        return False

