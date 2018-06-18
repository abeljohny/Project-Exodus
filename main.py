# Copyright 2018 Avengers. All Rights Reserved.
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.
# ==============================================================================
import pygame, sys
from pygame.locals import *

WINDOW_WIDTH = 640
WINDOW_HEIGHT = 480
WHITE = (255, 255, 255)
RYU_WIDTH = 50
RYU_HEIGHT = 105
COLS_IDLE = 4
COLS_WALK = 5
CLOCK = pygame.time.Clock()
FPS = 12


class ExoSpritesheet:
    def __init__(self, filename, cols):
        self.sheet = pygame.image.load(filename).convert_alpha()
        self.indx = 0
        self.cols = cols
        self.rect = self.sheet.get_rect()
        self.frames = []
        # issue: self.frames having only first frame??!!
        for i in range(cols):
            self.frames.append(self.sheet.subsurface(pygame.Rect(i * 50, 0, RYU_WIDTH, RYU_HEIGHT)))
            print(i * 50)
        # self.cellWidth = int(self.rect.width / cols)
        # self.cellHeight = int(self.rect.height)
        # self.cells = list([(index % cols * self.cellWidth, index / cols * self.cellHeight) for index in range(cols)])

    def draw(self, surface):
        # pass
        surface.fill(WHITE)
        surface.blit(self.frames[self.indx], (0, 0))

        if self.indx == self.cols - 1:
            self.indx = 0
        else:
            self.indx = self.indx + 1

        # surface.blit(self.sheet, (50, 0), area=(51, 0, RYU_WIDTH, RYU_HEIGHT))
        # surface.blit(self.sheet, (100, 0), area=(102, 0, RYU_WIDTH, RYU_HEIGHT))
        # surface.blit(self.sheet, (150, 0), area=(153, 0, RYU_WIDTH, RYU_HEIGHT))


# def draw_background(screen):
#     road_img = pygame.image.load("Assets/asphalt.png").convert_alpha()
#     road_img = pygame.transform.scale(road_img, (480, 400)) # scale & rotate(90) this motherfucker
#     road_img = pygame.transform.rotate(road_img, DEG_90)
#     road_img_rect = road_img.get_rect(center = (WINDOW_WIDTH/2, WINDOW_HEIGHT - 100))
#     # that's right BLIT this fucker!!!!!!!!!!!!!!
#     screen.blit(road_img, road_img_rect)
#     tree_img = pygame.image.load("Assets/trees.png").convert_alpha()
#     # tree_img = pygame.transform.rotate(tree_img, DEG_90)
#     tree_img_rect = tree_img.get_rect(center=(WINDOW_WIDTH/2-420, WINDOW_HEIGHT - 260))
#     tree_img = pygame.transform.scale(tree_img, (380, 350))
#     screen.blit(tree_img, tree_img_rect)

def exit():
    print('-----------------------------')
    print('Shutting down systems: exit(0)')
    print('-----------------------------')
    pygame.quit()
    sys.exit()


def main():
    pygame.init()
    display_surface = pygame.display.set_mode((WINDOW_WIDTH, WINDOW_HEIGHT))
    display_surface.fill(WHITE)
    pygame.display.set_caption('Project Exodus')

    ryu_idle = ExoSpritesheet('Assets/ryu-idle.png', COLS_IDLE)
    # ryu_walking = ExoSpritesheet('Assets/ryu-walking.png', COLS_WALK)

    while True:
        for event in pygame.event.get():
            if event.type == KEYUP:
                if event.key == K_ESCAPE:
                    exit()
            elif event.type == QUIT:
                exit()

        ryu_idle.draw(display_surface)
        # ryu_walking.draw(display_surface)
        pygame.display.update()
        CLOCK.tick(FPS)





    # draw_background(DISPLAY)
    # ss = spritesheet("Assets/ryu-idle.png")
    # # image = ss.image_at(0, 0, 50, 105)
    # images = []
    # images = ss.images_at((0, 0, 50, 105), (0, 0, 100, 105), colorkey=(255, 255, 255))
    #
    # while True:
    #     for event in pygame.event.get():
    #         if event.type == QUIT:
    #             pygame.quit()
    #             sys.exit()
    #     pygame.display.update()


if __name__ == "__main__":
    main()