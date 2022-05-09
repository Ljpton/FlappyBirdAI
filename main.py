import pygame
import os
import random
import sys
import neat
import math

pygame.init();

SCREEN_HEIGHT = 512
SCREEN_WIDTH = 288
SCREEN = pygame.display.set_mode((SCREEN_WIDTH, SCREEN_HEIGHT))

pygame_icon = pygame.image.load(os.path.join("Assets/icon", "favicon.ico"))
pygame.display.set_icon(pygame_icon)

pygame.display.set_caption("flappybird AI")

FLAP = [pygame.image.load(os.path.join("Assets/png", "redbird-upflap.png")),
        pygame.image.load(os.path.join("Assets/png", "redbird-midflap.png")),
        pygame.image.load(os.path.join("Assets/png", "redbird-downflap.png"))]

PIPE_BOTTOM = pygame.image.load(os.path.join("Assets/png", "pipe-green.png"))
PIPE_TOP = pygame.transform.flip(PIPE_BOTTOM, False, True)

BACKGROUND = pygame.image.load(os.path.join("Assets/png", "background.png"))

FONT = pygame.font.Font(os.path.join("Assets/fonts", "FlappyBirdRegular.ttf"), 64)
STATISTICS_FONT = pygame.font.Font(os.path.join("Assets/fonts", "Consolas.ttf"), 16)

high_score = 0
fps = 30

class Bird:
    X_POS = 90
    Y_POS = 320
    FLAP_VELOCITY = 8

    def __init__(self, img=FLAP[0]):
        self.image = img
        self.bird_flap = False
        self.flap_velocity = self.FLAP_VELOCITY
        self.rect = pygame.Rect(self.X_POS, self.Y_POS, img.get_width(), img.get_height())
        self.color = (random.randint(0, 255), random.randint(0, 255), random.randint(0, 255))
        self.flap_index = 0

    def update(self):
        self.animate()

        if self.bird_flap:
            self.flap()

        self.rect.y -= self.flap_velocity
        self.flap_velocity -= 0.8

    def flap(self):
        self.flap_index = 0
        self.flap_velocity = self.FLAP_VELOCITY
        self.bird_flap = False

    def animate(self):
        self.flap_index += 1

        if self.flap_index < 3:
            self.image = FLAP[0]
        if 3 <= self.flap_index < 6:
            self.image = FLAP[1]
        if 6 <= self.flap_index < 9:
            self.image = FLAP[2]
        if 9 <= self.flap_index < 12:
            self.image = FLAP[1]
        if 12 <= self.flap_index:
            self.image = FLAP[0]

    def draw(self, SCREEN):
        SCREEN.blit(self.image, (self.rect.x, self.rect.y))
        pygame.draw.rect(SCREEN, self.color, (self.rect.x, self.rect.y, self.rect.width, self.rect.height), 2)
        for obstacle in obstacles:
            pygame.draw.line(SCREEN, self.color, (self.rect.x + 17, self.rect.y + 12), obstacle.rect.center, 2)


class Obstacle:
    def __init__(self, image, height):
        self.image = image
        self.rect = self.image.get_rect()
        self.rect.x = SCREEN_WIDTH
        self.rect.y = height

    def update(self):
        self.rect.x -= game_speed
        if self.rect.x < -self.rect.width:
            obstacles.pop()

    def draw(self, SCREEN):
        SCREEN.blit(self.image, self.rect)


def remove(index):
    birds.pop(index)
    ge.pop(index)
    nets.pop(index)


def distance(pos_a, pos_b):
    dx = pos_a[0] - pos_b[0]
    dy = pos_a[1] - pos_b[1]
    return math.sqrt(dx ** 2 + dy ** 2)


def eval_genomes(genomes, config):
    global fps, game_speed, points, obstacles, ge, nets, birds, high_score, pipe_difficulty
    clock = pygame.time.Clock()
    points = 0

    obstacles = []
    birds = []
    ge = []
    nets = []

    game_speed = 2
    pipe_difficulty = 0

    for genome_id, genome in genomes:
        birds.append(Bird())
        ge.append(genome)
        net = neat.nn.FeedForwardNetwork.create(genome, config)
        nets.append(net)
        genome.fitness = 0

    def score():
        global points, game_speed, pipe_difficulty
        points += 1
        for g in ge:
            g.fitness += 1
        if points % 250 == 0:
            if game_speed == 8:
                pipe_difficulty = min(pipe_difficulty + 4, 32)
            else:
                game_speed = min(game_speed + 1, 8)
        text = FONT.render(str(points), True, (0, 0, 0))
        SCREEN.blit(text, (18, 18))

    def statistics():
        global birds, ge
        text_1 = STATISTICS_FONT.render("Birds live: " + str(len(birds)), True, (0, 0, 0))
        text_2 = STATISTICS_FONT.render("Generation: " + str(pop.generation + 1), True, (0, 0, 0))
        text_3 = STATISTICS_FONT.render("High Score: " + str(max(points, high_score)), True, (0, 0, 0))
        text_4 = STATISTICS_FONT.render("Game Speed: " + str(game_speed), True, (0, 0, 0))
        text_5 = STATISTICS_FONT.render("Pipe Diff.: " + str(pipe_difficulty), True, (0, 0, 0))

        SCREEN.blit(text_1, (132, 18))
        SCREEN.blit(text_2, (132, 34))
        SCREEN.blit(text_3, (132, 50))
        SCREEN.blit(text_4, (132, 66))
        SCREEN.blit(text_5, (132, 82))

    def background():
        SCREEN.blit(BACKGROUND, (0, 0))

    run = True
    while run:
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                pygame.quit()
                sys.exit()

            if event.type == pygame.KEYDOWN:
                if event.key == pygame.K_1:
                    fps = 30
                elif event.key == pygame.K_2:
                    fps = 60
                elif event.key == pygame.K_3:
                    fps = 120
                elif event.key == pygame.K_4:
                    fps = 240

        SCREEN.fill((255, 255, 255))

        background()

        for bird in birds:
            bird.update()
            bird.draw(SCREEN)

        if len(birds) == 0:
            break

        if len(obstacles) == 0:
            random_height = random.randint(SCREEN_HEIGHT - PIPE_BOTTOM.get_height(), SCREEN_HEIGHT - 96)
            obstacles.append(Obstacle(PIPE_BOTTOM, random_height))
            obstacles.append(Obstacle(PIPE_TOP, random_height - (496 - pipe_difficulty)))

        for obstacle in obstacles:
            obstacle.draw(SCREEN)
            obstacle.update()
            for i, bird in enumerate(birds):
                if bird.rect.colliderect(obstacle.rect) or bird.rect.y < 0 or bird.rect.y > SCREEN_HEIGHT:
                    print("Fitness: " + str(ge[i].fitness))
                    if points > high_score:
                        high_score = points
                    remove(i)

        for i, bird in enumerate(birds):
            output = nets[i].activate((SCREEN_HEIGHT, bird.rect.y, bird.flap_velocity,
                                       distance((bird.rect.x, bird.rect.y), obstacle.rect.midtop)))
            if output[0] > 0.5:
                bird.bird_flap = True

        SCREEN.blit(STATISTICS_FONT.render("[1-4]: toggle sim. speed", True, (0, 0, 0)), (18, 480))

        statistics()
        score()

        clock.tick(fps)
        pygame.display.update()


def run(c_path):
    global pop
    config = neat.config.Config(
        neat.DefaultGenome,
        neat.DefaultReproduction,
        neat.DefaultSpeciesSet,
        neat.DefaultStagnation,
        c_path
    )

    pop = neat.Population(config)
    pop.run(eval_genomes, 50)


if __name__ == '__main__':
    local_dir = os.path.dirname(__file__)
    config_path = os.path.join(local_dir, 'config.txt')
    run(config_path)
