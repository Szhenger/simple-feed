# feed/management/commands/run_feed_updater.py

from django.core.management.base import BaseCommand
from feed.util import update_feeds

class Command(BaseCommand):
    help = 'Runs the feed updater to fetch and store RSS content'

    def handle(self, *args, **options):
        self.stdout.write(self.style.NOTICE("Starting feed update..."))
        update_feeds()
        self.stdout.write(self.style.SUCCESS("Feed update complete."))
