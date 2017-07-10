from __future__ import print_function
import csv, datetime, sys
from django.core.management.base import BaseCommand, CommandError

from routeplanning.models import Flight
from common.helpers import utc

class Command(BaseCommand):
    help = 'Load flights from fixtures/flights.csv'

    def str_to_datetime(self, str):
        parts = str.split(' ')
        date_parts = parts[0].split('/')
        date = int(date_parts[0])
        month = int(date_parts[1])
        year = int(date_parts[2])
        hour = 0
        minute = 0
        second = 0

        if len(parts) > 1:
            time_parts = parts[1].split(':')
            hour = int(time_parts[0])
            minute = int(time_parts[1])
            second = int(time_parts[2])

        return datetime.datetime(year, month, date, hour, minute, second, tzinfo=utc)

    def handle(self, *args, **options):
        count = 1
        errors = 0
        with open('routeplanning/fixtures/flights.csv') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',', quotechar='"')
            for row in csvreader:
                try:
                    flight=Flight(
                        number=int(row[1][3:]),
                        origin=row[2],
                        destination=row[3],
                        scheduled_out_datetime=self.str_to_datetime(row[4]),
                        scheduled_in_datetime=self.str_to_datetime(row[6])
                    )
                    flight.save()
                except Exception as e:
                    errors += 1
                    print('')
                    print('Error occurred at line ' + str(count) + ': ' + str(e))
                    sys.stdout.flush()

                count += 1
                if count % 10 == 0:
                    print('.', end='')
                    sys.stdout.flush()

        print('')
        print(str(errors) + ' errors occurred during import process.')
