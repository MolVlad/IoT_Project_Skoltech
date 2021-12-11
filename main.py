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
import socket

ports = [50003,50018,50004,50002,50005,50006,50007,50011,50012,50013,50008,50009,50010,50014,50015,50016]

hrm_device = "/dev/ttyUSB0"

try:
	hrm_serial = serial.Serial(hrm_device, baudrate=115200, timeout=0.01)
	print("HRM is successfully connected")
except:
	print("HRM is not connected")
	os.system("ls /dev/ | grep USB")
	exit()

sampling_rate = 36
calibration_duration = 1
proba_threshold = 0.5

localIP     = '' #specify your server IP
localPort_imu   = 60001 # specify port
localPort_data   = 60002 # specify port
bufferSize  = 1024 #define buffer size

queue_mouse = queue.Queue(maxsize=10000)
queue_move = queue.Queue(maxsize=10000)
queue_keyboard = queue.Queue(maxsize=10000)
queue_pc_data = queue.Queue(maxsize=10000)
queue_hrm = queue.Queue(maxsize=10000)
queue_imu = queue.Queue(maxsize=10000)

UDP_socket_imu = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM) #create socket
UDP_socket_imu.bind((localIP, localPort_imu)) # bind port and ip
UDP_socket_imu.settimeout(0.01)

UDP_socket_data = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM) #create socket
UDP_socket_data.bind((localIP, localPort_data)) # bind port and ip
UDP_socket_data.settimeout(0.01)

def inference(queue_pc_data, queue_hrm, queue_imu):
	queue_pc_data.queue.clear()
	queue_hrm.queue.clear()
	queue_imu.queue.clear()

	while True:
		start = time.time()

		item = queue_pc_data.get()
		clicks, presses, movements = np.array(item.split(","), dtype=float)
		#print(time.time() - start)

		hrm_rate = float(queue_hrm.get())
		#print(time.time() - start)

		item = queue_imu.get()
		imu_left_linaccel_x, imu_left_linaccel_y, imu_left_linaccel_z, \
			imu_left_gyro_x, imu_left_gyro_y, imu_left_gyro_z, \
			imu_right_linaccel_x, imu_right_linaccel_y, imu_right_linaccel_z, \
			imu_right_gyro_x, imu_right_gyro_y, imu_right_gyro_z = np.array(item.split(","), dtype=float)
		#print(time.time() - start)

		features = np.array([clicks, movements, presses, hrm_rate,
			imu_left_linaccel_x, imu_left_linaccel_y, imu_left_linaccel_z,
			imu_left_gyro_x, imu_left_gyro_y, imu_left_gyro_z,
			imu_right_linaccel_x, imu_right_linaccel_y, imu_right_linaccel_z,
			imu_right_gyro_x, imu_right_gyro_y, imu_right_gyro_z])

		#print(queue_pc_data.qsize(), queue_hrm.qsize(), queue_imu.qsize())

		print(array2str(features))
		UDP_socket_data.sendto(bytes(array2str(features), "utf-8"),("13.40.48.121",50027))

def hrm_reader(queue_hrm):
	local_timestamp = global_timestamp

	hrm_rate = 70
	received_data = True
	while True:
		try:
			received = int(hrm_serial.readline()[:2])
			if received > 60:
				hrm_rate = received
				received_data = True
		except:
			pass

		if time.time() > local_timestamp:
			local_timestamp += 1.

			queue_hrm.put(str(hrm_rate))
			if not received_data:
				print("HRM is not connected")
			received_data = False

def enough_data(data_for_calibration, amount):
    return len(data_for_calibration['l']) > amount and \
        len(data_for_calibration['r']) > amount

def calibrate(data_for_calibration):
	if len(data_for_calibration['l']):
		median_left = np.median(data_for_calibration['l'][-sampling_rate*calibration_duration:], axis=0)
	else:
		median_left = np.array([0.,0.,0.,0.,0.,0.])
	if len(data_for_calibration['r']):
		median_right = np.median(data_for_calibration['r'][-sampling_rate*calibration_duration:], axis=0)
	else:
		median_right = np.array([0.,0.,0.,0.,0.,0.])
    
	calibration = {'l': {'median':median_left}, 'r': {'median':median_right}}
	return calibration

def preprocess_imu(data_for_inference, calibration):
	if len(data_for_inference['l']):
		left = abs(np.mean(data_for_inference['l'] - calibration['l']['median'], axis=0))
	else:
		left = np.array([0.,0.,0.,0.,0.,0.])
	if len(data_for_inference['r']):
		right = abs(np.mean(data_for_inference['r'] - calibration['r']['median'], axis=0))
	else:
		right = np.array([0.,0.,0.,0.,0.,0.])

	return np.concatenate([left, right])

def array2str(array):
    string = ""
    for element in array:
        string += str(element) + ","
    return string[:-1]

def imu_server(queue_imu):
	local_timestamp = global_timestamp

	data_for_calibration = {'l': [], 'r': []}
	data_for_inference = {'l': [], 'r': []}
	calibration_needed = True
	calibration = {'l': {'median':np.array([0,0,0,0,0,0])}, 'r': {'median':np.array([0,0,0,0,0,0])}}

	start = time.time()
	while True:
		try:
			received_bytes = UDP_socket_imu.recv(bufferSize)
			message = received_bytes.decode('utf-8').replace('\n', '').split(',')
			name = message.pop(0)
			data = np.array(message, dtype = float)

			if calibration_needed:
				data_for_calibration[name].append(data)
				end = time.time()
				if end - start > calibration_duration:
					calibration_needed = False
					calibration = calibrate(data_for_calibration)
			else:
				data_for_inference[name].append(data)

				if time.time() > local_timestamp:
					local_timestamp += 1.

					queue_imu.put(array2str(preprocess_imu(data_for_inference, calibration)))
					data_for_inference = {'l': [], 'r': []}
		except:
			pass

def mouse_on_move(x, y):
	queue_move.put(str(x)+","+str(y))

def mouse_on_click(x, y, button, pressed):
	if pressed:
		queue_mouse.put("mouse click")

def keyboard_on_press(key):
	queue_keyboard.put("keyboard press")

def pc_data_reader(queue_mouse, queue_keyboard, queue_move, queue_pc_data):
	local_timestamp = global_timestamp

	clicks_statistics = [0, 0, 0, 0]
	presses_statistics = [0, 0, 0, 0]
	movements_statistics = [0, 0, 0, 0]

	clicks = 0
	presses = 0

	item = queue_move.get()
	last_x, last_y = np.array(item.split(","), dtype=float)
	movements = 0

	print("Detecting...")
	
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
		
		if time.time() > local_timestamp:
			local_timestamp += 1.

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

pc_data_thread = Thread(target=pc_data_reader, args=(queue_mouse, queue_keyboard, queue_move, queue_pc_data))
mouse_listener = mouse.Listener(on_move=mouse_on_move, on_click=mouse_on_click)
keyboard_listener = keyboard.Listener(on_press=keyboard_on_press)
hrm_thread = Thread(target=hrm_reader, args=(queue_hrm,))
imu_server_thread = Thread(target=imu_server, args=(queue_imu,))
inference_thread = Thread(target=inference, args=(queue_pc_data, queue_hrm, queue_imu))

global_timestamp = time.time()

pc_data_thread.start()
mouse_listener.start()
keyboard_listener.start()
hrm_thread.start()

queue_pc_data.get()

imu_server_thread.start()
print("Waiting for calibration...")
queue_imu.get()
print("Done")

time.sleep(1)

inference_thread.start()



