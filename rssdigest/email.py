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


log = logging.getLogger(__name__)


EmailContent = namedtuple('EmailContent', 'subject html text')


# TODO: move to config file
class MailGunConfig(object):

    api_url         = 'https://api.mailgun.net/v2'
    api_key         = staticconf.get_string('MAILGUN_API_KEY', namespace='app_config')
    email_from      = 'Rss Digest <Erica.Lenton@albertahealthservices.ca>'
    reply_to        = 'Erica Lenton <Erica.Lenton@albertahealthservices.ca>'
    list_domain     = 'app15574223.mailgun.org'


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


class DigestEmailRenderer(object):

    config = DigestEmailConfig

    def __init__(self, feed, date=datetime.date.today()):
        self.feed = feed
        self.date = date
        self.renderer = pystache.Renderer()

    def render_template(self, template_name, context):
        return self.renderer.render_path(template_name, context)

    def build_email(self):
        context = self.build_context()
        html = pynliner.Pynliner().from_string(
            self.render_template(self.config.html_template, context)).run()
        return EmailContent(
            subject=context.title,
            html=html,
            text=self.render_template(self.config.text_template, context))

    def build_context(self):
        return DigestEmailContext(self.feed, self.date)


# TODO: text version
class DigestEmailContext(object):

    def __init__(self, feed, date):
        self.feed = feed.feed
        self.config = feed.config
        self.recent_items = feed.recent_items
        self.date = date

    @property
    def title(self):
         return '%s digest for %s' % (
            self.config.name,  self.date.strftime('%B %d, %Y'))
   
    @property
    def url(self):
        return self.feed.feed.link

    @property
    def issue(self):
        return self.feed.feed['prism_coverdisplaydate']        

    # TODO: feedparser is broken for image
    @property
    def image(self):
        return None

    @property
    def items(self):
        return [self.prepare_item(item) for item in self.recent_items]

    def prepare_item(self, item):
        return {
            'url':          item['link'],
            'title':        item['title'],
            'short_title':  truncate(item['title'], 80),
            'date':         item['prism_publicationdate'],
            'author':       item['author'],
            'text':         item['summary'],
            'keywords':     self.prepare_keywords(item),
            'slug':         slugify(item['title']),
            'publisher':    self.publisher(item)
        }

    def prepare_keywords(self, item):
        return None if not item.get('tags') else item['tags'][0]['term']

    def publisher(self, item):
        return 'Vol. %s No. %s %s-%s' % (
            item['prism_volume'],
            item['prism_number'],
            item['prism_startingpage'],
            item['prism_endingpage'])


def slugify(value):
    return re.sub(r'\W+', '-', value.lower())


def truncate(value, max_length):
    if len(value) <= max_length:
        return value
    return value[:max_length] + '...'


class DigestEmail(object):

    mail_config = MailGunConfig

    def __init__(self, feed, renderer):
        self.feed = feed
        self.renderer = renderer

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
            self.mail_config,
            self.feed.config.list_name,
            self.renderer.build_email()))


def send_digest(feed):
    renderer = DigestEmailRenderer(feed)
    return DigestEmail(feed, renderer).send()
