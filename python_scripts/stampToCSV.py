from datetime import datetime
from sys import argv

with open(argv[1]) as f:
	data = f.read().split('\n')

with open('/export/a04/wpovell/quora_times.csv', 'w') as f:
	for n in data:
		if not n or not n.isdigit():
			continue
		dt = datetime.fromtimestamp(int(n))
		s = dt.strftime("%Y,%m,%d\n")
		f.write(s)
