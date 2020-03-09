from collections import defaultdict
from decimal import Decimal
from functools import partial


def get_formatted_report(report):
    formatted_report = dict()
    for row in report:
        if row[2] in formatted_report:
            if row[0] in formatted_report[row[2]]:
                formatted_report[row[2]][row[0]] += row[1]
            else:
                formatted_report[row[2]][row[0]] = row[1]
        else:
            formatted_report[row[2]] = {}
            formatted_report[row[2]][row[0]] = row[1]
    return formatted_report
