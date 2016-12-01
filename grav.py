import numpy as np

import pygame
from pygame.locals import *
from pygame import gfxdraw

import copy

pygame.init()
pygame.font.init()
Font = pygame.font.SysFont("Calibri", 10)
Font2 = pygame.font.SysFont('Calibri', 11)

G = 2.01e-1 #m^3/(kg s^2)

class body:
	def __init__(self, mass, pos):
		self.mass = mass
		self.acceleration_vector = np.asarray([0., 0., 0.])	# x, y and z coordinates respectively
		self.velocity = np.asarray([0., 0., 0.,])

		self.pos_array = []

		self.force_vector = np.asarray([0., 0., 0.,])
		self.pos = np.asarray(pos).astype(float)
		self.prev_pos = np.asarray(pos).astype(float)

		self.color = [np.random.randint(0, 255), np.random.randint(0, 255), np.random.randint(0, 255)]

		self.in_place = False

	def calculate_grav(self, other_bodies):
		force_w_direction = np.asarray([0., 0., 0.,])
		
		for i in other_bodies:
			dist = distance(self.pos, i.pos)
			
			if dist < 2:	  # Probably really close together
				pass
			else:
				force = G * (self.mass * i.mass)/dist ** 2  # Points in direction i.pos - self.pos
				direction = normalize(i.pos - self.pos)

				force_w_direction += direction * force
			
		self.force_vector = force_w_direction 
		self.acceleration_vector = force_w_direction/self.mass   # F = ma, so acceleration = F\m
	
	
	def update(self):
		self.prev_pos = copy.deepcopy(self.pos)
		self.velocity += self.acceleration_vector
		self.pos += self.velocity 

		#if len(self.pos_array) == 600:
		#	del self.pos_array[0]

		#self.pos_array.append(copy.deepcopy(self.pos))

def normalize(vec):
	n = np.linalg.norm(vec)
	return vec/n

def distance(vec_1, vec_2):
	return np.linalg.norm(vec_1 - vec_2)

def sigmoid(val):
	return 1/(1 + np.e**-val)

def clamp(val, min, max):
	if val < min:
		return min
	elif val > max:
		return max
	return val

def sqrt(val):
	return val ** 0.4

def softmax(x):
	"""Compute softmax values for each sets of scores in x."""
	e_x = np.exp(x - np.max(x))
	return e_x / e_x.sum(axis=0) # only difference	

def main():
	screen = pygame.display.set_mode((1000, 1000))
	#screen.fill((0, 0, 0))

	#bodies = [body(mass = np.random.randint(10, 1000), pos = [np.random.randint(100, 900), np.random.randint(100, 900), np.random.randint(100, 900)]) for i in range (10)]
	bodies = []
	#for i in range (len(bodies)):
	#	bodies[i].velocity = np.asarray([np.random.randint(-300, 300), np.random.randint(-300, 300), np.random.randint(-300, 300)]).astype(float)/1000

	cont = True
	shiftx = 0
	add_shiftx = 0
	shifty = 0
	add_shifty = 0
	dragging = False 
	drag_pos = [0, 0]
	pause = False
	index = 0
	scale = 1
	tracing = False
	following = False
	setting_velocity = False

	manipulating_body = False
	difference = np.asarray([0., 0.,])

	trace = pygame.Surface((10000, 10000))
	trace.fill((0, 0, 0))

	delete = Font2.render('Delete', 1, (255, 100, 100))
	goto = Font2.render('Goto', 1, (100, 255, 100))

	while cont:
		try:
			bodies[index].pos == 1
		except IndexError:
			index = 0


		bodies_to_delete = []
		bodies_to_add = []
		bodies_to_add_velocity = []
		
		mouse_pos = np.asarray(pygame.mouse.get_pos())

		for event in pygame.event.get():
			if event.type == pygame.QUIT:
				cont = False 
			
			elif event.type == pygame.MOUSEBUTTONDOWN:
				if event.dict['button'] == 4:
					bodies[index].mass += 10
				elif event.dict['button'] == 5:
					bodies[index].mass -= 10
					if bodies[index].mass < 0:
						bodies[index].mass = 1
					
				if pygame.mouse.get_pressed() == (0, 0, 1) or pygame.mouse.get_pressed() == (0, 1, 0) or pygame.mouse.get_pressed() == (1, 0, 0):

					if screen.get_at(mouse_pos) != (0, 0, 0) and screen.get_at(mouse_pos) != (255, 100, 100):
						for i in range (len(bodies)):
							
							if tuple(bodies[i].color) == screen.get_at(mouse_pos)[0:3]:
								index = i
						
								manipulating_body = True
								print manipulating_body
								dragging = False

					else:
						if pygame.mouse.get_pressed() != (1, 0, 0):
							bodies.append(body(mass = 1, pos = [mouse_pos[0] - shiftx, mouse_pos[1] - shifty, 0]))
							dragging = False
						else:
							dragging =True
							drag_pos = mouse_pos
				
				else:
					
					dragging = True
					drag_pos = mouse_pos 
			
			
			elif event.type == pygame.KEYDOWN:
				if event.key == pygame.K_SPACE:
					pause = not pause	
				elif event.key == pygame.K_DELETE:
					del bodies[index]
				elif event.key == pygame.K_t:
					tracing = not tracing 
				elif event.key == pygame.K_r:
					trace.fill((0, 0, 0))
				elif event.key == pygame.K_ESCAPE:
					bodies[index].velocity = np.asarray([0., 0., 0.,])
				elif event.key == pygame.K_p:
					bodies[index].in_place = not bodies[index].in_place
				elif event.key == pygame.K_f:
					following = not following
			
	
			elif event.type == pygame.MOUSEMOTION:
				if dragging:
					add_shiftx = mouse_pos[0] - drag_pos[0]
					add_shifty = mouse_pos[1] - drag_pos[1]
				if manipulating_body and pygame.mouse.get_pressed() == (0, 1, 0):
					dist = distance(bodies[index].pos[0:2] + shift_vec[0:2], np.asarray(mouse_pos))
					bodies[index].mass = dist
				if manipulating_body and pygame.mouse.get_pressed() == (1, 0, 0):
					dragging = False
					bodies[index].pos = np.asarray([float((np.asarray(mouse_pos) - shift_vec[0:2])[0]), float((np.asarray(mouse_pos) - shift_vec[0:2])[1]), 0.])

			elif event.type == pygame.MOUSEBUTTONUP:
				
				manipulating_body = False
				dragging = False
				shiftx += add_shiftx
				shifty += add_shifty
				add_shiftx = 0
				add_shifty = 0

		screen.fill((0, 0, 0))
		if tracing:
			#trace.scroll(dx = add_shiftx, dy = add_shifty)
			screen.blit(trace, shift_vec - 5000)


		if manipulating_body and pygame.mouse.get_pressed() == (0, 0, 1):
			  # print 'drawing'
			pygame.draw.aaline(screen, (255, 100, 100), bodies[index].pos[0:2].astype(int) + shift_vec[0:2], np.asarray(mouse_pos) )
			pygame.gfxdraw.aacircle(screen, ( np.asarray(mouse_pos))[0], (np.asarray(mouse_pos))[1], 5,  (100, 100, 255))

			difference = np.asarray(mouse_pos) - bodies[index].pos[0:2].astype(int) - shift_vec[0:2]
			difference/=2

			setting_velocity = True
			bodies[index].velocity = np.asarray([float(-difference[0]/100.0), float(-difference[1]/100.0), 0.,])
			#pygame.draw.aaline(screen, (100, 255, 100), bodies[index].pos[0:2].astype(int) + shift_vec[0:2], bodies[index].pos[0:2].astype(int) + shift_vec[0:2] -difference)

		if following:
			shift_vec = -copy.deepcopy(bodies[index].pos[0:2].astype(int)) + 500
		elif dragging:
			
			shift_vec = np.asarray([shiftx + add_shiftx, shifty + add_shifty])
		else:
			shift_vec = np.asarray([shiftx, shifty])

		

		if not pause:
			for i in range(len(bodies)):
				bodies[i].calculate_grav(bodies[0:i] + bodies[i + 1:])
			for i in range (len(bodies)):	
				if not bodies[i].in_place:
					bodies[i].update()
		for i in range (len(bodies)):
			
			for j in range (len(bodies)):
				if distance(bodies[i].pos, bodies[j].pos) < (int(sqrt(bodies[i].mass))  + int(sqrt(bodies[j].mass)) ) and distance(bodies[i].pos, bodies[j].pos) != 0:
					# Collision
					
					if bodies[i].mass > bodies[j].mass:
						larger = i
						smaller = j
					else:
						larger = j
						smaller = i
					
					if bodies[i].mass < 100 or bodies[j].mass < 100:
						bodies[larger].mass += bodies[smaller].mass 
						bodies_to_delete.append(smaller)
					else:
					
						direction_vec = normalize(bodies[smaller].pos - bodies[larger].pos)
						bodies_to_add = np.random.randint(3, 5)
					
						random_nums = np.random.uniform(size = bodies_to_add)
						ratios = softmax(random_nums)
					
						bodies[larger].mass += bodies[smaller].mass/2.0
						half_mass = bodies[smaller].mass /2.0
					
						for body_ in range (bodies_to_add):
							vector = normalize(direction_vec + np.random.uniform(low = -0.1, high = 0.1, size = 3))
							dir_vector = copy.deepcopy(vector) * (int(sqrt(bodies[larger].mass)) + int(sqrt(ratios[body_] * half_mass)) + 50)
							bodies_to_add.append(body(mass = ratios[body_] * half_mass, pos = bodies[larger].pos + dir_vector))
							bodies_to_add[-1].velocity = copy.deepcopy(np.asarray(vector))/1
					
						bodies_to_delete.append(smaller)
					pause = True
			pos = bodies[i].pos[0:2] + shift_vec[0:2]

			if tracing and not pause:
				

				pygame.draw.aaline(trace, bodies[i].color, bodies[i].prev_pos[0:2].astype(int) + 5000 , bodies[i].pos[0:2].astype(int) + 5000 )
			
			if pos[0] > 1000 or pos[0] < 0 or pos[1] > 1000 or pos[1] < 0:
				
				mass = Font2.render(str(round(bodies[i].mass, 3)), 1, (255, 255, 255))
				velocity = Font2.render(str(np.round(bodies[i].velocity, 3)), 1, (100, 100, 255))
				dist = distance(np.asarray([500, 500]), pos)
				dist_marker = Font2.render('(' + str(round(dist, 3)) + 'm)', 1, (255, 255, 255))
				
				
				vec = normalize(pos - np.asarray([500., 500.]))
				
				angle =( np.math.atan2(vec[0], vec[1]) - np.math.atan2(normalize(np.asarray([0., 1.,]))[1], normalize(np.asarray([0., 1.,]))[0]))
				#angle = np.math.acos(np.dot(vec, normalize(np.asarray([0., 1.]))))
				
				angle = abs(angle)

				angle_in_degrees = np.math.degrees(angle)
				angle -= np.math.radians(int((angle_in_degrees + 45))/90 * 90)

				length =(500/np.cos(angle)) 
				#print length
				pygame.draw.aaline(screen, bodies[i].color, 500 + (vec * (length - 60)).astype(int), 500 + (vec * (length)).astype(int))

				text_pos = 500+ (vec * (length - 90)).astype(int)
				screen.blit(mass, (text_pos[0], text_pos[1]))
				screen.blit(velocity, (text_pos[0], text_pos[1] + 12))

				screen.blit(dist_marker, (text_pos[0] + 1, text_pos[1] + 24))

				mouse_pos = mouse_pos 
				if (text_pos[0] + 50) >mouse_pos[0] > text_pos[0] and (text_pos[1] + 50) > mouse_pos[1] > (text_pos[1] + 40):
					pygame.draw.rect(screen, (240, 240, 240), (text_pos[0], text_pos[1] + 40, 50, 10))
					if pygame.mouse.get_pressed() == (1, 0, 0):
						bodies_to_delete.append(i)

				if (text_pos[0] + 50) >mouse_pos[0] > text_pos[0] and (text_pos[1] + 65) > mouse_pos[1] > (text_pos[1] + 55):
					pygame.draw.rect(screen, (240, 240, 240), (text_pos[0], text_pos[1] + 55, 50, 10))
					if pygame.mouse.get_pressed() == (1, 0, 0):
						vec = -copy.deepcopy(bodies[i].pos[0:2].astype(int)) + 500
						shiftx = vec[0]
						shifty = vec[1]
						print 'click'

				screen.blit(delete, (text_pos[0], text_pos[1] + 40))
				screen.blit(goto, (text_pos[0] + 1, text_pos[1] + 55))
				
			else:
				try:
					mouse_pos_ = mouse_pos 

					text_pos = copy.deepcopy(bodies[i].pos[0:2]) + shift_vec[0:2] + np.asarray([int(sqrt(bodies[i].mass )) + 6 + 2 *  (i == index) + 5, int(sqrt(bodies[i].mass )) - 28 + 2 *  (i == index)])
					

					
					if (text_pos[0] + 50) >mouse_pos_[0] > text_pos[0] and (text_pos[1] + 50) > mouse_pos_[1] > (text_pos[1] + 40):
						pygame.draw.rect(screen, (240, 240, 240), (text_pos[0], text_pos[1] + 40, 50, 10))
						if pygame.mouse.get_pressed() == (1, 0, 0):
							bodies_to_delete.append(i)

					screen.blit(delete, (text_pos[0], text_pos[1] + 40))

					pos = Font.render(str(np.round(bodies[i].pos, 3)), 1, (255, 255, 255))
					mass = Font.render(str(round(bodies[i].mass, 3)), 1, (255, 255, 255))
					velocity = Font.render(str(np.round(bodies[i].velocity, 3)), 1, (100, 100, 255))

					screen.blit(mass, bodies[i].pos[0:2] + shift_vec[0:2] + np.asarray([int(sqrt(bodies[i].mass )) + 6 + 2 *  (i == index) + 5 ,int(sqrt(bodies[i].mass )) + 2 *  (i == index)]))
				
					screen.blit(velocity, bodies[i].pos[0:2] + shift_vec[0:2] + np.asarray([int(sqrt(bodies[i].mass )) + 6 + 2 *  (i == index) + 5 ,int(sqrt(bodies[i].mass )) - 11 + 2 *  (i == index)]))

					screen.blit(pos, bodies[i].pos[0:2] + shift_vec[0:2] + np.asarray([int(sqrt(bodies[i].mass )) + 6 + 2 *  (i == index) + 5 ,int(sqrt(bodies[i].mass )) - 24 + 2 *  (i == index)]))

					pygame.gfxdraw.aacircle(screen, bodies[i].pos[0:2].astype(int)[0] + shift_vec[0], bodies[i].pos[0:2].astype(int)[1] + shift_vec[1], int(sqrt(bodies[i].mass)) + 6 + 2 * (i == index), (255 *  (i == index), 0, 0))
					pygame.gfxdraw.filled_circle(screen, bodies[i].pos[0:2].astype(int)[0] + shift_vec[0], bodies[i].pos[0:2].astype(int)[1] + shift_vec[1], int(sqrt(bodies[i].mass)) + 6 + 2 *  (i == index), (255 *  (i == index), 0, 0))

					pygame.gfxdraw.aacircle(screen, bodies[i].pos[0:2].astype(int)[0] + shift_vec[0], bodies[i].pos[0:2].astype(int)[1] + shift_vec[1], int(sqrt(bodies[i].mass)) + 5, bodies[i].color)
					pygame.gfxdraw.filled_circle(screen, bodies[i].pos[0:2].astype(int)[0] + shift_vec[0], bodies[i].pos[0:2].astype(int)[1] + shift_vec[1], int(sqrt(bodies[i].mass)) + 5, bodies[i].color)

					factor_down = 1

					pygame.draw.aaline(screen, (255, 100, 100), bodies[i].pos[0:2].astype(int) + shift_vec, bodies[i].pos[0:2].astype(int) + shift_vec + ((bodies[i].force_vector[0:2] * factor_down) * 100).astype(int))
					pygame.draw.aaline(screen, (100, 255, 100), bodies[i].pos[0:2].astype(int) + shift_vec, bodies[i].pos[0:2].astype(int) + shift_vec + ((bodies[i].acceleration_vector[0:2] * factor_down) * 10).astype(int))
					pygame.draw.aaline(screen, (100, 100, 255), bodies[i].pos[0:2].astype(int) + shift_vec, bodies[i].pos[0:2].astype(int) + shift_vec + ((bodies[i].velocity[0:2] * factor_down) * 50).astype(int))
				except OverflowError:
					bodies_to_delete.append(i)
			
		bodies = [i for j, i in enumerate(bodies) if j not in bodies_to_delete]
		for i in bodies_to_add:
			bodies.append(copy.deecopy(bodies_to_add[i]))

		pygame.display.flip()

if __name__ == "__main__":
	main()
