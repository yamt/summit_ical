#!/usr/bin/env python

import argparse
import re
import sys
import demjson
import simplejson as json
import pprint
from icalendar import Calendar, Event, Timezone, TimezoneStandard, TimezoneDaylight
from dateutil.parser import parse
from dateutil.tz import gettz
from pytz import utc


PATTERN_STR = r'summit.locations\[([0-9]*)\] =.*?({.*?});'
PATTERN2_STR = r'<.*?>'

PATTERN = re.compile(PATTERN_STR, re.MULTILINE | re.DOTALL)
PATTERN2 = re.compile(PATTERN2_STR, re.MULTILINE | re.DOTALL)
REPLACE_MAP = {
    '&nbsp;': ' ',
    '&lt;': "<",
    '&gt;': ">",
    '&amp;': "&",
}

def main(infiles=None, outfile=None, locfile=None, **kwargs):
    cal = Calendar()
    cal['dtstart'] = '20180519T080000'
    cal['summary'] = 'OpenStack Summit Vancouver 2018'
    tz = Timezone(TZID='America/Vancouver')
    tz.add_component(TimezoneStandard(DTSTART="20171105T020000",
                                      TZOFFSETFROM="-0700",
                                      TZOFFSETTO="-0800",
                                      RDATE="20181104T020000",
                                      TZNAME="PST"))
    tz.add_component(TimezoneDaylight(DTSTART="20180311T020000",
                                      TZOFFSETFROM="-0800",
                                      TZOFFSETTO="-0700",
                                      TZNAME="PDT"))
    cal.add_component(tz)

    locations = {}
    match = PATTERN.finditer(locfile.read())
    for entry in match:
        locations[entry.group(1)] = demjson.decode(entry.group(2))
    #pprint.pprint(locations)

    for infile in infiles:
        data = json.load(infile)
        if data is None:
            return
        pprint.pprint(data)

        for session in data['events']:
            timezone_str = session.get('time_zone_id')
            tzinfos = {"UN": gettz(timezone_str)}
            start_datetime_str = session.get('start_datetime')
            start_datetime = parse(start_datetime_str + " UN", tzinfos=tzinfos)
            start_datetime_utc = start_datetime.astimezone(utc)
            end_datetime_str = session.get('end_datetime')
            end_datetime = parse(end_datetime_str + " UN", tzinfos=tzinfos)
            end_datetime_utc = end_datetime.astimezone(utc)
            desc = PATTERN2.sub('', session.get('abstract'))
            for pre, post in REPLACE_MAP.items():
                desc = desc.replace(pre, post)

            event = Event()
            event.add('dtstart', start_datetime_utc)
            event.add('dtend', end_datetime_utc)
            event.add('summary', session.get('title'))
            event.add('location', locations.get(str(session.get('location_id')), {}).get('name_nice', ""))
            event.add('description', desc)
            event.add('uid', "%s@openstacksummitboston2017" % session.get('id'))
            cal.add_component(event)

    outfile.write(cal.to_ical())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('outfile', nargs='?', type=argparse.FileType('w'),
                        default=sys.stdout)
    parser.add_argument('locfile', nargs='?', type=argparse.FileType('r'))
    parser.add_argument('infiles', nargs='*', type=argparse.FileType('r'),
                        default=[sys.stdin])

    args = parser.parse_args()
    main(**args.__dict__)
