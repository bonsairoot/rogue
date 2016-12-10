import tdl
from gameobject import GameObject
from maps import Map

SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50
LIMIT_FPS = 20


FOV_ALGO = 'BASIC'  # default FOV algorithm
FOV_LIGHT_WALLS = True
TORCH_RADIUS = 10

root = tdl.init(SCREEN_WIDTH, SCREEN_HEIGHT, title="Roguelike", fullscreen=False)
fov_recompute = True


def handle_keys(player, current_map):
    global fov_recompute
    user_input = tdl.event.key_wait()

    if user_input.key == 'ENTER' and user_input.alt:
        # Alt+Enter: toggle fullscreen
        tdl.set_fullscreen(True)
    elif user_input.key == 'ESCAPE':
        return True  # exit game

    # movement keys
    if user_input.key == 'UP':
        player.move(0, -1, current_map)
        fov_recompute = True
    elif user_input.key == 'DOWN':
        player.move(0, 1, current_map)
        fov_recompute = True
    elif user_input.key == 'LEFT':
        player.move(-1, 0, current_map)
        fov_recompute = True
    elif user_input.key == 'RIGHT':
        player.move(1, 0, current_map)
        fov_recompute = True


def render_all(console, current_map, objects):
    global fov_recompute
    color_dark_wall = (0, 0, 100)
    color_light_wall = (130, 110, 50)
    color_dark_ground = (50, 50, 150)
    color_light_ground = (200, 180, 50)
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
                    if wall:
                        console.draw_char(x, y, None, fg=None, bg=color_dark_wall)
                    else:
                        console.draw_char(x, y, None, fg=None, bg=color_dark_ground)
                else:
                    if wall:
                        console.draw_char(x, y, None, fg=None, bg=color_light_wall)
                    else:
                        console.draw_char(x, y, None, fg=None, bg=color_light_ground)

    # draw all objects in the list
    for obj in objects:
        obj.draw()

    # blit the contents of "con" to the root console and present it
    root.blit(console, 0, 0, SCREEN_WIDTH, SCREEN_HEIGHT, 0, 0)


def main():
    tdl.set_font('resources/prestige12x12_gs_tc.png', greyscale=True, altLayout=True)
    tdl.setFPS(LIMIT_FPS)
    con = tdl.Console(SCREEN_WIDTH, SCREEN_HEIGHT)

    player = GameObject(SCREEN_WIDTH//2, SCREEN_HEIGHT//2, '@', (255, 255, 255), con)
    npc = GameObject(SCREEN_WIDTH//2 - 5, SCREEN_HEIGHT//2, '@', (255, 255, 0), con)
    objects = [player, npc]
    start_map = Map(45, 80)
    player.x = start_map.spawn_x
    player.y = start_map.spawn_y

    while not tdl.event.is_window_closed():
        # draw all objects in the list
        render_all(con, start_map, objects)

        tdl.flush()

        # erase all objects at their old locations, before they move
        for object in objects:
            object.clear()

        # handle keys and exit game if needed
        exit_game = handle_keys(player, start_map)
        if exit_game:
            break

if __name__ == "__main__":
    main()
