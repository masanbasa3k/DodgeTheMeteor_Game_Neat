import pygame
import random
import time
import os
import random
pygame.font.init()


WIDTH = 600
HEIGHT = 700

WIN = pygame.display.set_mode((WIDTH, HEIGHT))
pygame.display.set_caption("Dodge This!")

ASTRONAUT = pygame.transform.scale(pygame.image.load(os.path.join("imgs/meteor_dodge","astronaut_guy.png")), (WIDTH, HEIGHT))
ASTRONAUT = pygame.transform.scale(ASTRONAUT, (64,64))


METEORS_IMG = [pygame.transform.scale2x(pygame.image.load(os.path.join("imgs/meteor_dodge","meteor1.png"))),
           pygame.transform.scale2x(pygame.image.load(os.path.join("imgs/meteor_dodge","meteor2.png"))),
           pygame.transform.scale2x(pygame.image.load(os.path.join("imgs/meteor_dodge","meteor3.png"))),
           pygame.transform.scale2x(pygame.image.load(os.path.join("imgs/meteor_dodge","meteor4.png"))),
           pygame.transform.scale2x(pygame.image.load(os.path.join("imgs/meteor_dodge","meteor5.png")))]

METEORS = []

for img in METEORS_IMG:
    img = pygame.transform.scale(img, (32,32))
    METEORS.append(img)



BG = pygame.transform.scale(pygame.image.load(os.path.join("imgs/meteor_dodge","bg.jpeg")), (WIDTH, HEIGHT))

FONT = pygame.font.SysFont("comicsans",30)

ITEM_W, ITEM_H = 10, 10
ITEM_SPD = 5

class Player:
    width = 64
    height = 64
    VEL = 5
    dir = "right"
    angle = 0
    
    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y
        self.img = ASTRONAUT
        self.img_rvrs = pygame.transform.flip(self.img, True, False)
        self.mask = pygame.mask.from_surface(self.img)

    def draw(self, window):
        if self.dir == "right":
            self.angle = 330
            rotated_player = pygame.transform.rotate(self.img, self.angle)

        elif self.dir == "left":
            self.angle = 30
            rotated_player = pygame.transform.rotate(self.img_rvrs, self.angle)

        window.blit(rotated_player, (self.x, self.y))


class Meteor:
    width = 32
    height = 32
    angle = 0

    def __init__(self, x, y) -> None:
        self.x = x
        self.y = y
        self.img = METEORS[random.randint(0,4)]
        self.mask = pygame.mask.from_surface(self.img)

    def move(self):
        self.y += ITEM_SPD

    def draw(self, window):
        rotated_item = pygame.transform.rotate(self.img, self.angle)
        window.blit(rotated_item, (self.x, self.y))
        self.angle += 1

def collide(obj1, obj2):
    offset_x = obj2.x - obj1.x
    offset_y = obj2.y - obj1.y
    return obj1.mask.overlap(obj2.mask, (offset_x, offset_y)) != None

def draw(player, elapsed_time, items):
    WIN.blit(BG, (0,0))

    time_text = FONT.render(f"{round(elapsed_time)}",1,"white")
    WIN.blit(time_text,(10, 10))


    player.draw(WIN)


    for item in items:
        item.draw(WIN)
        

    pygame.display.update()


def main():
    run = True
    hit = False

    player = Player(200,HEIGHT - 100)

    clock = pygame.time.Clock()
    start_time = time.time()
    elapsed_time = 0

    item_add_increment = 2000
    meteor_count = 0

    meteors = []
    item_angle = 0
    player_angle = 0

    while run:
        meteor_count += clock.tick(60)
        elapsed_time = time.time() - start_time

        # quit game
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                quit()

        if meteor_count > item_add_increment:
            for _ in range(random.randint(3,7)):# how many meteor
                meteor_x = random.randint(0, WIDTH - 32)
                meteor = Meteor(meteor_x, 0)
                meteors.append(meteor)

            item_add_increment = max(200, item_add_increment - 50) # decreasing meteor coming time
            meteor_count = 0
        
        keys = pygame.key.get_pressed()
        if keys[pygame.K_LEFT] and (player.x - player.VEL >= 10):
            player.dir = "left"
            player.x -= player.VEL
        if keys[pygame.K_RIGHT] and (player.x + player.VEL + player.width <= WIDTH-10):
            player.dir = "right"
            player.x += player.VEL

        for meteor in meteors[:]:
            meteor.move()

            if meteor.y > HEIGHT:
                meteors.remove(meteor)
            elif (meteor.y + meteor.height >= player.y) and collide(meteor, player):
                meteors.remove(meteor)
                hit = True
                break

        if hit:
            lost_text = FONT.render("You Lost!", 1, "white")
            WIN.blit(lost_text, (WIDTH/2 - lost_text.get_width()/2, HEIGHT/2 - lost_text.get_height()/2))
            pygame.display.update()  
            pygame.time.delay(3000)
            break

        draw(player, elapsed_time, meteors)
        item_angle += 1

    pygame.quit()

if __name__ == "__main__":
    main()
