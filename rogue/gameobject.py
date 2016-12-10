class GameObject:
    # this is a generic object: the player, a monster, an item, the stairs...
    # it's always represented by a character on screen.
    def __init__(self, x, y, char, color, con):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.con = con

    def move(self, dx, dy, current_map):
        # move by the given amount
        if (not current_map[self.x + dx][self.y + dy].blocked):
            self.x += dx
            self.y += dy

    def draw(self):
        # draw the character that represents this object at its position
        self.con.draw_char(self.x, self.y, self.char, self.color)

    def clear(self):
        # erase the character that represents this object
        self.con.draw_char(self.x, self.y, ' ', self.color, bg=None)
