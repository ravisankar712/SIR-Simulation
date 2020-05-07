import pygame as pg 
import person as person
import numpy as np
import matplotlib.pyplot as plt

##parameters under control
pop_size = 300
compartments = 9  #must be a complete square
initilial_infected = 1
infection_probability = 0.5
perception_radius = 20 #in pixels
recovery_time = 250 #in frames
time_for_symptoms_to_start = 100 #in frames. This is the time after which person will go to quarantine
interstate_travel_probability = 0.002
quarantine_facility = True 
prob_showing_symptoms = 0.8  #probability that patient shows symptoms
social_distancing_starts_at = 50
quarantine_starts_at = 20 #the threshold number of patients after which quarantine and social dist starts
airport_shuts_at = 50 #the threshold after which interstate travel stops
dynamical_rule_changes = True #if true, quarantining, social distancing etc. will be stopped again if the number goes below the threshold



##setting up the population and the scene
pg.init()
width = 600
height = 600
clock = pg.time.Clock()
frame_rate = 40
res = int(np.sqrt(compartments))
#if there is quarantine facility, the dimensions of the boxes are rescaled(aesthetics!)
if quarantine_facility:
	width = res * 150
	height= res * 150
person.width = width
person.height = height
if quarantine_facility:
	canvas = pg.display.set_mode((int(width + width/res), int(height + height/res)))
else:
	canvas = pg.display.set_mode((int(width), int(height)))

#initialising the population
pop = [person.Person(np.random.random()*width, np.random.random()*height, compartments) 
			for i in range(pop_size)]

#initialising the initial infected
for i in range(initilial_infected):
	pop[i].condition = 'I'

#initialising the population with the given parameters and condtions
for p in pop:
	p.prob_inf = infection_probability
	p.perception = perception_radius
	p.recovery_time = recovery_time
	p.prob_interstate = interstate_travel_probability
	p.symptom_time = time_for_symptoms_to_start
	p.set_quarantinezone(quarantine_facility)
	p.set_symptoms(prob_showing_symptoms)

##drawing the compartments
def draw_grid(compartments):
	for i in range(res + 1):
		x = i * width / res
		y = i * height / res
		pg.draw.line(canvas, (255, 255, 255), (0, y), (width, y), 3)
		pg.draw.line(canvas, (255, 255, 255), (x, 0), (x, height), 3)
	if quarantine_facility == True:
		pg.draw.rect(canvas, (0, 100, 0, 50), [width, height, int(width/res), int(height/res)])
		pg.draw.line(canvas, (0, 255, 0), (width, height), (width, int(height + height/res)), 3)
		pg.draw.line(canvas, (0, 255, 0), (width, height), (int(width + width/res), height), 3)

#for the plot
d = 0
days = []
Ns = []
Ni = []
Nr = []
Q = False	#quarantine condition flag
A = False	#Travel condition flag
S = False	#social distancing flag
while True:
	for event in pg.event.get():
		if event.type == pg.QUIT:
			#plotting
			plt.plot(days, Ns, label = 'Unaffacted', color='blue')
			plt.plot(days, Ni, label = 'Infected with symptoms', color='red')
			plt.plot(days, Nr, label = 'Recovered',color='green')
			plt.legend()
			plt.suptitle('SIR Model')
			plt.xlabel('Time (in days)')
			plt.ylabel('Number of individuals')
			plt.show()
			pg.quit()
			quit()

	#counting in each frame
	ns = 0
	nr = 0
	ni = 0
	for p in pop:
		if p.condition == 'S':
			ns += 1
		elif p.condition == 'I' and p.symptoms:
			ni += 1
		else:
			nr += 1
	Ns.append(ns)
	Nr.append(nr)
	Ni.append(ni)
	days.append(d)
	d += 1

	canvas.fill(51)
	draw_grid(compartments)
	for p in pop:
		p.show()
		p.walk()
		if dynamical_rule_changes: #chacks for the condition every frame(hence dynamic changes in rules while the run)
			Q = Ni[-1] >= quarantine_starts_at
			A = Ni[-1] >= airport_shuts_at
			S = Ni[-1] >= social_distancing_starts_at
		else:		#chack the conditions till the condtions are true(hence no changes in rules while the run)
			if not Q:
				Q = Ni[-1] >= quarantine_starts_at
			if not A:
				A = Ni[-1] >= airport_shuts_at
			if not S:
				S = Ni[-1] >= social_distancing_starts_at

		if S:
			p.social_distancing(pop)
		if Q:
			p.get_quarantined()
		if not A:
			p.travel_interstate()
		p.get_infection(pop)
		p.update()

	pg.display.update()
	clock.tick(frame_rate)