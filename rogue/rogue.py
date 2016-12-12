import tdl
import colors
from gameobject import GameObject, Fighter
from maps import Map

SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
LIMIT_FPS = 20

FOV_ALGO = 'BASIC'  # default FOV algorithm
FOV_LIGHT_WALLS = True
TORCH_RADIUS = 10

COLOR_DARK_WALL = (0, 0, 100)
COLOR_LIGHT_WALL = (130, 110, 50)
COLOR_DARK_GROUND = (50, 50, 150)
COLOR_LIGHT_GROUND = (200, 180, 50)

root = tdl.init(SCREEN_WIDTH, SCREEN_HEIGHT, title="Roguelike", fullscreen=False)
fov_recompute = True
game_state = 'playing'


def handle_keys(player, current_map, objects):
    global fov_recompute
    user_input = tdl.event.key_wait()

    if user_input.key == 'ENTER' and user_input.alt:
        # Alt+Enter: toggle fullscreen
        tdl.set_fullscreen(True)
    elif user_input.key == 'ESCAPE':
        return 'exit'# exit game

    if game_state == 'playing':
        # movement keys
        if user_input.key == 'UP':
            fov_recompute = player.move_or_attack(0, -1, current_map, objects)
        elif user_input.key == 'DOWN':
            fov_recompute = player.move_or_attack(0, 1, current_map, objects)
        elif user_input.key == 'LEFT':
            fov_recompute = player.move_or_attack(-1, 0, current_map, objects)
        elif user_input.key == 'RIGHT':
            fov_recompute = player.move_or_attack(1, 0, current_map, objects)
    else:
        return 'didnt-take-turn'


def render_all(console, current_map, objects):
    global fov_recompute
    if fov_recompute:
        fov_recompute = False
        visible_tiles = tdl.map.quickFOV(objects[0].x, objects[0].y,
                                         current_map.is_visible_tile,
                                         fov=FOV_ALGO,
                                         radius=TORCH_RADIUS,
                                         lightWalls=FOV_LIGHT_WALLS)
        # go through all tiles, and set their background color
        for y in range(current_map.height):
            for x in range(current_map.width):
                visible = (x, y) in visible_tiles
                wall = current_map[x][y].block_sight
                if not visible:
                    # it's out of the player's FOV
                    if current_map[x][y].explored:
                        if wall:
                            console.draw_char(x, y, None, fg=None, bg=COLOR_DARK_WALL)
                        else:
                            console.draw_char(x, y, None, fg=None, bg=COLOR_DARK_GROUND)
                else:
                    if wall:
                        console.draw_char(x, y, None, fg=None, bg=COLOR_LIGHT_WALL)
                    else:
                        console.draw_char(x, y, None, fg=None, bg=COLOR_LIGHT_GROUND)
                    # visible tiles are explored
                    current_map[x][y].explored = True

    # draw all objects in the list
    for obj in objects:
        obj.draw(console)

    # player stats
    console.draw_str(1, SCREEN_HEIGHT -2, 'HP: ' + str(objects[0].fighter.hp) + '/' +
                     str(objects[0].fighter.max_hp) + ' ')

    # blit the contents of "con" to the root console and present it
    root.blit(console, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0)


def main():
    tdl.set_font('resources/arial10x10.png', greyscale=True, altLayout=True)
    tdl.setFPS(LIMIT_FPS)
    con = tdl.Console(SCREEN_WIDTH, SCREEN_HEIGHT)

    fighter_component = Fighter(hp=30, defense=2, power=5)
    player = GameObject(SCREEN_WIDTH//2, SCREEN_HEIGHT//2, '@', "player", colors.white, blocks=True, fighter=fighter_component)
    objects = [player]
    start_map = Map(45, 80)
    start_map.populate(objects)
    player.x = start_map.spawn_x
    player.y = start_map.spawn_y
    player_action = None

    while not tdl.event.is_window_closed():
        # draw all objects in the list
        render_all(con, start_map, objects)

        tdl.flush()

        # erase all objects at their old locations, before they move
        for object in objects:
            object.clear(con)

        # handle keys and exit game if needed
        player_action = handle_keys(player, start_map, objects)
        if game_state == 'playing' and player_action != 'didnt-take-turn':
            for obj in objects:
                if obj != player:
                    obj.ai.take_turn(player, start_map.is_visible_tile(obj.x, obj.y), start_map, objects)
        if player_action == 'exit':
            break

if __name__ == "__main__":
    main()
