# Importing basic python libraries

import os 
import time
import numpy as np
import math
import threading
import sys
import time
# Importing Myoware libraries 
from queue import Queue
from acquire_data import *
from bio_signal_processing import *
from pyomyo import Myo, emg_mode
from pynq_dpu import DpuOverlay


size = 40
data = get_data()[0:8,1:size+1] 
data =  preprocess(data)
data = np.float32(data) # Convert to float 
data = np.expand_dims(data, axis=2) # Expand dimensions to (channels, samples, 1)


# Importing DPU Overlay blocks and .xmodel
overlay = DpuOverlay("dpu.bit")
overlay.load_model("model.xmodel")


dpu = overlay.runner

inputTensors = dpu.get_input_tensors()
outputTensors = dpu.get_output_tensors()

shapeIn = tuple(inputTensors[0].dims)
shapeOut = tuple(outputTensors[0].dims)
outputSize = int(outputTensors[0].get_data_size() / shapeIn[0])

softmax = np.empty(outputSize)

# Buffer defination to store input and output data. They will be reused during multiple runs.

output_data = [np.empty(shapeOut, dtype=np.float32, order="C")]
input_data = [np.empty(shapeIn, dtype=np.float32, order="C")]
emg = input_data[0]


def calculate_softmax(data):
    
    result = np.exp(data)
    return result

gesture_list = ['Large diamter grasp', 'Meduim diameter grasp',
               'Three finger sphere grasp', 'Prismatic pinch grasp',
               'Power grasp', 'Cut', 'Rest']
while True:
    
    size = 40
    data = get_data()[0:8,1:size+1] 
    data =  preprocess(data)
    data = np.float32(data) # Convert to float 
    data = np.expand_dims(data, axis=2) # Expand dimensions to (channels, samples, 1)
    
    emg[0, ...] = data
    
    job_id = dpu.execute_async(input_data, output_data)
    dpu.wait(job_id)
    temp = [j.reshape(1, outputSize) for j in output_data]
    softmax = calculate_softmax(temp[0][0])
    prediction = softmax.argmax()
    data = 0
    print("Predicted gesture is {}".format(gesture_list[prediction]))
    time.sleep(2)
    
    
del overlay
del dpu