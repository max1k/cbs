#!/usr/bin/env python3

import re
import requests
from glob import glob
from os.path import join, split
def send_file(url, file_name, path):
	response=requests.get(url)
	#print(response.text)

	m = re.search(r'enctype="multipart/form-data" method="post" action="(?P<action>[\w\/]+)"', response.text)
	form_action=m.group('action')

	m = re.search(r"type='hidden' name='(?P<name>\w+)' value='(?P<value>\w+)'", response.text)
	csrf_name = m.group('name')
	cssrf_value = m.group('value')

	m = re.search(r'name="(?P<filename>\w+)" type="file"', response.text)
	file_input_name = m.group('filename')
	postdata={
		csrf_name : cssrf_value
		}
	
	full_name=join(path, file_name)
	files={
		file_input_name: (file_name, open(full_name,'rb').read())
		}

	session = requests.session()
	response = session.post(url, data=postdata, files=files)
	return response

path='/home/max1k/Документы/311P/OUT/'
mask='S*.xml'
url='http://127.0.0.1:8000/p311/new/'

for filename in glob('{0}{1}'.format(path, mask)):
	r = send_file(url, split(filename)[1], path)
	print(filename)

path='/home/max1k/Документы/311P/OUT/'
mask='S*.XML'

for filename in glob('{0}{1}'.format(path, mask)):
	r = send_file(url, split(filename)[1], path)
	print(filename)

path='/home/max1k/Документы/311P/IN/'
mask='S*.XML'

for filename in glob('{0}{1}'.format(path, mask)):
	r = send_file(url, split(filename)[1], path)
	print(filename)

path='/home/max1k/Документы/311P/IN/'
mask='UV*.xml'

for filename in glob('{0}{1}'.format(path, mask)):
	r = send_file(url, split(filename)[1], path)
	print(filename)