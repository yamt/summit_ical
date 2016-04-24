#!/usr/bin/env python

import re
import codecs
import csv
import json
import pprint
import pytz
import sys
from datetime import datetime, timedelta

from HTMLParser import HTMLParser
from icalendar import Calendar, Event

pattern = re.compile(r"""^.*Description: """)

locations = {}
locations["25"] = "Austin Convention Center"
locations["38"] = "JW Marriott Austin"
locations["39"] = "Hilton Austin"
locations["40"] = "Austin Convention Center - Level 1 - Room 1"
locations["41"] = "Rainey Street"
locations["42"] = "JW Marriott Austin - Level 3 - Salon A"
locations["43"] = "JW Marriott Austin - Level 3 - Salon B"
locations["44"] = "JW Marriott Austin - Level 3 - Salon C"
locations["45"] = "JW Marriott Austin - Level 3 - Salon D"
locations["46"] = "JW Marriott Austin - Level 3 - Salon E"
locations["47"] = "JW Marriott Austin - Level 3 - Salon F"
locations["48"] = "JW Marriott Austin - Level 3 - Salon G"
locations["49"] = "JW Marriott Austin - Level 3 - Salon H"
locations["50"] = "JW Marriott Austin - Level 3 - MR 301"
locations["51"] = "JW Marriott Austin - Level 3 - MR 302"
locations["52"] = "Austin Convention Center - Level 1 - Ballroom A"
locations["53"] = "Austin Convention Center - Level 1 - Ballroom B"
locations["54"] = "Austin Convention Center - Level 1 - Ballroom C"
locations["55"] = "Austin Convention Center - Level 4 - Ballroom E"
locations["56"] = "Austin Convention Center - Level 4 - Ballroom F"
locations["57"] = "Austin Convention Center - Level 4 - Ballroom G"
locations["58"] = "Austin Convention Center - Level 4 - Ballroom D"
locations["59"] = "Austin Convention Center - Level 4 - MR 12 A/B "
locations["60"] = "Austin Convention Center - Level 4 - MR 15"
locations["61"] = "Austin Convention Center - Level 4 - MR 17 A/B"
locations["62"] = "Austin Convention Center - Level 4 - MR 16 A/B"
locations["63"] = "Austin Convention Center - Level 4 - MR 18 A/B"
locations["64"] = "Austin Convention Center - Level 4 - MR 18 C/D"
locations["65"] = "Austin Convention Center - Level 4 - MR 19 A/B"
locations["66"] = "Austin Convention Center - Level 1 - Expo Hall 1"
locations["67"] = "Austin Convention Center - Level 1 - Expo Hall 5"
locations["68"] = "Austin Convention Center - Level 1 - Expo Hall 2/3"
locations["69"] = "Austin Convention Center - Level 1 - Marketplace Expo Hall 4"
locations["70"] = "Hilton Austin - Level 4 - Salon C"
locations["71"] = "Austin Convention Center - Level 1 - Solar Atrium"
locations["72"] = "Lounges"
locations["73"] = "Hilton Austin - Level 6 - Salon F"
locations["74"] = "Hilton Austin - Level 6 - Salon G"
locations["75"] = "Hilton Austin - Level 6 - Salon H"
locations["76"] = "Hilton Austin - Level 6 - Salon J"
locations["77"] = "Hilton Austin - Level 6 - Salon K"
locations["78"] = "Hilton Austin - Level 6 - MR 613"
locations["79"] = "Austin Convention Center - Level 1 - Marketplace Theater"
locations["80"] = "Austin Convention Center - Level 4 - MR 11A/B"
locations["81"] = "Austin Convention Center - Level 4 - MR 13A"
locations["82"] = "Austin Convention Center - Level 4 - MR 13B"
locations["83"] = "Hilton Austin - Salon A"
locations["84"] = "Hilton Austin - Salon B"
locations["85"] = "Hilton Austin - Salon D"
locations["86"] = "Hilton Austin - Salon E"
locations["87"] = "Hilton Austin - MR 400"
locations["88"] = "Hilton Austin - Boardroom 401"
locations["89"] = "Hilton Austin - MR 402"
locations["90"] = "Hilton Austin - Boardroom 403"
locations["91"] = "Hilton Austin - MR 404"
locations["92"] = "Hilton Austin - MR 406"
locations["93"] = "Hilton Austin - MR 408"
locations["94"] = "Hilton Austin - MR 410"
locations["95"] = "Hilton Austin - MR 412"
locations["96"] = "Hilton Austin - MR 414"
locations["97"] = "Hilton Austin - MR 415A"
locations["98"] = "Hilton Austin - MR 415B"
locations["99"] = "Hilton Austin - MR 416A"
locations["100"] = "Hilton Austin - MR 416B"
locations["101"] = "Hilton Austin - MR 417A"
locations["102"] = "Hilton Austin - MR 417B"
locations["103"] = "The Belmont"
locations["104"] = "Austin Convention Center - Level 1 - MR 1"
locations["105"] = "Hilton Austin - Salon A2"
locations["106"] = "Hilton Austin - Salon B2"
locations["107"] = "Hilton Austin - Salon D2"
locations["108"] = "JW Marriott Austin - Level 3 - MR 303"
locations["109"] = "Hilton Austin - Level 6 - Salons H/J/K"
locations["110"] = "Hilton Austin - Level 6 - Salons H/J/K"
locations["111"] = "Cooper\'s Pit Bar-B-Que"

tracks = {}
tracks["20"] = "Enterprise IT Strategies"
tracks["21"] = "Evaluating OpenStack"
tracks["22"] = "Architectural Decisions"
tracks["23"] = "Case Studies"
tracks["24"] = "Networking"
tracks["25"] = "Storage"
tracks["26"] = "Operations"
tracks["27"] = "Security"
tracks["28"] = "HPC / Research"
tracks["29"] = "Big Data"
tracks["30"] = "Cloud App Development"
tracks["31"] = "Containers"
tracks["32"] = "Telecom / NFV"
tracks["33"] = "Project Updates"
tracks["34"] = "How to Contribute"
tracks["35"] = "Upstream Development"
tracks["36"] = "Related OSS Projects"
tracks["37"] = "Cloudfunding"
tracks["38"] = "Products & Services"
tracks["39"] = "Community Building"
tracks["40"] = "Working Groups"
tracks["41"] = "Birds of a Feather"
tracks["42"] = "Hands-on Workshops"
tracks["43"] = "Other"
tracks["44"] = "Analyst"
tracks["45"] = "Sponsored Sessions"
tracks["46"] = "Keynotes"
tracks["47"] = "Intensive Training"
tracks["48"] = "#vBrownBag"
tracks["None"] = "Other"

FROM_FORMAT = "%Y-%m-%d %H:%M:%S"
TO_FORMAT = "%Y%m%dT%H%M%SZ"
CDT = pytz.timezone('US/Central')
UTC = pytz.timezone('utc')
TIMEDIFF = timedelta(hours=5)
UTCNOW = datetime.strftime(datetime.utcnow(), TO_FORMAT)

class MLStripper(HTMLParser):
    def __init__(self):
        self.reset()
        self.fed = []
    def handle_data(self, d):
        self.fed.append(d)
    def get_data(self):
        return ''.join(self.fed)

def strip_tags(html):
    if html is None:
        return ''
    s = MLStripper()
    s.feed(html)
    return s.get_data().replace('\\n', '').replace('\n', '')
      
main_cal = Calendar()
main_cal['version'] = '2.0'
main_cal['prodid'] = '-//yosshy/openstacksummitaustin2016//NONSGML v1.0//EN'
main_cal['summary'] = 'OpenStack Summit Austin 2016'

design_cal = Calendar()
design_cal['version'] = '2.0'
design_cal['prodid'] = '-//yosshy/openstackdesignsummitaustin2016//NONSGML v1.0//EN'
design_cal['summary'] = 'OpenStack Design Summit Austin 2016'

tracks_cal = {}
for key, value in tracks.items():
    tracks_cal[key] = Calendar()
    tracks_cal[key]['version'] = '2.0'
    tracks_cal[key]['prodid'] = '-//yosshy/openstackdesignsummitaustin2016//NONSGML v1.0//EN'
    tracks_cal[key]['summary'] = value

for i in range(24, 30):
    with codecs.open("04%d.json" % i, 'r', 'utf_8') as f:
        obj = json.load(f, 'utf_8')
        for event in obj.get('events'):
            ev = {}
            ev2 = Event()
            for k, v in event.items():
                if isinstance(v, basestring):
                    ev[k] = strip_tags(v)
                else:
                    ev[k] = v
            ev2['summary'] = strip_tags(event.get('title'))
            abst = event.get('abstract')
            if abst is not None:
                abst = pattern.sub('', abst)
                abst = abst.replace('\r\n', '')
                abst = abst.replace('\r', '')
                abst = abst.replace('<br />', '')
                #print(abst)
                ev2['description'] = strip_tags(abst)
            ev2['location'] = locations[str(event.get('location_id'))]
            dt = datetime.strptime(event['start_datetime'], FROM_FORMAT) + TIMEDIFF
            ev2['dtstart'] = datetime.strftime(dt, TO_FORMAT)
            dt = datetime.strptime(event['end_datetime'], FROM_FORMAT) + TIMEDIFF
            ev2['dtend'] = datetime.strftime(dt, TO_FORMAT)
            ev2['dtstamp'] = UTCNOW
            if 2 in event.get('summit_types_id', []):
                design_cal.add_component(ev2)
            elif 1 in event.get('summit_types_id', []):
                main_cal.add_component(ev2)
            track_id = str(event.get('track_id'))
            tracks_cal[track_id].add_component(ev2)
            

with open('austin_summit.ics', 'w') as f:
    f.write(main_cal.to_ical())

with open('austin_design_summit.ics', 'w') as f:
    f.write(design_cal.to_ical())


def get_filename(name):
    newname = name.replace(' ', '_')
    newname = re.sub(r'\W', '', name)
    return newname

for key, value in tracks.items():
    with open('austin_%s.ics' % get_filename(value), 'w') as f:
        f.write(tracks_cal[key].to_ical())
