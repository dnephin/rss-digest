"""
 Send emails to the list.
"""

from collections import namedtuple
import datetime
import logging
import pynliner
import pystache
import re
import requests
import staticconf
from staticconf import schema


log = logging.getLogger(__name__)


EmailContent = namedtuple('EmailContent', 'subject html text')


class MailGunConfig(schema.Schema):
    namespace       = 'DEFAULT'
    config_path     = 'email.mailgun'

    api_url         = schema.string()
    api_key         = staticconf.get_string('MAILGUN_API_KEY', namespace='app_config')
    email_from      = schema.string()
    reply_to        = schema.string()
    list_domain     = schema.string()


class DigestEmailConfig(object):
    
    html_template   = 'templates/daily_digest_email/html.mustache'
    text_template   = 'templates/daily_digest_email/text.mustache'


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


# TODO: MailGunApi class
def get_mailing_lists(config):
    url = '%s/%s' % (config.api_url, 'lists')
    return requests.get(url, auth=('api', config.api_key)).json()


def create_list(config, address, name):
    url = '%s/%s' % (config.api_url, 'lists')
    return requests.post(url,
        auth=('api', config.api_key),
        data={
            'address': address,
            'name':    name
    })


class DigestEmailRenderer(object):

    config = DigestEmailConfig()

    def __init__(self, feed, date=datetime.date.today()):
        self.feed = feed
        self.date = date
        self.renderer = pystache.Renderer(string_encoding='utf8')

    def render_template(self, template_name, context):
        return self.renderer.render_path(template_name, context)

    def build_email(self):
        context = self.build_context()
        html_content = self.render_template(self.config.html_template, context)
        html = pynliner.Pynliner().from_string(html_content).run()
        return EmailContent(
            subject=context.title,
            html=html,
            text=self.render_template(self.config.text_template, context))

    def build_context(self):
        return DigestEmailContext(self.feed, self.date)


class DigestEmailContext(object):

    def __init__(self, feed, date):
        self.feed = feed
        self.config = feed.config
        self.date = date

    @property
    def title(self):
         return '%s digest for %s' % (
            self.config.name,  self.date.strftime('%B %d, %Y'))
   
    @property
    def url(self):
        return self.feed.feed['channel']['link']

    @property
    def issue(self):
        return self.feed.issue

    @property
    def image(self):
        return self.feed.image

    @property
    def items(self):
        return [self.prepare_item(item) for item in self.feed.items()]

    def prepare_item(self, item):
        return {
            'url':          item['link'],
            'title':        item['title'],
            'short_title':  truncate(item['title'], 80),
            'date':         item['date'],
            'author':       item.get('author'),
            'text':         item['summary'],
            'keywords':     item.get('keywords'),
            'slug':         slugify(item['title']),
            'publication':  item.get('publication'),
        }

def slugify(value):
    return re.sub(r'\W+', '-', value.lower())


def truncate(value, max_length):
    if len(value) <= max_length:
        return value
    return value[:max_length] + '...'


class DigestEmail(object):

    mail_config = MailGunConfig()

    def __init__(self, feed, renderer):
        self.feed = feed
        self.renderer = renderer

    def handle_response(self, http_response):
        if http_response.status_code == 200:
            log.info("%s: sent %d feed entries: %s",
                self.feed.config.name,
                len(self.feed.items()),
                http_response.content)
            return

        log.warn("%s: send failed! %d %s",
            self.feed.config.name,
            http_response.status_code,
            http_response.content)

    def send(self):
        self.handle_response(send_email(
            self.mail_config,
            self.feed.config.list_name,
            self.renderer.build_email()))


def send_digest(feed):
    renderer = DigestEmailRenderer(feed)
    return DigestEmail(feed, renderer).send()

