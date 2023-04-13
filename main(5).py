import pygame
import random
import time
import sys
import os
import math

weapons = ['pistol', 'shotgun', 'machine gun']
pygame.init()
pygame.display.set_caption("Game")
size = width, height = 1200, 800
screen = pygame.display.set_mode(size)


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


bg = load_image('bg1.png')
begin_im = load_image('begin.png')
im1 = load_image('1.png')
im2 = load_image('2.png')
im3 = load_image('3.png')
go_im = load_image('gameover.png')
gobg_im = load_image('gameover_bg.png')
gomm_im = load_image('gameover_mm.png')
play_im = load_image('play.png')

shoot = pygame.mixer.Sound("data/выстрел.mp3")
recharge = pygame.mixer.Sound("data/перезарядка.mp3")
lose = pygame.mixer.Sound("data/проигрыш.mp3")
hurt = pygame.mixer.Sound("data/hurt.mp3")

all_sprites = pygame.sprite.Group()


class Bullet_Sprite(pygame.sprite.Sprite):
    def __init__(self, x, y, x1, y1, group):
        super().__init__(group)     
        self.x1 = x1
        self.y1 = y1
        self.x = x
        self.y = y
        
        image = self.rotate(load_image("bullet.png"), self.x, self.y, self.x1, self.y1)
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y

    def update(self, x, y):
        self.rect.x = x
        self.rect.y = y

    def rotate(self, image, x, y, x1, y1):
        dx = x1 - x
        dy = y1 - y

        angle = (180 / math.pi) * math.atan2(-dy, dx) - 90
        image = pygame.transform.rotate(image, angle)
        return image


class Bullet:
    def __init__(self, x, y, x_1, y_1, speed):
        self.x, self.y = x, y
        self.speed_x = speed * ((x_1 - x) / (((x - x_1) ** 2 + (y - y_1) ** 2))**0.5)
        self.speed_y = speed * ((y_1 - y) / (((x - x_1) ** 2 + (y - y_1) ** 2))**0.5)
        
        self.sprite = Bullet_Sprite(self.x, self.y, x_1, y_1, all_sprites)

    def update(self, screen):
        self.x += self.speed_x
        self.y += self.speed_y
        
        self.sprite.update(self.x, self.y)
        # pygame.draw.circle(screen, pygame.Color('orange'), (self.x, self.y), 5)

    def get_coords(self):
        return self.x, self.y

    def get_sprite(self):
        return self.sprite    


class Player_Sprite(pygame.sprite.Sprite):

    image = load_image("player.png")

    def __init__(self, x, y, group):
        super().__init__(group)
        self.image = Player_Sprite.image
        self.rect = self.image.get_rect()

        self.rect.x = x
        self.rect.y = y

    def update(self, *args):
        self.rect.x = args[0]
        self.rect.y = args[1]


class Player_AnimatedSprite(pygame.sprite.Sprite):
    def __init__(self, x, y, group):
        super().__init__(group)
        sheet1 = load_image("Ходьба лево.png")
        sheet2 = load_image("Ходьба право.png")
        sheet3 = load_image("Стрельба лево.png")
        sheet4 = load_image("Стрельба право.png")
        self.frames_left = []
        self.frames_right = []
        self.shooting_left = []
        self.shooting_right = []
        self.frames_left = self.cut_sheet(sheet1, 4, 1, self.frames_left)
        self.frames_right = self.cut_sheet(sheet2, 4, 1, self.frames_right)
        self.shooting_left = self.cut_sheet(sheet3, 2, 1, self.shooting_left)
        self.shooting_right = self.cut_sheet(sheet4, 2, 1, self.shooting_right)
        self.cur_frame = 0
        self.image = self.frames_left[self.cur_frame]
        self.rect = self.rect.move(x, y)

    def cut_sheet(self, sheet, columns, rows, ar):
        self.rect = pygame.Rect(0, 0, sheet.get_width() // columns,
                                sheet.get_height())
        for j in range(rows):
            for i in range(columns):
                frame_location = (self.rect.w * i, self.rect.h * j)
                ar.append(sheet.subsurface(pygame.Rect(
                    frame_location, self.rect.size)))

        new_frame = []
        for i in ar:
            for _ in range(3):
                new_frame.append(i)
        ar = new_frame[:]
        return ar

    def update(self, x, y, flag):
        if flag:
            self.image = None
            if self.rect.x < flag:
                self.rect.x = x
                self.rect.y = y
                self.cur_frame = (self.cur_frame + 1) % len(self.shooting_right)
                self.image = self.shooting_right[self.cur_frame]
            else:
                self.rect.x = x
                self.rect.y = y
                self.cur_frame = (self.cur_frame + 1) % len(self.shooting_left)
                self.image = self.shooting_left[self.cur_frame]
        elif self.rect.x != x or self.rect.y != y:
            if self.rect.x < x:
                self.rect.x = x
                self.rect.y = y
                self.cur_frame = (self.cur_frame + 1) % len(self.frames_right)
                self.image = self.frames_right[self.cur_frame]
            else:
                self.rect.x = x
                self.rect.y = y
                self.cur_frame = (self.cur_frame + 1) % len(self.frames_left)
                self.image = self.frames_left[self.cur_frame]




class Player:
    def __init__(self, pos, r, width, height, speed_x, speed_y, weapon):
        # self.x, self.y, self.r = pos[0], pos[1], r
        self.x, self.y, self.r = width // 2, height // 2, r
        self.width, self.height = width, height
        self.speed_x, self.speed_y = speed_x, speed_y
        self.weapon = weapon

        self.sprite = Player_AnimatedSprite(self.x, self.y, all_sprites)
        self.w_sprite = pygame.sprite.Sprite()
        self.w_sprite.image = self.weapon_sprite()
        self.w_sprite.rect = self.w_sprite.image.get_rect()
        all_sprites.add(self.w_sprite)
        
        self.w_sprite.rect.x = 70
        self.w_sprite.rect.y = 650

    def update(self, screen):
        if self.x + self.speed_x + self.r >= self.width or self.x + self.speed_x - self.r <= 0:
            self.speed_x = self.speed_x * (-1)
        if self.y + self.speed_y + self.r >= self.height or self.y + self.speed_y - self.r <= 0:
            self.speed_y = self.speed_y * (-1)
        self.x += self.speed_x
        self.y += self.speed_y

        self.sprite.update(self.x, self.y, False)
        # pygame.draw.circle(screen, pygame.Color('green'), (self.x, self.y), self.r)

    def set_speed(self, x, y):
        self.speed_y = y
        self.speed_x = x

    def change_weapon(self, weapon):
        self.weapon = weapon
        self.w_sprite.image = self.weapon_sprite()

    def weapon_sprite(self):
        if self.weapon == 'pistol':
            image = load_image("weapon1.png")
        elif self.weapon == 'shotgun':
            image = load_image("weapon2.png")
        elif self.weapon == 'machine gun':
            image = load_image("weapon3.png")
            
        return image


class Enemy_Sprite(pygame.sprite.Sprite):
    def __init__(self, x, y, power, group):
        super().__init__(group)
        if power == 1:
            image = load_image("enemy1.png")
        if power == 2:
            image = load_image("enemy2.png")
        if power == 3:
            image = load_image("enemy3.png")        
        
        self.image = image
        self.rect = self.image.get_rect()
        
        self.rect.x = x
        self.rect.y = y

    def update(self, *args):
        self.rect.x = args[0]
        self.rect.y = args[1]


class Enemy:
    def __init__(self, pos, r, width, height, speed):
        self.x, self.y = pos[0], pos[1]
        self.width, self.height = width, height
        self.speed = speed
        self.flag = True
        if level == 'easy':
            self.power = random.choice([1, 1, 1, 1, 1, 1, 2, 2, 2, 3])
        elif level == 'medium':
            self.power = random.choice([1, 1, 1, 2, 2, 2, 2, 3, 3, 3])
        elif level == 'hard':
            self.power = random.choice([1, 1, 2, 2, 2, 3, 3, 3, 3, 3])
            
        self.r = r * self.power
        colors = ['white', 'blue', 'red']
        self.color = colors[self.power - 1]

        self.sprite = Enemy_Sprite(self.x, self.y, self.power, all_sprites)

    def explosion(self):
        # print('BOOM!')
        # pygame.draw.circle(screen, pygame.Color('red'), (self.x, self.y), self.r * 5)

        pygame.draw.rect(screen, (255, 0, 0, 10), (0, 0, width, height))
        self.flag = False
        all_sprites.remove(self.sprite)

    def update(self, screen, player_x, player_y):
        self.speed_x = self.speed * ((player_x - self.x) / (((self.x - player_x) ** 2 + (self.y - player_y) ** 2))**0.5)
        self.speed_y = self.speed * ((player_y - self.y) / (((self.x - player_x) ** 2 + (self.y - player_y) ** 2))**0.5)

        self.x += self.speed_x
        self.y += self.speed_y

        if self.flag:
            # pygame.draw.circle(screen, pygame.Color(self.color), (self.x, self.y), self.r)
            self.sprite.update(self.x, self.y)
        if abs(self.x - player_x) <= 30 and abs(self.y - player_y) <= 30 and self.flag:
            self.explosion()

    def get_coords(self):
        return self.x, self.y

    def get_power(self):
        return self.power

    def change_power(self):
        self.power -= 1

    def get_sprite(self):
        return self.sprite
    
    def is_collided(self, sprite1):
        return self.sprite.rect.colliderect(sprite1.rect)


def game_over(im1):
    screen.blit(im1, (0, 0))
    font = pygame.font.Font('data/F77 Minecraft.ttf', 50)
    text1 = font.render("Ваш счет: " + str(count), True, (255, 255, 255))
    text2 = font.render("Рекорд: " + str(record), True, (255, 255, 255))
    screen.blit(text1, (432, 130))
    screen.blit(text2, (432, 180))


def begin(im, level):
    screen.blit(im, (0, 0))
    font = pygame.font.Font('data/F77 Minecraft.ttf', 25)
    text = font.render("уровень: " + level, True, (255, 255, 255))
    screen.blit(text, (490, 670))


if __name__ == '__main__':
    count = 0
    
    life = 20
    count_life = 20
    weapon_count = 1
    win = True
    gameover = False
    
    f = open('Рекорд.txt', 'r+')
    f1 = f.readline()
    record = int(f1)
    level = 'easy'
    running = True
    screen.fill(pygame.Color('black'))

    pygame.mixer.music.load('data/bg_music.mp3')
    enemies_count = 5
    im = begin_im
    im_go = go_im
    ms = True
    pos = None
    fps = 20
    clock = pygame.time.Clock()
    enemies = []
    bullets = []
    player = Player([250, 300], 30, width, height, 0, 0, 'pistol')
    weapon_reloading = time.time()
    play = False
    
    pygame.mixer.music.play(-1)
    
    while running:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                running = False
            if event.type == pygame.MOUSEMOTION:
                if not play:
                    if 452 <= pygame.mouse.get_pos()[0] <= 748 and 302 <= pygame.mouse.get_pos()[1] <= 371:
                        im = im1
                    elif 452 <= pygame.mouse.get_pos()[0] <= 748 and 393 <= pygame.mouse.get_pos()[1] <= 460:
                        im = im2
                    elif 452 <= pygame.mouse.get_pos()[0] <= 748 and 482 <= pygame.mouse.get_pos()[1] <= 545:
                        im = im3
                    elif 452 <= pygame.mouse.get_pos()[0] <= 748 and 586 <= pygame.mouse.get_pos()[1] <= 644:
                        im = play_im
                    else:
                        im = begin_im
                        
                elif not win:
                    if 380 <= pygame.mouse.get_pos()[0] <= 819 and 476 <= pygame.mouse.get_pos()[1] <= 567:
                        im_go = gobg_im
                    elif 433 <= pygame.mouse.get_pos()[0] <= 767 and 589 <= pygame.mouse.get_pos()[1] <= 658:
                        im_go = gomm_im
                    else:
                        im_go = go_im

            elif event.type == pygame.MOUSEBUTTONDOWN:
                all_sprites.draw(screen)
                if play:
                    if win:
                        pygame.mixer.music.unpause()
                        if 70 < pygame.mouse.get_pos()[0] < 210 and 650 < pygame.mouse.get_pos()[1] < 730:
                            weapon = ['pistol', 'shotgun', 'machine gun']
                            weapon_count = weapon_count % 3 + 1
                            player.change_weapon(weapon[weapon_count - 1])

                        else:
                            if player.weapon == 'pistol' and time.time() - weapon_reloading > 1:
                                bullet = Bullet(player.x, player.y, pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1], 20)
                                bullets.append(bullet)
                                player.sprite.update(player.sprite.rect.x, player.sprite.rect.y, pygame.mouse.get_pos()[0])
                                shoot.play()
                                weapon_reloading = time.time()
                            elif player.weapon == 'shotgun' and time.time() - weapon_reloading > 3:
                                player.sprite.update(player.sprite.rect.x, player.sprite.rect.y,
                                                     pygame.mouse.get_pos()[0])
                                if (pygame.mouse.get_pos()[1] - player.y):
                                    tg = abs((pygame.mouse.get_pos()[0] - player.x) / (pygame.mouse.get_pos()[1] - player.y))
                                else:
                                    tg = abs((pygame.mouse.get_pos()[0] - player.x))
                                x1 = 10
                                y1 = x1 / tg
                                if pygame.mouse.get_pos()[0] <= player.x:
                                    x1 = -1 * x1
                                if pygame.mouse.get_pos()[1] <= player.y:
                                    y1 = y1 * -1
                                x1 = x1 + player.x
                                y1 = y1 + player.y

                                bullet1 = Bullet(player.x, player.y, x1 + 2,
                                                 y1 + 2, 20)
                                bullet2 = Bullet(player.x, player.y, x1 + 5,
                                                 y1 + 1, 20)
                                bullet3 = Bullet(player.x, player.y, x1, y1, 20)
                                bullet4 = Bullet(player.x, player.y, x1 - 1,
                                                 y1 - 1, 20)
                                bullet5 = Bullet(player.x, player.y, x1 - 2,
                                                 y1 - 2, 20)

                                bullets.append(bullet1)
                                bullets.append(bullet2)
                                bullets.append(bullet3)
                                bullets.append(bullet4)
                                bullets.append(bullet5)
                                shoot.play()
                                weapon_reloading = time.time()

                            elif player.weapon == "machine gun" and time.time() - weapon_reloading > 0.3:
                                player.sprite.update(player.sprite.rect.x, player.sprite.rect.y,
                                                     pygame.mouse.get_pos()[0])
                                bullet = Bullet(player.x, player.y, pygame.mouse.get_pos()[0], pygame.mouse.get_pos()[1], 20)
                                bullets.append(bullet)
                                shoot.play()
                                weapon_reloading = time.time()
                    else:
                        if 380 <= pygame.mouse.get_pos()[0] <= 819 and 476 <= pygame.mouse.get_pos()[1] <= 567:
                            win = True
                            ms = True
                            count_life = life
                            count = 0    
                            for elem in enemies:
                                all_sprites.remove(elem.get_sprite())
                            enemies = []
                            gameover = True
            else:
                if not gameover:
                    if 452 <= pygame.mouse.get_pos()[0] <= 748 and 302 <= pygame.mouse.get_pos()[1] <= 371:
                        level = 'easy'
                    elif 452 <= pygame.mouse.get_pos()[0] <= 748 and 393 <= pygame.mouse.get_pos()[1] <= 460:
                        level = 'medium'
                    elif 452 <= pygame.mouse.get_pos()[0] <= 748 and 482 <= pygame.mouse.get_pos()[1] <= 545:
                        level = 'hard'
                    elif 452 <= pygame.mouse.get_pos()[0] <= 748 and 586 <= pygame.mouse.get_pos()[1] <= 644:
                        play = True
                        gameover = False
                        win = True
                    
                elif gameover and (433 <= pygame.mouse.get_pos()[0] <= 767 and 589 <= pygame.mouse.get_pos()[1] <= 658):
                    play = False
                    ms = True
                    count_life = life
                    count = 0
                    for elem in enemies:
                        all_sprites.remove(elem.get_sprite())
                    enemies = []
                    gameover = False

        if play:
            if level == 'easy':
                enemies_count = 4
            if level == 'medium':
                enemies_count = 7
            if level == 'hard':
                enemies_count = 10
            
            r = random.randint(1, 10)
            if r == 5:
                if len(enemies) < enemies_count:
                    enemy = Enemy([random.randint(0, width), random.randint(0, 50)], 15, width, height, 5)
                    enemies.append(enemy)
    
                if len(enemies) < enemies_count:
                    enemy = Enemy([random.randint(0, width), random.randint(height - 50, height)], 15, width, height, 5)
                    enemies.append(enemy)
    
                if len(enemies) < enemies_count:
                    enemy = Enemy([random.randint(0, 50), random.randint(0, height)], 15, width, height, 5)
                    enemies.append(enemy)

                if len(enemies) < enemies_count:
                    enemy = Enemy([random.randint(width - 50, width), random.randint(0, height)], 15, width, height, 5)
                    enemies.append(enemy)
    
            keys = pygame.key.get_pressed()
    
            if win:

                pygame.mixer.music.unpause()
                
                if keys[pygame.K_a] and keys[pygame.K_w]:
                    player.set_speed(-5, -5)
                elif keys[pygame.K_w] and keys[pygame.K_d]:
                    player.set_speed(5, -5)
                elif keys[pygame.K_d] and keys[pygame.K_s]:
                    player.set_speed(5, 5)
                elif keys[pygame.K_a] and keys[pygame.K_s]:
                    player.set_speed(-5, 5)
                elif keys[pygame.K_a]:
                    player.set_speed(-5, 0)
                elif keys[pygame.K_d]:
                    player.set_speed(5, 0)
                elif keys[pygame.K_w]:
                    player.set_speed(0, -5)
                elif keys[pygame.K_s]:
                    player.set_speed(0, 5)
                else:
                    player.set_speed(0, 0)
    
                if keys[pygame.K_1]:
                    player.change_weapon('pistol')
                    weapon_count = 1
                if keys[pygame.K_2]:
                    player.change_weapon('shotgun')
                    weapon_count = 2
                if keys[pygame.K_3]:
                    player.change_weapon('machine gun')
                    weapon_count = 3
        
                # screen.fill(pygame.Color('black'))
                screen.blit(bg, (0, 0))
                all_sprites.draw(screen)
                player.update(screen)
    
                pygame.draw.rect(screen, pygame.Color("red"), (850, 700, 300, 20))
                pygame.draw.rect(screen, pygame.Color("green"), (850, 700, (300 / life) * count_life, 20))
    
                for i in enemies:
                    if i.flag:
                        i.update(screen, player.x, player.y)
                    else:
                        enemies.remove(i)
                        if count_life == 1:
                            win = False
                        count_life -= 1
                        hurt.play()
                for i in bullets:
                    i.update(screen)
                    all_sprites.draw(screen)
    
                    if i.get_coords()[0] > width or i.get_coords()[0] < 0 or i.get_coords()[1] > height or i.get_coords()[1] < 0:
                        bullets.remove(i)
    
                for i in bullets:
                    for j in enemies:
                        a = i.get_coords()[0]
                        b = i.get_coords()[1]
                        
                        a1 = j.get_coords()[0]
                        b1 = j.get_coords()[1]
        
                        # if (a - a1) ** 2 + (b - b1) ** 2 <= j.r ** 2:
                        if j.is_collided(i.get_sprite()):
                            if i in bullets:
                                bullets.remove(i)
                                all_sprites.remove(i.get_sprite())
                            j.change_power()
                            if j.get_power() == 0:
                                enemies.remove(j)
                                all_sprites.remove(j.get_sprite())
                            count += 1
                            record = max(record, count)
                            f.seek(0)
                            f.write(str(record))
                            print(record)


                if player.weapon == 'pistol':
                    if time.time() - weapon_reloading >= 1:
                        pygame.draw.rect(screen, pygame.Color("green"), (0, 0, width, 30))
                    else:
                        pygame.draw.rect(screen, pygame.Color("red"),
                                         pygame.Rect(0, 0, width * (time.time() - weapon_reloading), 30))

                elif player.weapon == 'shotgun':
                    if time.time() - weapon_reloading >= 3:
                        pygame.draw.rect(screen, pygame.Color("green"), (0, 0, width, 30))
                    else:
                        pygame.draw.rect(screen, pygame.Color("red"),
                                         pygame.Rect(0, 0, (width / 3) * (time.time() - weapon_reloading), 30))
                if player.weapon == 'machine gun':
                    if time.time() - weapon_reloading >= 0.3:
                        pygame.draw.rect(screen, pygame.Color("green"), (0, 0, width, 30))
    
                    else:
                        pygame.draw.rect(screen, pygame.Color("red"),
                                         pygame.Rect(0, 0, (width / 0.3) * (time.time() - weapon_reloading), 30))
                        # recharge.play()
        
            else:
                pygame.mixer.music.pause()
                game_over(im_go)
                gameover = True
                if ms:
                    lose.play(0)
                    ms = False
        else:
            begin(im, level)
            pygame.mixer.music.pause()

        clock.tick(fps)
        pygame.display.flip()
    pygame.quit()

