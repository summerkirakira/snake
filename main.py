from typing import Union, Tuple
from engine import SEngine, ItemType, Direction, Point, SnakePoint, WallPoint, FruitPoint, GameStatus
from pathlib import Path
import pygame
import json
from pygame.locals import (
    K_UP,
    K_DOWN,
    K_LEFT,
    K_RIGHT,
    K_r,
    K_SPACE
)

if Path('./config.json').exists():
    game_config: dict = json.loads(Path('./config.json').read_text())
else:
    game_config: dict = {
        'screen_width': 800,
        'screen_height': 800,
        'block_size': 20,
        'caption': "贪吃蛇",
        'is_paused': False
    }
    Path('./config.json').write_text(json.dumps(game_config, indent=4, ensure_ascii=False))

snake_engine: SEngine = SEngine(int(game_config['screen_width'] / game_config['block_size']), int(game_config['screen_height'] / game_config['block_size']))
snake_engine.status = GameStatus.RUNNING

item_matrix: list[list[ItemType]] = [[ItemType.UNDEFINED for j in range(snake_engine.plane_height)] for i in range(snake_engine.plane_width)]

pygame.init()

screen = pygame.display.set_mode([game_config['screen_width'], game_config['screen_height']])
screen.fill((0, 0, 0))

pygame.display.set_caption(game_config['caption'])


def snake_control(key: pygame.constants):
    if key == K_SPACE:
        snake_engine.pause_game()
    elif key == K_UP:
        snake_engine.set_direction(Direction.UP)
    elif key == K_DOWN:
        snake_engine.set_direction(Direction.DOWN)
    elif key == K_LEFT:
        snake_engine.set_direction(Direction.LEFT)
    elif key == K_RIGHT:
        snake_engine.set_direction(Direction.RIGHT)
    elif key == K_r:
        snake_engine.restart()
        snake_engine.status = GameStatus.RUNNING


def rect_position(point: Point) -> pygame.Rect:
    rect_size: int = game_config['block_size']
    return pygame.Rect(point.position_x * rect_size, point.position_y * rect_size, rect_size, rect_size)


def rect_draw(point: Point, color: Tuple[int, int, int] = None) -> bool:
    if item_matrix[point.position_x][point.position_y] != point.get_type():
        if color is None:
            if point.get_type() == ItemType.WALL:
                color = (83, 255, 26)
            elif point.get_type() == ItemType.FRUIT:
                color = (255, 26, 26)
            elif point.get_type() == ItemType.SNAKE:
                color = (26, 255, 255)
            elif point.get_type() == ItemType.UNDEFINED:
                color = (0, 0, 0)
        pygame.draw.rect(screen, color, rect_position(point))
        item_matrix[point.position_x][point.position_y] = point.get_type()
        return True
    else:
        return False


def update_blocks():
    new_item_matrix: list[list[Point]] = [[Point(j, i) for j in range(snake_engine.plane_height)] for i in range(snake_engine.plane_width)]
    for point in snake_engine.wall_points:
        new_item_matrix[point.position_y][point.position_x] = point
    for point in snake_engine.snake_points:
        new_item_matrix[point.position_y][point.position_x] = point
    for point in snake_engine.fruit_points:
        new_item_matrix[point.position_y][point.position_x] = point
    for j in new_item_matrix:
        for i in j:
            rect_draw(i)
    # print(f"wall_points: {len(snake_engine.wall_points)} snake_points: {len(snake_engine.snake_points)} fruit_points: {len(snake_engine.fruit_points)}")


is_running: bool = True
while is_running:
    for event in pygame.event.get():
        if event.type == pygame.QUIT:
            is_running = False
            snake_engine.quit_game()
        elif event.type == pygame.KEYDOWN:
            snake_control(event.key)
    update_blocks()
    pygame.display.flip()
    pygame.display.set_caption(f"贪吃蛇 分数: {snake_engine.score} 状态: {snake_engine.status}")