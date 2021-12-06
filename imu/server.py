import socket
import numpy as np

localIP     = '192.168.0.103' #specify your server IP
localPort   = 60001 # specify port
bufferSize  = 1024 #define buffer size

LEFT_IMU = '192.168.0.108' #specify adress of the left imu
RIGHT_IMU = '192.168.0.110' #specify adress of the right imu

left = []
right = []

left_avg = []
right_avg = []
# data for calibration
data_for_calibration = []
med_acc_x, med_acc_y, med_acc_z, med_gyro_x, med_gyro_y, med_gyro_z = 0
ql_acc_x, qr_acc_x, ql_acc_y, qr_acc_y, ql_acc_z, qr_acc_z = 0
ql_gyro_x, qr_gyro_x, ql_gyro_y, qr_gyro_y, ql_gyro_z, qr_gyro_z = 0

normalized_medians = [0, 0, 0, 0, 0, 0] # need to divide each value by N - number of samples ((x1-c + x2-c +...+ xn-c)/n = np.mean(x) - c/n)
# для клиппинга берем что то типо min(max(число, квантиль))
def write_raw_data_to_queue(rec_data, imu_side):
    if rec_data is None or rec_data == []:
        return
    else:
        if imu_side == LEFT_IMU:
            left.append(np.abs(rec_data)) # append absolute value
        elif imu_side == RIGHT_IMU:
            right.append(np.abs(rec_data)) # append absolute value

def calibration(sampling_rate, time_duration):
    if len(data_for_calibration) < sampling_rate * time_duration:
        return
    else:
        pass
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
             print(right_avg.pop(0))


if __name__ == "__main__":
    run_server()
# [0 0.36 0.4 0.533 0.567 1]
# [-60 -60 0 0 -60 -60]