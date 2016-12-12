#coding=utf-8
import httplib
import time
import sys
import os
from keras.models import Sequential, load_model
from keras.layers.core import Dense, Dropout, Activation, Flatten
from keras.layers.advanced_activations import PReLU
from keras.layers.convolutional import Convolution2D, MaxPooling2D
from keras.optimizers import SGD, Adadelta, Adagrad
from keras.utils import np_utils, generic_utils
from six.moves import range
import numpy as np
from keras import backend as K
import time
# K.set_image_dim_ordering('th')

ip = '183.172.138.76'
ensure_delta = 500
finger_data_dim = 63
num_classes = 6

httpClient = None
model = load_model("model.h5")
sign = ["飞机","电话","你","坏","拳","七"]
last_pre_sign = ""
null_data_notify = "没有手势数据"
last_sign_produce_time = time.time()

try:
	while True:  
		httpClient = httplib.HTTPConnection(ip, 8000, timeout = 30)
		httpClient.request('GET', '/')
		response = httpClient.getresponse()
		response_arr = response.read().replace('\r\n', '').split(' ')
		if(len(response_arr) == 1):
			if(last_pre_sign != null_data_notify):
				last_pre_sign = null_data_notify
				last_sign_produce_time = last_sign_produce_time - ensure_delta
				print last_pre_sign
			continue
		inp = map(float, response_arr)
		inp = np.array(inp).reshape(-1,finger_data_dim)
		x_abs_max = max(inp.max(), -inp.min()) + 1 #TODO
		test_x = inp / 247.9712

		proba = model.predict(test_x, batch_size=1, verbose=0)
		if proba.shape[-1] > 1:
			pre_label = proba.argmax(axis=-1)
		else:
			pre_label = (proba > 0.5).astype('int32')
		pre_type = int(pre_label[0])
		# print pre_type
		pre_sign = sign[pre_type]
		if(pre_sign != last_pre_sign):
			passed_time = (time.time() - last_sign_produce_time) * 1000.0
			# print "passed_time: " + str(passed_time) + "ms"
			if(passed_time > ensure_delta):
				last_sign_produce_time = time.time()
				last_pre_sign = pre_sign
				print pre_sign
		else:
			continue

		oup = str(pre_type);

		httpClient = httplib.HTTPConnection(ip, 8000, timeout = 30)
		httpClient.request('GET', '/' + oup);
		response = httpClient.getresponse().read().replace('\r\n', '')

		# print response
except Exception, e:
	print e
finally:
	if httpClient:
		httpClient.close()
