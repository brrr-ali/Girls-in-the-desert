import os
import random
import sys
import pygame

pygame.init()
FPS = 30
WIDTH = 800
HEIGHT = 600
THIRSTY = pygame.USEREVENT + 1
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
LEVEL_MAPS = {1: 'map.txt', 2: 'map2.txt', 3: 'map3.txt', 4: 'map4.txt', 5: 'map5.txt'}
TIME_IN_LEVEl = [5, 10, 10, 10, 10]
GRAVITY = 0.2


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
    'bottle_of_water': load_image('bottle.png', -1),
    'piece_ground': load_image('кусокземли.png', -1),
    'poison': load_image('poison.png', -1),
    'chest': load_image('chest.png', -1),
}
tile_width = tile_height = 50
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
danger = pygame.sprite.Group()
bottles = pygame.sprite.Group()
chest = pygame.sprite.Group()


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
                bottles.add(Tile('bottle_of_water', x, y))
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '-':
                Tile('poison', x, y).add(danger)
            elif level[y][x] == '&':
                Tile('piece_ground', x, y)
            elif level[y][x] == 'h':
                Tile('piece_ground', x, y)
                player_ = Girl(x, y - 1)
            elif level[y][x] == 'c':
                Tile('chest', x, y).add(chest)
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


class Girl(AnimatedSprite):
    def __init__(self, x, y):
        super().__init__(load_image("girlr.png", -1), 3, 1, x * tile_width, y * tile_height)
        self.v, self.x, self.y = 0.1, x, y
        player_group.add(self)
        self.bottles_of_water = 3

    def update(self):
        super().update()
        if pygame.sprite.spritecollideany(self, tiles_group):
            if pygame.sprite.spritecollideany(self, bottles):
                self.bottles_of_water += 1
                game.remaining_time -= 2000
                pygame.sprite.spritecollideany(self, bottles).kill()
            if pygame.sprite.spritecollideany(self, chest):
                game.win()
        self.rect.y += tile_height
        if pygame.sprite.spritecollideany(self, tiles_group):
            if pygame.sprite.spritecollideany(self, bottles):
                self.bottles_of_water += 1
                game.remaining_time -= 2000
                pygame.sprite.spritecollideany(self, bottles).kill()
            if pygame.sprite.spritecollideany(self, chest):
                game.win()
            if pygame.sprite.spritecollideany(self, danger):
                # self.rect.y += tile_height
                game.game_over(['Вы погибли при сражении с опасностью.'])
            self.rect.x += tile_width * self.v
            if pygame.key.get_pressed()[pygame.K_RIGHT]:
                self.rect.x += tile_width
            if pygame.key.get_pressed()[pygame.K_UP]:
                self.rect.y -= tile_height * 2
            self.rect.y -= tile_height
        if self.rect.y >= HEIGHT:
            game.game_over(['Вы упали в пропасть.', 'В следущий раз будте внимательней.'])

        '''if pygame.sprite.spritecollideany(self, tiles_group):
            if pygame.key.get_pressed()[pygame.K_RIGHT]:
                self.rect.x += tile_width
            if pygame.key.get_pressed()[pygame.K_UP]:1
                self.rect.y -= tile_height * 2
            self.rect.x += tile_width * self.v
        if self.rect.y >= HEIGHT:
            game.game_over()
        if pygame.sprite.spritecollideany(self, chest):
            game.win()
        if pygame.sprite.spritecollideany(self, danger):
            game.game_over()
        if pygame.sprite.spritecollideany(self, bottles):
            self.bottles_of_water += 1
            game.remaining_time -= 2000
            pygame.sprite.spritecollideany(self, bottles).kill()'''


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
    pygame.mixer.music.load('music2.mp3')
    pygame.mixer.music.play(-1)
    game.new_play(["Девушка в пустыне", "",
                   "Найди сундук сокровищами, но следи за осташимся количество воды.",
                   "Для выключения музыки нажми - 1, для включения - 2"],
                  pygame.font.Font(None, 30))


'''class Particle(pygame.sprite.Sprite):
    # сгенерируем частицы разного размера
    fire = [load_image("star.png")]
    for scale in (5, 10, 20):
        fire.append(pygame.transform.scale(fire[0], (scale, scale)))

    def __init__(self, pos, dx, dy):
        super().__init__(all_sprites)
        self.image = random.choice(self.fire)
        self.rect = self.image.get_rect()

        # у каждой частицы своя скорость — это вектор
        self.velocity = [dx, dy]
        # и свои координаты
        self.rect.x, self.rect.y = pos

        # гравитация будет одинаковой (значение константы)
        self.gravity = GRAVITY

    def update(self):
        # применяем гравитационный эффект:
        # движение с ускорением под действием гравитации
        self.velocity[1] += self.gravity
        # перемещаем частицу
        self.rect.x += self.velocity[0]
        self.rect.y += self.velocity[1]
        # убиваем, если частица ушла за экран
        if not self.rect.colliderect((0, 0, WIDTH, HEIGHT)):
            self.kill()
'''


class Game:
    def __init__(self, level):
        self.hero, self.level_x, self.level_y = generate_level(load_level(LEVEL_MAPS[level]))
        self.level = level
        self.remaining_time = 0
        self.camera = Camera()

    def update(self):
        self.camera.update(self.hero)
        # обновляем положение всех спрайтов
        Tile('bottle_of_water', 0, 0)
        font = pygame.font.Font(None, 50)
        text = font.render(str(self.hero.bottles_of_water), True, (0, 0, 0))
        screen.blit(text, (30, 20))
        for sprite in all_sprites:
            self.camera.apply(sprite)
        all_sprites.update()
        all_sprites.draw(screen)
        player_group.draw(screen)
        t = clock.tick(FPS)
        self.remaining_time += t
        if (self.remaining_time >= TIME_IN_LEVEl[self.level - 1] * 1000
                or self.hero.bottles_of_water < 0):
            self.game_over(['У вас закончилась вода'])
        pygame.display.flip()

    def win(self):
        self.level += 1
        self.new_play(['YOU WIN!'], pygame.font.Font(None, 50))

    def game_over(self, reason):
        self.new_play(['GAME OVER', *reason], pygame.font.Font(None, 50))

    def new_play(self, intro_text, font):
        screen.blit(sky, (0, 0))
        text_coord = 10
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
                    self.__init__(self.level)
                    return  # начинаем игру
            pygame.display.flip()
            clock.tick(FPS)


if __name__ == "__main__":
    remaining_time = 0
    time = pygame.time.Clock
    running = True
    sky = load_image('landscape.jpg')
    game = Game(1)
    start_screen()
    pygame.mixer.music.set_volume(0.5)
    pygame.time.set_timer(THIRSTY, 2000)
    while running:
        screen.blit(sky, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                terminate()
            elif event.type == THIRSTY:
                game.hero.bottles_of_water -= 1
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_1:
                    pygame.mixer.music.pause()
                elif event.key == pygame.K_2:
                    pygame.mixer.music.unpause()
        game.update()
    pygame.quit()
