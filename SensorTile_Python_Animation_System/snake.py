import pygame
import SensorTile_Serial
import sys
import numpy as np
from random import randint

# Global Variables
BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
PINK = (255, 77, 255)
GREEN = (10, 255, 37)

segment_width = 15
segment_margin = 3
grid_unit = segment_width + segment_margin

x_change = grid_unit
y_change = 0

tilt_thresh = 500

# Serial setup according to command line arguments
python_version = sys.version[0]

if len(sys.argv) != 2:
	print ("Wrong Number of Arguments!")
	print ("Please use format: python SensorTile_Animation_args.py SerialAddress")

else:

	address = sys.argv[1]
	if python_version == "2":
		python3 = False

	else:
		python3 = True

baud_rate = 9600

timeout = 2


# data parameters
x_len = 200
tx = [0] * x_len
ty = [0] * x_len


# serial initialization
sensortile = SensorTile_Serial.serial_SensorTile(address, baud_rate, timeout, python3)
sensortile.init_connection()


# Game Initialization
screen = pygame.display.set_mode([540, 360])
pygame.display.set_caption('Snake Game')
clock = pygame.time.Clock()
pygame.font.init()
font = pygame.font.SysFont('mono', 24, bold=True)

# Classes
class Segment(pygame.sprite.Sprite):
	def __init__(self, x, y):
		super(Segment, self).__init__()

		self.image = pygame.Surface([segment_width, segment_width])
		self.image.fill(WHITE)

		self.rect = self.image.get_rect()
		self.rect.x = x
		self.rect.y = y

class Food(pygame.sprite.Sprite):
	def __init__(self):
		super(Food, self).__init__()

		self.image = pygame.Surface([segment_width, segment_width])
		self.image.fill(PINK)

		self.rect = self.image.get_rect()
		self.rect.x = self.randomCoord(screen.get_width())
		self.rect.y = self.randomCoord(screen.get_height())

	def randomCoord(self, upperBound):
		coord = randint(0, upperBound//(grid_unit)-1) * grid_unit
		return coord

	def eaten(self):
		self.rect.x = self.randomCoord(screen.get_width())
		self.rect.y = self.randomCoord(screen.get_height())

class GameStats:
	def __init__(self, score = 0):
		self.score = score

	def increaseScore(self):
		self.score += 1

	def displayScore(self):
		text = 'Score: ' + str(self.score)
		fw, fh = font.size(text)
		surface = font.render(text, True, GREEN)
		screen.blit(surface, ((screen.get_width() - fw)//2, 10))

	def gameOver(self):
		screen.fill(BLACK)
		text = 'Game Over'
		fw, fh = font.size(text)
		surface = font.render(text, True, GREEN)
		screen.blit(surface, ((screen.get_width() - fw)//2, 140))

		textScore = 'Score: ' + str(self.score)
		fw, fh = font.size(textScore)
		surface = font.render(textScore, True, GREEN)
		screen.blit(surface, ((screen.get_width() - fw)//2, 170))

allspriteslist = pygame.sprite.Group()

snake_segments = []

for i in range(3):
	x = 252 - (segment_width + segment_margin) * i
	y = 36
	segment = Segment(x, y)

	snake_segments.append(segment)
	allspriteslist.add(segment)


food = Food()
allspriteslist.add(food)

gamestats = GameStats()

# Runs our game
done = False
while not done:

	# get displacement, acceleration
	tilt_x_list, tilt_y_list = sensortile.collect_data()

	# Add dis and accel to lists
	tx.extend(tilt_x_list)
	ty.extend(tilt_y_list)

	# Limit x and y lists to 200 samples - 2s 
	t_x = tx[-1]
	t_y = ty[-1] 

	if t_x < -tilt_thresh: # left
		x_change = grid_unit *-1
		y_change = 0
	elif t_x > tilt_thresh: # right
		x_change = grid_unit 
		y_change = 0
	elif t_y < -tilt_thresh: # down
		x_change = 0
		y_change = grid_unit
	elif t_y > tilt_thresh: # up
		x_change = 0
		y_change = grid_unit *-1

	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			# shutdown the system after closing the plot
			sensortile.close_connection()
			pygame.quit()

		if event.type == pygame.KEYDOWN:
			if event.key == pygame.K_LEFT:
				x_change = grid_unit * -1
				y_change = 0
			if event.key == pygame.K_RIGHT:
				x_change = grid_unit 
				y_change = 0
			if event.key == pygame.K_DOWN:
				x_change = 0
				y_change = grid_unit
			if event.key == pygame.K_UP:
				x_change = 0
				y_change = grid_unit * -1

	# check if overlapped food
	if snake_segments[0].rect.x == food.rect.x and snake_segments[0].rect.y == food.rect.y:
		food.eaten()
		gamestats.increaseScore()
	else:
		old_segment = snake_segments.pop()
		allspriteslist.remove(old_segment)

	x = snake_segments[0].rect.x + x_change
	y = snake_segments[0].rect.y + y_change
	segment = Segment(x, y)

	snake_segments.insert(0, segment)
	allspriteslist.add(segment)


	first_segment = snake_segments[0].rect
	# if goes off screen
	if first_segment.x < 0 or first_segment.x > screen.get_width():
		break
	if first_segment.y < 0 or first_segment.y > screen.get_height():
		break

	for seg in snake_segments[1:]:
		if first_segment.x == seg.rect.x and first_segment.y == seg.rect.y:
			done = True
			break

	# Draw everything
	screen.fill(BLACK)

	allspriteslist.draw(screen)

	gamestats.displayScore()

	pygame.display.flip()
	clock.tick(5)


exit = False
while not exit:
	for event in pygame.event.get():
		if event.type == pygame.QUIT:
			sensortile.close_connection()
			pygame.quit()
			# shutdown the system after closing the plot
			

	gamestats.gameOver()
	pygame.display.flip()

sensortile.close_connection()
pygame.quit()