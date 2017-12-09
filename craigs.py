import smtplib
import json

from craigslist import CraigslistHousing
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from datetime import datetime
from slackclient import SlackClient

HR = 60 * 60
DAY = HR * 24
GREEN = 'green'
YELLOW = 'cantaloupe'
RED = 'cranberry'

CONFIG = "/tmp/craigs.ini"


def mailit(subject, body, to, email):
    try:
        print email
        server = smtplib.SMTP(email['server'], int(email['port']))
        server.starttls()
        server.login(email['user'], email['password'])
        print "Email login successful"
    except Exception as e:
        print "Email login failed. %s" % e
        return

    message = MIMEMultipart('alternative')
    message['Subject'] = subject
    message['To'] = ', '.join(to)
    message['From'] = email['user']
    message.attach(MIMEText(body, 'html'))

    server.sendmail(email['user'], to, message.as_string())
    server.quit()


def time_fmt(date_time, job, do_color=True):

    post_time = datetime.strptime(date_time, '%Y-%m-%d %H:%M')
    delta = (datetime.now() - post_time).total_seconds()
    if delta < int(job['green_thr']) * DAY:
        color = GREEN
    elif delta < int(job['yellow_thr']) * DAY:
        color = YELLOW
    else:
        color = RED

    t_str = post_time.strftime('%m/%d %I:%M%p')
    if do_color:
        ret = '<font color = %s>' % color + t_str + '</font>'
    else:
        ret = t_str

    return ret


def slackit(slack, msg):
    sc = SlackClient(slack['token'])
    sc.api_call("chat.postMessage", channel=slack['channel'], text=msg, username='craigbot',
                icon_emoji=':robot_face:')

if __name__ == '__main__':
    with open(CONFIG) as config_file:
        cfg = json.load(config_file)

    body = ""
    s_body = ""
    for job in cfg['job_list']:
        for query in job['queries']:
            body = "%s Listings<BR>" % query['name']
            s_body = "%s Listings\n" % query['name']
            body += "----------------------------------<BR>"
            s_body += "----------------------------------\n"

            cl = CraigslistHousing(site=query['site'], category=query['category'], filters=query['filters'])

            results = cl.get_results(sort_by='newest', limit=20)
            for result in results:
                body += ("%s:\t(%5s)\t<a href=%s>%s</a>\n<BR>" %
                         (time_fmt(result['datetime'], job), result['price'], result['url'], result['name']))
                s_body += ("%s:\t(%5s)\t%s\n" %
                           (time_fmt(result['datetime'], job, False), result['price'], result['name']))
            body += '<BR><BR>'
            s_body += '\n\n'

        body += "<font color = %s>Green</font> - Under %d days old<BR>" % (GREEN, job['green_thr'])
        body += "<font color = %s>Yellow</font> - Over %d days old<BR>" % (YELLOW, job['green_thr'])
        body += "<font color = %s>Red</font> - Over %d days old<BR>" % (RED, job['yellow_thr'])

#        mailit(job['subject'], body, job['sendto'], cfg['email'])
        slackit(cfg['slack'], s_body)

    exit(0)
