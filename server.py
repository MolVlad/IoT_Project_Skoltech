from pynput import mouse, keyboard
from datetime import datetime
import numpy as np
import queue
from threading import Thread
import time
import os
import serial
import socket
import pickle


with open('model.pkl', 'rb') as fid:
	loaded_model = pickle.load(fid)

bufferSize  = 1024 #define buffer size

UDP_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM) #create socket
UDP_socket.bind(("", 50027)) # bind port and ip

while True:
	received_bytes = UDP_socket.recv(bufferSize)
	print(received_bytes)

#predicted_proba = loaded_model.predict_proba([features])[:,1]

#print(array2str(features.round(2)))
#print(predicted_proba)

#	for i, _ in enumerate(features):
#		UDP_socket_imu.sendto(bytes(str(features[i].round(2)), "utf-8"),("13.40.48.121",ports[i]))
#
#	UDP_socket_imu.sendto(bytes(str(predicted_proba.round(2)[0]), "utf-8"),("13.40.48.121",50020))
#	UDP_socket_imu.sendto(bytes(str(int(predicted_proba.round(2)[0] > proba_threshold)), "utf-8"),("13.40.48.121",50021))
#
#	return predicted_proba > proba_threshold
	
