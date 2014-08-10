#!/usr/bin/env python

# Analogue PiPong using the PiMagic interface board, channels A0/A1
# ( based on the original PiPong by Liam Fraser - 28/07/2012.
#    www.linuxuser.co.uk/tutorials/make-a-game-on-raspberry-pi )
# @croz_tech   V1.0  21/09/2013  (Steve Crozier)
#              - Note that the first version has only one analogue paddle on A0


import pygame # Provides what we need to make a game
import sys # Gives us the sys.exit function to close our program
import random # Can generate random positions for the pong ball
import pyfirmata # Connection/comms to the PiMagic with firmata protocol

from pygame.locals import *
from pygame import *

# Our main game class
class PiPong:
	
	def __init__(self):
		
		# Make the display size a member of the class
		self.displaySize = (640, 480)
		
		# Initialize pygame
		pygame.init()
		
		# Create a clock to manage time
		self.clock = pygame.time.Clock()
		
		# Set the window title
		display.set_caption("Pi Pong")
		
		# Create the window
		self.display = display.set_mode(self.displaySize)
			
		# Create the background, passing through the display size
		self.background = Background(self.displaySize)
	
		# Create a board object for the piMagic
		self.board=pyfirmata.Arduino('/dev/ttyAMA0')
		
		# Start an interator thread to prevent buffer overflow
		self.iter8 = pyfirmata.util.Iterator(self.board)
		self.iter8.start()
		
		# Set up pins
		# A0.. analogue input
		self.pin0 = self.board.get_pin('a:0:i')
		
		# Discard reads until A0 reads valid
		while self.pin0.read() is None:
			pass
		
		# Create two bats, a ball and add them to a sprite group
		self.player1Bat = Bat(self.displaySize, "player1")
		self.player2Bat = Bat(self.displaySize, "player2")
		self.ball = Ball(self.displaySize)
		self.sprites = sprite.Group(self.player1Bat, self.player2Bat,
		self.ball)
		
	
	def run(self):
		# Runs the game loop
		
		while True:
			# The code here runs when every frame is drawn
					
			# Handle Events
			self.handleEvents()
			
			# Draw the background
			self.background.draw(self.display)
						
			# Update and draw the sprites
			self.sprites.update()
			self.sprites.draw(self.display)
			
			# Check for bat collisions
			self.ball.batCollisionTest(self.player1Bat)
			self.ball.batCollisionTest(self.player2Bat)
			
			# Update the full display surface to the screen
			display.update()
			
			# Read the analogue paddle(s)
			self.bat1pos = self.pin0.read()
			self.player1Bat.moveTo(self.bat1pos)
			
			# Limit the game to 30 frames per second
			self.clock.tick(30)
			
	def handleEvents(self):
		
		# Handle events, starting with the quit event
		for event in pygame.event.get():
			if event.type == QUIT:
				pygame.quit()
				self.board.exit()
				sys.exit()
			
			if event.type == KEYDOWN:
				# Find which key was pressed and start moving appropriate bat
				if event.key == K_s:
					# Start moving bat
					self.player1Bat.startMove("down")
				elif event.key == K_w:
					self.player1Bat.startMove("up")
				if event.key == K_DOWN:
					self.player2Bat.startMove("down")
				elif event.key == K_UP:
					self.player2Bat.startMove("up")
			
			if event.type == KEYUP:
				if event.key == K_s or event.key == K_w:
					self.player1Bat.stopMove()
				elif event.key == K_DOWN or event.key == K_UP:
					self.player2Bat.stopMove()
				
# The class for the background
class Background:
	
	def __init__(self, displaySize):
		
		# Set our image to a new surface, the size of the screen rectangle
		self.image = Surface(displaySize)
		
		# Fill the image with a green colour (specified as R,G,B)
		self.image.fill((27, 210, 57))
		
		# Get width proportionate to display size
		lineWidth = displaySize[0] / 80
		
		# Create a rectangle to make the white line
		lineRect = Rect(0, 0, lineWidth, displaySize[1])
		lineRect.centerx  = displaySize[0] / 2
		draw.rect(self.image, (255, 255, 255), lineRect)
		
	def draw(self, display):
			
		# Draw the background to the display that has been passed in
		display.blit(self.image, (0,0))

# The class for the bats on either side
class Bat(sprite.Sprite):
	
	def __init__(self, displaySize, player):
			
		# Initialize the sprite base class
		super(Bat, self).__init__()
		
		# Make player a member variable
		self.player = player
		
		# Get a width and height values proportionate to the display size
		width = displaySize[0] / 80
		height = displaySize[1] / 6
		self.dispheight = displaySize[1]
		
		# Create an image for the sprite using the width and height
		# we just worked out
		self.image = Surface((width, height))
		
		# Create the sprites rectangle from the image
		self.rect = self.image.get_rect()
		
		# Set the rectangle's location depending on the player
		if player == "player1":
			# Left side
			self.rect.centerx = displaySize[0] / 20
			# Fill dark green
			self.image.fill((0, 128, 0))
		elif player == "player2":
			# Right side
			self.rect.centerx = displaySize[0] - displaySize[0] / 20
			# Fill dark red
			self.image.fill((128, 0, 0))
		
		# Center the rectangle vertically
		self.rect.centery = displaySize[1] / 2
		
		# Set a bunch of direction and moving variables
		self.moving = False
		self.direction = "none"
		self.speed = 13
		
	def startMove(self, direction):
		
		# Set the moving flag to true
		self.direction = direction
		self.moving = True
		
	def update(self):
		
		if self.moving:
			# Move the bat up or down if moving
			if self.direction == "up":
				self.rect.centery -= self.speed
			elif self.direction == "down":
				self.rect.centery += self.speed
				
	def stopMove(self):

		self.moving = False
		
	def moveTo(self,pos):
		
		self.rect.centery = (self.dispheight)*pos

# The class for the ball
class Ball(sprite.Sprite):
	
	def __init__(self, displaySize):
			
		# Initialize the sprite base class
		super(Ball, self).__init__()
		
		# Get the display size for working out collisions later
		self.displaySize = displaySize
		
		# Get a width and height values proportionate to the display size
		width = displaySize[0] / 30
		height = displaySize[1] / 30
		
		# Create an image for the sprite
		self.image = Surface((width, height))
		
		# Fill the image blue
		self.image.fill((27, 224, 198))
		
		# Create the sprites rectangle from the image
		self.rect = self.image.get_rect()
			
		# Work out a speed
		self.speed = displaySize[0] / 110
	
		# Reset the ball
		self.reset()
	
	def reset(self):
		
		# Start the ball directly in the centre of the screen
		self.rect.centerx = self.displaySize[0] / 2
		self.rect.centery = self.displaySize[1] / 2
		
		# Start the ball moving to the left or right (pick randomly)
		# Vector(x, y)
		if random.randrange(1, 3) == 1:
			# move to left
			self.vector = (-1, 0)
		else:
			# move to right
			self.vector = (1, 0)
	
	def update(self):
		
		# Check if the ball has hit a wall
		if self.rect.midtop[1] <= 0:
			# Hit top side
			self.reflectVector()
		elif self.rect.midleft[0] <= 0:
			# Hit left side
			self.reset()
		elif self.rect.midright[0] >= self.displaySize[0]:
			self.reset()
		elif self.rect.midbottom[1] >= self.displaySize[1]:
			# Hit bottom side
			self.reflectVector()
		
		# Move in the direction of the vector
		self.rect.centerx += (self.vector[0] * self.speed)
		self.rect.centery += (self.vector[1] * self.speed)
	
	def reflectVector(self):
		
		# Gets the current angle of the ball and reflects it, for bouncing
		# off walls
		deltaX = self.vector[0]
		deltaY = - self.vector[1]
		self.vector = (deltaX, deltaY)
		
		
	def batCollisionTest(self, bat):
	
		# Check if the ball has had a collision with the bat
		if Rect.colliderect(bat.rect, self.rect):
			
			# Work out the difference between the start and end points
			deltaX = self.rect.centerx - bat.rect.centerx
			deltaY = self.rect.centery - bat.rect.centery
			
			# Make the values smaller so it's not too fast
			deltaX = deltaX / 12
			deltaY = deltaY / 12
			
			# Set the balls new direction
			self.vector = (deltaX, deltaY)
			
if __name__ == '__main__':
	game = PiPong()
	game.run()

