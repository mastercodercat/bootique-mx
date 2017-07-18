from __future__ import print_function
import csv, datetime, sys
from django.core.management.base import BaseCommand, CommandError

from routeplanning.models import Flight
from common.helpers import utc, str_to_datetime

class Command(BaseCommand):
    help = 'Load flights from fixtures/flights.csv'

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
                        scheduled_out_datetime=str_to_datetime(row[4]),
                        scheduled_in_datetime=str_to_datetime(row[6])
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
