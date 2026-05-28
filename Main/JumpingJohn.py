import pygame
import sys
import math
import random
pygame.init()
SCREEN_WIDTH  = 800
SCREEN_HEIGHT = 500
screen = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))
pygame.display.set_caption("Jumping John")
clock = pygame.time.Clock()
FPS   = 60
SKY_BLUE    = (135, 206, 235)
SKY_DUSK    = ( 80,  60, 120)
SKY_NIGHT   = ( 15,  15,  40)
GREEN       = ( 34, 139,  34)
DARK_GREEN  = ( 20,  90,  20)
BROWN       = (139,  90,  43)
STONE       = (110, 110, 110)
DARK_STONE  = ( 70,  70,  70)
LAVA_RED    = (200,  40,  10)
LAVA_ORANGE = (255, 120,   0)
YELLOW      = (255, 220,   0)
COIN_GOLD   = (255, 200,   0)
WHITE       = (255, 255, 255)
BLACK       = (  0,   0,   0)
RED         = (220,  50,  50)
ORANGE      = (255, 140,   0)
GRAY        = (180, 180, 180)
DARK_GRAY   = ( 80,  80,  80)
PURPLE      = (120,  40, 180)
ICE_BLUE    = (180, 220, 255)
font_title = pygame.font.SysFont("Arial", 42, bold=True)
font_big   = pygame.font.SysFont("Arial", 32, bold=True)
font_mid   = pygame.font.SysFont("Arial", 24, bold=True)
font_small = pygame.font.SysFont("Arial", 20)
font_tiny  = pygame.font.SysFont("Arial", 16)
DIFFICULTY_SETTINGS = {
    "Easy":   {"enemy_speed_mult": 0.6, "lives": 5, "coin_bonus": 10, "color": GREEN},
    "Normal": {"enemy_speed_mult": 1.0, "lives": 3, "coin_bonus": 15, "color": YELLOW},
    "Hard":   {"enemy_speed_mult": 1.6, "lives": 2, "coin_bonus": 25, "color": RED},
}
selected_difficulty = "Normal"
class Platform:
    def __init__(self, x, y, w, h, color=GREEN, top_color=DARK_GREEN):
        self.rect      = pygame.Rect(x, y, w, h)
        self.color     = color
        self.top_color = top_color
    def draw(self, surface):
        pygame.draw.rect(surface, self.color, self.rect, border_radius=4)
        top = pygame.Rect(self.rect.x, self.rect.y, self.rect.width, 8)
        pygame.draw.rect(surface, self.top_color, top, border_radius=4)
class Coin:
    def __init__(self, x, y):
        self.x         = x
        self.y         = y
        self.radius    = 10
        self.collected = False
        self.timer     = 0
    def update(self):
        self.timer += 1
    def draw(self, surface):
        if not self.collected:
            bob = int(3 * (abs((self.timer % 60) - 30) / 30 - 0.5) * 2)
            cx = int(self.x)
            cy = int(self.y + bob)
            pygame.draw.circle(surface, COIN_GOLD, (cx, cy), self.radius)
            pygame.draw.circle(surface, YELLOW,    (cx, cy), self.radius - 3)
            pygame.draw.circle(surface, WHITE,     (cx - 3, cy - 3), 3)
    def check_collect(self, player_rect):
        r = pygame.Rect(self.x - self.radius, self.y - self.radius,
                        self.radius * 2, self.radius * 2)
        return r.colliderect(player_rect)
class Enemy:
    def __init__(self, x, y, left_bound, right_bound,
                 etype="slime", speed=2.0):
        self.x           = float(x)
        self.y           = float(y)
        self.width       = 32
        self.height      = 28
        self.left_bound  = left_bound
        self.right_bound = right_bound
        self.speed       = speed
        self.direction   = 1
        self.etype       = etype
        self.timer       = 0
        self.alive       = True
        self.base_y      = float(y)
    @property
    def rect(self):
        return pygame.Rect(int(self.x), int(self.y), self.width, self.height)
    def update(self, diff_mult):
        if not self.alive:
            return
        self.timer += 1
        spd = self.speed * diff_mult
        if self.etype in ("bat", "ghost"):
            self.x += self.direction * spd
            self.y  = self.base_y + math.sin(self.timer * 0.05) * 18
        else:
            self.x += self.direction * spd
        if self.x <= self.left_bound:
            self.x         = self.left_bound
            self.direction = 1
        if self.x + self.width >= self.right_bound:
            self.x         = self.right_bound - self.width
            self.direction = -1
    def draw(self, surface):
        if not self.alive:
            return
        cx     = int(self.x + self.width  // 2)
        cy     = int(self.y + self.height // 2)
        wobble = int(math.sin(self.timer * 0.15) * 2)
        if self.etype == "slime":
            body = pygame.Rect(int(self.x), int(self.y) + wobble,
                               self.width, self.height - 4)
            pygame.draw.ellipse(surface, (50, 180, 50), body)
            pygame.draw.ellipse(surface, (30, 130, 30), body, 2)
            pygame.draw.circle(surface, WHITE, (cx - 6, cy - 2 + wobble), 5)
            pygame.draw.circle(surface, WHITE, (cx + 6, cy - 2 + wobble), 5)
            ed = 1 if self.direction == 1 else -1
            pygame.draw.circle(surface, BLACK, (cx - 6 + ed*2, cy - 2 + wobble), 3)
            pygame.draw.circle(surface, BLACK, (cx + 6 + ed*2, cy - 2 + wobble), 3)
        elif self.etype == "bat":
            pygame.draw.ellipse(surface, PURPLE,
                                pygame.Rect(int(self.x)+6, int(self.y)+6,
                                            self.width-12, self.height-6))
            flap = int(math.sin(self.timer * 0.3) * 6)
            pygame.draw.ellipse(surface, (160, 80, 220),
                                pygame.Rect(int(self.x)-10, int(self.y)+flap, 18, 12))
            pygame.draw.ellipse(surface, (160, 80, 220),
                                pygame.Rect(int(self.x)+self.width-8,
                                            int(self.y)+flap, 18, 12))
            pygame.draw.circle(surface, RED, (cx-4, int(self.y)+10), 3)
            pygame.draw.circle(surface, RED, (cx+4, int(self.y)+10), 3)
        elif self.etype == "skull":
            pygame.draw.circle(surface, GRAY, (cx, cy-2+wobble), 14)
            pygame.draw.rect(surface, GRAY,
                             pygame.Rect(cx-10, cy+6+wobble, 20, 8), border_radius=3)
            pygame.draw.circle(surface, BLACK, (cx-5, cy-4+wobble), 4)
            pygame.draw.circle(surface, BLACK, (cx+5, cy-4+wobble), 4)
            pygame.draw.rect(surface, BLACK, pygame.Rect(cx-7, cy+8+wobble, 4, 5))
            pygame.draw.rect(surface, BLACK, pygame.Rect(cx-1, cy+8+wobble, 4, 5))
            pygame.draw.rect(surface, BLACK, pygame.Rect(cx+5, cy+8+wobble, 4, 5))
        elif self.etype == "lava":
            pulse = int(math.sin(self.timer * 0.1) * 3)
            pygame.draw.circle(surface, LAVA_RED,    (cx, cy+wobble), 14+pulse)
            pygame.draw.circle(surface, LAVA_ORANGE, (cx, cy+wobble), 10+pulse)
            pygame.draw.circle(surface, YELLOW,      (cx, cy+wobble), 5)
        elif self.etype == "ghost":
            ghost_color = (220, 220, 255)
            pygame.draw.ellipse(surface, ghost_color,
                                pygame.Rect(int(self.x)+2, int(self.y)+2,
                                            self.width-4, self.height-6))
            pygame.draw.rect(surface, ghost_color, 
                             pygame.Rect(int(self.x)+2, cy-2,
                                         self.width-4, self.height//2))
            pygame.draw.circle(surface, BLACK, (cx-5, cy-2), 4)
            pygame.draw.circle(surface, BLACK, (cx+5, cy-2), 4)
            pygame.draw.circle(surface, WHITE, (cx-4, cy-3), 2)
            pygame.draw.circle(surface, WHITE, (cx+6, cy-3), 2)
class Player:
    def __init__(self, x, y, move_speed=5, jump_strength=-14):
        self.width         = 36
        self.height        = 44
        self.rect          = pygame.Rect(x, y, self.width, self.height)
        self.vel_x         = 0
        self.vel_y         = 0
        self.on_ground     = False
        self.facing_right  = True
        self.walk_timer    = 0
        self.jump_squash   = 1.0
        self.move_speed    = move_speed
        self.jump_strength = jump_strength
        self.invincible    = 0
    def handle_input(self):
        keys = pygame.key.get_pressed()
        self.vel_x = 0
        if keys[pygame.K_LEFT]:
            self.vel_x = -self.move_speed
            self.facing_right = False
        if keys[pygame.K_RIGHT]:
            self.vel_x = self.move_speed
            self.facing_right = True
        if (keys[pygame.K_SPACE] or keys[pygame.K_UP]) and self.on_ground:
            self.vel_y = self.jump_strength
            self.on_ground = False
            self.jump_squash = 0.6
    def apply_physics(self, gravity=0.6):
        self.vel_y += gravity
        if self.vel_y > 20:
            self.vel_y = 20
        self.rect.x += int(self.vel_x)
        self.rect.y += int(self.vel_y)
        self.jump_squash += (1.0 - self.jump_squash) * 0.15
        if self.vel_x != 0 and self.on_ground:
            self.walk_timer += 1
        else:
            self.walk_timer = 0
        if self.invincible > 0:
            self.invincible -= 1
    def handle_platforms(self, platforms):
        self.on_ground = False
        for plat in platforms:
            if self.rect.colliderect(plat.rect):
                if self.vel_y > 0 and self.rect.bottom - self.vel_y <= plat.rect.top + 5:
                    self.rect.bottom = plat.rect.top
                    self.vel_y = 0
                    self.on_ground = True
                    self.jump_squash = 1.2
                elif self.vel_y < 0 and self.rect.top - self.vel_y >= plat.rect.bottom - 5:
                    self.rect.top = plat.rect.bottom
                    self.vel_y = 2
                elif self.vel_x > 0:
                    self.rect.right = plat.rect.left
                elif self.vel_x < 0:
                    self.rect.left = plat.rect.right
    def keep_on_screen(self):
        if self.rect.left < 0:
            self.rect.left = 0
        if self.rect.right > SCREEN_WIDTH:
            self.rect.right = SCREEN_WIDTH
    def check_enemy_hit(self, enemies):
        """
        Stomp from above  -> enemy dies, player bounces.
        Side touch        -> player loses a life (with brief invincibility).
        Returns True if player was hurt.
        """
        if self.invincible > 0:
            return False
        for e in enemies:
            if not e.alive:
                continue
            if self.rect.colliderect(e.rect):
                if (self.vel_y > 0 and
                        self.rect.bottom - self.vel_y <= e.rect.top + 14):
                    e.alive = False
                    self.vel_y = -8
                    return False
                else:
                    self.invincible = 90
                    return True
        return False
    def draw(self, surface):
        if self.invincible > 0 and (self.invincible // 6) % 2 == 0:
            return
        sq   = self.jump_squash
        cx   = self.rect.centerx
        cy   = self.rect.centery
        dw   = int(self.width  * sq)
        dh   = int(self.height * (2.0 - sq))
        swing = int(7 * math.sin(self.walk_timer * 0.25)) if self.vel_x != 0 else 0
        ed    = 1 if self.facing_right else -1
        SUIT_MAIN   = ( 30, 144, 255)
        SUIT_DARK   = ( 10,  80, 160)
        SUIT_LIGHT  = (100, 180, 255)
        VISOR_BG    = ( 10,  20,  60)
        VISOR_SHINE = ( 80, 160, 255)
        HELMET      = (220, 230, 255)
        HELMET_RIM  = (160, 170, 200)
        GLOVE       = (255, 200,  40)
        BOOT        = ( 40,  40,  80)
        BOOT_SOLE   = (255, 200,  40)
        BADGE       = (255,  60,  60)
        body_top    = cy - dh // 2 + 8
        body_bottom = cy + dh // 2
        body_left   = cx - dw // 2
        body_right  = cx + dw // 2
        leg_h   = int(14 * (2.0 - sq))
        leg_w   = max(9, int(10 * sq))
        foot_h  = 6
        foot_w  = 13
        ll_x = cx - leg_w - 2
        ll_y = body_bottom - 4
        pygame.draw.rect(surface, SUIT_DARK,
                         pygame.Rect(ll_x, ll_y + swing, leg_w, leg_h),
                         border_radius=4)
        pygame.draw.rect(surface, BOOT,
                         pygame.Rect(ll_x - 1, ll_y + leg_h - 2 + swing,
                                     foot_w, foot_h),
                         border_radius=3)
        pygame.draw.rect(surface, BOOT_SOLE,
                         pygame.Rect(ll_x - 1, ll_y + leg_h + foot_h - 4 + swing,
                                     foot_w, 3),
                         border_radius=2)
        rl_x = cx + 2
        rl_y = body_bottom - 4
        pygame.draw.rect(surface, SUIT_DARK,
                         pygame.Rect(rl_x, rl_y - swing, leg_w, leg_h),
                         border_radius=4)
        pygame.draw.rect(surface, BOOT,
                         pygame.Rect(rl_x - 1, rl_y + leg_h - 2 - swing,
                                     foot_w, foot_h),
                         border_radius=3)
        pygame.draw.rect(surface, BOOT_SOLE,
                         pygame.Rect(rl_x - 1, rl_y + leg_h + foot_h - 4 - swing,
                                     foot_w, 3),
                         border_radius=2)
        body_rect = pygame.Rect(body_left, body_top, dw, dh - 10)
        pygame.draw.rect(surface, SUIT_MAIN, body_rect, border_radius=8)
        stripe = pygame.Rect(body_left + 3, body_top + 4, 4, dh - 18)
        pygame.draw.rect(surface, SUIT_LIGHT, stripe, border_radius=2)
        bx = cx + ed * 4
        by = body_top + int((dh - 10) * 0.42)
        pygame.draw.circle(surface, BADGE, (bx, by), 5)
        pygame.draw.circle(surface, YELLOW, (bx, by), 3)
        belt_y = body_top + int((dh - 10) * 0.72)
        pygame.draw.rect(surface, SUIT_DARK,
                         pygame.Rect(body_left + 2, belt_y, dw - 4, 4),
                         border_radius=2)
        pygame.draw.rect(surface, GLOVE,
                         pygame.Rect(cx - 3, belt_y, 6, 4),
                         border_radius=1)
        arm_y    = body_top + 6
        arm_h    = int((dh - 10) * 0.45)
        arm_swing = int(5 * math.sin(self.walk_timer * 0.25)) if self.vel_x != 0 else 0
        pygame.draw.rect(surface, SUIT_MAIN,
                         pygame.Rect(body_left - 7, arm_y - arm_swing, 8, arm_h),
                         border_radius=4)
        pygame.draw.circle(surface, GLOVE,
                           (body_left - 3, arm_y + arm_h - arm_swing), 5)
        pygame.draw.rect(surface, SUIT_MAIN,
                         pygame.Rect(body_right - 1, arm_y + arm_swing, 8, arm_h),
                         border_radius=4)
        pygame.draw.circle(surface, GLOVE,
                           (body_right + 4, arm_y + arm_h + arm_swing), 5)
        hr  = int(13 * sq)
        hy  = body_top - hr + 5
        pygame.draw.circle(surface, HELMET, (cx, hy), hr)
        pygame.draw.circle(surface, HELMET_RIM, (cx, hy), hr, 2)
        visor_w = int(hr * 1.3)
        visor_h = int(hr * 0.9)
        visor_rect = pygame.Rect(cx - visor_w // 2, hy - visor_h // 2,
                                 visor_w, visor_h)
        pygame.draw.ellipse(surface, VISOR_BG, visor_rect)
        pygame.draw.line(surface, VISOR_SHINE,
                         (cx - visor_w // 2 + 3, hy - visor_h // 2 + 3),
                         (cx - visor_w // 2 + 3, hy + 1), 2)
        pygame.draw.line(surface, VISOR_SHINE,
                         (cx - visor_w // 2 + 7, hy - visor_h // 2 + 3),
                         (cx - visor_w // 2 + 7, hy - 2), 1)
        antenna_x = cx + ed * (hr - 4)
        pygame.draw.line(surface, HELMET_RIM,
                         (antenna_x, hy - hr),
                         (antenna_x + ed * 3, hy - hr - 7), 2)
        pygame.draw.circle(surface, YELLOW,
                           (antenna_x + ed * 3, hy - hr - 8), 2)
def get_level_data(level_num):
    """Return a dict with platforms, coins, enemies, sky, tip, name."""
    if level_num == 1:
        platforms = [
            Platform(0,   460, 800, 40, GREEN, DARK_GREEN),
            Platform(100, 370, 150, 20),
            Platform(320, 300, 140, 20),
            Platform(530, 230, 140, 20),
            Platform(680, 160, 120, 20),
            Platform(50,  270, 100, 20),
            Platform(420, 170, 110, 20),
        ]
        coins = [
            Coin(160, 345), Coin(240, 345),
            Coin(380, 275), Coin(450, 275),
            Coin(590, 205), Coin(660, 205),
            Coin(720, 135), Coin(750, 135),
            Coin( 80, 245), Coin(460, 145),
        ]
        enemies = []
        return dict(platforms=platforms, coins=coins, enemies=enemies,
                    sky=SKY_BLUE, name="Level 1 – Green Hills",
                    tip="Collect all 10 coins to advance!  No enemies here.")
    elif level_num == 2:
        platforms = [
            Platform(0,   460, 800, 40, GREEN, DARK_GREEN),
            Platform(80,  370, 160, 20),
            Platform(300, 300, 160, 20),
            Platform(540, 230, 160, 20),
            Platform(680, 360, 130, 20),
            Platform(160, 220, 120, 20),
            Platform(400, 160, 120, 20),
            Platform(700, 150, 100, 20),
        ]
        coins = [
            Coin(130, 345), Coin(210, 345),
            Coin(360, 275), Coin(430, 275),
            Coin(590, 205), Coin(660, 205),
            Coin(200, 195), Coin(450, 135),
            Coin(730, 125), Coin(720, 335),
        ]
        enemies = [
            Enemy(120, 438,   0, 260, etype="slime", speed=1.8),
            Enemy(350, 438, 260, 560, etype="slime", speed=2.0),
            Enemy(600, 438, 560, 800, etype="slime", speed=1.6),
            Enemy(100, 348,  80, 240, etype="slime", speed=1.5),
        ]
        return dict(platforms=platforms, coins=coins, enemies=enemies,
                    sky=SKY_BLUE, name="Level 2 – Slime Forest",
                    tip="Slimes appeared! Stomp them from ABOVE to defeat them.")
    elif level_num == 3:
        platforms = [
            Platform(0,   460, 800, 40, STONE, DARK_STONE),
            Platform(60,  380, 130, 20, STONE, DARK_STONE),
            Platform(250, 310, 150, 20, STONE, DARK_STONE),
            Platform(480, 240, 150, 20, STONE, DARK_STONE),
            Platform(660, 170, 140, 20, STONE, DARK_STONE),
            Platform(100, 230, 120, 20, STONE, DARK_STONE),
            Platform(340, 170, 110, 20, STONE, DARK_STONE),
            Platform(580, 380, 130, 20, STONE, DARK_STONE),
        ]
        coins = [
            Coin(100, 355), Coin(170, 355),
            Coin(300, 285), Coin(380, 285),
            Coin(530, 215), Coin(610, 215),
            Coin(690, 145), Coin(750, 145),
            Coin(150, 205), Coin(380, 145),
        ]
        enemies = [
            Enemy(200, 200,   0, 400, etype="bat",   speed=2.0),
            Enemy(500, 150, 300, 700, etype="bat",   speed=2.2),
            Enemy(650, 260, 500, 800, etype="bat",   speed=1.8),
            Enemy(100, 438,   0, 200, etype="slime", speed=1.8),
            Enemy(400, 438, 200, 600, etype="slime", speed=2.0),
            Enemy(660, 438, 600, 800, etype="slime", speed=2.2),
        ]
        return dict(platforms=platforms, coins=coins, enemies=enemies,
                    sky=(40, 40, 80), name="Level 3 – Bat Cave",
                    tip="Bats float up and down – time your jumps carefully!")
    elif level_num == 4:
        platforms = [
            Platform(0,   460, 800, 40, STONE, DARK_STONE),
            Platform(50,  390, 110, 20, STONE, DARK_STONE),
            Platform(220, 320, 130, 20, STONE, DARK_STONE),
            Platform(420, 260, 130, 20, STONE, DARK_STONE),
            Platform(620, 190, 130, 20, STONE, DARK_STONE),
            Platform(130, 240, 100, 20, STONE, DARK_STONE),
            Platform(330, 180, 100, 20, STONE, DARK_STONE),
            Platform(520, 120, 100, 20, STONE, DARK_STONE),
            Platform(700, 380, 100, 20, STONE, DARK_STONE),
            Platform(680, 300, 110, 20, STONE, DARK_STONE),
        ]
        coins = [
            Coin( 90, 365), Coin(160, 365),
            Coin(260, 295), Coin(330, 295),
            Coin(460, 235), Coin(530, 235),
            Coin(655, 165), Coin(725, 165),
            Coin(360, 155), Coin(555,  95),
        ]
        enemies = [
            Enemy(100, 438,   0, 220, etype="skull", speed=2.2),
            Enemy(350, 438, 220, 540, etype="skull", speed=2.4),
            Enemy(600, 438, 540, 800, etype="skull", speed=2.0),
            Enemy(250, 298, 220, 350, etype="skull", speed=2.0),
            Enemy(430, 238, 420, 550, etype="skull", speed=1.8),
            Enemy(300, 170,   0, 430, etype="bat",   speed=2.5),
            Enemy(600, 130, 430, 800, etype="bat",   speed=2.8),
        ]
        return dict(platforms=platforms, coins=coins, enemies=enemies,
                    sky=SKY_DUSK, name="Level 4 – Skull Ruins",
                    tip="Skulls are faster. Bats everywhere. Stay sharp!")
    elif level_num == 5:
        platforms = [
            Platform(0,   460, 800, 40, (80, 30, 10), LAVA_RED),
            Platform(60,  390, 110, 20, STONE, DARK_STONE),
            Platform(230, 320, 120, 20, STONE, DARK_STONE),
            Platform(420, 250, 120, 20, STONE, DARK_STONE),
            Platform(610, 180, 120, 20, STONE, DARK_STONE),
            Platform(130, 240,  90, 20, STONE, DARK_STONE),
            Platform(330, 170,  90, 20, STONE, DARK_STONE),
            Platform(520, 100, 100, 20, STONE, DARK_STONE),
            Platform(690, 370, 110, 20, STONE, DARK_STONE),
            Platform(680, 290, 120, 20, STONE, DARK_STONE),
            Platform(  0, 310,  90, 20, STONE, DARK_STONE),
        ]
        coins = [
            Coin( 95, 365), Coin(165, 365),
            Coin(270, 295), Coin(340, 295),
            Coin(455, 225), Coin(520, 225),
            Coin(645, 155), Coin(715, 155),
            Coin(360, 145), Coin(555,  75),
        ]
        enemies = [
            Enemy( 80, 438,   0, 220, etype="lava",  speed=2.5),
            Enemy(350, 438, 220, 540, etype="lava",  speed=2.8),
            Enemy(620, 438, 540, 800, etype="lava",  speed=2.5),
            Enemy(250, 298, 220, 350, etype="skull", speed=2.5),
            Enemy(430, 228, 420, 540, etype="skull", speed=2.2),
            Enemy(300, 160,   0, 430, etype="ghost", speed=1.8),
            Enemy(600, 110, 430, 800, etype="ghost", speed=2.0),
            Enemy(100, 220,   0, 220, etype="bat",   speed=3.0),
        ]
        return dict(platforms=platforms, coins=coins, enemies=enemies,
                    sky=SKY_NIGHT, name="Level 5 – Lava Castle  (FINAL)",
                    tip="All enemy types! Lava balls, ghosts, skulls & bats. Good luck!")
def draw_background(surface, sky_color, level_num):
    surface.fill(sky_color)
    if level_num in (1, 2):
        pygame.draw.circle(surface, YELLOW, (730, 70), 45)
        pygame.draw.circle(surface, (255, 240, 100), (730, 70), 38)
        for cx, cy, cw, ch in [(100,60,120,40),(350,40,100,35),(600,70,140,45)]:
            pygame.draw.ellipse(surface, WHITE, (cx, cy, cw, ch))
            pygame.draw.ellipse(surface, WHITE, (cx+20, cy-15, cw-30, ch+5))
    elif level_num == 3:
        for sx in range(0, 800, 80):
            pts = [(sx, 0), (sx+40, 0), (sx+20, 60)]
            pygame.draw.polygon(surface, (60, 60, 90), pts)
    elif level_num == 4:
        pygame.draw.circle(surface, (220, 200, 120), (700, 80), 40)
        pygame.draw.circle(surface, SKY_DUSK, (720, 65), 30)
    elif level_num == 5:
        random.seed(42)
        for _ in range(60):
            sx = random.randint(0, 800)
            sy = random.randint(0, 300)
            pygame.draw.circle(surface, WHITE, (sx, sy), 1)
def draw_hud(surface, score, lives, level_num, coins_left, diff):
    sc = font_small.render("Score: " + str(score), True, WHITE)
    pygame.draw.rect(surface, (0,0,0), pygame.Rect(8, 6, sc.get_width()+10, 26),
                     border_radius=4)
    surface.blit(sc, (13, 8))
    ll = font_small.render("Lives:", True, WHITE)
    surface.blit(ll, (12, 34))
    for i in range(lives):
        pygame.draw.circle(surface, RED, (84 + i * 24, 46), 8)
    cl = font_small.render("Coins: " + str(coins_left), True, COIN_GOLD)
    surface.blit(cl, (12, 60))
    lv = font_small.render("Lvl " + str(level_num) + "/5", True, WHITE)
    surface.blit(lv, (SCREEN_WIDTH - lv.get_width() - 10, 8))
    dcol = DIFFICULTY_SETTINGS[diff]["color"]
    db   = font_small.render(diff, True, dcol)
    surface.blit(db, (SCREEN_WIDTH - db.get_width() - 10, 32))
    if level_num == 1:
        hint = font_tiny.render("Arrow keys = Move   SPACE = Jump   Stomp enemies from above!", True, DARK_GRAY)
        surface.blit(hint, (SCREEN_WIDTH//2 - hint.get_width()//2, SCREEN_HEIGHT - 20))
def draw_panel(surface, x, y, w, h):
    s = pygame.Surface((w, h))
    s.set_alpha(210)
    s.fill((20, 20, 40))
    surface.blit(s, (x, y))
    pygame.draw.rect(surface, (80, 80, 120), pygame.Rect(x, y, w, h), 2, border_radius=8)
def draw_main_menu(surface, diff):
    surface.fill((20, 20, 50))
    random.seed(7)
    for _ in range(80):
        sx = random.randint(0, 800)
        sy = random.randint(0, 500)
        pygame.draw.circle(surface, WHITE, (sx, sy), 1)
    t1 = font_title.render("SUPER PLATFORMER", True, YELLOW)
    surface.blit(t1, (SCREEN_WIDTH//2 - t1.get_width()//2, 45))
    t2 = font_tiny.render("5 Levels  |  5 Enemy Types  |  3 Difficulty Modes", True, GRAY)
    surface.blit(t2, (SCREEN_WIDTH//2 - t2.get_width()//2, 98))
    draw_panel(surface, 240, 130, 320, 185)
    options = [
        ("ENTER   -  Start Game",   WHITE),
        ("I       -  Instructions", GRAY),
        ("S       -  Settings",     GRAY),
        ("ESC     -  Quit",         DARK_GRAY),
    ]
    for i, (txt, col) in enumerate(options):
        r = font_small.render(txt, True, col)
        surface.blit(r, (260, 143 + i * 40))
    draw_panel(surface, 240, 328, 320, 36)
    dcol = DIFFICULTY_SETTINGS[diff]["color"]
    dm   = font_small.render("Difficulty: " + diff, True, dcol)
    surface.blit(dm, (SCREEN_WIDTH//2 - dm.get_width()//2, 336))
    draw_panel(surface, 60, 385, 680, 90)
    wl = font_tiny.render("WORLDS:", True, GRAY)
    surface.blit(wl, (80, 394))
    worlds = ["1-Green Hills","2-Slime Forest","3-Bat Cave","4-Skull Ruins","5-Lava Castle"]
    colors = [GREEN, (100,200,100), PURPLE, GRAY, LAVA_ORANGE]
    for i, (w, col) in enumerate(zip(worlds, colors)):
        wt = font_tiny.render(w, True, col)
        surface.blit(wt, (80 + i * 130, 418))
        wt2 = font_tiny.render(["No enemies","Slimes","Bats+Slimes","Skulls+Bats","ALL types"][i], True, DARK_GRAY)
        surface.blit(wt2, (80 + i * 130, 444))
    pygame.display.flip()
def draw_instructions(surface):
    surface.fill((10, 20, 40))
    draw_panel(surface, 50, 20, 700, 460)
    title = font_big.render("HOW TO PLAY", True, YELLOW)
    surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 35))
    sections = [
        ("CONTROLS", YELLOW, font_mid),
        ("Left / Right Arrow Keys  =  Move your character", WHITE, font_small),
        ("SPACE  or  Up Arrow      =  Jump", WHITE, font_small),
        ("ESC                      =  Quit the game", WHITE, font_small),
        ("", WHITE, font_small),
        ("GOAL", YELLOW, font_mid),
        ("Collect ALL coins on each level to advance to the next.", WHITE, font_small),
        ("Complete all 5 levels to win the game!", WHITE, font_small),
        ("", WHITE, font_small),
        ("ENEMIES  (new ones appear each level!)", YELLOW, font_mid),
        ("Slime  - walks back and forth on platforms  (Level 2+)", (100,220,100), font_small),
        ("Bat    - floats up and down through the air  (Level 3+)", (180,120,255), font_small),
        ("Skull  - faster walker, hard to avoid  (Level 4+)", GRAY, font_small),
        ("Lava   - fast fireball on the ground  (Level 5)", ORANGE, font_small),
        ("Ghost  - drifts slowly through the air  (Level 5)", ICE_BLUE, font_small),
        ("", WHITE, font_small),
        ("STOMP an enemy by jumping and landing ON TOP of it!", COIN_GOLD, font_mid),
        ("", WHITE, font_small),
        ("Press  ENTER  or  BACKSPACE  to return to menu", GRAY, font_small),
    ]
    y = 85
    for text, color, fnt in sections:
        if text:
            r = fnt.render(text, True, color)
            surface.blit(r, (75, y))
        y += fnt.size("A")[1] + 5
    pygame.display.flip()
def draw_settings(surface, diff):
    surface.fill((10, 20, 40))
    draw_panel(surface, 80, 30, 640, 430)
    title = font_big.render("SETTINGS", True, YELLOW)
    surface.blit(title, (SCREEN_WIDTH//2 - title.get_width()//2, 50))
    sub = font_mid.render("Choose Difficulty  (press 1, 2, or 3)", True, WHITE)
    surface.blit(sub, (SCREEN_WIDTH//2 - sub.get_width()//2, 100))
    diffs = ["Easy", "Normal", "Hard"]
    for i, d in enumerate(diffs):
        cfg    = DIFFICULTY_SETTINGS[d]
        is_sel = (d == diff)
        bx     = SCREEN_WIDTH//2 - 220
        by     = 148 + i * 98
        box = pygame.Surface((440, 80))
        box.set_alpha(220)
        box.fill((40, 40, 80) if not is_sel else (50, 70, 140))
        surface.blit(box, (bx, by))
        border_col = cfg["color"] if is_sel else (60, 60, 100)
        pygame.draw.rect(surface, border_col,
                         pygame.Rect(bx, by, 440, 80), 3, border_radius=6)
        key_r = font_mid.render(str(i+1), True, cfg["color"])
        surface.blit(key_r, (bx + 14, by + 28))
        name_r = font_mid.render(d, True, cfg["color"])
        surface.blit(name_r, (bx + 50, by + 10))
        desc = ("Lives: " + str(cfg["lives"]) +
                "   Enemy Speed: x" + str(cfg["enemy_speed_mult"]) +
                "   Coin Bonus: +" + str(cfg["coin_bonus"]) + " pts")
        dr = font_tiny.render(desc, True, GRAY)
        surface.blit(dr, (bx + 50, by + 48))
        if is_sel:
            sel_r = font_tiny.render("SELECTED", True, cfg["color"])
            surface.blit(sel_r, (bx + 360, by + 10))
    back = font_small.render("Press  ENTER  or  BACKSPACE  to go back", True, GRAY)
    surface.blit(back, (SCREEN_WIDTH//2 - back.get_width()//2, 453))
    pygame.display.flip()
def draw_level_banner(surface, level_name, tip, timer):
    """Show a banner for the first ~4 seconds of a level."""
    if timer > 240:
        return
    alpha = 255 if timer < 150 else max(0, int(255 * (240 - timer) / 90))
    banner = pygame.Surface((700, 70))
    banner.set_alpha(alpha)
    banner.fill((10, 10, 30))
    pygame.draw.rect(banner, (80, 80, 120), pygame.Rect(0,0,700,70), 2, border_radius=8)
    nr = font_mid.render(level_name, True, YELLOW)
    tr = font_small.render(tip, True, (200, 200, 255))
    banner.blit(nr, (350 - nr.get_width()//2, 8))
    banner.blit(tr, (350 - tr.get_width()//2, 40))
    surface.blit(banner, (50, 12))
def draw_level_clear(surface, level_num, score):
    surface.fill((10, 50, 10))
    draw_panel(surface, 180, 130, 440, 240)
    if level_num < 5:
        msg = font_big.render("Level " + str(level_num) + " Clear!", True, YELLOW)
        nxt = font_small.render("Press ENTER for Level " + str(level_num+1), True, GRAY)
    else:
        msg = font_big.render("YOU WIN!  All 5 Levels!", True, YELLOW)
        nxt = font_small.render("Press ENTER to play again", True, GRAY)
    sc  = font_small.render("Score: " + str(score), True, WHITE)
    surface.blit(msg, (SCREEN_WIDTH//2 - msg.get_width()//2, 160))
    surface.blit(sc,  (SCREEN_WIDTH//2 - sc.get_width()//2,  220))
    surface.blit(nxt, (SCREEN_WIDTH//2 - nxt.get_width()//2, 275))
    pygame.display.flip()
def draw_game_over(surface, score, level_num):
    surface.fill((50, 10, 10))
    draw_panel(surface, 180, 130, 440, 240)
    msg   = font_big.render("GAME OVER", True, RED)
    lv    = font_small.render("Reached Level " + str(level_num), True, GRAY)
    sc    = font_small.render("Final Score: " + str(score), True, WHITE)
    retry = font_small.render("Press ENTER to try again", True, GRAY)
    surface.blit(msg,   (SCREEN_WIDTH//2 - msg.get_width()//2,   158))
    surface.blit(lv,    (SCREEN_WIDTH//2 - lv.get_width()//2,    208))
    surface.blit(sc,    (SCREEN_WIDTH//2 - sc.get_width()//2,    238))
    surface.blit(retry, (SCREEN_WIDTH//2 - retry.get_width()//2, 278))
    pygame.display.flip()
def wait_for_enter():
    """Wait until ENTER is pressed."""
    while True:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                    return
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
def run_level(level_num, score_in, lives_in, diff):
    """
    Run a single level.
    Returns: (result_string, score, lives)
      result_string = "level_clear" | "game_over"
    """
    data       = get_level_data(level_num)
    platforms  = data["platforms"]
    coins      = data["coins"]
    enemies    = data["enemies"]
    sky_color  = data["sky"]
    tip        = data["tip"]
    name       = data["name"]
    cfg        = DIFFICULTY_SETTINGS[diff]
    spd_mult   = cfg["enemy_speed_mult"]
    coin_bonus = cfg["coin_bonus"]
    player     = Player(80, 380)
    score      = score_in
    lives      = lives_in
    banner_t   = 0
    while True:
        banner_t += 1
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit(); sys.exit()
            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_ESCAPE:
                    pygame.quit(); sys.exit()
        player.handle_input()
        player.apply_physics()
        player.handle_platforms(platforms)
        player.keep_on_screen()
        for e in enemies:
            e.update(spd_mult)
        if player.check_enemy_hit(enemies):
            lives -= 1
            if lives <= 0:
                return "game_over", score, 0
            player = Player(80, 380)
        for coin in coins:
            coin.update()
            if not coin.collected and coin.check_collect(player.rect):
                coin.collected = True
                score += coin_bonus
        if player.rect.top > SCREEN_HEIGHT:
            lives -= 1
            if lives <= 0:
                return "game_over", score, 0
            player = Player(80, 380)
        if all(c.collected for c in coins):
            score += level_num * 50
            return "level_clear", score, lives
        coins_left = sum(1 for c in coins if not c.collected)
        draw_background(screen, sky_color, level_num)
        for plat in platforms:
            plat.draw(screen)
        for coin in coins:
            coin.draw(screen)
        for e in enemies:
            e.draw(screen)
        player.draw(screen)
        draw_hud(screen, score, lives, level_num, coins_left, diff)
        draw_level_banner(screen, name, tip, banner_t)
        pygame.display.flip()
        clock.tick(FPS)
def main():
    global selected_difficulty
    state         = "menu"
    score         = 0
    lives         = DIFFICULTY_SETTINGS[selected_difficulty]["lives"]
    current_level = 1
    while True:
        if state == "menu":
            draw_main_menu(screen, selected_difficulty)
            waiting = True
            while waiting:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit(); sys.exit()
                    if event.type == pygame.KEYDOWN:
                        if event.key in (pygame.K_RETURN, pygame.K_KP_ENTER):
                            score = 0
                            current_level = 1
                            lives = DIFFICULTY_SETTINGS[selected_difficulty]["lives"]
                            state = "playing"
                            waiting = False
                        elif event.key == pygame.K_i:
                            state = "instructions"
                            waiting = False
                        elif event.key == pygame.K_s:
                            state = "settings"
                            waiting = False
                        elif event.key == pygame.K_ESCAPE:
                            pygame.quit(); sys.exit()
        elif state == "instructions":
            draw_instructions(screen)
            choosing = True
            while choosing:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit(); sys.exit()
                    if event.type == pygame.KEYDOWN:
                        if event.key in (pygame.K_RETURN, pygame.K_BACKSPACE,
                                         pygame.K_KP_ENTER):
                            choosing = False
                        elif event.key == pygame.K_ESCAPE:
                            pygame.quit(); sys.exit()
            state = "menu"
        elif state == "settings":
            draw_settings(screen, selected_difficulty)
            choosing = True
            while choosing:
                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        pygame.quit(); sys.exit()
                    if event.type == pygame.KEYDOWN:
                        if event.key == pygame.K_1:
                            selected_difficulty = "Easy"
                            draw_settings(screen, selected_difficulty)
                        elif event.key == pygame.K_2:
                            selected_difficulty = "Normal"
                            draw_settings(screen, selected_difficulty)
                        elif event.key == pygame.K_3:
                            selected_difficulty = "Hard"
                            draw_settings(screen, selected_difficulty)
                        elif event.key in (pygame.K_RETURN, pygame.K_BACKSPACE,
                                           pygame.K_KP_ENTER):
                            choosing = False
                        elif event.key == pygame.K_ESCAPE:
                            pygame.quit(); sys.exit()
            state = "menu"
        elif state == "playing":
            result, score, lives = run_level(
                current_level, score, lives, selected_difficulty)
            if result == "level_clear":
                draw_level_clear(screen, current_level, score)
                wait_for_enter()
                if current_level >= 5:
                    state = "menu"
                else:
                    current_level += 1
            elif result == "game_over":
                draw_game_over(screen, score, current_level)
                wait_for_enter()
                score = 0
                current_level = 1
                lives = DIFFICULTY_SETTINGS[selected_difficulty]["lives"]
                state = "menu"
main()