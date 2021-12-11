import numpy as np
import socket
import pickle


with open('model.pkl', 'rb') as fid:
	loaded_model = pickle.load(fid)

bufferSize  = 1024 #define buffer size

target_ip = "192.168.1.5"
target_port = 60002
local_port = 60003

proba_threshold = 0.5

ports = [50003,50018,50004,50002,50005,50006,50007,50011,50012,50013,50008,50009,50010,50014,50015,50016]

UDP_socket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM) #create socket
UDP_socket.bind(("", local_port)) # bind port and ip

def array2str(array):
    string = ""
    for element in array:
        string += str(element) + ","
    return string[:-1]

while True:
	received_bytes = UDP_socket.recv(bufferSize)
	features = np.array(received_bytes.decode('utf-8').replace('\n', '').split(','), dtype=float)
	predicted_proba = loaded_model.predict_proba([features])[:,1]

	print("Received data:", array2str(features.round(2)))
	print("Burnout probability:", round(predicted_proba[0],2))
	print()

	for i, _ in enumerate(features):
		UDP_socket.sendto(bytes(str(features[i].round(2)), "utf-8"),("13.40.48.121",ports[i]))

	UDP_socket.sendto(bytes(str(predicted_proba.round(2)[0]), "utf-8"),("13.40.48.121",50020))
	UDP_socket.sendto(bytes(str(int(predicted_proba.round(2)[0] > proba_threshold)), "utf-8"),("13.40.48.121",50021))

	UDP_socket.sendto(bytes(str(int(predicted_proba.round(2)[0] > proba_threshold)), "utf-8"),(target_ip, target_port))
	
