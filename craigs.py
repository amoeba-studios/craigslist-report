import smtplib

from craigslist import CraigslistHousing
from datetime import datetime

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

HR = 60 * 60
DAY = HR * 24
GREEN_THR = DAY * 2
YELLOW_THR = DAY * 4


def time_fmt(date_time):

    post_time = datetime.strptime(date_time, '%Y-%m-%d %H:%M')
    delta = (datetime.now() - post_time).total_seconds()
    if delta < GREEN_THR:
        color = 'green'
    elif delta < YELLOW_THR:
        color = 'yellow'
    else:
        color = 'red'

    t_str = post_time.strftime('%m/%d %I:%M%p')
    ret = color + ' ' + t_str
    return ret


if __name__ == '__main__':

    # for query in queries:
    #     print "\n%s Listings" % query['name']
    #     print "------------------------------------------------------------"
    #     cl = CraigslistHousing(site=query['site'], category=query['category'], filters=query['filters'])
    #
    #     results = cl.get_results(sort_by='newest', limit=20)
    #     for result in results:
    #         print("%s:\t(%5s)\t%s" % (time_fmt(result['datetime']), result['price'], result['name']) )
    fromA = ''
    to = ''
    subj = 'Test Subject'
    date = '12/8/2017'
    txt = 'Testing Body'

    msg = "From: %s\nTo: %s\nSubject: %s\nDate: %s\n\n%s" % (fromA, to, subj, date, txt)
    try:
        server = smtplib.SMTP('smtp.mail.yahoo.com', 587)
        server.starttls()
        server.login('', '')
        server.sendmail(fromA, to, msg)
        print "sendmail succeeded"
    except Exception as e:
        print "sendmail failed"
        print e
