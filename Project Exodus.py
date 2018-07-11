from enum import Enum, IntEnum
from consts import *
import sys
import time
import random
import os
import copy
import json
import tkinter.messagebox
import pygame
import vlc


class GameState(Enum):
    NULL = 1,
    INITIAL = 2
    FINISHER = 3


class PlayerState(Enum):
    IDLE = 1
    WALKING = 2
    HADOUKEN = 3
    PROJECTILE = 4
    PROJECTILE_COMP = 5
    PUNCH = 6
    KICK = 7


class ENLIFE(IntEnum):
    FULL = 1
    THREE_FOUR = 2
    HALF = 3
    DEAD = 4
    FULL_RECT = 5
    THREE_FOUR_RECT = 6
    HALF_RECT = 7
    DEAD_RECT = 8


class Logger:
    def __init__(self, filename):
        self.file_handler = open(filename, 'w', encoding="utf8")

    def log(self, desc, *args):
        if DEBUGGING_MOD:
            self.file_handler.write("{0}".format(desc + ' ' + (''.join(repr(args)) if args else '') + '\n'))

    def exit(self):
        self.file_handler.close()


class Player:
    def __init__(self, playerName):
        self.state = PlayerState.IDLE
        self.projectiles = []
        self.playerName = playerName
        self.__position = {'x': 0, 'y': 0}
        self.current_frame = 0
        self.frames = collections.defaultdict(list)
        self.spritesheet = None

    def add_state(self, filename, cols, state, framestart_buffer=None, framelength_buffer=None):
        self.spritesheet = pygame.image.load(filename).convert_alpha()
        if framelength_buffer is None and framestart_buffer is None:
            for i in range(cols):
                self.frames[state].append(self.spritesheet.subsurface(pygame.Rect(i * 50, 0, RYU_WIDTH, RYU_HEIGHT)))
        else:
            if framestart_buffer is None or framelength_buffer is None:
                exit("EXIT::Frame start & Frame length buffers need to provided")
            for i in range(cols):
                self.frames[state].append(self.spritesheet.subsurface(pygame.Rect(framestart_buffer[i], 0,
                                                                                  framelength_buffer[i], RYU_HEIGHT)))
        GAME_LOGGER.log("{0}".format("Player Name: " + self.playerName + " Added state " + repr(state) +
                                     " Filename: " + filename))

    def load_state(self, state, surface):
        global SND_HADOUKEN

        # start hadouken always from frame #1
        if self.state == PlayerState.HADOUKEN and self.current_frame > 0:
            self.state = PlayerState.HADOUKEN
            if self.current_frame == len(self.frames[PlayerState.HADOUKEN]) - 1:
                self.projectiles.append(copy.copy(self.__position))
                SND_HADOUKEN.play()
        elif self.state != state:
            self.current_frame = 0
            self.state = state
        self.draw(self.state, surface, self.__position)
        if self.state != PlayerState.IDLE:
            GAME_LOGGER.log("{0}".format("Player Name: " + self.playerName + " Loaded state " + repr(state)))

    def draw(self, state, surface, position):
        global FPS, KABALI_FPS, GAME_OVER
        global g_enemy_health
        global DAMAGE_HADOUKEN
        global HADOUKEN_SHIFT

        frame_length = len(self.frames[state])
        if self.current_frame >= frame_length - 1:
            self.current_frame = 0
        else:
            self.current_frame = self.current_frame + 1
        surface.blit(self.frames[state][self.current_frame], (position['x'], position['y']))
        # draw mf blasts
        for indx, pos in enumerate(self.projectiles):
            if self.projectiles[indx]['x'] > (ENEMY_POSITION.x - 50):
                surface.blit(self.frames[PlayerState.PROJECTILE_COMP][0], (ENEMY_POSITION.x - 50, self.__position['y']))
                del self.projectiles[indx]
                g_enemy_health -= DAMAGE_HADOUKEN
                HADOUKEN_SHIFT = True
                if FPS == KABALI_FPS:
                    GAME_OVER = True
            else:
                self.projectiles[indx]['x'] += 70
                surface.blit(self.frames[PlayerState.PROJECTILE][0], (self.projectiles[indx]['x'], self.projectiles[indx]['y']))

    @property
    def position(self):
        return self.__position

    @position.setter
    def position(self, position):
        self.__position['x'] = position['x']
        self.__position['y'] = position['y']


def exit(text='', logger=None):
    if logger and DEBUGGING_MOD:
        logger.log(text)
        logger.exit()
    pygame.font.quit()
    pygame.mixer.quit()
    pygame.quit()
    sys.exit()


def display_error(error_txt, ext=True):
    response = tkinter.messagebox.showerror("System Error", error_txt)
    if ext and response == 'ok':
        exit()


def load_sounds():
    global SND_HADOUKEN, SND_KP1, SND_KP2, SND_KP3, SND_FIGHT, SND_FINISHER
    global PATH_HADOUKEN, PATH_KP1, PATH_KP2, PATH_KP3, PATH_FIGHT, PATH_FINISHER

    SND_HADOUKEN = pygame.mixer.Sound(PATH_HADOUKEN)
    SND_HADOUKEN.set_volume(0.3)
    SND_KP1 = pygame.mixer.Sound(PATH_KP1)
    SND_KP1.set_volume(0.3)
    SND_KP2 = pygame.mixer.Sound(PATH_KP2)
    SND_KP2.set_volume(0.3)
    SND_KP3 = pygame.mixer.Sound(PATH_KP3)
    SND_FIGHT = pygame.mixer.Sound(PATH_FIGHT)
    SND_FINISHER = pygame.mixer.Sound(PATH_FINISHER)
    GAME_LOGGER.log("./Assets/Sounds files loaded")


def load_states(player):
    global PATH_IDLE, PATH_WALK, PATH_HADOUKEN, PATH_PROJECTILE, PATH_PROJECTILE_COMP, \
            PATH_LP, PATH_MHP, PATH_FLP, PATH_FMP, PATH_LMK, PATH_HK

    player.add_state(PATH_IDLE, COLS_IDLE, PlayerState.IDLE)
    player.add_state(PATH_WALK, COLS_WALK, PlayerState.WALKING)
    player.add_state(PATH_HADOUKEN_BLST, COLS_HADOUKEN, PlayerState.HADOUKEN, FRAMESTART_HADOUKEN, FRAMELENGTH_HADOUKEN)
    player.add_state(PATH_PROJECTILE, COLS_PROJECTILE, PlayerState.PROJECTILE, FRAMESTART_PROJECTILE, FRAMELENGTH_PROJECTILE)
    player.add_state(PATH_PROJECTILE_COMP, COLS_PROJECTILE, PlayerState.PROJECTILE_COMP, FRAMESTART_PROJECTILE, FRAMELENGTH_PROJECTILE)
    player.add_state(PATH_LP, COLS_LP, PlayerState.PUNCH, FRAMESTART_LP, FRAMELENGTH_LP)
    player.add_state(PATH_MHP, COLS_MHP, PlayerState.PUNCH, FRAMESTART_MHP, FRAMELENGTH_MHP)
    player.add_state(PATH_FLP, COLS_FLP, PlayerState.PUNCH)
    player.add_state(PATH_FMP, COLS_FMP, PlayerState.PUNCH, FRAMESTART_FMP, FRAMELENGTH_FMP)
    player.add_state(PATH_LMK, COLS_LMK, PlayerState.KICK, FRAMESTART_LMK, FRAMELENGTH_LMK)
    player.add_state(PATH_HK, COLS_HK, PlayerState.KICK, FRAMESTART_HK, FRAMELENGTH_HK)


def load_gamedata():
    global PATH_KP1, PATH_KP2, PATH_KP3, PATH_HADOUKEN, PATH_BGMUSIC, PATH_INTRO, PATH_CREDITS, \
        PATH_GAMEDATA, PATH_LOADING_SCREEN, PATH_WIN_ICON
    global BG_FRAMES, EN_FRAMES
    global WIN_CAPTION, PATH_LOADING_SCREEN, PATH_WIN_ICON
    global START_TIME
    global PLAYER_NAME
    global g_enemy_health, ENEMY_HEALTH_34, ENEMY_HEALTH_HALF, ENEMY_HEALTH_DEAD
    global KEY_PAUSE, KEY_KICK, KEY_PUNCH, KEY_HADOUKEN, KEY_LEFT, KEY_RIGHT
    global DEBUGGING_MOD, PATH_DEBUG_FILE

    with open(PATH_GAMEDATA) as gamedata_json:
        try:
            gamedata = json.load(gamedata_json)
            #  load sound paths
            l_tmp = gamedata['asset directory']['sounds']['punch/kick-miss-1']
            if l_tmp.lower() != 'default':
                PATH_KP1 = copy.copy(l_tmp) if l_tmp != '' else PATH_KP1
                if not os.path.exists(PATH_KP1):
                    display_error('File path ' + PATH_KP1 + ' does not exist in '
                                                            'asset directory/sounds/punch/kick-miss-1 (gamedata.json)')
            l_tmp = gamedata['asset directory']['sounds']['punch/kick-miss-2']
            if l_tmp.lower() != 'default':
                PATH_KP2 = copy.copy(l_tmp) if l_tmp != '' else PATH_KP2
                if not os.path.exists(PATH_KP2):
                    display_error('File path ' + PATH_KP2 + ' does not exist in '
                                                            'asset directory/sounds/punch/kick-miss-2 (gamedata.json)')
            l_tmp = gamedata['asset directory']['sounds']['punch/kick-hit']
            if l_tmp.lower() != 'default':
                PATH_KP3 = copy.copy(l_tmp) if l_tmp != '' else PATH_KP3
                if not os.path.exists(PATH_KP3):
                    display_error('File path ' + PATH_KP3 + ' does not exist in '
                                                            'asset directory/sounds/punch/kick-hit (gamedata.json)')
            l_tmp = gamedata['asset directory']['sounds']['hadouken']
            if l_tmp.lower() != 'default':
                PATH_HADOUKEN = copy.copy(l_tmp) if l_tmp != '' else PATH_HADOUKEN
                if not os.path.exists(PATH_HADOUKEN):
                    display_error('File path ' + PATH_HADOUKEN + ' does not exist in '
                                                                 'asset directory/sounds/hadouken (gamedata.json)')
            l_tmp = gamedata['asset directory']['sounds']['bg-music']
            if l_tmp.lower() != 'default':
                PATH_BGMUSIC = copy.copy(l_tmp) if l_tmp != '' else PATH_BGMUSIC
                if not os.path.exists(PATH_KP1):
                    display_error('File path ' + PATH_BGMUSIC + ' does not exist!')
            l_tmp = gamedata['asset directory']['sounds']['bg-music-start']
            if l_tmp.lower() != 'default':
                START_TIME = copy.copy(int(l_tmp)) if l_tmp != '' else START_TIME

            # load video paths
            l_tmp = gamedata['asset directory']['video']['intro']
            if l_tmp.lower() != 'default':
                PATH_INTRO = copy.copy(l_tmp) if l_tmp != '' else PATH_INTRO
                if not os.path.exists(PATH_INTRO):
                    display_error('File path ' + PATH_INTRO + ' does not exist in '
                                                              'asset directory/video/intro (gamedata.json)')
            l_tmp = gamedata['asset directory']['video']['credits']
            if l_tmp.lower() != 'default':
                PATH_CREDITS = copy.copy(l_tmp) if l_tmp != '' else PATH_CREDITS
                if not os.path.exists(PATH_KP1):
                    display_error('File path ' + PATH_CREDITS + ' does not exist in '
                                                               'asset directory/video/credits (gamedata.json)')
            # load background frames
            for i in range(1, 9):
                l_tmp = gamedata['asset directory']['textures']['bg-frames']['bg-frames-'+str(i)]
                if l_tmp.lower() != 'default':
                    if not os.path.exists(l_tmp.lower()):
                        display_error(
                            'File path ' + l_tmp + ' does not exist in asset directory/textures/bg-frames/bg-frames-'
                            + str(i) + ' (gamedata.json)')
                    BG_FRAMES['img'].append(pygame.image.load(l_tmp))
                    BG_FRAMES['rect'].append(BG_FRAMES['img'][-1].get_rect())
                else:
                    BG_FRAMES['img'].append(pygame.image.load('./Assets/Textures/bg_frames/frame-'+str(i)+'.png'))
                    BG_FRAMES['rect'].append(BG_FRAMES['img'][-1].get_rect())

            # load enemy frames (ordering in en_frames/ paramount)
            for i in range(1, 5):
                l_tmp = gamedata['asset directory']['textures']['en-frames']['en-frames-'+str(i)]
                if l_tmp.lower() != 'default':
                    if not os.path.exists(l_tmp.lower()):
                        display_error(
                            'File path ' + l_tmp + ' does not exist in asset directory/textures/en-frames/en-frames-'
                            + str(i) + ' (gamedata.json)')
                    EN_FRAMES[ENLIFE(i)] = pygame.image.load(l_tmp)
                    EN_FRAMES[ENLIFE(i + 3)] = EN_FRAMES[ENLIFE(i)].get_rect()
                else:
                    EN_FRAMES[ENLIFE(i)] = pygame.image.load('./Assets/Textures/en_frames/k'+str(i)+'.png')
                    EN_FRAMES[ENLIFE(i + 3)] = EN_FRAMES[ENLIFE(i)].get_rect()

            # set player controls
            l_tmp = gamedata['player']['controls']['punch']
            if l_tmp.lower() != 'default':
                KEY_PUNCH = copy.copy(ord(l_tmp)) if l_tmp != '' else KEY_PUNCH
            l_tmp = gamedata['player']['controls']['kick']
            if l_tmp.lower() != 'default':
                KEY_KICK = copy.copy(ord(l_tmp)) if l_tmp != '' else KEY_KICK
            l_tmp = gamedata['player']['controls']['hadouken']
            if l_tmp.lower() != 'default':
                KEY_HADOUKEN = copy.copy(ord(l_tmp)) if l_tmp != '' else KEY_HADOUKEN
            l_tmp = gamedata['player']['controls']['move-right']
            if l_tmp.lower() != 'default':
                KEY_RIGHT = copy.copy(ord(l_tmp)) if l_tmp != '' else KEY_RIGHT
            l_tmp = gamedata['player']['controls']['move-left']
            if l_tmp.lower() != 'default':
                KEY_LEFT = copy.copy(ord(l_tmp)) if l_tmp != '' else KEY_LEFT

            # set console controls
            l_tmp = gamedata['console']['controls']['pause']
            if l_tmp.lower() != 'default':
                KEY_PAUSE = copy.copy(ord(l_tmp)) if l_tmp != '' else KEY_PAUSE

            # check all keys are unique
            controls_set = {KEY_PUNCH, KEY_KICK, KEY_HADOUKEN, KEY_PAUSE, KEY_LEFT, KEY_RIGHT}
            if len(controls_set) != 4:
                display_error("Control Keys must be unique")

            # set window title
            l_tmp = gamedata['console']['window-title']
            if l_tmp.lower() != 'default':
                WIN_CAPTION = copy.copy(l_tmp) if l_tmp != '' else WIN_CAPTION

            # set loading screen path
            l_tmp = gamedata['console']['loading-screen']
            if l_tmp.lower() != 'default':
                PATH_LOADING_SCREEN = copy.copy(l_tmp) if l_tmp != '' else PATH_LOADING_SCREEN
                if not os.path.exists(PATH_LOADING_SCREEN):
                    display_error('File path ' + PATH_LOADING_SCREEN + ' does not exist in console/loading-screen (gamedata.json)')

            # set window icon path
            l_tmp = gamedata['console']['window-icon']
            if l_tmp.lower() != 'default':
                PATH_WIN_ICON = copy.copy(l_tmp) if l_tmp != '' else PATH_WIN_ICON
                if not os.path.exists(PATH_WIN_ICON):
                    display_error('File path ' + PATH_WIN_ICON + ' does not exist in console/window-icon (gamedata.json)')

            # set player name
            l_tmp = gamedata['player']['name']
            if l_tmp.lower() != 'default':
                PLAYER_NAME = copy.copy(l_tmp) if l_tmp != '' else PLAYER_NAME

            # set enemy params
            l_tmp = gamedata['enemy']['full-health']
            if l_tmp.lower() != 'default':
                g_enemy_health = copy.copy(int(l_tmp)) if l_tmp != '' else g_enemy_health
            l_tmp = gamedata['enemy']['3/4-health']
            if l_tmp.lower() != 'default':
                ENEMY_HEALTH_34 = copy.copy(int(l_tmp)) if l_tmp != '' else ENEMY_HEALTH_34
            l_tmp = gamedata['enemy']['half-health']
            if l_tmp.lower() != 'default':
                ENEMY_HEALTH_HALF = copy.copy(int(l_tmp)) if l_tmp != '' else ENEMY_HEALTH_HALF
            l_tmp = gamedata['enemy']['zero-health']
            if l_tmp.lower() != 'default':
                ENEMY_HEALTH_DEAD = copy.copy(int(l_tmp)) if l_tmp != '' else ENEMY_HEALTH_DEAD
            if not (g_enemy_health > ENEMY_HEALTH_34 and ENEMY_HEALTH_34 > ENEMY_HEALTH_HALF and ENEMY_HEALTH_HALF > ENEMY_HEALTH_DEAD):
                display_error("Enemy health values incorrect! Must be descending values. (gamedata.json)")

            # set debugging mode & file path
            l_tmp = gamedata['console']['debugging']['mode']
            if l_tmp.lower() == "on":
                DEBUGGING_MOD = True
            l_tmp = gamedata['console']['debugging']['output-file']
            if l_tmp.lower() != 'default':
                PATH_DEBUG_FILE = copy.copy(l_tmp) if l_tmp != '' else PATH_DEBUG_FILE

        except Exception as exp:    # all exceptions go to display_error()
            display_error(exp.__repr__())


def main():
    global BLACK, GREEN, RED
    global FPS, GAME_OVER, KABALI_FPS, WIN_CAPTION, FONT_SIZE, START_TIME
    global PLAYER_NAME
    global g_enemy_health, ENEMY_SHIFT_KP, ENEMY_SHIFT_HD, ENEMY_POSITION, DAMAGE_PUNCHES_KICKS, ENEMY_HEALTH_DEAD, \
        ENEMY_HEALTH_HALF, ENEMY_HEALTH_34
    global KEY_PAUSE, KEY_KICK, KEY_PUNCH, KEY_HADOUKEN, KEY_LEFT, KEY_RIGHT
    global SND_KP1, SND_KP2, SND_KP3, SND_FIGHT
    global HADOUKEN_SHIFT
    global BG_FRAMES, BG_FRAMES_COUNT, EN_FRAMES
    global PATH_INTRO, PATH_CREDITS, PATH_BGMUSIC
    global GAME_LOGGER, PATH_DEBUG_FILE, DEBUGGING_MOD, PLAYER_ACTIVE, GSTATE_TXT_POSITION

    background_frame = 0
    paused = False
    game_state = GameState.NULL

    load_gamedata()

    CLOCK = pygame.time.Clock()
    GAME_LOGGER = Logger(PATH_DEBUG_FILE)
    enemy_position = {'x': ENEMY_POSITION.x, 'y': ENEMY_POSITION.y}
    enemy_state = ENLIFE.FULL
    current_state = PlayerState.IDLE
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.mixer.init()
    pygame.font.init()
    pygame.init()

    # set window icon
    app_icon = pygame.image.load(PATH_WIN_ICON)
    pygame.display.set_icon(app_icon)

    display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    display_surface.fill(BLACK)
    pygame.display.set_caption(WIN_CAPTION)
    GAME_LOGGER.log("Display Surface Initialization: OK", WINDOW_WIDTH, WINDOW_HEIGHT)
    font = pygame.font.SysFont('Consolas', FONT_SIZE)
    GAME_LOGGER.log("Pygame Initialization: OK")
    GAME_LOGGER.log("Pygame Font Initialization (Consolas): OK")

    # load splash screen
    loading_image = pygame.image.load(PATH_LOADING_SCREEN)

    # create vlc instance & player for intro
    vlc_instance = vlc.Instance()
    media_intro = vlc_instance.media_new(PATH_INTRO)
    player_intro = vlc_instance.media_player_new()
    player_intro.set_hwnd(pygame.display.get_wm_info()['window'])
    player_intro.set_media(media_intro)
    pygame.mixer.quit()
    player_intro.play()

    while PLAYER_ACTIVE:
        if player_intro.get_state() == vlc.State.Ended:
            PLAYER_ACTIVE = False
        else:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    player_intro.stop()
                    player_intro.release()
                    vlc_instance.release()
                    exit("EXIT::INTRO_CLIP", GAME_LOGGER)
                elif event.type == pygame.KEYDOWN and event.key == KEY_ENTER:
                    PLAYER_ACTIVE = False

    player_intro.video_set_mouse_input(False)
    player_intro.video_set_key_input(False)
    player_intro.stop()
    player_intro.release()

    # display loading screen
    display_surface.blit(loading_image, [0, 0])
    pygame.display.update()

    # load progress texts
    font_fight = pygame.font.SysFont('vinerhanditc', 100)
    fight_text = font_fight.render("fight!", True, RED)
    finisher_text = font_fight.render("finish him!", True, RED)

    # load credits clip
    media_credits = vlc_instance.media_new(PATH_CREDITS)
    player_credits = vlc_instance.media_player_new()
    player_credits.set_hwnd(pygame.display.get_wm_info()['window'])
    player_credits.set_media(media_credits)

    # loading player assets
    ryu = Player(PLAYER_NAME)
    ryu.position['x'] = START_POSITION.x
    ryu.position['y'] = START_POSITION.y
    load_states(ryu)

    # loading player sounds
    pygame.mixer.pre_init(44100, -16, 2, 512)
    pygame.mixer.init()
    load_sounds()
    attack_sounds = [SND_KP1, SND_KP2]
    len_sounds = len(attack_sounds)
    GAME_LOGGER.log("./Assets/Video files loaded")

    pygame.mixer.music.load(PATH_BGMUSIC)
    pygame.mixer.music.play(-1, START_TIME)

    while not GAME_OVER:
        if game_state == GameState.NULL:
            game_state = GameState.INITIAL
            start_time = time.time()
            elasped_time = None

        keys = pygame.key.get_pressed()
        if (keys[KEY_RIGHT] or keys[K_RIGHT]) and not paused:
            current_state = PlayerState.WALKING
            if ryu.position['x'] < (ENEMY_POSITION.x - 50):
                ryu.position['x'] = ryu.position['x'] + 25
            ryu.position = ryu.position
            GAME_LOGGER.log("{0}".format('K_d::' + repr(ryu.position)))
        elif (keys[KEY_LEFT] or keys[K_LEFT]) and not paused:
            current_state = PlayerState.WALKING
            if ryu.position['x'] > 0:
                ryu.position['x'] = ryu.position['x'] - 25
            ryu.position = ryu.position
            GAME_LOGGER.log("{0}".format('K_a::' + repr(ryu.position)))
        elif keys[KEY_PUNCH] and not paused:
            current_state = PlayerState.PUNCH
            GAME_LOGGER.log("{0}".format('K_s::' + repr(ryu.position)))
            if FPS == KABALI_FPS:
                GAME_OVER = True
                GAME_LOGGER.log("GAME OVER {0}".format('K_s::' + repr(ryu.position)))
        elif keys[KEY_KICK] and not paused:
            current_state = PlayerState.KICK
            GAME_LOGGER.log("{0}".format('K_x::' + repr(ryu.position)))
            if FPS == KABALI_FPS:
                GAME_OVER = True
                GAME_LOGGER.log("GAME OVER {0}".format('K_x::' + repr(ryu.position)))

        for event in pygame.event.get():
            if event.type == KEYUP:
                current_state = PlayerState.IDLE
            elif event.type == KEYDOWN:
                if event.key == KEY_HADOUKEN:
                    current_state = PlayerState.HADOUKEN
                elif event.key == KEY_PUNCH:
                    current_state = PlayerState.PUNCH
                elif event.key == KEY_KICK:
                    current_state = PlayerState.KICK
                elif event.key == KEY_PAUSE:
                    paused = not paused
                    GAME_LOGGER.log("Paused Status: " + str(paused))
                elif event.key == pygame.K_0 and pygame.key.get_mods() & pygame.KMOD_CTRL and not paused:
                    DEBUGGING_MOD = not DEBUGGING_MOD
            elif event.type == QUIT:
                exit("EXIT::Normal Exit", GAME_LOGGER)

        if not paused:
            pygame.mixer.music.unpause()
            if current_state == PlayerState.KICK or current_state == PlayerState.PUNCH:
                if ryu.position['x'] == (ENEMY_POSITION.x - 50):
                    enemy_position['x'] += ENEMY_SHIFT_KP
                    g_enemy_health -= DAMAGE_PUNCHES_KICKS
                    SND_KP3.play()
                    GAME_LOGGER.log("State.KICK / State.PUNCH::ENEMY_POSITION: " + repr(enemy_position))
                    GAME_LOGGER.log("State.KICK / State.PUNCH::ENEMY HEALTH: " + str(g_enemy_health))
                else:
                    attack_sounds[random.randrange(len_sounds - 1)].play()

            if HADOUKEN_SHIFT:
                enemy_position['x'] += ENEMY_SHIFT_HD
                HADOUKEN_SHIFT = False
                GAME_LOGGER.log("HADOUKEN_SHIFT::ENEMY_POSITION: " + repr(enemy_position))

            ryu.load_state(current_state, display_surface)

            if g_enemy_health <= ENEMY_HEALTH_DEAD:
                enemy_state = ENLIFE.DEAD
            elif g_enemy_health <= ENEMY_HEALTH_HALF:
                if game_state == GameState.INITIAL and elasped_time > 1:
                    start_time = time.time()
                    game_state = GameState.FINISHER
                enemy_state = ENLIFE.HALF
            elif g_enemy_health <= ENEMY_HEALTH_34:
                enemy_state = ENLIFE.THREE_FOUR

            display_surface.blit(EN_FRAMES[enemy_state], (enemy_position['x'], enemy_position['y']))
            enemy_position['x'] = ENEMY_POSITION.x
            elasped_time = time.time() - start_time
            if game_state == GameState.INITIAL and elasped_time < 1:
                display_surface.blit(fight_text, (GSTATE_TXT_POSITION.x, GSTATE_TXT_POSITION.y))
                SND_FIGHT.play()
            elif game_state == GameState.FINISHER and elasped_time < 1:
                display_surface.blit(finisher_text, (GSTATE_TXT_POSITION.x-120, GSTATE_TXT_POSITION.y))
                SND_FINISHER.play()

            if DEBUGGING_MOD:
                cmd = "DEBUGGING ON"
                text_surface = font.render(cmd, False, GREEN)
                display_surface.blit(text_surface, (0, 0))

            pygame.display.update()

            # draw enemy & background
            if g_enemy_health > ENEMY_HEALTH_DEAD:
                display_surface.blit(BG_FRAMES['img'][background_frame], BG_FRAMES['rect'][background_frame])
                background_frame += 1
                if background_frame >= BG_FRAMES_COUNT:
                    background_frame = 0
            else:
                FPS = KABALI_FPS

            CLOCK.tick(FPS)

        else:
            pygame.mixer.music.pause()
            cmd = "PAUSED"
            text_surface = font.render(cmd, False, GREEN)
            display_surface.blit(text_surface, (0, 0))
            pygame.display.update(pygame.Rect(0, 0, WINDOW_WIDTH, FONT_SIZE))

    FPS = 12
    while True:
        for event in pygame.event.get():
            if event.type == KEYUP:
                current_state = PlayerState.IDLE
            elif event.type == KEYDOWN:
                if event.key == K_SPACE:
                    current_state = PlayerState.HADOUKEN
            elif event.type == QUIT:
                exit("EXIT::Normal Exit", GAME_LOGGER)

        PLAYER_ACTIVE = True
        pygame.mixer.quit()
        player_credits.play()

        while PLAYER_ACTIVE:
            if player_credits.get_state() == vlc.State.Ended:
                PLAYER_ACTIVE = False
            else:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        player_credits.stop()
                        player_credits.release()
                        vlc_instance.release()
                        exit("EXIT::CREDITS_CLIP", GAME_LOGGER)

        player_credits.stop()
        player_credits.release()
        vlc_instance.release()
        exit("EXIT::EOP", GAME_LOGGER)

        CLOCK.tick(FPS)


if __name__ == "__main__":
    main()
