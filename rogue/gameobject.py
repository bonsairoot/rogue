import math
import colors
import config
from config import message


objects = []
inventory = []


def init(player_spawn_x, player_spawn_y):
    global objects
    fighter_component = Fighter(hp=30, defense=2, power=5,
                                           death_function=player_death)
    player = GameObject(player_spawn_x, player_spawn_y, '@', "player",
                                   colors.white, blocks=True, fighter=fighter_component)
    objects = ObjectList(player)


class ObjectList(list):
    def __init__(self,player):
        list.__init__(self,[player])
        self.player = player


class GameObject:
    # this is a generic object: the player, a monster, an item, the stairs...
    # it's always represented by a character on screen.
    def __init__(self, x, y, char, name, color, blocks=False, fighter=None, ai=None, item=None):
        self.x = x
        self.y = y
        self.char = char
        self.color = color
        self.name = name
        self.blocks = blocks
        self.fighter = fighter
        if self.fighter:
            self.fighter.owner = self
        self.ai = ai
        if self.ai:
            self.ai.owner = self
        self.item = item
        if self.item:
            self.item.owner = self

    def move(self, dx, dy, current_map):
        # move by the given amount
        if (not current_map.is_blocked(self.x + dx, self.y + dy, objects)):
            self.x += dx
            self.y += dy
            return True

        return False

    def move_towards(self, target_x, target_y, current_map):
        dx = target_x - self.x
        dy = target_y - self.y
        distance = math.sqrt(dx ** 2 + dy ** 2)

        # normalize it to length 1 (preserving direction), then round it and
        # convert to int so the movement is restricted to the map grid

        dx = int(round(dx / distance))
        dy = int(round(dy / distance))
        self.move(dx, dy, current_map)

    def distance_to(self, other):
        dx = other.x - self.x
        dy = other.y - self.y
        return math.sqrt(dx ** 2 + dy ** 2)

    def move_or_attack(self, dx, dy, current_map):
        # the coordinates the player is moving to/attacking
        x = self.x + dx
        y = self.y + dy

        # try to find an attackable object there
        target = None
        for obj in objects:
            if obj.fighter and obj.x == x and obj.y == y:
                target = obj
                break

        # attack if target found, move otherwise
        if target is not None:
            self.fighter.attack(target)
        else:
            return self.move(dx, dy, current_map)

        return False

    def draw(self, con, visible_tiles):
        # draw the character that represents this object at its position
        if (self.x, self.y) in visible_tiles:
            con.draw_char(self.x, self.y, self.char, self.color, bg=None)

    def clear(self, con):
        # erase the character that represents this object
        con.draw_char(self.x, self.y, ' ', self.color, bg=None)

    def send_to_back(self):
        global objects
        objects.remove(self)
        objects.insert(0, self)


class Fighter:
    def __init__(self, hp, defense, power, death_function=None):
        self.max_hp = hp
        self.hp = hp
        self.defense = defense
        self.power = power
        self.death_function = death_function

    def take_damage(self, damage):
        if damage > 0:
            self.hp -= damage
        if self.hp <= 0:
            function = self.death_function
            if function is not None:
                function(self.owner)

    def attack(self, target):
        damage = self.power - target.fighter.defense

        if damage > 0:
            message(self.owner.name.capitalize() + ' attacks ' +
                    target.name + ' for ' + str(damage) + ' hit points.')
            target.fighter.take_damage(damage)
        else:
            message(self.owner.name.capitalize() + ' attacks ' +
                    target.name + ' but it has no effect!')

    def heal(self, amount):
        self.hp += amount
        if self.hp > self.max_hp:
            self.hp = self.max_hp

class BasicMonster:
    # AI for a basic monster.
    def take_turn(self, visible_tiles, current_map):
        monster = self.owner
        if (monster.x, monster.y) in visible_tiles:
            # move towars the player
            if monster.distance_to(objects.player) >= 2:
                monster.move_towards(objects.player.x, objects.player.y, current_map)

            # in attack range
            elif objects.player.fighter.hp > 0:
                monster.fighter.attack(objects.player)


def monster_death(monster):
    # transform it into a nasty corpse! it doesn't block, can't be
    # attacked and doesn't move
    message(monster.name.capitalize() + ' is dead!', colors.orange)
    monster.char = '%'
    monster.color = colors.dark_red
    monster.blocks = False
    monster.fighter = None
    monster.ai = None
    monster.name = 'remains of ' + monster.name
    monster.send_to_back()


def player_death(player):
    # the game ended!
    message('You died!', colors.red)
    config.game_state = 'dead'

    # for added effect, transform the player into a corpse!
    player.char = '%'
    player.color = colors.dark_red


class Item:
    def __init__(self, use_function=None):
        self.use_function = use_function

    # an item that can be picked up and used
    def pick_up(self):
        # add to the inventory and remove from the map
        if len(inventory) > 25:
            message('Your inventory is full, cannot pick up ' + self.owner.name + '.', colors.red)
        else:
            inventory.append(self.owner)
            objects.remove(self.owner)
            message('You picked up a ' + self.owner.name + '!', colors.green)

    def use(self):
        if self.use_function is None:
            message('The ' + self.owner.name + ' cannot be used.')
        else:
            if self.use_function() != 'cancelled':
                inventory.remove(self.owner)  # destroy after use, unless it was cancelled


def cast_heal():
    if objects.player.fighter.hp == objects.player.fighter.max_hp:
        message('You are already at full health.', colors.red)
        return 'cancelled'

    message('Your wounds start to feel better!', colors.light_violet)
    objects.player.fighter.heal(4)
