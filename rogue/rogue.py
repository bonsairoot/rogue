import tdl
import colors
import config
from gameobject import GameObject, Fighter, player_death
from maps import Map

SCREEN_WIDTH = 80
SCREEN_HEIGHT = 50

MAP_WIDTH = 80
MAP_HEIGHT = 43

LIMIT_FPS = 20
BAR_WIDTH = 20
PANEL_HEIGHT = 7
PANEL_Y = SCREEN_HEIGHT - PANEL_HEIGHT
MSG_X = BAR_WIDTH + 2

FOV_ALGO = 'BASIC'  # default FOV algorithm
FOV_LIGHT_WALLS = True
TORCH_RADIUS = 10

COLOR_DARK_WALL = (0, 0, 100)
COLOR_LIGHT_WALL = (130, 110, 50)
COLOR_DARK_GROUND = (50, 50, 150)
COLOR_LIGHT_GROUND = (200, 180, 50)

tdl.set_font('resources/arial10x10.png', greyscale=True, altLayout=True)
root = tdl.init(SCREEN_WIDTH, SCREEN_HEIGHT, title="Roguelike", fullscreen=False)
tdl.setFPS(LIMIT_FPS)
console = tdl.Console(MAP_WIDTH, MAP_HEIGHT)
panel = tdl.Console(SCREEN_WIDTH, PANEL_HEIGHT)
fov_recompute = True
mouse_coord = (0,0)

def handle_keys(player, current_map, objects):
    global fov_recompute
    global mouse_coord

    keypress = False
    for event in tdl.event.get():
        if event.type == 'KEYDOWN':
            user_input = event
            keypress = True
        if event.type == 'MOUSEMOTION':
            mouse_coord = event.cell

    if not keypress:
        return 'didnt-take-turn'

    if user_input.key == 'ENTER' and user_input.alt:
        # Alt+Enter: toggle fullscreen
        tdl.set_fullscreen(True)
    elif user_input.key == 'ESCAPE':
        return 'exit'# exit game

    if config.game_state == 'playing':
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

def render_bar(x, y, total_width, name, value, maximum, bar_color, back_color):
    #render a bar (HP, experience, etc). first calculate the width of the bar
    bar_width = int(float(value) / maximum * total_width)

    #render the background first
    panel.draw_rect(x, y, total_width, 1, None, bg=back_color)

    #now render the bar on top
    if bar_width > 0:
        panel.draw_rect(x, y, bar_width, 1, None, bg=bar_color)

    #finally, some centered text with the values
    text = name + ': ' + str(value) + '/' + str(maximum)
    x_centered = x + (total_width-len(text))//2
    panel.draw_str(x_centered, y, text, fg=colors.white, bg=None)

def render_all(current_map, objects, player):
    global visible_tiles
    global fov_recompute
    if fov_recompute:
        fov_recompute = False
        visible_tiles = tdl.map.quickFOV(player.x, player.y,
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
        if obj != player:
            obj.draw(console, visible_tiles)
    player.draw(console, visible_tiles)
    root.blit(console, 0, 0, MAP_WIDTH, MAP_HEIGHT, 0, 0)


    #prepare to render the GUI panel
    panel.clear(fg=colors.white, bg=colors.black)

    #print the game messages, one line at a time
    y = 1
    for (line, color) in config.game_msgs:
        panel.draw_str(MSG_X, y, line, bg=None, fg=color)
        y += 1

    #show the player's stats
    render_bar(1, 1, BAR_WIDTH, 'HP', player.fighter.hp, player.fighter.max_hp,
        colors.light_red, colors.darker_red)

    # display names of objects under the mouse
    panel.draw_str(1, 0, get_names_under_mouse(objects), bg=None, fg=colors.light_gray)

    #blit the contents of "panel" to the root console
    root.blit(panel, 0, PANEL_Y, SCREEN_WIDTH, PANEL_HEIGHT, 0, 0)

def get_names_under_mouse(objects):

    #return a string with the names of all objects under the mouse
    (x, y) = mouse_coord

    #create a list with the names of all objects at the mouse's coordinates and in FOV
    names = [obj.name for obj in objects
        if obj.x == x and obj.y == y and (obj.x, obj.y) in visible_tiles]

    names = ', '.join(names)  #join the names, separated by commas
    return names.capitalize()

def init():
    config.MSG_WIDTH = SCREEN_WIDTH - BAR_WIDTH - 2
    config.MSG_HEIGHT = PANEL_HEIGHT - 1
    #a warm welcoming message!
    config.message('Welcome stranger! Prepare to perish in the Tombs of the Ancient Kings.', colors.red)

def main():
    init()
    fighter_component = Fighter(hp=30, defense=2, power=5, death_function=player_death)
    player = GameObject(SCREEN_WIDTH//2, SCREEN_HEIGHT//2, '@', "player", colors.white, blocks=True,
                        fighter=fighter_component)
    objects = [player]
    start_map = Map(MAP_HEIGHT, MAP_WIDTH)
    start_map.populate(objects)
    player.x = start_map.spawn_x
    player.y = start_map.spawn_y
    player_action = None

    while not tdl.event.is_window_closed():
        # draw all objects in the list
        render_all(start_map, objects, player)

        tdl.flush()

        # erase all objects at their old locations, before they move
        for obj in objects:
            obj.clear(console)

        # handle keys and exit game if needed
        player_action = handle_keys(player, start_map, objects)
        if config.game_state == 'playing' and player_action != 'didnt-take-turn':
            for obj in objects:
                if obj.ai:
                    obj.ai.take_turn(player, visible_tiles, start_map, objects)
        if player_action == 'exit':
            break

if __name__ == "__main__":
    main()
