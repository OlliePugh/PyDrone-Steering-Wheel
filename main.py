import pygame
import sys
from threading import Thread
import time
from pyardrone import ARDrone
import cv2

simulate = False
drone_speed_reducer = 0.3
flying = False

def takeoff(_drone):
	global flying
	print("TAKING OFF")
	_drone.takeoff()
	flying = True

def land(_drone):
	global flying
	print("LANDING")
	_drone.land()
	flying = False

class Wheel():
	def __init__(self, joystick):
		self.joystick = joystick
		self.joystick.init()
		self.thread = Thread(target=self.thread_routine, daemon=True) # Create a thread to manage the inputs
		self.thread.start()  # start the thread

	def update_inputs(self):
		pygame.event.pump()
		self.angle = self.joystick.get_axis(0)
		self.accelerator = (self.joystick.get_axis(2)-1)*-(1/2)
		self.brake = (self.joystick.get_axis(3)-1)*-(1/2)
		self.up_paddle = self.joystick.get_button(4)
		self.down_paddle = self.joystick.get_button(5)
		self.take_off_button = self.joystick.get_button(3)
		self.land_button = self.joystick.get_button(0)

	def thread_routine(self):
		while True:
			self.update_inputs()

def main():
	global stop_threads
	pygame.display.init()
	pygame.joystick.init()

	joysticks = [pygame.joystick.Joystick(x) for x in range(pygame.joystick.get_count())]  # get a list of all joystick

	wheel = None

	if len(joysticks) == 1:
		wheel = Wheel(joysticks[0])
	else:
		for i in range(len(joysticks)):
			print((i+1), "=", joysticks[i].get_name())

	while wheel is None:  # while the wheel has not been set
		try:
			wheel = WHeel(joysticks[int(input("Which controller is the wheel?"))-1])
		except:
			print("Invalid Input")
			pass

	drone = ARDrone()
	#drone.navdata_read.wait()  # wait until nav data is ready
	drone.video_ready.wait()

	try:
		while True:
			if not simulate:
				cv2.imshow("im", drone.frame)
				if cv2.waitKey(10) == ord(' '):
					break
			if not flying and wheel.take_off_button == 1:  # takeoff
				takeoff(drone)
			elif flying:
				if wheel.land_button == 1:
					land(drone)
				if not simulate:
					drone.move(forward=wheel.accelerator*drone_speed_reducer, backward=wheel.brake*drone_speed_reducer, cw=wheel.angle*drone_speed_reducer,
					up=wheel.up_paddle*drone_speed_reducer, down=wheel.down_paddle*drone_speed_reducer)
				print("forward=%.2f backward=%.2f cw=%.2f up=%.2f down=%.2f" % (
				wheel.accelerator*drone_speed_reducer, wheel.brake*drone_speed_reducer, wheel.angle*drone_speed_reducer,
				wheel.up_paddle*drone_speed_reducer, wheel.down_paddle*drone_speed_reducer))
	except KeyboardInterrupt:
		quit()
	finally:
		land(drone)


if __name__ == "__main__":
	main()
