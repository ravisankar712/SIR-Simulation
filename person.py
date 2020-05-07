import numpy as np
import pygame as pg

pg.init()
width = 600
height = 600
canvas = pg.display.set_mode((width, height))

class Person:

	def __init__(self, x, y, compartments = 1):
		self.pos = np.array([x, y])
		self.vel = np.random.random(2) * 2 - 1
		self.acc = np.zeros(2)
		self.maxSpeed = 5.0
		self.Speed_memory = self.maxSpeed
		self.size = 4
		self.perception = 50
		self.condition = 'S'
		self.prob_inf = 0.02 #prob of getting infected
		self.clock = 0			#internal clock to keep track of recovery time
		#compartmentalising the object based on its pos
		self.res = int(np.sqrt(compartments))
		grid_x = int(self.res * self.pos[0]/width)
		grid_y = int(self.res * self.pos[1]/height)
		self.locality = [grid_x, grid_y]

		#intercompartment travel stuff
		self.prob_interstate = 0.002 #prob of traveling to another compartment
		self.flying = False				#variable is true only when traveling to other compartments
		self.next_locality = []			#the compartment to which the object is flying
		self.next_pos = np.zeros(2)		#the position to which object is flying

		#recovery and other stuff.
		self.recovery_time = 120
		self.symptoms = True
		self.under_quarantine = False	
		self.symptom_time = 50
		self.quarantine_zone = True

	#making some objects symptomless based on a given prob
	def set_symptoms(self, prob):
		if np.random.random() < prob:
			pass
		else:
			self.symptoms = False

	#making the quarantine zone facility on and off
	def set_quarantinezone(self, value):
		self.quarantine_zone = value

	#drawing
	def show(self):
		if self.condition == 'S':
			color = (0, 200, 255)	#susceptible are blue
		elif self.condition == 'I':
			if self.symptoms:
				color = (255, 100, 0)	#infected with symptoms is red
			else:
				color = (255, 255, 0)	#infected without symptoms is yellow
		elif self.condition == 'R':
			color = (255, 255, 255)		#recovered is white

		#if object is newly infected, its radius doubles for a short time. blink() keeps the track of it
		if self.blink():				
			r = self.size * 2
		else:
			r = self.size

		pg.draw.circle(canvas, color, [int(self.pos[0]), int(self.pos[1])], int(r))

	def blink(self):
		blink = False
		if 1 < self.clock < 10:
			blink = True
		return blink

	def update(self):
		self.edges()
		if self.condition == 'I': #if infected, check for recovery. If not recovered, internal clock ticks
			self.recovery()
			self.clock += 1
		self.vel += self.acc
		#limiting the speed
		if np.linalg.norm(self.vel) > self.maxSpeed:
			self.vel = self.vel/np.linalg.norm(self.vel) * self.maxSpeed
		self.pos += self.vel
		self.acc *= 0.0

	def edges(self):
		#collides with edges only when not flying
		if not self.flying:
			x, y = self.pos
			i, j = self.locality 

			#finding edges based on the locality.
			lower_x = i * width / self.res
			upper_x = (i + 1) * width / self.res
			lower_y = j * height / self.res
			upper_y = (j + 1) * height / self.res

			if x < lower_x :
				self.pos[0] = lower_x 
				self.acc[0] *= -1
				self.vel[0] *= -1
			if x > upper_x - self.size:
				self.pos[0] = upper_x - self.size
				self.acc[0] *= -1
				self.vel[0] *= -1
			if y < lower_y :
				self.pos[1] = lower_y
				self.acc[1] *= -1
				self.vel[1] *= -1
			if y > upper_y - self.size:
				self.pos[1] = upper_y - self.size
				self.acc[1] *= -1
				self.vel[1] *= -1
		else:
			self.fly(self.next_pos[0], self.next_pos[1])

	#the random walk
	def walk(self):
		if np.random.random() < 0.5:
			self.acc += (np.random.random(2) - 0.5) * 2
		# if np.linalg.norm(self.acc) > self.maxSpeed:
			# self.acc = self.acc/np.linalg.norm(self.acc) * self.maxSpeed 

	def get_infection(self, other):
		#if susceptible, and see another which is infected under the perception radius,
		#while both self and other are not flying, then get infected with some probability
		if self.condition == 'S':
			for o in other:
				if o.condition == 'I' and o.locality == self.locality and not o.flying and not self.flying:
					d = np.linalg.norm(self.pos - o.pos)
					if 0 < d < self.perception:
						if np.random.random() < self.prob_inf:
							self.condition = 'I'

	#I becomes R after the recovery time.
	def recovery(self):
		if self.condition == 'I' and self.clock > self.recovery_time:
			self.condition = 'R'

	#social distancing is a repulsive force, towards someone in the same compartment, who is not flying.
	#perception is twice as that of infection.
	def social_distancing(self, other):
		for o in other:
			if o.locality == self.locality and not o.flying and not self.flying:
				f = self.pos - o.pos
				d = np.linalg.norm(f)
				if 0 < d < self.perception * 2:
					self.acc += f/d * self.maxSpeed 

	#intercompartment traveling. Doesnt do so while flying or under quarantine.
	def travel_interstate(self):
		if np.random.random() < self.prob_interstate and not self.flying and not self.under_quarantine:
			new_x = np.random.random() * width
			new_y = np.random.random() * height
			
			grid_x = int(self.res * new_x/width)
			grid_y = int(self.res * new_y/height)
			new_locality = [grid_x, grid_y]
			if self.locality ==  new_locality :
				pass
			elif self.quarantine_zone and new_locality == [self.res - 1, self.res - 1]:
				pass
			else:
				self.next_locality = [grid_x, grid_y]
				self.next_pos = np.array([new_x, new_y])
				self.flying = True

	#flying to another pos
	def fly(self, x, y):
		new_pos = np.array([x, y])
		f = self.pos - new_pos
		d = np.linalg.norm(f)

		if d > width/(self.res*2):
			self.acc -= f
			self.maxSpeed += 1

		else:
			self.pos = self.next_pos
			self.locality = self.next_locality
			self.maxSpeed = self.Speed_memory
			self.flying = False

	#quarantining, if there is facility and object shows symptoms (it takes a while to show the symptoms)
	def get_quarantined(self):
		if self.quarantine_zone and self.symptoms and self.condition == 'I' and not self.under_quarantine and self.clock > self.symptom_time:
			#quarantine is implemented using the fly. An additional compartment at the end, of width 100
			self.next_locality = [self.res, self.res]
			self.next_pos = np.array([width + width/(self.res*2), height + height/(self.res*2)])
			#if inside quarantine zone, stop doing inter compartment, dont percieve anyone. Else fly to the zone!
			if np.linalg.norm(self.next_pos - self.pos) < width/(self.res*2):
				self.under_quarantine = True
				self.prob_interstate = -1
				self.perception = 0
				self.maxSpeed = 2.0 #under quarantine, max speed is reduced (just for aesthetic purposes!)
			else:
				self.maxSpeed += 2 #when going to quarantine, speed increses(aesthetics!)
				self.flying = True