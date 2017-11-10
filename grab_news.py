import os
import feedparser
import googletrans
import redis
import logging

redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
rss_url = os.environ.get('URL', 'https://hnrss.org/frontpage')
logger = logging.getLogger('bot')
logging.basicConfig(level=logging.DEBUG)


def main():
    r = redis.from_url(redis_url)
    feed = feedparser.parse(rss_url)
    translator = googletrans.Translator()

    for entry in feed['entries']:

        if 'show hn:' in entry['title'].lower():
            continue

        if 'ask hn:' in entry['title'].lower():
            continue

        t = translator.translate(entry['title'], dest='uz', src='en')
        text = '{title}\n\n{link}'.format(title=t.text, link=entry['link'])

        if r.sismember('published_posts', text):
            logger.info(
                'Post {text} already published, skipping...'.format(
                    text=text))
            continue

        logger.info('Saving post {text} to redis...'.format(text=text))
        r.sadd('unpublished_posts', text)


if __name__ == '__main__':
    main()
