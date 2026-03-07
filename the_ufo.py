import pygame, random, time
from pygame.locals import *

# ================= VARIABLES =================
SCREEN_WIDHT = 430
SCREEN_HEIGHT = 600

SPEED = 15
GRAVITY = 2.5
GAME_SPEED = 15

GROUND_WIDHT = 2 * SCREEN_WIDHT
GROUND_HEIGHT = 100

PIPE_WIDHT = 80
PIPE_HEIGHT = 500
PIPE_GAP = 150

pygame.init()
pygame.mixer.init()

screen = pygame.display.set_mode((SCREEN_WIDHT, SCREEN_HEIGHT))
pygame.display.set_caption("The UFO By radjaa")

clock = pygame.time.Clock()

# ================= LOAD ASSETS =================
BACKGROUND = pygame.image.load('assets/sprites/background-day.png')
BACKGROUND = pygame.transform.scale(BACKGROUND,(SCREEN_WIDHT,SCREEN_HEIGHT))

BEGIN_IMAGE = pygame.image.load('assets/sprites/message.png').convert_alpha()
GAME_OVER_IMAGE = pygame.image.load('assets/sprites/gameover.png').convert_alpha()

wing_sound = pygame.mixer.Sound('assets/audio/wing.wav')
hit_sound = pygame.mixer.Sound('assets/audio/hit.wav')

# ================= BACKGROUND SCROLL =================
bg_x1 = 0
bg_x2 = SCREEN_WIDHT
BG_SPEED = 2

def draw_background():
    global bg_x1,bg_x2

    screen.blit(BACKGROUND,(bg_x1,0))
    screen.blit(BACKGROUND,(bg_x2,0))

    bg_x1 -= BG_SPEED
    bg_x2 -= BG_SPEED

    if bg_x1 <= -SCREEN_WIDHT:
        bg_x1 = SCREEN_WIDHT

    if bg_x2 <= -SCREEN_WIDHT:
        bg_x2 = SCREEN_WIDHT

# ================= BIRD =================
class Bird(pygame.sprite.Sprite):

    def __init__(self):
        pygame.sprite.Sprite.__init__(self)

        size = (50,35)

        self.images = [
            pygame.transform.scale(pygame.image.load('assets/sprites/bluebird-upflap.png').convert_alpha(),size),
            pygame.transform.scale(pygame.image.load('assets/sprites/bluebird-midflap.png').convert_alpha(),size),
            pygame.transform.scale(pygame.image.load('assets/sprites/bluebird-downflap.png').convert_alpha(),size)
        ]

        self.current_image = 0
        self.image = self.images[self.current_image]

        self.rect = self.image.get_rect()
        self.rect[0] = SCREEN_WIDHT/6
        self.rect[1] = SCREEN_HEIGHT/2

        self.mask = pygame.mask.from_surface(self.image)

        self.speed = 0

    def update(self):

        self.current_image = (self.current_image+1)%3
        self.image = self.images[self.current_image]

        self.speed += GRAVITY
        self.rect[1] += self.speed

    def bump(self):

        self.speed = -SPEED
        wing_sound.play()

# ================= PIPE =================
class Pipe(pygame.sprite.Sprite):

    def __init__(self,inverted,xpos,ysize):

        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.image.load('assets/sprites/pipe-green.png').convert_alpha()
        self.image = pygame.transform.scale(self.image,(PIPE_WIDHT,PIPE_HEIGHT))

        self.rect = self.image.get_rect()
        self.rect[0] = xpos

        if inverted:
            self.image = pygame.transform.flip(self.image,False,True)
            self.rect[1] = -(self.rect[3]-ysize)
        else:
            self.rect[1] = SCREEN_HEIGHT - ysize

        self.mask = pygame.mask.from_surface(self.image)
        self.passed = False

    def update(self):
        self.rect[0] -= GAME_SPEED

# ================= GROUND =================
class Ground(pygame.sprite.Sprite):

    def __init__(self,xpos):

        pygame.sprite.Sprite.__init__(self)

        self.image = pygame.image.load('assets/sprites/base.png').convert_alpha()
        self.image = pygame.transform.scale(self.image,(GROUND_WIDHT,GROUND_HEIGHT))

        self.rect = self.image.get_rect()
        self.rect[0] = xpos
        self.rect[1] = SCREEN_HEIGHT - GROUND_HEIGHT

        self.mask = pygame.mask.from_surface(self.image)

    def update(self):
        self.rect[0] -= GAME_SPEED

# ================= FUNCTIONS =================
def is_off_screen(sprite):
    return sprite.rect[0] < -(sprite.rect[2])

def get_random_pipes(xpos):

    size = random.randint(100,300)

    pipe = Pipe(False,xpos,size)
    pipe_inverted = Pipe(True,xpos,SCREEN_HEIGHT-size-PIPE_GAP)

    return pipe,pipe_inverted

def read_high_score():
    try:
        with open("highscore.txt","r") as f:
            return int(f.read())
    except:
        return 0

def save_high_score(score):
    with open("highscore.txt","w") as f:
        f.write(str(score))

def reset_game():

    global bird, score, game_over

    bird.rect[1] = SCREEN_HEIGHT/2
    bird.speed = 0

    pipe_group.empty()
    ground_group.empty()

    for i in range(2):
        ground = Ground(GROUND_WIDHT*i)
        ground_group.add(ground)

    for i in range(2):
        pipes = get_random_pipes(SCREEN_WIDHT*i + 800)
        pipe_group.add(pipes[0])
        pipe_group.add(pipes[1])

    score = 0
    game_over = False

# ================= OBJECT GROUPS =================
bird_group = pygame.sprite.Group()
bird = Bird()
bird_group.add(bird)

ground_group = pygame.sprite.Group()
for i in range(2):
    ground = Ground(GROUND_WIDHT*i)
    ground_group.add(ground)

pipe_group = pygame.sprite.Group()
for i in range(2):
    pipes = get_random_pipes(SCREEN_WIDHT*i + 800)
    pipe_group.add(pipes[0])
    pipe_group.add(pipes[1])

# ================= SCORE =================
score = 0
font = pygame.font.Font(None,40)
high_score = read_high_score()

# ================= START SCREEN =================
begin = True

while begin:

    clock.tick(15)

    for event in pygame.event.get():

        if event.type == QUIT:
            pygame.quit()

        if event.type == KEYDOWN:

            if event.key == K_SPACE or event.key == K_UP:
                bird.bump()
                begin = False

    draw_background()

    screen.blit(BEGIN_IMAGE,(120,150))

    bird_group.draw(screen)
    ground_group.draw(screen)

    pygame.display.update()

# ================= MAIN GAME =================
game_over = False

while True:

    clock.tick(30)

    for event in pygame.event.get():

        if event.type == QUIT:
            pygame.quit()

        if event.type == KEYDOWN:

            if game_over and event.key == K_SPACE:
                reset_game()

            elif not game_over and (event.key == K_SPACE or event.key == K_UP):
                bird.bump()

    if not game_over:

        draw_background()

        for pipe in pipe_group.sprites():

            if pipe.rect[0] + PIPE_WIDHT < bird.rect[0] and not pipe.passed:
                score += 0.5
                pipe.passed = True

        if is_off_screen(pipe_group.sprites()[0]):

            pipe_group.remove(pipe_group.sprites()[0])
            pipe_group.remove(pipe_group.sprites()[0])

            pipes = get_random_pipes(SCREEN_WIDHT*2)

            pipe_group.add(pipes[0])
            pipe_group.add(pipes[1])

        if is_off_screen(ground_group.sprites()[0]):

            ground_group.remove(ground_group.sprites()[0])

            new_ground = Ground(GROUND_WIDHT-20)
            ground_group.add(new_ground)

        bird_group.update()
        pipe_group.update()
        ground_group.update()

        pipe_group.draw(screen)
        bird_group.draw(screen)
        ground_group.draw(screen)

        score_text = font.render(f"Score: {int(score)}",True,(255,255,255))
        screen.blit(score_text,(10,10))

        high_text = font.render(f"High Score: {int(high_score)}",True,(255,255,255))
        screen.blit(high_text,(SCREEN_WIDHT-high_text.get_width()-10,10))

        pygame.display.update()

        if (pygame.sprite.groupcollide(bird_group,ground_group,False,False,pygame.sprite.collide_mask) or
            pygame.sprite.groupcollide(bird_group,pipe_group,False,False,pygame.sprite.collide_mask)):

            hit_sound.play()
            time.sleep(1)

            game_over = True

            if score > high_score:
                high_score = score
                save_high_score(high_score)

    else:

        draw_background()

        screen.blit(GAME_OVER_IMAGE,
        (SCREEN_WIDHT/2-GAME_OVER_IMAGE.get_width()/2,
         SCREEN_HEIGHT/2-GAME_OVER_IMAGE.get_height()/2))

        restart_text = font.render("Press SPACE to Restart",True,(255,255,255))
        screen.blit(restart_text,(SCREEN_WIDHT/2-restart_text.get_width()/2,SCREEN_HEIGHT/2+80))

        pygame.display.update()
