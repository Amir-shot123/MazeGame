import pygame, random, sys

# ⚙️ تنظیمات اولیه
pygame.init()
CELL = 20
LEVEL = 1
SPEED = 120  # پیکسل در ثانیه
OFFSET_Y = 60
font = pygame.font.SysFont("consolas", 24)
screen = pygame.display.set_mode((800, 600))
pygame.display.set_caption("Maze Game")
clock = pygame.time.Clock()

# 🎨 رنگ‌ها
WHITE = (255,255,255)
BLACK = (10,10,10)
GRAY = (100,100,100)
LIGHT_GRAY = (180,180,180)
BLUE = (50,150,255)
GREEN = (0,255,140)
RED = (255,80,80)
YELLOW = (255,200,0)
ORANGE = (255,140,0)

# 🔆 افکت نور دور بازیکن
light_surface = pygame.Surface((CELL*4, CELL*4), pygame.SRCALPHA)
for i in range(5):
    pygame.draw.circle(light_surface, (0,255,255,80 - i*15), (CELL*2, CELL*2), CELL*2 - i*3)

def create_maze(size):
    maze = [['w'] * size for _ in range(size)]
    def carve(x, y):
        maze[y][x] = 'p'
        dirs = [(0,-2),(2,0),(0,2),(-2,0)]
        random.shuffle(dirs)
        for dx, dy in dirs:
            nx, ny = x+dx, y+dy
            if 0 < nx < size and 0 < ny < size and maze[ny][nx] == 'w':
                maze[y+dy//2][x+dx//2] = 'p'
                carve(nx, ny)
    carve(1, 1)
    maze[1][0] = 'p'; maze[-2][-1] = 'p'
    return maze

def draw_button(text, rect, hover, color):
    pygame.draw.rect(screen, LIGHT_GRAY if hover else color, rect, border_radius=10)
    label = font.render(text, True, WHITE)
    screen.blit(label, (rect.centerx - label.get_width() // 2, rect.y + 10))

def show_menu():
    while True:
        screen.fill((30, 30, 60))
        mx, my = pygame.mouse.get_pos()
        btns = {
            "start": pygame.Rect(300, 220, 200, 50),
            "settings": pygame.Rect(300, 290, 200, 50),
            "quit": pygame.Rect(300, 360, 200, 50)
        }
        draw_button("Start Game", btns["start"], btns["start"].collidepoint(mx, my), GREEN)
        draw_button("Settings", btns["settings"], btns["settings"].collidepoint(mx, my), ORANGE)
        draw_button("Quit", btns["quit"], btns["quit"].collidepoint(mx, my), RED)
        title = font.render("maze", True, YELLOW)
        screen.blit(title, (400 - title.get_width() // 2, 130))
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN:
                for name, btn in btns.items():
                    if btn.collidepoint(mx, my): return name

def show_settings():
    global SPEED
    while True:
        screen.fill((20, 20, 50))
        mx, my = pygame.mouse.get_pos()
        speed_btn = pygame.Rect(300, 250, 200, 50)
        back_btn = pygame.Rect(300, 320, 200, 50)
        draw_button(f"Speed: {SPEED:.0f} (+)", speed_btn, speed_btn.collidepoint(mx, my), BLUE)
        draw_button("Back", back_btn, back_btn.collidepoint(mx, my), GRAY)
        pygame.display.flip()
        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.MOUSEBUTTONDOWN:
                if speed_btn.collidepoint(mx, my): SPEED = min(SPEED + 20, 300)
                if back_btn.collidepoint(mx, my): return

def can_move(rect, maze, size):
    gx1 = int(rect.left // CELL)
    gy1 = int(rect.top // CELL)
    gx2 = int((rect.right - 1) // CELL)
    gy2 = int((rect.bottom - 1) // CELL)
    for gy in range(gy1, gy2 + 1):
        for gx in range(gx1, gx2 + 1):
            if 0 <= gx < size and 0 <= gy < size:
                if maze[gy][gx] != 'p':
                    return False
    return True

def play_level():
    global LEVEL
    size = min(31, 21 + (LEVEL // 3) * 2)
    maze = create_maze(size)
    player = pygame.Rect(0, CELL, CELL, CELL)
    start_time = pygame.time.get_ticks()

    while True:
        dt = clock.tick(60) / 1000
        screen.fill(BLACK)

        for y in range(size):
            for x in range(size):
                tile = maze[y][x]
                color = WHITE if tile == 'p' else BLACK
                if (y, x) == (1, 0): color = GREEN
                if (y, x) == (size - 2, size - 1): color = RED
                pygame.draw.rect(screen, color, (x * CELL, y * CELL + OFFSET_Y, CELL, CELL))

        lx = int(player.x + CELL/2 - light_surface.get_width()/2)
        ly = int(player.y + OFFSET_Y + CELL/2 - light_surface.get_height()/2)
        screen.blit(light_surface, (lx, ly), special_flags=pygame.BLEND_RGBA_ADD)
        pygame.draw.rect(screen, BLUE, (player.x, player.y + OFFSET_Y, CELL, CELL))

        pygame.draw.rect(screen, GRAY, (0, 0, 800, OFFSET_Y))
        elapsed = (pygame.time.get_ticks() - start_time) // 1000
        info = font.render(f"Level: {LEVEL}   Time: {elapsed}s", True, WHITE)
        screen.blit(info, (10, 10))
        pygame.display.flip()

        for e in pygame.event.get():
            if e.type == pygame.QUIT: pygame.quit(); sys.exit()
            if e.type == pygame.KEYDOWN and e.key == pygame.K_ESCAPE:
                return "menu"

        keys = pygame.key.get_pressed()
        dx = dy = 0
        if keys[pygame.K_LEFT]: dx -= SPEED * dt
        if keys[pygame.K_RIGHT]: dx += SPEED * dt
        if keys[pygame.K_UP]: dy -= SPEED * dt
        if keys[pygame.K_DOWN]: dy += SPEED * dt

        test_rect = player.move(dx, 0)
        if can_move(test_rect, maze, size): player.x += dx

        test_rect = player.move(0, dy)
        if can_move(test_rect, maze, size): player.y += dy

        gx, gy = int(player.x // CELL), int(player.y // CELL)
        if (gy, gx) == (size - 2, size - 1):
            LEVEL += 1
            return "next"

# 🚀 اجرای بازی
while True:
    choice = show_menu()
    if choice == "settings":
        show_settings()
    elif choice == "start":
        while True:
            result = play_level()
            if result == "menu": break
    elif choice == "quit":
        pygame.quit(); sys.exit()
