"""
 Send emails to the list.
"""

class MailGunConfig(object):

    api_url = 'https://api.mailgun.net/v2'
    api_key = ''
    email_from = 'Rss Digest'
    reply_to = 'Erica Lenton <Erica.Lenton@albertahealthservices.ca>'
    list_domain = 'app15574223.mailgun.org'


def send_email(config, list_name, subject, html, text):
    return requests.post(config.api_url,
        auth=('api', config.api_key),
        data={
            'from':         config.email_from,
            'to':           '%s@%s' % (list_name, config.list_domain),
            'h:Reply-To':   config.reploy_to, 
            'subject':      subject,
            'text':         text,
            'html':         html
        })


def send_digest(feed):
    pass
