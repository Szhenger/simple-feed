import feedparser, schedule, threading
from datetime import datetime, timedelta
from .models import Feed, Item

# Create your utilty functions here.

def get_items(feed):
    """
    Input: feed of class Feed 
    Side Effect: Inserts all items into feed
    Output: None
    """
    reader = feedparser.parse(feed.feed_url)
    num_items = len(reader.entries)

    # Add the items of the feed as Item instances
    for i in range(num_items):
        reader_item = reader.entries[num_items - (i + 1)]
        if reader_item.published:
            try:
                reader_item_date = datetime.strptime(reader_item.published, "%a, %d %b %Y %H:%M:%S %Z")
            except:
                reader_item_date = datetime.strptime(reader_item.published, "%a, %d %b %Y %H:%M:%S %z")
        else:
            reader_item_date = reader_item.published
        item = Item(
            feed=feed,
            title=reader_item.title,
            url=reader_item.link,
            content=reader_item.description,
            date_published=reader_item_date
        )
        item.save()

# Updates the items of the feeds
def update_feeds():
    """
    Input: None
    Side Effect: Updates every feed of class Feed 
    Output: None
    """
    feeds = Feed.objects.all()

    # Add new items of the feed as Item instances
    for feed in feeds:
        reader = feedparser.parse(feed.feed_url)
        num_items = len(reader.entries)
        for i in range(num_items):
            reader_item = reader.entries[num_items - (i + 1)]
            reader_last_update = datetime.now() - timedelta(days=1)
            if reader_item.published:
                try:
                    reader_item_date = datetime.strptime(reader_item.published, "%a, %d %b %Y %H:%M:%S %Z")
                except:
                    reader_item_date = datetime.strptime(reader_item.published, "%a, %d %b %Y %H:%M:%S %z")
            else:
                reader_item_date = reader_last_update
            if reader_item_date >= reader_last_update:
                item = Item(
                    feed=feed,
                    title=reader_item.title,
                    url=reader_item.link,
                    content=reader_item.description,
                    date_published=reader_item_date
                )
                item.save()


def queue_tasks():
    """
    Input: None
    Side Effect: Runs queued tasks
    Output: None
    """
    while True:
        schedule.run_pending()


# Schedule every feed to be updated at 07:30 everyday
schedule.every().day.at("07:30").do(update_feeds)

# Execute the scheduled tasks in a separate thread
thread = threading.Thread(target=queue_tasks)
thread.start()
