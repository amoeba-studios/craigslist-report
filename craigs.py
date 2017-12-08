import os
import sys
import pprint

from craigslist import CraigslistHousing

queries = [
    {
        'name': 'Cedar Point',
        'site': 'dallas',
        'category': 'apa',
        'filters': {
            'query': '"cedar+point"'
        }
    },
    {
        'name': 'Thorn Manor',
        'site': 'dallas',
        'category': 'apa',
        'filters': {
            'query': '"thorn+manor"'
        }
    },
]


def time_fmt(datetime):
    suffix='am'
    fields = datetime.split(' ')
    date = fields[0][5:].replace('-', '/')
    hr = int(fields[1].split(':')[0])
    if hr >= 12:
        suffix='pm'
        if hr > 12:
            hr -= 12
    min = fields[1].split(':')[1]

    str = "%s\t%2d:%s%s" % (date, hr, min, suffix)
    return str


if __name__ == '__main__':

    for query in queries:
        print "\n%s Listings" % query['name']
        print "------------------------------------------------------------"
        cl = CraigslistHousing(site=query['site'], category=query['category'], filters=query['filters'])

        results = cl.get_results(sort_by='newest', limit=20)
        for result in results:
            print("%s:\t(%5s)\t%s" % (time_fmt(result['datetime']), result['price'], result['name']) )
#            pprint.pprint(result)
#            print("\n")

