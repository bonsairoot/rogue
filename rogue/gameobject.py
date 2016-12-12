class GameObject:
    # this is a generic object: the player, a monster, an item, the stairs...
    # it's always represented by a character on screen.
    def __init__(self, x, y, char, name, color, blocks=False):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks = blocks

    def move(self, dx, dy, current_map, objects):
        # move by the given amount
        if (not current_map.is_blocked(self.x + dx, self.y + dy, objects)):
            self.x += dx
            self.y += dy
            return True

        return False

    def move_or_attack(self, dx, dy, current_map, objects):
        # the coordinates the player is moving to/attacking
        x = self.x + dx
        y = self.y + dy

        # try to find an attackable object there
        target = None
        for obj in objects:
            if obj.x == x and obj.y == y:
                target = obj
                break

        # attack if target found, move otherwise
        if target is not None:
            print('The ' + target.name + ' laughs at your puny efforts to attack him!')
        else:
            return self.move(dx, dy, current_map, objects)

        return False

    def draw(self,con):
        # draw the character that represents this object at its position
        con.draw_char(self.x, self.y, self.char, self.color)

    def clear(self,con):
        # erase the character that represents this object
        con.draw_char(self.x, self.y, ' ', self.color, bg=None)
