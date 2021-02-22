import os
import sys
import pygame
import pygame_gui

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
danger = pygame.sprite.Group()


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


def game_over():
    # intro_text = ["GAME OVER", "Для того, чтобы начать с начала,", " нажмите любую клавишу"]
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

    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                terminate()
            elif (event.type == pygame.KEYDOWN and event.key != pygame.K_1 and
                  event.key != pygame.K_2) or \
                    event.type == pygame.MOUSEBUTTONDOWN:

                init()
                return  # начинаем игру1
        pygame.display.flip()
        clock.tick(FPS)


def terminate():
    pygame.quit()
    sys.exit()


def generate_level(level):
    player_, x, y = None, None, None
    for y in range(len(level)):
        for x in range(len(level[y])):
            if level[y][x] == '@':
                Tile('empty', x, y)
            elif level[y][x] == '#':
                Tile('wall', x, y)
            elif level[y][x] == '-':
                Tile('poison', x, y).add(danger)
            elif level[y][x] == '&':
                Tile('piece_ground', x, y)
            elif level[y][x] == 'h':
                Tile('piece_ground', x, y)
                player_ = Girls(0.1, x, y)
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

    def update2(self):
        self.rect.y += tile_height
        if pygame.sprite.spritecollideany(self, tiles_group):
            if pygame.sprite.spritecollideany(self, danger):
                print('game over')
                self.rect.y += tile_height
                game_over()
            self.rect.x += clock.tick(FPS) * self.v
            if pygame.key.get_pressed()[pygame.K_RIGHT]:
                self.rect.x += tile_width
            if pygame.key.get_pressed()[pygame.K_UP]:
                self.rect.y -= tile_height * 2
            if pygame.key.get_pressed()[pygame.K_LEFT]:
                self.rect.x -= tile_width
            self.rect.y -= tile_height


class Camera:
    # зададим начальный сдвиг камеры
    def __init__(self):
        self.dx = 0
        self.dy = 0

    # сдвинуть объект obj на смещение камеры
    def apply(self, obj):
        obj.rect.x += self.dx
        obj.rect.y += self.dy
        '''if 0 <= obj.rect.x < WIDTH:
            obj.rect.x %= (level_x * tile_width)
        if 0 <= obj.rect.y < HEIGHT:
            obj.rect.y %= (level_y * tile_height)'''
        # obj.rect.y %= (level_y * tile_height)

    # позиционировать камеру на объекте target
    def update(self, target):
        if not(0 <= target.rect.x < WIDTH):
            self.dx = -(target.rect.x + target.rect.w // 2 - WIDTH // 2)
        if not(0 <= target.rect.y < HEIGHT):
            print(target.rect.y + target.rect.h // 2 - HEIGHT // 2, target.rect.y)
            self.dy = -(target.rect.y + target.rect.h // 2 - HEIGHT // 2)


def init():
    global player
    # screen.fill((0, 0, 0))
    for el in all_sprites:
        el.kill()
    camera.dx, camera.dy = 0, 0
    # player.x, player.y, player.v = 0, 0, 1
    player, level_x, level_y = generate_level(field)
    # camera.apply(player)
    # camera.update(player)


def start_screen():
    pygame.mixer.init()
    pygame.mixer.music.load('music.mp3')
    pygame.mixer.music.play(-1)
    intro_text = ["Девушка в пустыне", "",
                  "Найди сундук сокровищами, но следи за осташимся количество воды.",
                  "Для выключения музыки нажми - 1, для включения - 2"]
    '''text = pygame_gui.elements.ui_text_box.UITextBox('\n'.join(intro_text),
                                                     relative_rect=pygame.Rect((100, 100),
                                                                               (300, 100)),
                                                     manager=manager)
    text.set_active_effect(pygame_gui.TEXT_EFFECT_TYPING_APPEAR)'''
    # fon = pygame.transform.scale(load_image('fon.jpg'), (WIDTH, HEIGHT))
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
                return  # начинаем игру
        pygame.display.flip()
        clock.tick(FPS)


if __name__ == "__main__":
    remaining_time = 10

    manager = pygame_gui.UIManager((800, 600))
    time = pygame.time.Clock
    running = True
    # field = load_level('map_3.txt')  # (input('Введите название файла с уровнем '))
    sky = load_image('landscape.jpg')
    start_screen()
    field = load_level('map.txt')
    player, level_x, level_y = generate_level(field)
    camera = Camera()
    pygame.mixer.music.set_volume(0.5)
    while running:

        screen.blit(sky, (0, 0))
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
                terminate()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_1:
                    pygame.mixer.music.pause()
                    # pygame.mixer.music.stop()
                elif event.key == pygame.K_2:
                    pygame.mixer.music.unpause()
            # manager.process_events(event)

        camera.update(player)
        # обновляем положение всех спрайтов
        for sprite in all_sprites:
            camera.apply(sprite)
        player.update2()
        all_sprites.update()
        all_sprites.draw(screen)
        player_group.draw(screen)
        t = clock.tick(FPS)
        '''manager.update(t)
        manager.draw_ui(screen)'''
        pygame.display.flip()
        # print(clock.
    pygame.quit()
