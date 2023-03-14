from settings import *
import pygame as pg
import math as m
from main import Game
import random as r
import sys

class Player:
    def __init__(self, game: Game):
        self.game = game
        self.x, self.y = PLAYER_POS
        self.angle = PLAYER_ANGLE
        self.shot = False
        self.health = PLAYER_MAX_HEALTH
        self.rel = 0
        self.health_recovery_delay = 1
        self.time_prev = pg.time.get_ticks()
        
    def recover_health(self):
        if self.check_health_recovery_delay() and self.health < PLAYER_MAX_HEALTH:
            self.health += 1
        
        
    def check_health_recovery_delay(self):
        time_now = pg.time.get_ticks()
        if time_now - self.time_prev > self.health_recovery_delay:
            self.time_prev = time_now
            return True
    def check_win(self):
        if self.game.npc_count == 0:
            self.game.screen.fill("black")
            self.game.object_renderer.win()
            pg.display.flip()
            pg.time.delay(1500)
            self.game.new_game()
    
    def check_game_over(self):
        if self.health < 1:
            self.game.object_renderer.game_over()
            pg.display.flip()
            pg.time.delay(1500)
            self.game.new_game()
    
    
    def get_damage(self, damage):
        self.health -= damage
        self.game.object_renderer.player_damage()
        self.game.sound.player_pain.play()
        self.check_game_over()
    def oops(self):
        self.x, self.y = r.randint(1, 30), r.randint(1, 30)
        
    def movement(self):
        sin_a = m.sin(self.angle)
        cos_a = m.cos(self.angle)
        dx, dy = 0, 0
        speed = PLAYER_SPEED * self.game.dt
        speed_sin = speed * sin_a
        speed_cos = speed * cos_a
        
        
        keys = pg.key.get_pressed()
        if keys[pg.K_w]:
            dx += speed_cos
            dy += speed_sin
        if keys[pg.K_s]:
            dx -= speed_cos
            dy -= speed_sin
        if keys[pg.K_a]:
            dx += speed_sin
            dx += -speed_cos
        if keys[pg.K_d]:
            dx -= speed_sin
            dy += speed_cos
            
        self.check_wall_collision(dx, dy)
        
        if keys[pg.K_LEFT]:
            self.angle -= PLAYER_ROT_SPEED * self.game.dt
        if keys[pg.K_RIGHT]:
            self.angle += PLAYER_ROT_SPEED * self.game.dt
        self.angle %= m.tau
    def check_wall(self, x, y):
        if self.game.admin.noclip:
            return True
        return (x, y) not in self.game.map.world_map
    
    def check_wall_collision(self, dx, dy):
        scale = PLAYER_SIZE_SCALE / self.game.dt
        if self.check_wall(int(self.x + dx * scale), int(self.y)):
            self.x += dx
        if self.check_wall(int(self.x), int(self.y + dy * scale)):
            self.y += dy
        
    def draw(self):
        pg.draw.line(self.game.screen, 'yellow', (self.x * 100, self.y * 100), (self.x * 100 + WIDTH * m.cos(self.angle), self.y * 100 + WIDTH * m.sin(self.angle)), 2)
        pg.draw.circle(self.game.screen, 'green', (self.x * 100, self.y * 100), 15)
    
    def mouse_control(self):
        mx, my = pg.mouse.get_pos()
        if mx < MOUSE_BORDER_LEFT or mx > MOUSE_BORDER_RIGHT:
            pg.mouse.set_pos([HALF_WIDTH, HALF_HEIGHT])
        self.rel = pg.mouse.get_rel()[0]
        self.rel = max(-MOUSE_MAX_REL, min(MOUSE_MAX_REL, self.rel))
        self.angle += self.rel * MOUSE_SENSITIVITY * self.game.dt
    def update(self):
        self.movement()
        self.mouse_control()
        self.recover_health()
        self.check_win()
    @property
    def pos(self):
        return self.x, self.y
    
    @property
    def map_pos(self):
        return int(self.x), int(self.y)
    
    def single_fire_event(self, e):
        if e.type == pg.MOUSEBUTTONDOWN:
            if e.button == 1 and not self.shot and not self.game.weapon.reloading:
                self.shot = True
                self.game.sound.shotgun.play()
                self.game.weapon.reloading = True
    
    
    