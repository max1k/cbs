#!/usr/bin/env python3

import re
import requests

response=requests.get('http://127.0.0.1:8000/p311/new/')
print(response.text)

m=re.search(r"type='hidden' name='(?P<name>\w+)' value='(?P<value>\w+)'", response.text)
crsf_name = m.group('name')
crsf_value = m.group('value')
m=re.search(r'name="(?P<filename>\w+)" type="file"', response.text)
file_input_name = m.group('filename')
m=re.search('form enctype="multipart/form-data" method="post" action="(?P<name>\w+)"', response.text)

postdata={
	m.group('name') : m.group('value')
}

session = requests.session()
response = s.post()
