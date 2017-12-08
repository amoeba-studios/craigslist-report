import os
import sys
import craigslist

from craigslist import CraigslistHousing




if __name__ == '__main__':

    cl = CraigslistHousing(site='dallas', category='apa', filters={'query': '"cedar+point"'})

    cl.show_filters()

    results = cl.get_results(sort_by='newest', limit=20)
    for result in results:
        print result
