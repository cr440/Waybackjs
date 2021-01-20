import requests
import re
import sys
from multiprocessing.dummy import Pool


def jslinks(host):
    r = requests.get(
        'https://web.archive.org/cdx/search/cdx?url=%s&output=json&fl=timestamp,original&filter=statuscode:200&collapse=digest' % host)
    results = r.json()
    if len(results) == 0:  # might find nothing
        return []
    results.pop(0)  # The first item is ['timestamp', 'original']
    return results


def getjspaths(snapshot):
    url = 'https://web.archive.org/web/{0}/{1}'.format(
        snapshot[0], snapshot[1])
    jsext = snapshot[0] + "js_"
    homepage = requests.get(url).text
    if jsext in homepage: 
        pathlist = []
        paths = re.findall(jsext + ".*", homepage)
        for p in paths:
            pp = p.split("\"")[0]
            pathlist.append(pp)
        return pathlist
    return []
    
if __name__ == '__main__':
    
    if len(sys.argv) < 2:
        print('Usage: python3 waybackjs.py <domain-name>')
        sys.exit()

    host = sys.argv[1]

    snapshots = jslinks(host)
    print('Found %s results' % len(snapshots))
    if len(snapshots) == 0:
        sys.exit()
        
    pool = Pool(4)
    links = pool.map(getjspaths, snapshots)
    # print(type(links))
    filename = '%s-jslinks.txt' % host
    print('[*] Saving results to %s' % filename)    
    paths = set()
    for i in links:
        paths.update(i)
    with open(filename, 'w') as f:
        f.write("https://web.archive.org/web/")
        f.write('\nhttps://web.archive.org/web/'.join(paths))
