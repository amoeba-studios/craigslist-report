#!/usr/bin/env python 

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

CONFIG = "craigs.ini"


class ColorCode(object):
    def __init__(self, code, slackstr):
        self.code = code
        self.slackstr = slackstr

GREEN = ColorCode('green', 'good')
YELLOW = ColorCode('cantaloupe', 'warning')
RED = ColorCode('cranberry', 'danger')
colors = [GREEN, YELLOW, RED]


def mailit(subject, body, to, email):
    try:
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


def time_fmt(date_time, job, email=True):

    post_time = datetime.strptime(date_time, '%Y-%m-%d %H:%M')
    delta = (datetime.now() - post_time).total_seconds()
    if delta < int(job['green_thr']) * DAY:
        color = GREEN
    elif delta < int(job['yellow_thr']) * DAY:
        color = YELLOW
    else:
        color = RED

    t_str = post_time.strftime('%m/%d %I:%M%p')
    if email:
        ret = '<font color=%s>' % color.code + t_str + '</font>'
    else:
        ret = t_str

    return ret, color


def slackit(slack, msg, att):
    sc = SlackClient(slack['token'])
    sc.api_call("chat.postMessage", channel=slack['channel'], text='Waking up to do work!', username='craigbot',
                icon_emoji=':robot_face:')
    sc.api_call("chat.postMessage", channel=slack['channel'], text=msg, username='craigbot',
                icon_emoji=':robot_face:', attachments=json.dumps(att))


if __name__ == '__main__':
    print "reading config"
    with open(CONFIG) as config_file:
        cfg = json.load(config_file)
    print "done reading config"

    attachments = []

    for job in cfg['job_list']:
        body = ""
        for query in job['queries']:
            body += "<B>%s Listings<B><BR>" % query['name']
            body += "-------------------------<BR>"
            attachments.append(dict(pretext="\n*_%s Listings_*" % query['name'], text="",
                                    mrkdwn_in=["pretext", "text", "fields"]))
            text = {GREEN.code: "", YELLOW.code: "", RED.code: ""}

            cl = CraigslistHousing(site=query['site'], category=query['category'], filters=query['filters'])
            results = cl.get_results(sort_by='newest', limit=5)
            for result in results:
                time_str, color = (time_fmt(result['datetime'], job))
                body += ("%s:\t(%5s)\t<a href=%s>%s</a>\n<BR>" %
                         (time_str, result['price'], result['url'], result['name']))

                time_str, color = time_fmt(result['datetime'], job, False)
                text[color.code] += ("%s: (%5s) <%s|%s>\n" %
                                     (time_str, result['price'], result['url'], result['name']))
            body += '<BR><BR>'

            for color in colors:
                if len(text[color.code]):
                    attachments.append(dict(color=color.slackstr, text='```' + text[color.code] + '```',
                                            mrkdwn_in=["pretext", "text", "fields"]))

        body += "<font color = %s>Green</font> - Under %d days old<BR>" % (GREEN.code, job['green_thr'])
        body += "<font color = %s>Yellow</font> - Over %d days old<BR>" % (YELLOW.code, job['green_thr'])
        body += "<font color = %s>Red</font> - Over %d days old<BR>" % (RED.code, job['yellow_thr'])

        mailit(job['subject'], body, job['sendto'], cfg['email'])
        slackit(cfg['slack'], "", attachments)

    print "done"
    exit(0)
