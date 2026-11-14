import os
import sys
from threading import Thread

from client import DishClient, ServerError

# the report is saved next to this program unless a file name is given
REPORT_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'iftar_report.txt')


def write_report(path, dishes, outcome):
    # runs in the thread: writes the records to a UTF-8 text file
    try:
        with open(path, 'w', encoding='utf-8') as report:
            report.write('Iftar menu report\n')
            report.write('=================\n')
            if len(dishes) == 0:
                report.write('No dishes saved yet.\n')
            total = 0
            for dish in dishes:
                line = '%d. %s (%s) - %.2f SAR\n' % (dish['id'], dish['name'],
                                                      dish['category'], dish['cost'])
                report.write(line)
                total = total + dish['cost']
            report.write('-----------------\n')
            report.write('Dishes: %d\n' % len(dishes))
            report.write('Total estimated cost: %.2f SAR\n' % total)
        # a thread cannot return a value, so it stores the result here
        outcome['saved'] = True
    except OSError as error:
        outcome['saved'] = False
        outcome['error'] = str(error)


def main():
    path = REPORT_FILE
    if len(sys.argv) > 1:
        path = sys.argv[1]

    # ask the JSON route of Flask for the saved records
    try:
        dishes = DishClient().list_dishes()
    except ServerError as error:
        print('Report not saved:', error)
        return 1

    # one thread writes the file, join() waits until it finishes
    outcome = {'saved': False, 'error': ''}
    worker = Thread(target=write_report, args=(path, dishes, outcome))
    worker.start()
    worker.join()

    if outcome['saved']:
        print('Report saved:', path, '(' + str(len(dishes)) + ' dishes)')
        return 0
    print('Report not saved:', outcome['error'])
    return 1


if __name__ == '__main__':
    sys.exit(main())
