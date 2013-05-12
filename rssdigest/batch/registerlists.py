import logging

from rssdigest import config, email


log = logging.getLogger(__name__)


feed_configs = config.get_feed_config('feeds')
mail_config = email.MailGunConfig()


def get_registered_lists():
    mailing_lists = email.get_mailing_lists(mail_config)
    return mailing_lists['items']


def get_configured_mapping():
    domain = mail_config.list_domain
    def build_address(conf):
        return '%s@%s' % (conf.list_name, domain), conf
    return dict(build_address(conf) for conf in feed_configs)


def create_lists(configured, registered):
    registered_addresses = set(l['address'] for l in registered)
    missing_lists = set(configured) - registered_addresses
    log.warn("Creating lists: %s", missing_lists)

    for list_address in missing_lists:
        feed_config = configured[list_address]
        email.create_list(mail_config, list_address, feed_config.name)


def run():
    registered_lists = get_registered_lists()
    configured_names = get_configured_mapping()
    create_lists(configured_names, registered_lists)
    
