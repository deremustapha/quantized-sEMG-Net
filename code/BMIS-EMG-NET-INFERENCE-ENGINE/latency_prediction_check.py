# Importing basic python libraries

import os 
import time
import numpy as np
import math
import threading
import sys
import time
from pynq_dpu import DpuOverlay
from scipy.io import loadmat
from queue import Queue

# Importing DPU Overlay blocks and .xmodel
overlay = DpuOverlay("dpu.bit")
overlay.load_model("model.xmodel")

dataset = loadmat('test_data')
data = dataset['data']
label = dataset['label']

data = np.expand_dims(data, axis=3)

dpu = overlay.runner

inputTensors = dpu.get_input_tensors()
outputTensors = dpu.get_output_tensors()

shapeIn = tuple(inputTensors[0].dims)
shapeOut = tuple(outputTensors[0].dims)
outputSize = int(outputTensors[0].get_data_size() / shapeIn[0])

softmax = np.empty(outputSize)


output_data = [np.empty(shapeOut, dtype=np.float32, order="C")]
input_data = [np.empty(shapeIn, dtype=np.float32, order="C")]
image = input_data[0]

def calculate_softmax(data):
    result = np.exp(data)
    return result

num_samples  = 50
for i in range(num_samples):
    image[0,...] = data[i]
    job_id = dpu.execute_async(input_data, output_data)
    dpu.wait(job_id)
    temp = [j.reshape(1, outputSize) for j in output_data]
    softmax = calculate_softmax(temp[0][0])
    prediction = softmax.argmax()

    print('Prediction: {}'.format(prediction))
    gnd_truth = label[i]
    print('True Label {}'.format(gnd_truth))

total = data.shape[0]
predictions = np.empty_like(label)
print("Gesture Recognition to Estimate Latency")

start = time.time()
for i in range(total):
    image[0,...] = data[i]
    job_id = dpu.execute_async(input_data, output_data)
    dpu.wait(job_id)
    temp = [j.reshape(1, outputSize) for j in output_data]
    softmax = calculate_softmax(temp[0][0])
    predictions[i] = softmax.argmax()

stop = time.time()
correct = np.sum(predictions==label)
execution_time = stop-start
#print("Overall accuracy: {}".format(correct/total))
print("Latency per window: {:.4f}s".format(execution_time / total))

del overlay
del dpu