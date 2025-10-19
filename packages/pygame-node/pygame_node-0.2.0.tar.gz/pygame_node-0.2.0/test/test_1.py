import math
import os

import pygame

from pygame_node.data.node import Size
from pygame_node import *

SCREEN_WIDTH, SCREEN_HEIGHT = 1200, 700
BgColor = (0x84, 0xC6, 0x69)


class MainScene(BaseScene):
    def __init__(self):
        super().__init__("Main")

    def init(self, params: 'BaseScene' = None):
        super().init(params)
        self.player = Sprite2D(self.TEXTURES_PATH / "player.svg")
        self.player.x = SCREEN_WIDTH / 2
        self.player.y = SCREEN_HEIGHT / 2
        self.player.size = Size(20, 20)
        self.text = Text("按 F 触发操作")
        self.text.style.background.color = Color(255, 255, 255, 0.4)
        self.text.style.color = Color(255, 255, 255)
        self.wall = Node("Wall")
        self.wall.x = 500
        self.wall.y = 400
        self.wall.size = Size(20, 20)
        self.wall.style.background.color = Color(255, 255, 255, 0.4)
        self.addNode(self.player)
        self.addNode(self.text)
        self.addNode(self.wall)

        @self.player.event
        def move(event: KeyDownEvent):
            if event.keycode == pygame.K_UP:
                event.node.y -= 5
            if event.keycode == pygame.K_DOWN:
                event.node.y += 5
            if event.keycode == pygame.K_LEFT:
                event.node.x -= 5
            if event.keycode == pygame.K_RIGHT:
                event.node.x += 5

    def update(self, dt: float) -> None:
        self.text.x = self.player.x + 20
        self.text.y = self.player.y + 20
        if math.sqrt((self.player.x - self.wall.x)**2 + (self.player.y - self.wall.y)**2) < 10:
            self.text.visible = True
        else:
            self.text.visible = False

def init():
    pygame.init()
    manager = SceneManager(MainScene())

    screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT), pygame.HWSURFACE | pygame.DOUBLEBUF, vsync=False)
    clock = pygame.time.Clock()
    BaseScene.font = Font(r"resources\font\Minecraft AE.ttf", 24)
    Node.font = BaseScene.font
    manager.switch("Main")
    pygame.key.set_repeat(100, 10)

    running = True
    while running:
        events = pygame.event.get()
        for event in events:
            if event.type == pygame.QUIT:
                running = False
                break

        manager.events(events)
        manager.update(clock.tick(0) / 1000.0)

        screen.fill(BgColor)
        manager.draw(screen)
        pygame.display.flip()
        print(f"FPS: {clock.get_fps()}", end="\r")

    pygame.quit()


if __name__ == '__main__':
    init()
