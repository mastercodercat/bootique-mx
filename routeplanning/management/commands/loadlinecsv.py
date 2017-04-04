from __future__ import print_function
import csv, datetime, sys
from django.core.management.base import BaseCommand, CommandError

from routeplanning.models import Line, LinePart
from home.helpers import utc

class Command(BaseCommand):
    help = 'Load lines and line parts from fixtures/lines.csv and fixtures/lineparts.csv'

    def handle(self, *args, **options):
        print('Loading lines')
        count = 1
        errors = 0
        with open('routeplanning/fixtures/lines.csv') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',')
            for row in csvreader:
                try:
                    line=Line(pk=int(row[0]), name=row[1])
                    line.save()
                except Exception as e:
                    errors += 1
                    print('')
                    print('Error occurred at line ' + str(count) + ': ' + str(e))
                    sys.stdout.flush()
                count += 1
                print('.', end='')
                sys.stdout.flush()
        print('')
        print(str(errors) + ' errors occurred during import process.')

        print('Loading line parts')
        count = 1
        errors = 0
        current_line = None
        with open('routeplanning/fixtures/lineparts.csv') as csvfile:
            csvreader = csv.reader(csvfile, delimiter=',')
            for row in csvreader:
                try:
                    line_id = int(row[2])
                    if not current_line or current_line.id != line_id:
                        current_line = Line.objects.get(pk=line_id)
                    line_part=LinePart(pk=int(row[0]), number=row[1], line=current_line)
                    line_part.save()
                except Exception as e:
                    errors += 1
                    print('')
                    print('Error occurred at line ' + str(count) + ': ' + str(e))
                    sys.stdout.flush()
                count += 1
                print('.', end='')
                sys.stdout.flush()
        print('')
        print(str(errors) + ' errors occurred during import process.')
