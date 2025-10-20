from collections import deque
import unicurses as uni
import random
import time

class Snake:
    def __init__(self) -> None:
        self.size = 1
        self.body = deque([(1, 2), (1, 3), (1, 4), (1, 5), (1, 6), (1, 7), (1, 8), (1, 9), (1, 10)])
        self.direction = 'right'

    def get_body(self) -> deque:
        return self.body

    def move(self) -> None:
        head = self.body[-1]
        self.body.popleft()
        if self.direction == 'right':
            self.body.append((head[0], head[1] + 1))
        elif self.direction == 'left':
            self.body.append((head[0], head[1] - 1))
        elif self.direction == 'up':
            self.body.append((head[0] - 1, head[1]))
        elif self.direction == 'down':
            self.body.append((head[0] + 1, head[1]))

    def set_direction(self, new_dir: str) -> None:
        if (new_dir == 'right' and self.direction == 'left'): return
        if (new_dir == 'left' and self.direction == 'right'): return
        if (new_dir == 'down' and self.direction == 'up'): return
        if (new_dir == 'up' and self.direction == 'down'): return
        self.direction = new_dir

    def check_alive(self, stdscr) -> bool:
        max_y = uni.getmaxy(stdscr)
        max_x = uni.getmaxx(stdscr)
        head = self.body[-1]
        head_x = head[1]
        head_y = head[0]

        if head_y < 0 or head_y > max_y:
            return False
        if head_x < 0 or head_x > max_x:
            return False

        tail = list(self.body)[:-1]
        if head in tail:
            return False

        return True

    def add_body(self):
        head = self.body[-1]
        if self.direction == 'right':
            self.body.append((head[0], head[1] + 1))
        elif self.direction == 'left':
            self.body.append((head[0], head[1] - 1))
        elif self.direction == 'up':
            self.body.append((head[0] - 1, head[1]))
        elif self.direction == 'down':
            self.body.append((head[0] + 1, head[1]))


class Apples:
    def __init__(self) -> None:
        self.positions = set()

    def add_apple(self, snake_body: deque, stdscr):
        max_y = uni.getmaxy(stdscr)
        max_x = uni.getmaxx(stdscr)
        apple_x = random.randint(0, max_x)
        apple_y = random.randint(0, max_y)
        if (apple_y, apple_x) in self.positions:
            apple_x = random.randint(0, max_x)
            apple_y = random.randint(0, max_y)

        if (apple_y, apple_x) in snake_body:
            apple_x = random.randint(0, max_x)
            apple_y = random.randint(0, max_y)

        self.positions.add((apple_y, apple_x))

    def delete_apple(self, apple_y: int, apple_x: int):
        self.positions.discard((apple_y, apple_x))

    def get_apples(self):
        return self.positions


def main():
    running = True
    uni.noecho()
    stdscr = uni.initscr()
    GAME_SPEED = 0.05
    uni.curs_set(0)
    uni.nodelay(stdscr, True)


    player = Snake()
    apples = Apples()

    while running:
        key = uni.getch()
        
        if key == ord('q'):
            running = False
        elif key == uni.KEY_UP or key == ord('w'):
            player.set_direction('up')
        elif key == uni.KEY_DOWN or key == ord('s'):
            player.set_direction('down')
        elif key == uni.KEY_LEFT or key == ord('a'):
            player.set_direction('left')
        elif key == uni.KEY_RIGHT or key == ord('d'):
            player.set_direction('right')    
            
        uni.clear()


        apples.add_apple(player.get_body(), stdscr)
        apples_postions = apples.get_apples()
        for apple_y, apple_x in apples_postions:
            uni.mvaddch(apple_y, apple_x, '.')
        player.move()
        if not player.check_alive(stdscr):
            running = False
            break

        player_body = player.get_body()
        player_head = player_body[-1]
        if player_head in apples_postions:
            apples.delete_apple(player_head[0], player_head[1])
            player.add_body()
        for x, y in player_body:

            uni.mvaddch(x, y, '#')

        uni.refresh()
        time.sleep(GAME_SPEED)

    uni.endwin()

# --- Program Entry ---
if __name__ == '__main__':
    main()