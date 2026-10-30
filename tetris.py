#!/usr/bin/env python3
import curses
import random
import time

# Фигуры тетриса (тетромино)
SHAPES = [
    [[1, 1, 1, 1]],                    # I
    [[1, 1], [1, 1]],                  # O
    [[0, 1, 0], [1, 1, 1]],            # T
    [[1, 0, 0], [1, 1, 1]],            # L
    [[0, 0, 1], [1, 1, 1]],            # J
    [[0, 1, 1], [1, 1, 0]],            # S
    [[1, 1, 0], [0, 1, 1]]             # Z
]

BOARD_WIDTH = 10
BOARD_HEIGHT = 20

def create_board():
    return [[0] * BOARD_WIDTH for _ in range(BOARD_HEIGHT)]

def valid_fit(shape, offset_x, offset_y, board):
    for r, row in enumerate(shape):
        for c, val in enumerate(row):
            if val:
                nx = offset_x + c
                ny = offset_y + r
                if nx < 0 or nx >= BOARD_WIDTH or ny >= BOARD_HEIGHT:
                    return False
                if ny >= 0 and board[ny][nx]:
                    return False
    return True

def merge_shape(shape, offset_x, offset_y, board, color):
    for r, row in enumerate(shape):
        for c, val in enumerate(row):
            if val:
                if 0 <= offset_y + r < BOARD_HEIGHT and 0 <= offset_x + c < BOARD_WIDTH:
                    board[offset_y + r][offset_x + c] = color

def clear_lines(board):
    new_board = [row for row in board if any(val == 0 for val in row)]
    cleared = BOARD_HEIGHT - len(new_board)
    for _ in range(cleared):
        new_board.insert(0, [0] * BOARD_WIDTH)
    return new_board, cleared

def main(stdscr):
    curses.curs_set(0)
    stdscr.nodelay(True)
    stdscr.timeout(100) # Скорость падения (мс)

    board = create_board()
    score = 0

    current_shape = random.choice(SHAPES)
    current_color = random.randint(1, 6)
    curr_x = BOARD_WIDTH // 2 - len(current_shape[0]) // 2
    curr_y = 0

    # Настройка цветов, если терминал поддерживает
    if curses.has_colors():
        curses.start_color()
        curses.init_pair(1, curses.COLOR_CYAN, curses.COLOR_BLACK)
        curses.init_pair(2, curses.COLOR_YELLOW, curses.COLOR_BLACK)
        curses.init_pair(3, curses.COLOR_MAGENTA, curses.COLOR_BLACK)
        curses.init_pair(4, curses.COLOR_GREEN, curses.COLOR_BLACK)
        curses.init_pair(5, curses.COLOR_RED, curses.COLOR_BLACK)
        curses.init_pair(6, curses.COLOR_BLUE, curses.COLOR_BLACK)

    fall_time = time.time()
    fall_speed = 0.4 # Секунд на шаг вниз

    while True:
        # Обработка ввода с клавиатуры
        key = stdscr.getch()
        if key == ord('q'): # Выход по 'q'
            break
        elif key == curses.KEY_LEFT:
            if valid_fit(current_shape, curr_x - 1, curr_y, board):
                curr_x -= 1
        elif key == curses.KEY_RIGHT:
            if valid_fit(current_shape, curr_x + 1, curr_y, board):
                curr_x += 1
        elif key == curses.KEY_DOWN:
            if valid_fit(current_shape, curr_x, curr_y + 1, board):
                curr_y += 1
        elif key == ord(' '): # Поворот на Пробел
            rotated = [list(row) for row in zip(*current_shape[::-1])]
            if valid_fit(rotated, curr_x, curr_y, board):
                current_shape = rotated

        # Гравитация (падение вниз)
        if time.time() - fall_time > fall_speed:
            if valid_fit(current_shape, curr_x, curr_y + 1, board):
                curr_y += 1
            else:
                merge_shape(current_shape, curr_x, curr_y, board, current_color)
                board, cleared = clear_lines(board)
                score += cleared * 100

                # Спавн новой фигуры
                current_shape = random.choice(SHAPES)
                current_color = random.randint(1, 6)
                curr_x = BOARD_WIDTH // 2 - len(current_shape[0]) // 2
                curr_y = 0

                if not valid_fit(current_shape, curr_x, curr_y, board):
                    # Проигрыш
                    break
            fall_time = time.time()

        # Отрисовка
        stdscr.clear()
        h, w = stdscr.getmaxyx()
        
        start_y = (h - BOARD_HEIGHT) // 2
        start_x = (w - BOARD_WIDTH * 2) // 2

        # Рисуем рамку и поле
        for r in range(BOARD_HEIGHT):
            try:
                stdscr.addstr(start_y + r, start_x - 1, "|")
                stdscr.addstr(start_y + r, start_x + BOARD_WIDTH * 2, "|")
            except:
                pass
            for c in range(BOARD_WIDTH):
                val = board[r][c]
                char = "[]" if val else " ."
                try:
                    if val and curses.has_colors():
                        stdscr.addstr(start_y + r, start_x + c * 2, char, curses.color_pair(val))
                    else:
                        stdscr.addstr(start_y + r, start_x + c * 2, char)
                except:
                    pass

        # Рисуем падающую фигуру
        for r, row in enumerate(current_shape):
            for c, val in enumerate(row):
                if val:
                    ny = curr_y + r
                    nx = curr_x + c
                    if 0 <= ny < BOARD_HEIGHT and 0 <= nx < BOARD_WIDTH:
                        char = "[]"
                        try:
                            if curses.has_colors():
                                stdscr.addstr(start_y + ny, start_x + nx * 2, char, curses.color_pair(current_color))
                            else:
                                stdscr.addstr(start_y + ny, start_x + nx * 2, char)
                        except:
                            pass

        # Вывод счета
        try:
            stdscr.addstr(start_y - 2, start_x, f"Счет: {score} | Выход: q")
        except:
            pass

        stdscr.refresh()

if __name__ == "__main__":
    curses.wrapper(main)
