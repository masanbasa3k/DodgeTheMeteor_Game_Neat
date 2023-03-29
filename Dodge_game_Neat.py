import pygame
import random
import time
import os
import random
import neat
import pickle
pygame.font.init()

GEN = 0
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
    
    def chase(self, meteors):
        pos = pygame.math.Vector2(self.x, self.y)
        enemy = min([e for e in meteors], key=lambda e: pos.distance_to(pygame.math.Vector2(e.x, e.y)))
        return enemy


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

def draw(players, elapsed_time, items , GEN):
    WIN.blit(BG, (0,0))

    time_text = FONT.render(f"{round(elapsed_time)}",1,"white")
    WIN.blit(time_text,(10, 10))

    gen = FONT.render(f"Gen: {round(GEN)}",1,"white")
    WIN.blit(gen,(10, 50))

    for player in players:
        player.draw(WIN)


    for item in items:
        item.draw(WIN)
        

    pygame.display.update()


def main(genomes, config):
    global GEN
    GEN += 1
    nets = []
    ge = []
    players = []

    for _, g in genomes:
        net = neat.nn.FeedForwardNetwork.create(g, config)
        nets.append(net)
        players.append(Player(200,HEIGHT - 100))
        g.fitness = 0
        ge.append(g)


    run = True

    clock = pygame.time.Clock()
    start_time = time.time()
    elapsed_time = 0

    item_add_increment = 2000
    meteor_count = 0

    meteors = []
    item_angle = 0

    while run and len(players) > 0:
        meteor_count += clock.tick(60)
        elapsed_time = time.time() - start_time

        # quit game
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                quit()

        if meteor_count > item_add_increment:
            for _ in range(4):# how many meteor
                meteor_x = random.randint(0, WIDTH - 32)
                meteor = Meteor(meteor_x, 0)
                meteors.append(meteor)

            item_add_increment = max(200, item_add_increment - 50) # decreasing meteor coming time
            meteor_count = 0
        
        for x, player in enumerate(players):
            
            if len(meteors) > 0:
                near_enemy = player.chase(meteors)
                #output for moving
                output = nets[x].activate((player.x, abs(player.x - near_enemy.x)))
                # output = nets[x].activate((player.x, near_enemy.x))
                decision = output.index(max(output))

                if decision == 0:
                    pass
                if decision == 1:
                    player.dir = "right"
                    player.x += player.VEL
                if decision == 2:
                    player.dir = "left"
                    player.x -= player.VEL


        for meteor in meteors[:]:
            meteor.move()

            if meteor.y > HEIGHT:
                meteors.remove(meteor)
                for g in ge:
                    g.fitness += 1/4
            
            for x, player in enumerate(players):
                if player.x < 0 or player.x > 500 or collide(meteor,player):
                    ge[x].fitness -= 2
                    players.pop(x)
                    nets.pop(x)
                    ge.pop(x)

        draw(players, elapsed_time, meteors, GEN)
        item_angle += 1

def run(config):
    # p = neat.Checkpointer.restore_checkpoint("neat-checkpoint")
    p = neat.Population(config)
    
    p.add_reporter(neat.StdOutReporter(True))
    stats = neat.StatisticsReporter()
    p.add_reporter(stats)
    # p.add_reporter(neat.Checkpointer(50))

    winner = p.run(main,50)

    #save the best winner
    with open("best_dodge.pickle","wb") as file:
        pickle.dump(winner, file)

    # show final stats
    print('\nBest genome:\n{!s}'.format(winner))

if __name__ == "__main__":
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, "config-dodge.txt")
    config = neat.config.Config(neat.DefaultGenome,
                                neat.DefaultReproduction,
                                neat.DefaultSpeciesSet,
                                neat.DefaultStagnation,
                                config_path)
    run(config)
