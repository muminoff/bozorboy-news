import os
import feedparser
import googletrans
import redis
import logging
import requests

redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
rss_url = os.environ.get('URL', 'https://hnrss.org/frontpage')
bitly_api_url = os.environ.get('BITLY_API_URL', 'https://api-ssl.bitly.com/v3/shorten')
bitly_access_token = os.environ.get('BITLY_ACCESS_TOKEN')
logger = logging.getLogger('bot')
logging.basicConfig(level=logging.INFO)


def shorten_url(url):
    params = {
        'access_token': bitly_access_token,
        'longUrl': url,
        'domain': 'j.mp'
    }
    response = requests.get(bitly_api_url, params=params)
    short_url = None

    try:
        short_url = response.json()['data']['url']
    except:
        pass

    return short_url


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

        link = shorten_url(entry['link'])
        if not link:
            link = entry['link']

        text = '{title} {link}'.format(title=t.text, link=link)

        if not r.sismember('published_posts', text):
            logger.info(text + '\n')
            r.sadd('unpublished_posts', text)


if __name__ == '__main__':
    main()
