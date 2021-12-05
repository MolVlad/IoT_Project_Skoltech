import socket
import numpy as np

localIP     = "192.168.0.103" #specify your IP
localPort   = 60001 # specify port
bufferSize  = 1024 #define buffer size

LEFT_IMU = '192.168.0.108' #specify adress of the left imu
RIGHT_IMU = '' #specify adress of the right imu

left = []
right = []

left_avg = []
right_avg = []


def write_raw_data_to_queue(rec_data, imu_side):
    if rec_data is None or rec_data == []:
        return
    else:
        if imu_side == LEFT_IMU:
            left.append(np.abs(rec_data)) # append absolute value
        elif imu_side == RIGHT_IMU:
            right.append(np.abs(rec_data)) # append absolute value

def preliminary_prepr(imu_side):
    if (left or right) is None or (left or right) == []:
        return
    else:
        if imu_side == LEFT_IMU:
            if len(left) < 36:
                return
            else:
                popped_queue = [left.pop(0) for i in range(36)] # 36 because of sampling rate (36 Hz)
                left_avg.append(np.mean(np.reshape(popped_queue, (36,6)), axis = 0)) # calculate avg value in 1 sec      
        elif imu_side == RIGHT_IMU:
            if len(right) < 36:
                return
            else:
                popped_queue = [right.pop(0) for i in range(36)] # 36 because of sampling rate (36 Hz)
                right_avg.append(np.mean(np.reshape(popped_queue, (36,6)), axis = 0)) # calculate avg value in 1 sec 
        
def run_server():
    UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM) #create socket
    UDPServerSocket.bind((localIP, localPort)) # bind port and ip
    while True:
        bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
        message = bytesAddressPair[0].decode('utf-8').replace('\n', '').split(',')
        received_data = list(np.array(message, dtype = float))
        address = bytesAddressPair[1]
        write_raw_data_to_queue(received_data, address[0])
        preliminary_prepr(address[0])
        if left_avg != []: 
            print(left_avg.pop(0)) # just for debug


if __name__ == "__main__":
    run_server()