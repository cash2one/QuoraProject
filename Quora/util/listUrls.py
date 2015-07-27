import json
import sys
sys.path.append('/home/wpovell/PyLinear')
from Pylinear.feature import getFiles

out = open('/export/a04/wpovell/scrapedUrls.txt', 'w')
for fn in getFiles('/export/a04/wpovell/scrape_data_ordered'):
    with open(fn) as f:
        data = json.load(f)
    try:    
        out.write('{}\n'.format(data['url']))
    except TypeError:
        print(fn)
out.close()
