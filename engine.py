from typing import Tuple
from enum import Enum
import time
import threading
import random


class GameStatus(Enum):
    STOP = 0
    RUNNING = 1
    PAUSE = 2
    GAMEOVER = 3

    def __str__(self):
        if self == GameStatus.RUNNING:
            return "运行中"
        elif self == GameStatus.PAUSE:
            return "暂停"
        elif self == GameStatus.GAMEOVER:
            return "游戏失败"
        elif self == GameStatus.STOP:
            return "停止"


class Direction(Enum):
    UP = 0
    DOWN = 1
    LEFT = 2
    RIGHT = 3


class ItemType(Enum):
    SNAKE = 0
    WALL = 1
    FRUIT = 2
    UNDEFINED = 3


class Point:

    def __init__(self, x: int, y: int):
        self.position_x = x
        self.position_y = y

    def __eq__(self, other) -> bool:
        if isinstance(other, Point):
            if self.position_x == other.position_x and self.position_y == other.position_y:
                return True
            else:
                return False
        else:
            return False

    def get_type(self) -> ItemType:
        if isinstance(self, SnakePoint):
            return ItemType.SNAKE
        elif isinstance(self, WallPoint):
            return ItemType.WALL
        elif isinstance(self, FruitPoint):
            return ItemType.FRUIT
        return ItemType.UNDEFINED

    def get_position(self) -> Tuple[int, int]:
        """
        get point position
        :return: Tuple[position_x, position_y]
        """
        return self.position_x, self.position_y

    def __str__(self) -> str:
        return f"[Point] x={self.position_x}, y={self.position_y}"


class SnakePoint(Point):
    def __str__(self) -> str:
        return f"[Snake Body Point] x={self.position_x}, y={self.position_y}"


class FruitPoint(Point):
    def __str__(self) -> str:
        return f"[Fruit Point] x={self.position_x}, y={self.position_y}"


class WallPoint(Point):
    def __str__(self) -> str:
        return f"[Wall Point] x={self.position_x}, y={self.position_y}"


class SEngine:
    def _generate_wall(self) -> list[WallPoint]:
        """
        generate walls on the edge of the plane
        :return: list[WallPoint]
        """
        wall_points = []
        for i in range(self.plane_height):
            for j in range(self.plane_width):
                if i == 0 or i == self.plane_height - 1:
                    wall_points.append(WallPoint(i, j))
                elif j == 0 or j == self.plane_width - 1:
                    wall_points.append(WallPoint(i, j))
        return wall_points

    def _generate_snake(self) -> list[SnakePoint]:
        """
        generate snake in the center of the plane
        :return: list[SnakePoint]
        """
        return [SnakePoint(int(self.plane_height / 2), int(self.plane_width / 2)),
                SnakePoint(int(self.plane_height / 2) + 1, int(self.plane_width / 2))]

    def _generate_fruit(self) -> list[FruitPoint]:
        fruit_points: list[FruitPoint] = []
        while len(fruit_points) < self.Const().fruit_num:
            is_overlapping: bool = False
            position_x = random.randint(0, self.plane_height - 1)
            position_y = random.randint(0, self.plane_width - 1)
            fruit_point: FruitPoint = FruitPoint(position_x, position_y)
            for wall_point in self.wall_points:
                if fruit_point == wall_point:
                    is_overlapping = True
                    break
            for snake_point in self.snake_points:
                if fruit_point == snake_point:
                    is_overlapping = True
                    break
            if not is_overlapping:
                fruit_points.append(fruit_point)
        return fruit_points

    def _init_direction(self) -> Direction:
        return Direction.UP

    def _init_score(self) -> int:
        return 0

    @staticmethod
    def _get_milli_time() -> int:
        return int(time.time() * 1000)

    def can_update(self) -> bool:
        return self._get_milli_time() - self.last_update > self.Const().frame_interval \
               and not self.lock.locked() \
               and self.status == GameStatus.RUNNING

    def is_hit_wall(self) -> bool:
        """
        Determine if the snake hit the wall
        :return: bool
        """
        for wall_point in self.wall_points:
            if wall_point == self.snake_points[0]:
                return True
        return False

    def is_hit_fruit(self) -> bool:
        """
        Determine if the snake hit the fruit
        :return: bool
        """
        for fruit_point in self.fruit_points:
            if fruit_point == self.snake_points[0]:
                return True
        return False

    def is_hit_body(self) -> bool:
        """
        Determine if the snake hit self
        :return: bool
        """
        for body_point in self.snake_points[1:]:
            if body_point == self.snake_points[0]:
                return True
        return False

    @property
    def score(self) -> int:
        return self._score * self.Const().score_per_body_point

    @score.setter
    def score(self, value):
        self._score:int = value

    @property
    def last_update(self) -> int:
        return self._last_update

    @last_update.setter
    def last_update(self, value):
        self._last_update: int = value
        self.tick += 1

    def _move_forward(self) -> Tuple[SnakePoint, SnakePoint]:
        """
        Move snake and update it position
        :return: new header point, last tail position
        """
        if self.direction == Direction.UP:
            self.snake_points.insert(0,
                                     SnakePoint(self.snake_points[0].position_x, self.snake_points[0].position_y - 1))
        elif self.direction == Direction.DOWN:
            self.snake_points.insert(0,
                                     SnakePoint(self.snake_points[0].position_x, self.snake_points[0].position_y + 1))
        elif self.direction == Direction.LEFT:
            self.snake_points.insert(0,
                                     SnakePoint(self.snake_points[0].position_x - 1, self.snake_points[0].position_y))
        elif self.direction == Direction.RIGHT:
            self.snake_points.insert(0,
                                     SnakePoint(self.snake_points[0].position_x + 1, self.snake_points[0].position_y))
        return self.snake_points[0], self.snake_points.pop()

    def set_direction(self, direction: Direction):
        if self.direction == Direction.LEFT and direction == Direction.RIGHT:
            return
        if self.direction == Direction.RIGHT and direction == Direction.LEFT:
            return
        if self.direction == Direction.UP and direction == Direction.DOWN:
            return
        if self.direction == Direction.DOWN and direction == Direction.UP:
            return
        self.direction = direction

    def set_game_status(self, status: GameStatus):
        self.status = status

    class Const:
        @property
        def frame_rates(self) -> int:
            return 2

        @property
        def frame_interval(self) -> int:
            return int(1000 / self.frame_rates)

        @property
        def score_per_body_point(self) -> int:
            return 1

        @property
        def fruit_num(self) -> int:
            return 2

    def _hit_fruit(self, tail_point: SnakePoint):
        self.score += 1
        self.snake_points.append(tail_point)
        self.fruit_points = self._generate_fruit()

    def _hit_wall(self, tail_point: SnakePoint):
        self.snake_points.pop(0)
        self.snake_points.append(tail_point)
        self.status = GameStatus.GAMEOVER

    def _hit_body(self):
        self.status = GameStatus.GAMEOVER

    def pause_game(self):
        if self.status == GameStatus.RUNNING:
            self.status = GameStatus.PAUSE
        elif self.status == GameStatus.PAUSE:
            self.status = GameStatus.RUNNING

    def quit_game(self):
        self.update_thread.is_terminated = True

    def _create_new(self, width:int, height: int):
        self.plane_width: int = width
        self.plane_height: int = height
        self.plane_matrix: list[list[int]] = [[0 for i in range(height)] for j in range(width)]
        self.wall_points: list[WallPoint] = self._generate_wall()
        self.snake_points: list[SnakePoint] = self._generate_snake()
        self.fruit_points: list[FruitPoint] = self._generate_fruit()
        self.direction: Direction = self._init_direction()
        self.score: int = self._init_score()
        self.last_update: int = self._get_milli_time()
        self.lock: threading.Lock = threading.Lock()
        self.status: GameStatus = GameStatus.STOP
        self.tick: int = 0

    def __init__(self, plane_width: int, plane_height: int, load_from_file: bool = False):
        self.plane_width: int = 0
        self.plane_height: int = 0
        self.plane_matrix: list[list[int]] = [[]]
        self.wall_points: list[WallPoint] = []
        self.snake_points: list[SnakePoint] = []
        self.fruit_points: list[FruitPoint] = []
        self.direction: Direction = Direction.UP
        self.score: int = 0
        self.tick: int = 0
        self.last_update: int = 0
        self.lock: threading.Lock = threading.Lock()
        self.status: GameStatus = GameStatus.STOP
        self.update_thread = self.FrameUpdateThread(self)
        if not load_from_file:
            self._create_new(width=plane_width, height=plane_height)
        self.update_thread.start()

    def update_frame(self) -> bool:
        if self.can_update():
            self.lock.acquire()
            _, last_tail_point = self._move_forward()
            if self.is_hit_wall():
                self._hit_wall(last_tail_point)
            elif self.is_hit_body():
                self._hit_body()
            elif self.is_hit_fruit():
                self._hit_fruit(last_tail_point)
            self.last_update = self._get_milli_time()
            self.lock.release()
        else:
            return False

    class FrameUpdateThread(threading.Thread):
        def __init__(self, engine: 'SEngine'):
            super().__init__()
            self.engine: SEngine = engine
            self.is_terminated: bool = False

        def run(self) -> None:
            while not self.is_terminated:
                while self.engine.status == GameStatus.RUNNING:
                    self.engine.update_frame()
                    time.sleep(self.engine.Const().frame_interval / 10 / 1000)


if __name__ == '__main__':
    snake_engine = SEngine(30, 30)
    snake_engine.status = GameStatus.RUNNING
    while True:
        for snake_point in snake_engine.snake_points:
            print(snake_point, end=" ")
        print(f"Status={snake_engine.status}, Score={snake_engine.score}", end=" ")
        print()
        time.sleep(0.5)
        snake_engine.set_direction(Direction.LEFT)
