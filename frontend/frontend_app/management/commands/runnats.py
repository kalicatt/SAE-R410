from django.core.management.base import BaseCommand
import asyncio
from frontend_app.nats_consumer import start_nats_consumer

class Command(BaseCommand):
    help = 'Starts the NATS consumer to listen for signup messages.'

    def handle(self, *args, **kwargs):
        loop = asyncio.get_event_loop()
        loop.run_until_complete(start_nats_consumer())
