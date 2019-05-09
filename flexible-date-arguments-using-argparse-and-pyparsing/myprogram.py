import argparse
import datetime
from dateutil.relativedelta import relativedelta

from pyparsing import (
    ParseException,
    pyparsing_common as ppc,
    CaselessKeyword,
    And,
    Or,
    StringEnd
)


class Interval(object):

    def __init__(self, start, end):
        self.start = start
        self.end = end

    def __str__(self):
        return 'from {start} to {end}'.format(start=self.start, end=self.end)


def handle_last(tokens):
    end = datetime.date.today()
    start = end - relativedelta(days=tokens.n)

    return Interval(start, end)


def handle_previous(tokens):

    if tokens.day:
        end = datetime.date.today()
        start = end - relativedelta(days=1)
        return Interval(start, end)

    elif tokens.week:
        end = datetime.date.today()
        start = end - relativedelta(days=7)
        return Interval(start, end)

    elif tokens.month:
        end = datetime.date.today()
        start = end - relativedelta(months=1)
        return Interval(start, end)


def handle_fromto(tokens):
    return Interval(tokens.start, tokens.end)

def make_date_parser():

    date_expr = ppc.iso8601_date.copy()
    date_expr.setParseAction(ppc.convertToDate())

    expr_last = And(
        CaselessKeyword('LAST') & ppc.integer.setResultsName('n') & StringEnd()
    ).setResultsName('interval').setParseAction(handle_last)

    expr_prev = And(
        CaselessKeyword('PREVIOUS') & Or(
            CaselessKeyword('DAY').setResultsName('day') | CaselessKeyword('WEEK').setResultsName('week') | CaselessKeyword('MONTH').setResultsName('month')
        ) + StringEnd()
    ).setResultsName('interval').setParseAction(handle_previous)

    expr_fromto_date = And(
        CaselessKeyword('FROM') + date_expr.setResultsName('start') + CaselessKeyword('TO') + date_expr.setResultsName('end') + StringEnd()
    ).setResultsName('interval').setParseAction(handle_fromto)

    parser = expr_fromto_date | expr_last | expr_prev

    return parser




class IntervalAction(argparse.Action):

    def __init__(self, option_strings, dest, **kwargs):

        self._parser = make_date_parser()

        super(IntervalAction, self).__init__(option_strings, dest, **kwargs)

    def __call__(self, parser, namespace, values, option_string=None):
        try:
            rv = self._parser.parseString(values)
        except ParseException:
            parser.error('argument %s is not valid' % '/'.join(self.option_strings))
        else:
            setattr(namespace, self.dest, rv.interval)


if __name__ == '__main__':

    parser = argparse.ArgumentParser()
    parser.add_argument('-i', '--interval', action=IntervalAction, required=True)

    args = parser.parse_args()

    print('interval: %s' % args.interval)
    print('interval start: %s' % args.interval.start)
    print('interval end: %s' % args.interval.end)
