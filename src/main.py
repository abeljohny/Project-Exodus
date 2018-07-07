from moviepy.editor import *
import pygame, sys, time, random, os
from enum import Enum, IntEnum
import copy
import json
import tkinter.messagebox
from src.consts import *


class State(Enum):
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
        self.state = State.IDLE
        self.projectiles = []
        self.playerName = playerName
        self.__position = {'x': 0, 'y': 0}
        self.current_frame = 0
        self.frames = collections.defaultdict(list)
        self.spritesheet = None

    def add_state(self, filename, cols, state, framestart_buffer=None, framelength_buffer=None):
        self.spritesheet = pygame.image.load(filename).convert_alpha()
        rect = self.spritesheet.get_rect()
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
        if self.state == State.HADOUKEN and self.current_frame > 0:
            self.state = State.HADOUKEN
            if self.current_frame == len(self.frames[State.HADOUKEN]) - 1:
                self.projectiles.append(copy.copy(self.__position))
                SND_HADOUKEN.play()

        elif self.state != state:
            self.current_frame = 0
            self.state = state
        self.draw(self.state, surface, self.__position)
        if self.state != State.IDLE:
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
            if self.projectiles[indx]['x'] > ( ENEMY_POSITION.x - 50 ): # (WINDOW_WIDTH - FRAMELENGTH_PROJECTILE[0]):
                surface.blit(self.frames[State.PROJECTILE_COMP][0], (ENEMY_POSITION.x - 50, self.__position['y']))
                del self.projectiles[indx]
                g_enemy_health -= DAMAGE_HADOUKEN
                HADOUKEN_SHIFT = True
                if FPS == KABALI_FPS:
                    GAME_OVER = True
            else:
                self.projectiles[indx]['x'] += 70
                surface.blit(self.frames[State.PROJECTILE][0], (self.projectiles[indx]['x'], self.projectiles[indx]['y']))

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


def load_sounds():
    global SND_HADOUKEN, SND_KP1, SND_KP2, SND_KP3
    SND_HADOUKEN = pygame.mixer.Sound(PATH_HADOUKEN)
    SND_HADOUKEN.set_volume(0.3)
    SND_KP1 = pygame.mixer.Sound(PATH_KP1)
    SND_KP1.set_volume(0.3)
    SND_KP2 = pygame.mixer.Sound(PATH_KP2)
    SND_KP2.set_volume(0.3)
    SND_KP3 = pygame.mixer.Sound(PATH_KP3)
    SND_KP3.set_volume(0.3)
    GAME_LOGGER.log("./Assets/Sounds files loaded")


def load_states(player):
    global PATH_IDLE, PATH_WALK, PATH_HADOUKEN, PATH_PROJECTILE, PATH_PROJECTILE_COMP, \
            PATH_LP, PATH_MHP, PATH_FLP, PATH_FMP, PATH_LMK, PATH_HK

    player.add_state(PATH_IDLE, COLS_IDLE, State.IDLE)
    player.add_state(PATH_WALK, COLS_WALK, State.WALKING)
    player.add_state(PATH_HADOUKEN_BLST, COLS_HADOUKEN, State.HADOUKEN, FRAMESTART_HADOUKEN, FRAMELENGTH_HADOUKEN)
    player.add_state(PATH_PROJECTILE, COLS_PROJECTILE, State.PROJECTILE, FRAMESTART_PROJECTILE, FRAMELENGTH_PROJECTILE)
    player.add_state(PATH_PROJECTILE_COMP, COLS_PROJECTILE, State.PROJECTILE_COMP, FRAMESTART_PROJECTILE, FRAMELENGTH_PROJECTILE)
    player.add_state(PATH_LP, COLS_LP, State.PUNCH, FRAMESTART_LP, FRAMELENGTH_LP)
    player.add_state(PATH_MHP, COLS_MHP, State.PUNCH, FRAMESTART_MHP, FRAMELENGTH_MHP)
    player.add_state(PATH_FLP, COLS_FLP, State.PUNCH)
    player.add_state(PATH_FMP, COLS_FMP, State.PUNCH, FRAMESTART_FMP, FRAMELENGTH_FMP)
    player.add_state(PATH_LMK, COLS_LMK, State.KICK, FRAMESTART_LMK, FRAMELENGTH_LMK)
    player.add_state(PATH_HK, COLS_HK, State.KICK, FRAMESTART_HK, FRAMELENGTH_HK)


def load_player_assets(player):
    load_states(player)
    load_sounds()


def load_gamedata():
    global PATH_KP1, PATH_KP2, PATH_KP3, PATH_HADOUKEN, PATH_BGMUSIC, PATH_INTRO, PATH_CREDITS
    global BG_FRAMES, EN_FRAMES
    global CAPTION
    global PLAYER_NAME
    global KEY_PAUSE, KEY_KICK, KEY_PUNCH, KEY_HADOUKEN
    global DEBUGGING_MOD

    l_path = None
    controls_set = None

    with open('./gamedata.json') as gamedata_json:
        gamedata = json.load(gamedata_json)
        #  load sound paths
        l_path = gamedata['asset directory']['sounds']['punch/kick-miss-1']
        if l_path.lower() != 'default':
            PATH_KP1 = copy.copy(l_path)
        l_path = gamedata['asset directory']['sounds']['punch/kick-miss-2']
        if l_path.lower() != 'default':
            PATH_KP2 = copy.copy(l_path)
        l_path = gamedata['asset directory']['sounds']['punch/kick-hit']
        if l_path.lower() != 'default':
            PATH_KP3 = copy.copy(l_path)
        l_path = gamedata['asset directory']['sounds']['hadouken']
        if l_path.lower() != 'default':
            PATH_HADOUKEN = copy.copy(l_path)
        l_path = gamedata['asset directory']['sounds']['bg-music']
        if l_path.lower() != 'default':
            PATH_BGMUSIC = copy.copy(l_path)
        # load video paths
        l_path = gamedata['asset directory']['video']['intro']
        if l_path.lower() != 'default':
            PATH_INTRO = copy.copy(l_path)
        l_path = gamedata['asset directory']['video']['credits']
        if l_path.lower() != 'default':
            PATH_CREDITS = copy.copy(l_path)
        # load background frames
        for i in range(1, 9):
            l_path = gamedata['asset directory']['textures']['bg-frames']['bg-frames-'+str(i)]
            if l_path.lower() != 'default':
                BG_FRAMES['img'].append(pygame.image.load(l_path))
                BG_FRAMES['rect'].append(BG_FRAMES['img'][-1].get_rect())
            else:
                BG_FRAMES['img'].append(pygame.image.load('./Assets/Textures/bg_frames/frame-'+str(i)+'.png'))
                BG_FRAMES['rect'].append(BG_FRAMES['img'][-1].get_rect())
        # load enemy frames (ordering in en_frames/ paramount)
        for i in range(1, 5):
            l_path = gamedata['asset directory']['textures']['en-frames']['en-frames-'+str(i)]
            if l_path.lower() != 'default':
                EN_FRAMES[ENLIFE(i)] = pygame.image.load(l_path)
                EN_FRAMES[ENLIFE(i + 3)] = EN_FRAMES[ENLIFE(i)].get_rect()
            else:
                EN_FRAMES[ENLIFE(i)] = pygame.image.load('./Assets/Textures/en_frames/k'+str(i)+'.png')
                EN_FRAMES[ENLIFE(i + 3)] = EN_FRAMES[ENLIFE(i)].get_rect()
        # set control keys
        l_path = gamedata['controls']['punch']
        if l_path.lower() != 'default':
            KEY_PUNCH = copy.copy(ord(l_path))
        l_path = gamedata['controls']['kick']
        if l_path.lower() != 'default':
            KEY_KICK = copy.copy(ord(l_path))
        l_path = gamedata['controls']['hadouken']
        if l_path.lower() != 'default':
            KEY_HADOUKEN = copy.copy(ord(l_path))
        l_path = gamedata['controls']['pause']
        if l_path.lower() != 'default':
            KEY_PAUSE = copy.copy(ord(l_path))
        # check all keys are unique
        controls_set = {KEY_PUNCH, KEY_KICK, KEY_HADOUKEN, KEY_PAUSE}
        if len(controls_set) != 4:
            tkinter.messagebox.showerror("System Error", "Control Keys must be unique")
            exit()
        # set window caption
        l_path = gamedata['console']['window-title']
        if l_path.lower() != 'default':
            CAPTION = copy.copy(l_path)
        # set player name
        l_path = gamedata['player']['name']
        if l_path.lower() != 'default':
            PLAYER_NAME = copy.copy(l_path)
        # set debugging mode
        l_path = gamedata['debugging']
        if l_path.lower() == "on":
            DEBUGGING_MOD = True


def main():
    global BLACK, GREEN
    global FPS, GAME_OVER, KABALI_FPS, CAPTION, FONT_SIZE
    global PLAYER_NAME
    global g_enemy_health, ENEMY_SHIFT_KP, ENEMY_SHIFT_HD, ENEMY_POSITION, DAMAGE_PUNCHES_KICKS, ENEMY_HEALTH_DEAD, \
        ENEMY_HEALTH_HALF, ENEMY_HEALTH_34
    global SND_KP1, SND_KP2, SND_KP3
    global HADOUKEN_SHIFT
    global BG_FRAMES, BG_FRAMES_COUNT, EN_FRAMES
    global PATH_INTRO, PATH_CREDITS, PATH_BGMUSIC
    global GAME_LOGGER, DEBUGGING_MOD

    background_frame = 0
    paused = False
    cmd = None

    load_gamedata()

    CLOCK = pygame.time.Clock()
    GAME_LOGGER = Logger('logs')
    enemy_position = {'x': ENEMY_POSITION.x, 'y': ENEMY_POSITION.y}
    enemy_state = ENLIFE.FULL
    current_state = State.IDLE

    pygame.init()
    pygame.mixer.pre_init(44100, -16, 2, 2048)
    pygame.mixer.init()
    pygame.font.init()
    font = pygame.font.SysFont('Consolas', FONT_SIZE)
    GAME_LOGGER.log("Pygame Initialization: OK")
    GAME_LOGGER.log("Pygame Font Initialization (Consolas): OK")
    display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    display_surface.fill(BLACK)
    pygame.display.set_caption(CAPTION)
    GAME_LOGGER.log("Display Surface Initialization: OK", WINDOW_WIDTH, WINDOW_HEIGHT)

    # loading player assets
    ryu = Player(PLAYER_NAME)
    ryu.position['x'] = START_POSITION.x
    ryu.position['y'] = START_POSITION.y
    load_player_assets(ryu)
    attack_sounds = [SND_KP1, SND_KP2]
    len_sounds = len(attack_sounds)
    intro_clip = VideoFileClip(PATH_INTRO)
    credits_clip = VideoFileClip(PATH_CREDITS)
    GAME_LOGGER.log("./Assets/Video files loaded")

    # load background frames
    # for file in os.listdir('./Assets/Textures/bg_frames'):
    #     background['img'].append(pygame.image.load('./Assets/Textures/bg_frames/' + file))
    #     background['rect'].append(background['img'][-1].get_rect())

    # load enemy frames (ordering in en_frames/ paramount)
    # for file in os.listdir('./Assets/Textures/en_frames'):
    #     EN_FRAMES[ENLIFE(int(file[1]))] = pygame.image.load('./Assets/Textures/en_frames/' + file)
    #     EN_FRAMES[ENLIFE(int(file[1])+ 3)] = EN_FRAMES[ENLIFE(int(file[1]))].get_rect()

    intro_clip.preview()
    pygame.mixer.music.load(PATH_BGMUSIC)
    pygame.mixer.music.play(-1, 23.6)

    while not GAME_OVER:
        keys = pygame.key.get_pressed()
        if keys[K_d] and not paused:
            current_state = State.WALKING
            if ryu.position['x'] < (ENEMY_POSITION.x - 50):
                ryu.position['x'] = ryu.position['x'] + 25
            ryu.position = ryu.position
            GAME_LOGGER.log("{0}".format('K_d::' + repr(ryu.position)))
        elif keys[K_a] and not paused:
            current_state = State.WALKING
            if ryu.position['x'] > 0:
                ryu.position['x'] = ryu.position['x'] - 25
            ryu.position = ryu.position
            GAME_LOGGER.log("{0}".format('K_a::' + repr(ryu.position)))
        elif keys[K_s] and not paused:
            current_state = State.PUNCH
            GAME_LOGGER.log("{0}".format('K_s::' + repr(ryu.position)))
            if FPS == KABALI_FPS:
                GAME_OVER = True
                GAME_LOGGER.log("GAME OVER {0}".format('K_s::' + repr(ryu.position)))
        elif keys[K_x] and not paused:
            current_state = State.KICK
            GAME_LOGGER.log("{0}".format('K_x::' + repr(ryu.position)))
            if FPS == KABALI_FPS:
                GAME_OVER = True
                GAME_LOGGER.log("GAME OVER {0}".format('K_x::' + repr(ryu.position)))

        for event in pygame.event.get():
            if event.type == KEYUP:
                current_state = State.IDLE
            elif event.type == KEYDOWN:
                if event.key == KEY_HADOUKEN:
                    current_state = State.HADOUKEN
                elif event.key == KEY_PUNCH:
                    current_state = State.PUNCH
                elif event.key == KEY_KICK:
                    current_state = State.KICK
                elif event.key == KEY_PAUSE:
                    paused = not paused
                    GAME_LOGGER.log("Paused Status: " + str(paused))
                elif event.key == pygame.K_h and pygame.key.get_mods() & pygame.KMOD_CTRL and  \
                        pygame.key.get_mods() & pygame.KMOD_SHIFT and not paused:
                    DEBUGGING_MOD = not DEBUGGING_MOD
            elif event.type == QUIT:
                exit("EXIT::Normal Exit", GAME_LOGGER)

        if not paused:
            pygame.mixer.music.unpause()
            if current_state == State.KICK or current_state == State.PUNCH:
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
                enemy_state = ENLIFE.HALF
            elif g_enemy_health <= ENEMY_HEALTH_34:
                enemy_state = ENLIFE.THREE_FOUR

            display_surface.blit(EN_FRAMES[enemy_state], (enemy_position['x'], enemy_position['y']))
            enemy_position['x'] = ENEMY_POSITION.x
            if DEBUGGING_MOD:
                cmd = "DEBUGGING ON"
                text_surface = font.render(cmd, False, GREEN)
                display_surface.blit(text_surface, (0, 0))
            pygame.display.update()
            # draw enemy & background
            if g_enemy_health > 100:
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
                current_state = State.IDLE
            elif event.type == KEYDOWN:
                if event.key == K_SPACE:
                    current_state = State.HADOUKEN
            elif event.type == QUIT:
                exit("EXIT::Normal Exit", GAME_LOGGER)

        credits_clip.preview()
        exit("EXIT::EOP", GAME_LOGGER)

        CLOCK.tick(FPS)


if __name__ == "__main__":
    main()