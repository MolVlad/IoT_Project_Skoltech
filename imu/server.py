import socket
import numpy as np
localIP     = "192.168.0.103" #specify your IP
localPort   = 60001 # specify port
bufferSize  = 1024
# Create a datagram socket
UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM)
# Bind to address and ip
UDPServerSocket.bind((localIP, localPort))
LEFT_IMU = '192.168.0.108' #specify adress of the left imu
RIGHT_IMU = '' #specify adress of the right imu
left_imu_acc_x = []
left_imu_acc_y = []
left_imu_acc_z = []
left_imu_gyro_x = []
left_imu_gyro_y = []
left_imu_gyro_z = []
right_imu_acc_x = []
right_imu_acc_y = []
right_imu_acc_z = []
right_imu_gyro_x = []
right_imu_gyro_y = []
right_imu_gyro_z = []

left = [left_imu_acc_x, left_imu_acc_y, left_imu_acc_z, left_imu_gyro_x, left_imu_gyro_y, left_imu_gyro_z]
right = [right_imu_acc_x, right_imu_acc_y, right_imu_acc_z, right_imu_gyro_x, right_imu_gyro_y, right_imu_gyro_z]

left_imu_acc_x_avg = []
left_imu_acc_y_avg = []
left_imu_acc_z_avg = []
left_imu_gyro_x_avg = []
left_imu_gyro_y_avg = []
left_imu_gyro_z_avg = []
right_imu_acc_x_avg = []
right_imu_acc_y_avg = []
right_imu_acc_z_avg = []
right_imu_gyro_x_avg = []
right_imu_gyro_y_avg = []
right_imu_gyro_z_avg = []

left_avg = [left_imu_acc_x_avg, left_imu_acc_y_avg, left_imu_acc_z_avg, left_imu_gyro_x_avg, left_imu_gyro_y_avg, left_imu_gyro_z_avg]
right_avg = [right_imu_acc_x_avg, right_imu_acc_y_avg, right_imu_acc_z_avg, right_imu_gyro_x_avg, right_imu_gyro_y_avg, right_imu_gyro_z_avg]

def write_raw_data_to_queue(rec_data, imu_side):
    if rec_data is None or rec_data == []:
        return
    else:
        if imu_side == LEFT_IMU:
            for index, queue in enumerate(left):
                queue.append(abs(rec_data[index])) # append absolute value
        elif imu_side == RIGHT_IMU:
            for index, queue in enumerate(right):
                queue.append(abs(rec_data[index])) # append absolute value

def preliminary_prepr(imu_side):
    if (left or right) is None or (left or right) == []:
        return
    else:
        if imu_side == LEFT_IMU:
            for index, queue in enumerate(left):
                if len(queue) < 36:
                    break
                else:
                    popped_queue = [queue.pop(0) for i in range(36)] # 36 because of sampling rate (36 Hz)
                    left_avg[index].append(np.mean(popped_queue)) # calculate avg value in 1 sec 
        elif imu_side == RIGHT_IMU:
            for index, queue in enumerate(right):
                if len(queue) < 36:
                    break
                else:
                    popped_queue = [queue.pop(0) for i in range(36)] # 36 because of sampling rate (36 Hz)
                    right_avg[index].append(np.mean(popped_queue)) # calculate avg value in 1 sec 
          
while True:
    bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
    message = bytesAddressPair[0].decode('utf-8').replace('\n', '').split(',')
    received_data = list(np.array(message, dtype = float))
    address = bytesAddressPair[1]
    write_raw_data_to_queue(received_data, address[0])
    preliminary_prepr(address[0])
    if left_imu_acc_x_avg != []: # just for debug
        print(left_imu_acc_x_avg[-1])
