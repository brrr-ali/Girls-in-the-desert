import os
import sys
import pygame

pygame.init()
FPS = 10
level_x, level_y = 16, 12
WIDTH = 800
HEIGHT = 600
MYEVENTTYPE = pygame.USEREVENT + 1
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()

TIME_IN_LEVEl = [5, 10, 10, 10, 10]


def load_image(name, colorkey=None):
    fullname = os.path.join('data', name)
    if not os.path.isfile(fullname):
        print(f"Файл с изображением '{fullname}' не найден")
        sys.exit()

    image = pygame.image.load(fullname)
    if colorkey is not None:
        image = image.convert()
        if colorkey == -1:
            colorkey = image.get_at((0, 0))
        image.set_colorkey(colorkey)
    else:
        image = image.convert_alpha()
    return image


tile_images = {
    'wall': load_image('лестницввправо.png', -1),
    'empty': load_image('лесенкавлево.png', -1),
    'bottle_of_water': load_image('bottle.png', -1),
    'piece_ground': load_image('кусокземли.png', -1),
    'poison': load_image('poison.png', -1)
}
player_image = load_image('лесенкавлево.png')
tile_width = tile_height = 50
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
danger = pygame.sprite.Group()
bottle = pygame.sprite.Group()


def load_level(filename):
    filename = "data/" + filename
    if not os.path.isfile(filename):
        print(f"Файл с уровнем '{filename}' не найден")
        sys.exit()
    # читаем уровень, убирая символы перевода строки
    with open(filename, 'r') as mapFile:
        level_map = [line.strip() for line in mapFile]

    # и подсчитываем максимальную длину
    max_width = max(map(len, level_map))

    # дополняем каждую строку пустыми клетками ('.')
    return list(map(lambda x: x.ljust(max_width, '.'), level_map))


def terminate():
    pygame.quit()
    sys.exit()


def generate_level(level):
    player_, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == 'w':
                bottle.add(Tile('bottle_of_water', x, y))
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '-':
                Tile('poison', x, y).add(danger)
            elif level[y][x] == '&':
                Tile('piece_ground', x, y)
            elif level[y][x] == 'h':
                Tile('piece_ground', x, y)
                player_ = Girls(0.1, x, y)
            elif level[y][x] == 'w':
                pass
    # вернем игрока, а также размер поля в клетках
    return player_, x + 1, y + 1


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, sheet, columns, rows, x, y):
        super().__init__(all_sprites)
        self.frames = []
        self.cut_sheet(sheet, columns, rows)
        self.cur_frame = 0
        self.image = self.frames[self.cur_frame]
        self.rect = self.rect.move(x, y)

    def cut_sheet(self, sheet, columns, rows):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns, sheet.get_height() // rows)
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                self.frames.append(sheet.subsurface(pygame.Rect(frame_location, self.rect.size)))

    def update(self):
        self.cur_frame = (self.cur_frame + 1) % len(self.frames)
        self.image = self.frames[self.cur_frame]


class Girls(AnimatedSprite):
    def __init__(self, v, x, y):
        super().__init__(load_image("girlr.png", -1), 3, 1, x * tile_width, y * tile_height)
        self.v, self.x, self.y = v, x, y
        player_group.add(self)
        self.bottles_of_water = 3

    def update2(self):
        self.rect.y += tile_height
        if pygame.sprite.spritecollideany(self, tiles_group):
            if pygame.sprite.spritecollideany(self, danger):
                print('game over')
                self.rect.y += tile_height
                game.game_over()
            if pygame.sprite.spritecollideany(self, bottle):
                self.bottles_of_water += 1
                game.remaining_time -= 2000
            self.rect.x += clock.tick(FPS) * self.v
            if pygame.key.get_pressed()[pygame.K_RIGHT]:
                self.rect.x += tile_width
            if pygame.key.get_pressed()[pygame.K_UP]:
                self.rect.y -= tile_height * 2
            '''if pygame.key.get_pressed()[pygame.K_LEFT]:
                self.rect.x -= tile_width'''
            self.rect.y -= tile_height
        if self.rect.y >= HEIGHT:
            game.game_over()


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0
        self.fl = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy

    # позиционировать камеру на объекте target
    def update(self, target):
        if not (0 <= target.rect.x < WIDTH // 2):
            self.fl = 1
        if self.fl:
            self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH // 2)


def start_screen():
    pygame.mixer.init()
    pygame.mixer.music.load('music.mp3')
    pygame.mixer.music.play(-1)
    intro_text = ["Девушка в пустыне", "",
                  "Найди сундук сокровищами, но следи за осташимся количество воды.",
                  "Для выключения музыки нажми - 1, для включения - 2"]
    screen.blit(sky, (0, 0))
    font = pygame.font.Font(None, 30)
    text_coord = 50
    for line in intro_text:
        string_rendered = font.render(line, 1, pygame.Color('black'))
        intro_rect = string_rendered.get_rect()
        text_coord += 10
        intro_rect.top = text_coord
        intro_rect.x = 10
        text_coord += intro_rect.height
        screen.blit(string_rendered, intro_rect)

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif event.type == pygame.KEYDOWN or \
                    event.type == pygame.MOUSEBUTTONDOWN:
                if event.key == pygame.K_1:
                    pygame.mixer.music.pause()
                elif event.key == pygame.K_2:
                    pygame.mixer.music.unpause()
                else:
                    return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)


class Game:
    def __init__(self, screen, level, hero, level_x, level_y):
        self.hero = hero
        self.screen = screen
        self.level, self.level_x, self.level_y = level, level_x, level_y
        self.remaining_time = 0
        self.camera = Camera()

    def update(self):
        self.camera.update(self.hero)
        # обновляем положение всех спрайтов
        for sprite in all_sprites:
            self.camera.apply(sprite)
        self.hero.update2()
        all_sprites.update()
        all_sprites.draw(screen)
        player_group.draw(screen)
        t = clock.tick(FPS)
        self.remaining_time += t
        if self.remaining_time >= TIME_IN_LEVEl[level - 1] * 1000:
            self.remaining_time = 0
            self.game_over()
        if self.hero.bottles_of_water < 0:
            self.game_over()
        print(self.hero.bottles_of_water)
        pygame.display.flip()

    def game_over(self):
        screen.blit(sky, (0, 0))
        intro_text = ["GAME OVER"]
        # fon = pygame.transform.scale(screen, (WIDTH, HEIGHT))
        # screen.blit(fon, (0, 0))
        font = pygame.font.Font(None, 50)
        text_coord = WIDTH // 2
        for line in intro_text:
            string_rendered = font.render(line, 1, pygame.Color('black'))
            intro_rect = string_rendered.get_rect()
            text_coord += 10
            intro_rect.top = text_coord
            intro_rect.x = 10
            text_coord += intro_rect.height
            screen.blit(string_rendered, intro_rect)
        fl = 0
        while True:
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                elif event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_1:
                        pygame.mixer.music.pause()
                    elif event.key == pygame.K_2:
                        pygame.mixer.music.unpause()
                    else:
                        fl = 1
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    fl = 1
                if fl:
                    for el in all_sprites:
                        el.kill()
                    self.hero.bottles_of_water = 3
                    self.camera.dx, self.camera.dy, self.camera.fl = 0, 0, 0
                    self.hero, self.level_x, self.level_y = generate_level(field)
                    return  # начинаем игру1
            pygame.display.flip()
            clock.tick(FPS)


if __name__ == "__main__":
    remaining_time = 0
    level = 1
    time = pygame.time.Clock
    running = True
    sky = load_image('landscape.jpg')
    start_screen()
    field = load_level('map.txt')
    game = Game(screen, level, *generate_level(field))
    pygame.mixer.music.set_volume(0.5)
    pygame.time.set_timer(MYEVENTTYPE, 2000)
    while running:
        screen.blit(sky, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                terminate()
            elif event.type == MYEVENTTYPE:
                game.hero.bottles_of_water -= 1
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_1:
                    pygame.mixer.music.pause()
                elif event.key == pygame.K_2:
                    pygame.mixer.music.unpause()
        game.update()
    pygame.quit()
