#! /usr/bin/env python
# -*- coding: utf-8 -*-
#
# Copyright Tim Henning 2014

from datetime import datetime, timedelta, date
from googleapiclient.discovery import build
from oauth2client.client import OAuth2WebServerFlow
from oauth2client.file import Storage
from oauth2client.tools import run_flow, argparser
import argparse
import httplib2
import inspect
import os
import pickle
import sys
import time

OAUTH2_CLIENT_ID = "326208479597-m597jdm6r5g422g84tc0qf74m08nstuo.apps.googleusercontent.com"
OAUTH2_CLIENT_SECRET = "fApsUPyvfpeP-hQY_q7ijWu6"

CALENDAR_HOTWORDS = ("college", "university", "school",
                     "schule", "studium",
                     u"école", "ecole", u"collège", u"études", "etudes")

class GoogleCalendarBackend():
    """ Calendar backend for Google Calendar. Uses OAuth2.0. """
    def __init__(self):
        self.script_dir = self.get_script_dir()
        self.calendar_service = None
        self.calendar_id = None
        self.authentication_tried = False
    
    def get_script_dir(self, follow_symlinks=True):
        if getattr(sys, 'frozen', False): # py2exe, PyInstaller, cx_Freeze
            path = os.path.abspath(sys.executable)
        else:
            path = inspect.getabsfile(self.get_script_dir)
        if follow_symlinks:
            path = os.path.realpath(path)
        path = os.path.dirname(path)
        if os.path.isfile(path):
            return path
        else:
            return ""
    
    def authenticate(self):
        self.authentication_tried = True
        try:
            self.calendar_service = self.get_calendar_service_object()
            self.calendar_id = self.get_calendar_id()
        except Exception as e:
            print e
            self.calendar_service = None
            self.calendar_id = None
    
    def get_calendar_service_object(self):
        flow = OAuth2WebServerFlow(
            client_id=OAUTH2_CLIENT_ID,
            client_secret=OAUTH2_CLIENT_SECRET,
            scope='https://www.googleapis.com/auth/calendar',
            user_agent='Scholaris/0.1')
        
        storage = Storage('calendar.dat')
        credentials = storage.get()
        if credentials is None or credentials.invalid:
            parser = argparse.ArgumentParser(parents=[argparser])
            flags = parser.parse_args()
            credentials = run_flow(flow, storage, flags)
        
        http = httplib2.Http(disable_ssl_certificate_validation=True)
        http = credentials.authorize(http)
        
        service = build(serviceName='calendar', version='v3', http=http)
        return service
    
    def logout(self):
        try:
            Storage('calendar.dat').delete()
            path = os.path.join(self.script_dir, "event_cache")
            if os.path.isfile(path):
                os.remove(path)
        except Exception as e:
            print e
    
    def get_calendar_id(self):
        """ Tries to guess the calendar containing timetable like events by hotwords. """
        if not self.authentication_tried:
            self.authenticate()
        service = self.calendar_service
        if not service:
            return ""
        response = service.calendarList().list(fields="items/summary,items/id").execute()
        if not response.has_key("items"):
            return None
        print 'Found %d calendars:' % len(response['items'])
        for i, calendar in enumerate(response['items']):
            print "{:d}: {} (ID: {})".format(i, calendar["summary"], calendar["id"])
        for calendar in response['items']:
            for hotword in CALENDAR_HOTWORDS:
                if hotword in calendar["summary"].lower():
                    print "Chose: {}".format(calendar["summary"])
                    return calendar["id"]
        print "Chose: {}".format(response['items'][0]["summary"])
        return response['items'][0]["id"]
    
    def get_events_today(self):
        path = os.path.join(self.script_dir, "event_cache")
        if not os.path.isfile(path):
            return self.get_events_from_day(date.today())
        try:
            file_object = open(path, 'r')
            content = pickle.load(file_object)
            file_object.close()
        except IOError:
            print "Error while reading file {}.".format(path)
            return self.get_events_from_day(datetime.now())
        file_date, events = content
        if file_date == date.today():
            print "Successfully read events from cache."
            return events
        else:
            return self.get_events_from_day(date.today())
    
    def get_events_from_day(self, day):
        if not self.authentication_tried:
            self.authenticate()
        if not self.calendar_service or not self.calendar_id:
            return []
        timeMin = (datetime(year=day.year, month=day.month, day=day.day)).isoformat() + "Z"
        timeMax = (datetime(year=day.year, month=day.month, day=day.day) + timedelta(days=1)).isoformat() + "Z"
        response = self.calendar_service.events().list(fields="items/summary,items/start,items/end,items/id,items/description,items/location", calendarId=self.calendar_id, orderBy="startTime", singleEvents=True, timeMin=timeMin, timeMax=timeMax, maxResults=100).execute()
        if not response.has_key("items"):
            self.update_cache([])
            return []
        self.update_cache(response["items"])
        return response["items"]
    
    def update_cache(self, events):
        path = os.path.join(self.script_dir, "event_cache")
        content = (date.today(), events)
        try:
            file_object = open(path, 'w')
            pickle.dump(content, file_object)
            file_object.close()
        except IOError:
            print "Could not write to file %s." % path
            return False
        print "Successfully updated event cache."
    
    def get_current_situation(self):
        events = self.get_simple_events(self.get_events_today())
        if len(events) < 1:
            return Situation(None, None, None)
        events = self.sort_events(events)
        now = time.time()
        if events[0].start > now:
            return Situation(None, None, events[0])
        if events[-1].end < now:
            return Situation(events[-1], None, None)
        if len(events) == 1:
            if events[0].end < now:
                return Situation(events[0], None, None)
            return Situation(None, events[0], None)
        if events[0].start < now and events[0].end > now:
            return Situation(None, events[0], events[1])
        if events[-1].start < now and events[-1].end > now:
            return Situation(events[-2], events[-1], None)
        for i in xrange(1, len(events)):
            if events[i].start > now:
                return Situation(events[i-1], None, events[i])
            if events[i].end > now:
                return Situation(events[i-1], events[i], events[i+1])
        print "Could not get current situation."
        return Situation(None, None, None)
    
    def get_simple_events(self, events):
        return [SimpleEvent().from_google_event(event) for event in events]
    
    def sort_events(self, events):
        changed = True
        while changed:
            changed = False
            for i in xrange(len(events) -1):
                if events[i].start > events[i+1].start:
                    changed = True
                    temp = events[i+1]
                    events[i+1] = events[i]
                    events[i] = temp
        return events

class Situation():
    """ Represents the current situation with last, current and next event. """
    def __init__(self, last=None, current=None, next_=None):
        self.last = last
        self.current = current
        self.next = next_
    
    def is_freetime(self):
        return not self.current and not self.next
    
    def relative_position_available(self):
        return self.current or (self.last and self.next)
    
    def get_current_length(self):
        if self.current:
            return self.current.end - self.current.start
        if self.last and self.next:
            return self.next.start - self.last.end
        return 0
    
    def has_last_break(self):
        return self.last and self.current
    
    def has_next_break(self):
        return self.current and self.next
    
    def get_last_break_length(self):
        return self.current.start - self.last.end
    
    def get_next_break_length(self):
        return self.next.start - self.current.end

class SimpleEvent():
    """ Represents an event with title, start, end, description and location. """
    def __init__(self, title="", start=0, end=0, description="", location="", google_id=""):
        self.title = title
        self.description = description
        self.start = start
        self.end = end
        self.location = location
        self.google_id = google_id
    
    def from_google_event(self, event):
        self.title = event["summary"]
        self.start = self.convert_isodate_to_seconds(event["start"]["dateTime"], ignore_tz=True)
        self.end = self.convert_isodate_to_seconds(event["end"]["dateTime"], ignore_tz=True)
        self.description = event.get("description", "")
        self.location = event.get("location", "")
        self.google_id = event["id"]
        return self
    
    def convert_isodate_to_seconds(self, ts, ignore_tz=False):
        """Takes ISO 8601 format(string) and converts into epoch time."""
        if ignore_tz:
            dt = datetime.strptime(ts[:-7],'%Y-%m-%dT%H:%M:%S')
        else:
            dt = datetime.strptime(ts[:-7],'%Y-%m-%dT%H:%M:%S')+\
                        timedelta(hours=int(ts[-5:-3]),
                        minutes=int(ts[-2:]))*int(ts[-6:-5]+'1')
        seconds = time.mktime(dt.timetuple())# + dt.microsecond/1000000.0
        return seconds
    
    def __repr__(self):
        return "{} - {}: {}".format(datetime.fromtimestamp(self.start), datetime.fromtimestamp(self.end), self.title)
