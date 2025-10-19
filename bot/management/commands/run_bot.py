# bot/management/commands/run_bot.py

import time
from django.core.management.base import BaseCommand
from bot.services import fetch_and_store_prices

class Command(BaseCommand):
    """
    Django management command to run the arbitrage bot.
    """
    help = 'Starts the arbitrage bot to fetch and store crypto prices.'

    def handle(self, *args, **kwargs):
        self.stdout.write(self.style.SUCCESS('Starting arbitrage bot...'))

        while True:
            try:
                # Call the main service function
                fetch_and_store_prices()

                # Wait for 10 seconds before the next check
                time.sleep(10)

            except KeyboardInterrupt:
                self.stdout.write(self.style.WARNING('Bot stopped by user.'))
                break
            except Exception as e:
                self.stderr.write(self.style.ERROR(f'An error occurred: {e}'))
                # Optional: wait longer after an error before retrying
                time.sleep(60)
