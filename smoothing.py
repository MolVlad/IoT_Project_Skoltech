import numpy as np

smoothed_data = [] # storage for smoothed data

def exponential_smoothing(data, halflife, window_size):
    """according to formula from here 
    https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.ewm.html
    weighted func"""
    alpha = 1 - np.exp(np.log(0.5) / halflife)
    weights = (1 - alpha) ** [i for i in range(0, window_size)]
    result = []
    for column in range(data.shape[1]):
        #firstly slice data by column then reverse column according to the formula from doc
        result.append((data[:, column][::-1] * weights).sum() / weights.sum()) # just explicit representation of formula
    return result

def apply_smoothing(data, halflife, halflife_in_window):
    global smoothed_data
    smoothed_data.append(exponential_smoothing(data, 
                                               halflife, 
                                               min(len(data), halflife * halflife_in_window)))
while len(data) > 0:
    apply_smoothing(5, 5)
    data = np.delete(data, (0), axis = 0) # moving window (pop the first row on each cycle)

"""
PSEUDO CODE HERE
while True: # main loop
    # window size in the paper is 25 (halflife * halflife_in_window = 5 * 5 = 25)
    # but when the sufficient amoun of data is not collected I suppose to reduce the window size
    # to the length of the collected data on current step
    # also it makes sense when we reach the end of the data
    data_to_smooth = data[: min(len(data), halflife * halflife_in_window)]
    data_to_smooth = np.reshape(data_to_smooth, (-1, 6))
    apply_smoothing(data_to_smooth, 5, 5)
    data.pop(0)
"""
"""
Крч идея такая:
размер окна в статье 25, но я предлагаю пока необходимых измерений не набралось рамер окна брать равным длине массива с измерениями
когда будет >=25 показаний, считаем окном в 25 элементов
мои функции принимают на вход матрицу N = min(len(data), 25) см. коммент выше и М = числу измеряемых показателей
я не помню в каком виде хранятся измеренные данные, поэтому пишу, что мне нужно их зарешейпить в таком формате
далее я применяю смузинг - он мапит эту таблицу в вектор рамзера числа показателей - так делаем на каждом кругу цикла
потом попаем первый элемент из исходного массива (data) - в котором хранились не сглаженные показатели
послеший шаг тип скользящее окно - мы всегда применяем окно к первым 25 элтам (ну или меньшим, смотри самое начало кома), если мы попаем нулевой элемент
на каждом кругу цикла, то как раз получаем бегущее окно
P.S. как вариант можно не смузить пока нет 25 элементов и только потом уже писать в финальный массив с данными
P.P.S. у них в статье такая же формула, но окно они используют встроенное
P.P.P.S. В ноутбуке смуз тест есть графики, в принципе нормально получается
"""