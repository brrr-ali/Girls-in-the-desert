import os
import sys
import random
import pygame

pygame.init()
FPS = 10
level_x, level_y = 16, 12
WIDTH = 800
HEIGHT = 600
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()


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
    'piece_ground': load_image('кусокземли.png', -1),
    'poison': load_image('poison.png', -1)
}
player_image = load_image('лесенкавлево.png')
tile_width = tile_height = 50
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()


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


def make_level():
    p = ['.', '#', '-', '&', '@']
    n = [['.' for _ in range(level_x)] for __ in range(level_y)]
    for i in range(20):
        n[random.randint(0, level_y - 1)][random.randint(0, level_x - 1)] = random.choice(p)
    return n


def terminate():
    pygame.quit()
    sys.exit()


def generate_level(level):
    new_player, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '@':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '-':
                Tile('poison', x, y)
            elif level[y][x] == '&':
                Tile('piece_ground', x, y)
            elif level[y][x] == 'h':
                new_player = Girls(0.1, x, y + 1)
    # вернем игрока, а также размер поля в клетках

    return new_player, x + 1, y + 1


class Tile(pygame.sprite.Sprite):
    def __init__(self, tile_type, pos_x, pos_y):
        super().__init__(tiles_group, all_sprites)
        self.image = tile_images[tile_type]
        self.rect = self.image.get_rect().move(
            tile_width * pos_x, tile_height * pos_y)


class Girls(pygame.sprite.Sprite):
    def __init__(self, v, x, y, *group):
        super().__init__(*group)
        self.v, self.x, self.y = v, x, y - 10
        self.girl = AnimatedSprite(load_image("girlr.png", -1), 3, 1, x * tile_width,
                                   y * tile_height)
        self.rect = self.girl.rect
        all_sprites.add(self.girl)

    def update(self):
        # print(pygame.sprite.spritecollideany(self, tiles_group))
        if pygame.sprite.spritecollideany(self, tiles_group):
            self.girl.rect.x += clock.tick(FPS) * self.v
            if pygame.key.get_pressed()[pygame.K_RIGHT]:
                self.girl.rect.x += 10
            if pygame.key.get_pressed()[pygame.K_UP]:
                self.girl.rect.y -= 10


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


if __name__ == "__main__":
    time = pygame.time.Clock
    running = True
    # start_screen()
    # field = load_level('map_3.txt')  # (input('Введите название файла с уровнем '))
    sky = load_image('landscape.jpg')
    field = load_level('map.txt')
    player, level_x, level_y = generate_level(field)
    # camera = Camera()
    # hero = Girls(30, )
    money = AnimatedSprite(load_image("money1.jpg", -1), 7, 2, 50, 50)
    while running:
        screen.blit(sky, (0, 0))
        # screen.fill('black')
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                terminate()

        # изменяем ракурс камеры
        # player.update()
        # camera.update(player)
        # обновляем положение всех спрайтов
        # for sprite in all_sprites:
        # camera.apply(sprite)

        all_sprites.update()
        player.update()
        all_sprites.draw(screen)
        player_group.draw(screen)
        pygame.display.flip()
        clock.tick(FPS)
    pygame.quit()
