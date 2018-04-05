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
import urllib


PATTERN_STR = r'<.*?>'
PATTERN2_STR = r'summit.locations\[([0-9]*)\] =.*?({.*?});'
PATTERN3_STR = r'summit.tracks\[([0-9]*)\] =.*?({.*?});'
PATTERN4_STR = r'[^a-zA-Z]+'

PATTERN = re.compile(PATTERN_STR, re.MULTILINE | re.DOTALL)
PATTERN2 = re.compile(PATTERN2_STR, re.MULTILINE | re.DOTALL)
PATTERN3 = re.compile(PATTERN3_STR, re.MULTILINE | re.DOTALL)
PATTERN4 = re.compile(PATTERN4_STR, re.MULTILINE | re.DOTALL)
REPLACE_MAP = {
    '&nbsp;': ' ',
    '&lt;': "<",
    '&gt;': ">",
    '&amp;': "&",
}

def main(infiles=None, locfile=None, **kwargs):
    locations = {}
    metadata_file = locfile.read()
    match = PATTERN2.finditer(metadata_file)
    for entry in match:
        locations[entry.group(1)] = demjson.decode(entry.group(2))

    tracks = {}
    match = PATTERN3.finditer(metadata_file)
    for entry in match:
        tracks[entry.group(1)] = demjson.decode(entry.group(2)).get('name')

    events = []
    for infile in infiles:
        data = json.load(infile)
        if data is None:
            continue
        events.extend(data['events'])

    for track_id, track_name in tracks.items():
        cal = Calendar()
        cal['dtstart'] = '20180519T080000'
        cal['summary'] = 'OpenStack Summit Vancouver 2018: ' + track_name
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

        for session in events:
            if track_id != str(session.get('track_id')):
                continue
            timezone_str = session.get('time_zone_id')
            tzinfos = {"UN": gettz(timezone_str)}
            start_datetime_str = session.get('start_datetime')
            start_datetime = parse(start_datetime_str + " UN", tzinfos=tzinfos)
            start_datetime_utc = start_datetime.astimezone(utc)
            end_datetime_str = session.get('end_datetime')
            end_datetime = parse(end_datetime_str + " UN", tzinfos=tzinfos)
            end_datetime_utc = end_datetime.astimezone(utc)
            desc = PATTERN.sub('', session.get('abstract'))
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
        with open("%s.ics" % PATTERN4.sub("-", track_name), "w") as f:
            f.write(cal.to_ical())


if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('locfile', nargs='?', type=argparse.FileType('r'))
    parser.add_argument('infiles', nargs='*', type=argparse.FileType('r'),
                        default=[sys.stdin])

    args = parser.parse_args()
    main(**args.__dict__)
