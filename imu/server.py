import socket
import numpy as np

localIP     = '192.168.133.121' #specify your server IP
localPort   = 60001 # specify port
bufferSize  = 1024 #define buffer size

LEFT_IMU = '192.168.133.244' #specify adress of the left imu
RIGHT_IMU = '192.168.133.181' #specify adress of the right imu

left = []
right = []

data_for_calibration_left = []
data_for_calibration_right = []

left_avg = []
right_avg = []

median_left = []
median_right = []
quantiles_right = []
quantiles_left = []

sampling_rate = 36
time_duration = 10

# TODO smothing
def exp_smoothing():
    pass

def write_raw_data_to_queue(rec_data, imu_side, calibration_flag = False):
    global left
    global right
    global data_for_calibration_left
    global data_for_calibration_right
    if rec_data is None or rec_data == []:
        return
    else:
        if imu_side == LEFT_IMU and calibration_flag:
            data_for_calibration_left.append(rec_data)
        elif imu_side == LEFT_IMU:
            for index, element in enumerate(rec_data): # clipping
                element = max(quantiles_left[0][index], element)
                element = min(quantiles_left[1][index], element)
                rec_data[index] = element
            data = rec_data - median_left # sub median
            left.append(np.abs(data)) # add abs values
        if imu_side == RIGHT_IMU and calibration_flag:
            data_for_calibration_right.append(rec_data)
        elif imu_side == RIGHT_IMU:
            for index, element in enumerate(rec_data): # clipping
                element = max(quantiles_right[0][index], element)
                element = min(quantiles_right[1][index], element)
                rec_data[index] = element
            data = rec_data - median_right # sub median
            left.append(np.abs(data)) # add abs values 

def calibration(sampling_rate, time_duration):
    global data_for_calibration_left
    global data_for_calibration_right
    global median_left
    global median_right
    global quantiles_left
    global quantiles_right
    data_for_calibration_left = data_for_calibration_left[: sampling_rate * time_duration]
    #data_for_calibration_right = data_for_calibration_right[: sampling_rate * time_duration] # add if right imu is working
    median_left = np.median(data_for_calibration_left, axis = 0)
    #median_right = np.median(data_for_calibration_right, axis = 0)
    quantiles_left = np.quantile(data_for_calibration_left, [0.005, 0.995], axis = 0)
    #quantiles_right = np.quantile(data_for_calibration_right, [0.005, 0.995], axis = 0)   # add if right imu is working

def resampling(imu_side):
    global left_avg
    global right_avg
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
        
def run_server(sampling_rate, time_duration):
    UDPServerSocket = socket.socket(family=socket.AF_INET, type=socket.SOCK_DGRAM) #create socket
    UDPServerSocket.bind((localIP, localPort)) # bind port and ip
    while True:
        bytesAddressPair = UDPServerSocket.recvfrom(bufferSize)
        message = bytesAddressPair[0].decode('utf-8').replace('\n', '').split(',')
        received_data = list(np.array(message, dtype = float))
        address = bytesAddressPair[1]
        if len(data_for_calibration_left) < sampling_rate * time_duration: # put condition for right buff
            write_raw_data_to_queue(received_data, address[0], calibration_flag = True)
        else:
            if quantiles_left == [] and quantiles_right == []: # put condition for right buff
                calibration(sampling_rate, time_duration)
            write_raw_data_to_queue(received_data, address[0])
            resampling(address[0])
            # debug stuff
            if left_avg != []:
                print(left_avg.pop(0))
            if right_avg != []:
                print(right_avg.pop(0))


if __name__ == "__main__":
    run_server(sampling_rate, time_duration)

#code from anton
"""
def time_ewa(series, halflife, mode):
    time_diffs = series.index / pd.Timedelta(seconds=1)
    time_diffs = time_diffs.values
    time_diffs = time_diffs.max() - time_diffs
    # Folmula from https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.ewm.html
    alpha = 1 - np.exp(np.log(0.5) / halflife)
    weights = (1 - alpha) ** time_diffs
    if mode == 'mean':  # Normalizing all weights to zero
        weights = weights / weights.sum()
    elif mode == 'sum':
        # Keeping weights as is
        pass
    else:
        raise ValueError(f'Don\'t know mode {mode}')

    result = (series * weights).sum()

    return result

def smooth_df(df, halflife, mode='mean'):
    window_size = pd.Timedelta(seconds=halflife * args.halflifes_in_window)
    df_smoothed = df.rolling(window=window_size).apply(lambda x: time_ewa(x, halflife, mode))

    return df_smoothed
"""