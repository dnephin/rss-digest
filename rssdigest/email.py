"""
 Send emails to the list.
"""

from collections import namedtuple
import logging
import requests
import staticconf


log = logging.getLogger(__name__)


EmailContent = namedtuple('EmailContent', 'subject html text')


# TODO: move to config file
class MailGunConfig(object):

    api_url         = 'https://api.mailgun.net/v2'
    api_key         = staticconf.get_string('MAILGUN_API_KEY', namespace='app_config')
    email_from      = 'Rss Digest <Erica.Lenton@albertahealthservices.ca>'
    reply_to        = 'Erica Lenton <Erica.Lenton@albertahealthservices.ca>'
    list_domain     = 'app15574223.mailgun.org'


def send_email(config, list_name, email_content):
    url = '%s/%s/%s' % (config.api_url, config.list_domain, 'messages')
    log.info("Making API request to %s", url)
    return requests.post(url,
        auth=('api', config.api_key),
        data={
            'from':         config.email_from,
            'to':           '%s@%s' % (list_name, config.list_domain),
            'h:Reply-To':   config.reply_to, 
            'subject':      email_content.subject,
            'text':         email_content.text,
            'html':         email_content.html
        })


class DigestEmail(object):

    config = MailGunConfig

    def __init__(self, feed):
        self.feed = feed

    def build_email(self):
        return EmailContent('Subject', 'html', 'text')

    def handle_response(self, http_response):
        if http_response.status_code == 200:
            log.info("%s: sent %d feed entries: %s",
                self.feed.config.name,
                len(self.feed.recent_items),
                http_response.content)
            return

        log.warn("%s: send failed! %d %s",
            self.feed.config.name,
            http_response.status_code,
            http_response.content)

    def send(self):
        self.handle_response(send_email(
            self.config,
            self.feed.config.list_name,
            self.build_email()))


def send_digest(feed):
    return DigestEmail(feed).send()

