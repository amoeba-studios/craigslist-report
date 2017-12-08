import smtplib

from craigslist import CraigslistHousing
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
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
    {
        'name': 'Arbor Terrace',
        'site': 'dallas',
        'category': 'apa',
        'filters': {
            'query': '"arbor+terrace"'
        }
    },
]

HR = 60 * 60
DAY = HR * 24
GREEN_THR = 2
YELLOW_THR = 4
GREEN = 'green'
YELLOW = 'cantaloupe'
RED = 'cranberry'

FROM = ''
TO = ['']
PASSWORD = ''


def time_fmt(date_time):

    post_time = datetime.strptime(date_time, '%Y-%m-%d %H:%M')
    delta = (datetime.now() - post_time).total_seconds()
    if delta < GREEN_THR * DAY:
        color = GREEN
    elif delta < YELLOW_THR * DAY:
        color = YELLOW
    else:
        color = RED

    t_str = post_time.strftime('%m/%d %I:%M%p')
    ret = '<font color = %s>' % color + t_str + '</font>'
    return ret


def mailit(subject, body, to, _from):
    try:
        server = smtplib.SMTP('smtp.mail.yahoo.com', 587)
        server.starttls()
        server.login(_from, PASSWORD)
        print "Email sent successful"
    except Exception as e:
        print "Email send failed. %s" % e
        return

    message = MIMEMultipart('alternative')
    message['Subject'] = subject
    message['To'] = ', '.join(to)
    message['From'] = _from
    message.attach(MIMEText(body, 'html'))

    server.sendmail(_from, to, message.as_string())
    server.quit()


if __name__ == '__main__':
    body = ""
    for query in queries:
        body += "%s Listings<BR>" % query['name']
        body += "----------------------------------<BR>"
        cl = CraigslistHousing(site=query['site'], category=query['category'], filters=query['filters'])

        results = cl.get_results(sort_by='newest', limit=20)
        for result in results:
            body += ("%s:\t(%5s)\t<a href=%s>%s</a>\n<BR>" %
                     (time_fmt(result['datetime']), result['price'], result['url'], result['name']))
        body += '<BR><BR>'

    body += "<font color = %s>Green</font> - Under %d days old<BR>" % (GREEN, GREEN_THR)
    body += "<font color = %s>Yellow</font> - Over %d days old<BR>" % (YELLOW, GREEN_THR)
    body += "<font color = %s>Red</font> - Over %d days old<BR>" % (RED, YELLOW_THR)

    subj = 'Daily apartment Listings'

    mailit(subj, body, TO, FROM)

