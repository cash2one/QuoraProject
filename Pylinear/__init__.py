import os

BASE_PATH = '/export/a04/wpovell'
if 'QUORA_BASE_PATH' in os.environ:
	BASE_PATH = os.environ['QUORA_BASE_PATH']
