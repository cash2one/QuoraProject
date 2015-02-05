from datetime import datetime

with open('/export/a04/wpovell/logs/CreateQuoraComms.o1319643') as f:
	data = f.read().split('\n')

with open('/export/a04/wpovell/quora_times.csv') as f:
	for n in data:
		dt = datetime.fromtimestamp(int(n))
		s = dt.strftime("%Y,%m,%d\n")
		f.write(s)