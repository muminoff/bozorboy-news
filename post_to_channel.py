import os
import logging
import asyncio
import aiotg
import redis

api_token = os.environ.get('API_TOKEN')
bot_name = os.environ.get('BOT_NAME')
bot = aiotg.Bot(api_token=api_token, name=bot_name)
channel = bot.channel(os.environ.get('CHANNEL_NAME', '@BozorvoyNews'))
redis_url = os.environ.get('REDIS_URL', 'redis://localhost:6379/0')
logger = logging.getLogger('bot')
logging.basicConfig(level=logging.DEBUG)


async def main():
    r = redis.from_url(redis_url)
    post = r.spop('unpublished_posts')
    text = post.decode('utf-8')

    logger.info('Publishing post {title} to channel...'.format(title=post))
    await channel.send_text(text)
    r.sadd('published_posts', text)

loop = asyncio.get_event_loop()
loop.run_until_complete(main())
