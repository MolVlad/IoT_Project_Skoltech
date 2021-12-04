#!/usr/bin/env python
# coding: utf-8

from pynput import mouse, keyboard
from datetime import datetime
import numpy as np
import queue
from threading import Thread
import time
import os
import serial

hrm_device = "/dev/ttyUSB1"
imu_left_device = "/dev/ttyUSB1"
imu_right_device = "/dev/ttyUSB1"

try:
	hrm_serial = serial.Serial(hrm_device, baudrate=115200, timeout=0.5)
	#imu_left_serial = serial.Serial(imu_left_device, baudrate=115200)
	#imu_right_serial = serial.Serial(imu_right_device, baudrate=115200)
except:
	os.system("ls /dev/ | grep USB")

clicks_max = 3
clicks_min = 0
presses_max = 3
presses_min = 0
movements_max = 500000
movements_min = 0
hrm_rate_max = 150
hrm_rate_min = 0
imu_left_x_min = 0
imu_left_x_max = 1000
imu_left_y_min = 0
imu_left_y_max = 1000
imu_left_z_min = 0
imu_left_z_max = 1000
imu_right_x_min = 0
imu_right_x_max = 1000
imu_right_y_min = 0
imu_right_y_max = 1000
imu_right_z_min = 0
imu_right_z_max = 1000

queue_mouse = queue.Queue(maxsize=10000)
queue_move = queue.Queue(maxsize=10000)
queue_keyboard = queue.Queue(maxsize=10000)
queue_pc_data = queue.Queue(maxsize=10000)
queue_hrm = queue.Queue(maxsize=10000)
queue_imu_left = queue.Queue(maxsize=10000)
queue_imu_right = queue.Queue(maxsize=10000)

def mouse_on_move(x, y):
	queue_move.put(str(x)+","+str(y))

def mouse_on_click(x, y, button, pressed):
	if pressed:
		queue_mouse.put("mouse click")

def keyboard_on_press(key):
	queue_keyboard.put("keyboard press")

def predict(features):
	return features[0] > 2
	
def inference(queue_pc_data, queue_hrm, queue_imu_left, queue_imu_right):
	while True:
		#start = time.time()

		item = queue_pc_data.get()
		#print(time.time() - start)
		clicks, presses, movements = np.array(item.split(","), dtype=float)
		clicks = np.clip(clicks, clicks_min, clicks_max)
		presses = np.clip(presses, presses_min, presses_max)
		movements = np.clip(movements, movements_min, movements_max)

		hrm_rate = float(queue_hrm.get())
		#print(time.time() - start)
		hrm_rate = np.clip(hrm_rate, hrm_rate_min, hrm_rate_max)

		item = queue_imu_left.get()
		#print(time.time() - start)
		imu_left_x, imu_left_y, imu_left_z = np.array(item.split(","), dtype=float)
		imu_left_x = np.clip(imu_left_x, imu_left_x_min, imu_left_x_max)
		imu_left_y = np.clip(imu_left_y, imu_left_y_min, imu_left_y_max)
		imu_left_z = np.clip(imu_left_z, imu_left_z_min, imu_left_z_max)

		item = queue_imu_right.get()
		#print(time.time() - start)
		imu_right_x, imu_right_y, imu_right_z = np.array(item.split(","), dtype=float)
		imu_right_x = np.clip(imu_right_x, imu_right_x_min, imu_right_x_max)
		imu_right_y = np.clip(imu_right_y, imu_right_y_min, imu_right_y_max)
		imu_right_z = np.clip(imu_right_z, imu_right_z_min, imu_right_z_max)

		print("clicks:", clicks, "presses", presses, "movements", movements, "hrm", hrm_rate,
			"imu_left_x", imu_left_x, "imu_left_y", imu_left_y, "imu_left_z", imu_left_z,
			"imu_right_x", imu_right_x, "imu_right_y", imu_right_y, "imu_right_z", imu_right_z)

		features = [clicks, presses, movements, hrm_rate,
			imu_left_x, imu_left_y, imu_left_z,
			imu_right_x, imu_right_y, imu_right_z]

		is_burnout = predict(features)
	
		if is_burnout:
			print("BURNOUT!")

def hrm_reader(queue_hrm):
	hrm_rate = 90
	start = time.time()
	while True:
		try:
			hrm_rate = int(hrm_serial.readline()[:2])
		except:
			print("HRM is not connected")

		end = time.time()
		if end - start > 1.0:
			queue_hrm.put(str(hrm_rate))


def imu_reader(queue_imu, device_imu, test):
	imu_x = test[0]
	imu_y = test[1]
	imu_z = test[2]

	start = time.time()
	while True:
		end = time.time()
		if end - start > 1.0:
			queue_imu.put(str(imu_x)+","+str(imu_y)+","+str(imu_z))

def pc_data_reader(queue_mouse, queue_keyboard, queue_move, queue_pc_data):
	clicks_statistics = [0, 0, 0, 0]
	presses_statistics = [0, 0, 0, 0]
	movements_statistics = [0, 0, 0, 0]

	clicks = 0
	presses = 0

	item = queue_move.get()
	last_x, last_y = np.array(item.split(","), dtype=float)
	movements = 0

	print("Detecting...")
	start = time.time()
	
	while True:
		try:
			item = queue_move.get_nowait()
			x,y = np.array(item.split(","), dtype=float)
			movements += np.sqrt((last_x - x) ** 2 + (last_y - y) ** 2)
		except:
			pass
		
		try:
			item = queue_keyboard.get_nowait()
			presses += 1
		except:
			pass	
		
		try:
			item = queue_mouse.get_nowait()
			clicks += 1
		except:
			pass	
		
		end = time.time()
		if end - start > 1.:
			clicks_statistics.append(clicks)
			presses_statistics.append(presses)
			movements_statistics.append(movements)

			clicks = 0
			presses = 0
			movements = 0

			clicks_avg = np.mean(clicks_statistics)
			presses_avg = np.mean(presses_statistics)
			movements_avg = np.mean(movements_statistics)

			clicks_statistics.pop(0)
			presses_statistics.pop(0)
			movements_statistics.pop(0)

			queue_pc_data.put(str(clicks_avg)+","+str(presses_avg)+","+str(movements_avg))

			start = time.time()

mouse_listener = mouse.Listener(
		on_move=mouse_on_move,
		on_click=mouse_on_click
)


keyboard_listener = keyboard.Listener(on_press=keyboard_on_press)

pc_data_thread = Thread(target=pc_data_reader, args=(queue_mouse, queue_keyboard, queue_move, queue_pc_data))
hrm_thread = Thread(target=hrm_reader, args=(queue_hrm,))
inference_thread = Thread(target=inference, args=(queue_pc_data, queue_hrm, queue_imu_left, queue_imu_right))
imu_left_thread = Thread(target=imu_reader, args=(queue_imu_left, imu_left_device, (228, 404, 999)))
imu_right_thread = Thread(target=imu_reader, args=(queue_imu_right, imu_right_device, (1, 2, 3)))

pc_data_thread.start()
mouse_listener.start()
keyboard_listener.start()
hrm_thread.start()
imu_left_thread.start()
imu_right_thread.start()
inference_thread.start()

