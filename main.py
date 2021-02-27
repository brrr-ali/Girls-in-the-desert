import os
import random
import sys
import pygame

pygame.init()
FPS = 20
WIDTH = 800
HEIGHT = 600
THIRSTY = pygame.USEREVENT + 1
screen = pygame.display.set_mode((WIDTH, HEIGHT))
clock = pygame.time.Clock()
LEVEL_MAPS = {1: 'map.txt', 2: 'map2.txt', 3: 'map3.txt', 4: 'map4.txt', 5: 'map5.txt',
              6: 'map6.txt', 7: 'map7.txt', 8: 'map8.txt', 9: 'map9.txt', 10: 'map10.txt'}
TIME_IN_LEVEl = [5, 10, 10, 10, 10, 10, 10, 10, 10, 10]
count_of_jewerly = 0
loss_of_jewelry = 0
GRAVITY = 0.35
pygame.display.set_caption('Girl in desert')


def load_image(name, colorkey=None):
    # функция для загрузки изображений
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
    'piece_ground': load_image('ground.png', -1),
    'poison': load_image('poison.png', -1),
    'chest': load_image('chest.png', -1),
    'jew': load_image('ringpurple.png', -1),
}
tile_width = tile_height = 50
all_sprites = pygame.sprite.Group()
tiles_group = pygame.sprite.Group()
player_group = pygame.sprite.Group()
danger = pygame.sprite.Group()
bottles = pygame.sprite.Group()
chest = pygame.sprite.Group()
particles = pygame.sprite.Group()
enemy = pygame.sprite.Group()
jewerly = pygame.sprite.Group()


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
            elif level[y][x] == 'e':
                Enemy(x, y)
            elif level[y][x] == 'j':
                Tile('jew', x, y).add(jewerly)
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


class Enemy(AnimatedSprite):
    def __init__(self, x, y):
        super().__init__(load_image("enemy.png", -1), 3, 1, x * tile_width, y * tile_height)
        self.v, self.x, self.y = 0.1, x, y
        enemy.add(self)

    def update(self):
        super().update()
        # перемещение врага
        self.rect.y += tile_height
        if pygame.sprite.spritecollideany(self, tiles_group):
            self.rect.y -= tile_height
            if pygame.sprite.spritecollideany(self, bottles):
                pygame.sprite.spritecollideany(self, bottles).kill()
            self.rect.x += tile_width * self.v


class Girl(AnimatedSprite):
    def __init__(self, x, y):
        super().__init__(load_image("girlr.png", -1), 3, 1, x * tile_width, y * tile_height)
        self.v, self.x, self.y = 0.08, x, y
        player_group.add(self)
        self.bottles_of_water = 3

    def update(self):
        super().update()
        global loss_of_jewelry
        # проверяем пересечение девочки и предметов
        if pygame.sprite.spritecollideany(self, tiles_group):
            if pygame.sprite.spritecollideany(self, bottles):
                self.bottles_of_water += 1
                game.elapsed_time -= 2000
                pygame.sprite.spritecollideany(self, bottles).kill()
            if pygame.sprite.spritecollideany(self, chest):
                game.win()
            if pygame.sprite.spritecollideany(self, jewerly):
                loss_of_jewelry += 1
                pygame.sprite.spritecollideany(self, jewerly).kill()
            if pygame.sprite.spritecollideany(self, enemy):
                game.game_over(['Этот человек отобрал у вас всю воду.'])
        self.rect.y += tile_height
        if pygame.sprite.spritecollideany(self, tiles_group):
            if pygame.sprite.spritecollideany(self, bottles):
                self.bottles_of_water += 1
                game.elapsed_time -= 2000
                pygame.sprite.spritecollideany(self, bottles).kill()
            if pygame.sprite.spritecollideany(self, chest):
                game.win()
            if pygame.sprite.spritecollideany(self, jewerly):
                loss_of_jewelry += 1
                pygame.sprite.spritecollideany(self, jewerly).kill()
            if pygame.sprite.spritecollideany(self, danger):
                game.game_over(['Вы задели яд.'])
            if pygame.key.get_pressed()[pygame.K_UP]:
                for i in range(0, tile_height, int(tile_height * 0.2)):
                    self.rect.y -= i
            self.rect.y -= tile_height
            if pygame.key.get_pressed()[pygame.K_RIGHT]:
                for i in range(0, int(tile_width * 1.2), 20):
                    self.rect.x += i
                    if pygame.sprite.spritecollideany(self, bottles):
                        self.bottles_of_water += 1
                        game.elapsed_time -= 2000
                        pygame.sprite.spritecollideany(self, bottles).kill()
                    if pygame.sprite.spritecollideany(self, danger):
                        game.game_over(['Вы задели яд.'])
                    if pygame.sprite.spritecollideany(self, enemy):
                        game.game_over(['Этот человек отобрал у вас всю воду.'])
                    if pygame.sprite.spritecollideany(self, jewerly):
                        loss_of_jewelry += 1
                        pygame.sprite.spritecollideany(self, jewerly).kill()
            self.rect.x += tile_width * self.v
        if self.rect.y >= HEIGHT:
            game.game_over(['Вы упали в пропасть.', 'В следущий раз будте внимательней.'])


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
    # включаем фоновую музыку
    pygame.mixer.init()
    pygame.mixer.music.load('data/music.mp3')
    pygame.mixer.music.play(-1)
    game.new_play(["        ДЕВУШКА В ПУСТЫНЕ", "",
                   "    Найди сундук с сокровищами, но следи ",
                   "        за оставшимся количеством воды.",
                   "    Для выключения музыки нажми - 1,",
                   "        для включения - 2"],
                  pygame.font.Font('data/ofont_ru_Roland.ttf', 35))


def create_particles(position):
    # количество создаваемых частиц
    particle_count = 20
    # возможные скорости
    numbers = range(-5, 6)
    for _ in range(particle_count):
        Particle(position, random.choice(numbers), random.choice(numbers)).add(particles)


class Particle(pygame.sprite.Sprite):
    # сгенерируем частицы разного размера
    fire = [load_image("bottle.png", -1)]
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


def clicked(rect, pos):
    # проверяет входит ли точка в заданную область
    return rect[0] <= pos[0] <= rect[0] + rect[2] and rect[1] <= pos[1] <= rect[1] + rect[3]


shop_fon = load_image('background0.jpg')
size_picture = 250, 188
shopwindows = [load_image('background0.jpg'), load_image('background1.png'),
               load_image('background2.png'), load_image('background3.jpg')]
size_button = 250, 40


class Game:
    def __init__(self, level, *args):
        if level in LEVEL_MAPS:
            self.hero, self.level_x, self.level_y = generate_level(load_level(LEVEL_MAPS[level]))
        else:
            self.win('Вы прошли все уровни.', 'Поздравляем с победой!')
        self.level = level
        self.elapsed_time = 0
        self.camera = Camera()
        if args:
            self.background_status = args[0]
        else:
            self.background_status = [2, 0, 0, 0]  # 0 - не куплено, 1 - куплено, 2 - выбрано
        self.sky = shopwindows[self.background_status.index(2)]
        self.counter_bottle = load_image('bottle.png', -1)
        self.counter_money = load_image('ringpurple.png', -1)

    def update(self):
        self.camera.update(self.hero)
        # обновляем положение всех спрайтов
        # делаем счетчик добытых ресурсов
        screen.blit(self.counter_bottle, (0, 0))
        screen.blit(self.counter_money, (70, 10))
        font = pygame.font.Font('data/ofont_ru_Roland.ttf', 20)
        text = font.render(str(self.hero.bottles_of_water), True, (0, 0, 0))
        text2 = font.render(str(count_of_jewerly + loss_of_jewelry), True, (0, 0, 0))
        screen.blit(text, (30, 20))
        screen.blit(text2, (130, 20))
        for sprite in all_sprites:
            self.camera.apply(sprite)
        all_sprites.update()
        all_sprites.draw(screen)
        enemy.draw(screen)
        player_group.draw(screen)
        t = clock.tick(FPS)
        self.elapsed_time += t
        if (self.elapsed_time >= TIME_IN_LEVEl[self.level - 1] * 1000
                or self.hero.bottles_of_water < 0):
            self.game_over(['У вас закончилась вода'])
        pygame.display.flip()

    def win(self, *text):
        global count_of_jewerly, loss_of_jewelry
        count_of_jewerly += loss_of_jewelry
        loss_of_jewelry = 0
        self.level += 1
        create_particles((WIDTH // 2, HEIGHT // 2))
        self.new_play(['        ПОБЕДА!', '',
                       'Странник, ты прошел этот путь,',
                       '    но это было только его начало...', *text],
                      pygame.font.Font('data/ofont_ru_Roland.ttf', 35))

    def game_over(self, reason):
        global loss_of_jewelry
        loss_of_jewelry = 0
        self.new_play(['            ПРОВАЛ...', '',
                       'Умереть в пустыне - не страшно',
                       '    там вас точно ждет покой.',
                       *reason], pygame.font.Font('data/ofont_ru_Roland.ttf', 35))

    def new_play(self, intro_text, font):
        while True:
            # выводим текст
            screen.blit(self.sky, (0, 0))
            screen.blit(shop_image, shop_rect[:2])
            if intro_text[0] == '        ПОБЕДА!':
                text = pygame.font.Font('data/ofont_ru_Roland.ttf', 50).render(
                    str(count_of_jewerly),
                    True, (0, 0, 0))
                screen.blit(self.counter_money, (0, 60))
                screen.blit(text, (50, 60))
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
            # отрисовываем частицы
            particles.update()
            particles.draw(screen)
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
                    # проверяем хочет ли игрок в магазин
                    if clicked(shop_rect, event.pos):
                        self.shop()
                    else:
                        fl = 1
                if fl:
                    for el in all_sprites:
                        el.kill()
                    self.__init__(self.level, self.background_status)
                    return  # начинаем игру
            pygame.display.flip()
            clock.tick(FPS)

    def shop(self):
        # создаем новый Surface, на него накладываем изображение фонов и делаем "кнопки"
        screen_shop = pygame.display.set_mode((WIDTH, HEIGHT))
        sales = [0, 5, 7, 10]
        rect_picture = [(100, i * size_picture[1] + 70 * (i + 1))
                        for i in range(len(sales) // 2)] + [
                           (WIDTH - (size_picture[0] + 100), i * size_picture[1] + 70 * (i + 1))
                           for i in range(len(sales) // 2)]
        rect_button = [(el[0], el[1] + size_picture[1] + 10, *size_button) for el in rect_picture]
        screen_shop.fill(pygame.Color(200, 200, 200))
        font = pygame.font.Font('data/ofont_ru_Roland.ttf', 46)
        string_rendered = font.render('Магазин', 1, pygame.Color(55, 55, 55))
        screen_shop.blit(string_rendered, (300, 5, 150, 150))
        global count_of_jewerly
        screen_shop.blit(self.counter_money, (5, 20))
        while True:
            text = pygame.font.Font('data/ofont_ru_Roland.ttf', 50).render(
                str(count_of_jewerly),
                True, (0, 0, 0))
            screen_shop.fill(pygame.Color(200, 200, 200),
                             pygame.Rect(50, 0, 40, 80))
            screen_shop.blit(text, (50, 0))
            screen.blit(screen_shop, (0, 0))
            for i in range(len(rect_button)):
                font = pygame.font.Font('data/ofont_ru_Roland.ttf', 26)
                fon = pygame.transform.scale(shopwindows[i], size_picture)
                screen_shop.blit(fon, rect_picture[i])
                screen_shop.fill(pygame.Color('white'), pygame.Rect(*rect_button[i]))
                # проверяем состояние каждого из фонов
                # возможные: 0 - не куплено, 1 - куплено, 2 - используется сейчас
                if game.background_status[i] == 0:
                    string_rendered = font.render(str(sales[i]), 1, pygame.Color(55, 55, 55))
                    screen_shop.blit(string_rendered, rect_button[i])
                elif game.background_status[i] == 1:
                    string_rendered = font.render('куплено', 1, pygame.Color(55, 55, 55))
                    screen_shop.blit(string_rendered, rect_button[i])
                elif game.background_status[i] == 2:
                    screen_shop.blit(load_image('check-mark.png'), (
                        rect_button[i][0] + size_button[0] // 2, rect_button[i][1], *size_button))
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    terminate()
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    for i in range(len(rect_button)):
                        # при нажатии на кнопку меняем статус фона
                        if clicked(rect_button[i], event.pos):
                            if self.background_status[i] == 0:
                                if sales[i] <= count_of_jewerly:
                                    count_of_jewerly -= sales[i]
                                    self.background_status[i] = 1
                                    error_size = 323, 39
                                    screen_shop.fill(pygame.Color(200, 200, 200),
                                                     pygame.Rect((WIDTH - error_size[0]) // 2,
                                                                 HEIGHT - error_size[1],
                                                                 *error_size))
                                else:
                                    string_rendered = font.render('Украшений не достаточно', 1,
                                                                  pygame.Color(55, 55, 55))
                                    screen_shop.blit(string_rendered,
                                                     ((WIDTH - string_rendered.get_width()) // 2,
                                                      HEIGHT - string_rendered.get_height(),
                                                      string_rendered.get_width(),
                                                      string_rendered.get_height()))
                            elif self.background_status[i] == 1:
                                self.background_status[self.background_status.index(2)] = 1
                                self.background_status[i] = 2
                                self.sky = shopwindows[i]
                                error_size = 323, 39
                                screen_shop.fill(pygame.Color(200, 200, 200),
                                                 pygame.Rect((WIDTH - error_size[0]) // 2,
                                                             HEIGHT - error_size[1],
                                                             *error_size))
                elif event.type == pygame.KEYDOWN:
                    # для того чтобы выйти из магазина, нажимаем на любую клавишу клавиатуры
                    return
            pygame.display.flip()
            clock.tick(FPS)


if __name__ == "__main__":
    elapsed_time = 0
    time = pygame.time.Clock
    running = True
    shop_image = load_image('shop.png', -1)
    shop_rect = (650, 450, *shop_image.get_size())
    game = Game(1)
    start_screen()
    pygame.mixer.music.set_volume(0.5)
    pygame.time.set_timer(THIRSTY, 2000)
    while running:
        screen.blit(game.sky, (0, 0))
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
