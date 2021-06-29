#!/usr/bin/env python
# -*- coding: utf-8 -*-

# This file is part of phishnet-api-v4.
# https://github.com/jflaherty/phishnet-api-v4

# Licensed under the GPL v4 license:
# http://www.opensource.org/licenses/GPL v4-license
# Copyright (c) 2019, Jay Flaherty <jayflaherty@gmail.com>

import json
import pytest
import os

# local imports
from phishnet_api_v4.api_client import PhishNetAPI
from phishnet_api_v4.exceptions import ParamValidationError, PhishNetAPIError
from phishnet_api_v4 import __version__


def test_version():
    assert __version__ == '0.1.0'


class TestMockPhishNetAPI:
    '''
    These tests are live integration tests that will be run everytime pytest is run.
    They use request_mock to mock the REST API calls.
    '''

    def test_authorize(self, requests_mock):
        api = PhishNetAPI('apikey123456789test1')
        with open('tests/data/authority.json') as f:
            authority_json = json.load(f)
        requests_mock.post(api.base_url + "authority/get", json=authority_json)
        api.authorize(80, '123456789abcdefghij')
        assert api.uid == 80
        assert api.appid == 12345
        assert api.authkey == "B6386A2485D94C73DAA"

    def test_get_recent_blogs(self, requests_mock):
        api = PhishNetAPI('apikey123456789test1')
        with open('tests/data/recent_blogs.json') as f:
            recent_blogs_json = json.load(f)
        requests_mock.post(api.base_url + "blog/get", json=recent_blogs_json)
        blogs_response = api.get_recent_blogs()
        assert blogs_response['response']['count'] == 3
        assert len(blogs_response['response']['data']) == 3

    def test_get_blogs(self, requests_mock):
        api = PhishNetAPI('apikey123456789test1')
        with open('tests/data/recent_blogs.json') as f:
            get_blogs_json = json.load(f)
        requests_mock.post(api.base_url + "blog/get", json=get_blogs_json)

        blogs_response = api.get_blogs(year=2009)
        assert blogs_response['response']['count'] == 3
        assert len(blogs_response['response']['data']) == 3

        with pytest.raises(ParamValidationError):
            api.get_blogs(year=2008)
            api.get_blogs(year=2020)

    def test_get_artists(self, requests_mock):
        api = PhishNetAPI('apikey123456789test1')
        with open('tests/data/all_artists.json') as f:
            all_artists_json = json.load(f)
        requests_mock.post(api.base_url + "artists/all", json=all_artists_json)

        artists_response = api.get_artists()
        assert artists_response['response']['count'] == 5
        assert len(artists_response['response']['data']) == 5
        assert artists_response['response']['data']['1']['artistid'] == 1

    def test_get_show_attendees(self, requests_mock):
        api = PhishNetAPI('apikey123456789test1')
        with open('tests/data/show_attendees.json') as f:
            show_attendees_json = json.load(f)
        requests_mock.post(api.base_url + "attendance/get",
                           json=show_attendees_json)

        attendees_response = api.get_show_attendees(showdate='1991-07-19')
        assert attendees_response['response']['count'] == 53
        assert len(attendees_response['response']['data']) == 53
        with pytest.raises(ParamValidationError):
            api.get_show_attendees(showdate='1991-13-19')
            api.get_show_attendees(showdate='1982-12-19')
            api.get_show_attendees(showid=0)

    def test_update_show_attendance(self, requests_mock):
        api = PhishNetAPI('apikey123456789test1')
        api.authkey = 'B6386A2485D94C73DAA'
        api.uid = 80
        with open('tests/data/add_attendance.json') as f:
            add_attendance_json = json.load(f)
        requests_mock.post(api.base_url + "attendance/add",
                           json=add_attendance_json)

        update_attendance_response = api.update_show_attendance(
            api.uid, showid=1252691618, update='add')
        assert update_attendance_response['error_message'] == "Successfully added 1997-11-30"
        assert update_attendance_response['response']['data']['action'] == 'add'
        assert update_attendance_response['response']['data']['showdate'] == '1997-11-30'
        assert update_attendance_response['response']['data']['showid'] == 1252691618
        shows_seen = update_attendance_response['response']['data']['shows_seen']
        assert shows_seen == '63'

        with open('tests/data/remove_attendance.json') as f:
            remove_attendance_json = json.load(f)
        requests_mock.post(api.base_url + "attendance/remove",
                           json=remove_attendance_json)

        update_attendance_response = api.update_show_attendance(
            api.uid, showid=1252691618, update='remove')
        assert update_attendance_response['error_message'] == "Successfully removed 1997-11-30"
        assert update_attendance_response['response']['data']['action'] == 'remove'
        assert update_attendance_response['response']['data']['showdate'] == '1997-11-30'
        assert update_attendance_response['response']['data']['showid'] == 1252691618
        assert update_attendance_response['response']['data']['shows_seen'] == str(
            int(shows_seen) - 1)

    def test_query_collections(self, requests_mock):
        api = PhishNetAPI('apikey123456789test1')
        with open('tests/data/query_collection.json') as f:
            query_collection_json = json.load(f)
        requests_mock.post(api.base_url + "collections/query",
                           json=query_collection_json)

        collections_response = api.query_collections(uid=1)
        assert collections_response['response']['count'] == 7
        assert len(collections_response['response']['data']) == 7
        assert collections_response['response']['data'][0]['count'] == 2

    def test_get_collection(self, requests_mock):
        api = PhishNetAPI('apikey123456789test1')
        with open('tests/data/get_collection.json') as f:
            get_collection_json = json.load(f)
        requests_mock.post(api.base_url + "collections/get",
                           json=get_collection_json)

        collection_response = api.get_collection(1294148902)
        assert collection_response['response']['data']['show_count'] == 7
        assert len(
            collection_response['response']['data']['shows']) == 7

    def test_get_all_jamcharts(self, requests_mock):
        api = PhishNetAPI('apikey123456789test1')
        with open('tests/data/all_jamcharts.json') as f:
            all_jamcharts_json = json.load(f)
        requests_mock.post(api.base_url + "jamcharts/all",
                           json=all_jamcharts_json)

        jamcharts_response = api.get_all_jamcharts()
        assert jamcharts_response['response']['count'] == 5
        assert len(jamcharts_response['response']['data']) == 5
        assert jamcharts_response['response']['data'][0]['songid'] == '2'

    def test_get_jamchart(self, requests_mock):
        api = PhishNetAPI('apikey123456789test1')
        with open('tests/data/get_jamchart.json') as f:
            get_jamchart_json = json.load(f)
        requests_mock.post(api.base_url + "jamcharts/get",
                           json=get_jamchart_json)

        jamchart_response = api.get_jamchart(7)
        assert jamchart_response['response']['data']['songid'] == 7
        assert len(
            jamchart_response['response']['data']['entries']) == 7

    def test_get_all_people(self, requests_mock):
        api = PhishNetAPI('apikey123456789test1')
        with open('tests/data/all_people.json') as f:
            all_people_json = json.load(f)
        requests_mock.post(api.base_url + "people/all",
                           json=all_people_json)

        people_response = api.get_all_people()
        assert people_response['response']['count'] == 12
        assert len(people_response['response']['data']) == 12
        assert people_response['response']['data'][0]['personid'] == 5710

    def test_get_all_people_types(self, requests_mock):
        api = PhishNetAPI('apikey123456789test1')
        with open('tests/data/all_people_types.json') as f:
            all_people_types_json = json.load(f)
        requests_mock.post(api.base_url + "people/get",
                           json=all_people_types_json)

        people_types_response = api.get_all_people_types()
        assert people_types_response['response']['count'] == 9
        assert len(people_types_response['response']['data'].keys()) == 9
        assert people_types_response['response']['data']["1"] == "The Band"

    def test_get_appearances(self, requests_mock):
        api = PhishNetAPI('apikey123456789test1')
        with open('tests/data/get_appearances.json') as f:
            get_appearances_json = json.load(f)
        requests_mock.post(api.base_url + "people/appearances",
                           json=get_appearances_json)

        appearances_response = api.get_appearances(79)
        assert appearances_response['response']['count'] == 1
        assert len(appearances_response['response']['data']) == 1
        assert appearances_response['response']['data'][0]['personid'] == 79

        with pytest.raises(ParamValidationError):
            api.get_appearances(79, 1982)

    def test_get_relationships(self, requests_mock):
        api = PhishNetAPI('apikey123456789test1')
        with open('tests/data/get_relationships.json') as f:
            get_relationships_json = json.load(f)
        requests_mock.post(api.base_url + "relationships/get",
                           json=get_relationships_json)

        relationships_response = api.get_relationships(1)
        assert relationships_response['response']['count'] == 2
        assert len(relationships_response['response']['data'].keys()) == 2
        assert len(relationships_response['response']['data']["friends"].keys(
        )) == 13
        assert len(relationships_response['response']['data']["fans"].keys(
        )) == 13

    def test_query_reviews(self, requests_mock):
        api = PhishNetAPI('apikey123456789test1')
        with open('tests/data/query_reviews.json') as f:
            query_reviews_json = json.load(f)
        requests_mock.post(api.base_url + "reviews/query",
                           json=query_reviews_json)

        reviews_response = api.query_reviews(uid=1, showid=1394573037)
        assert reviews_response['response']['count'] == 1
        assert len(reviews_response['response']['data']) == 1
        assert reviews_response['response']['data'][0]['reviewid'] == 1375467602

    def test_get_setlist(self, requests_mock):
        api = PhishNetAPI('apikey123456789test1')
        with open('tests/data/latest_setlist.json') as f:
            get_setlist_json = json.load(f)
        requests_mock.post(api.base_url + "setlists/get",
                           json=get_setlist_json)

        setlist_response = api.get_setlist(showid=1252698446)
        assert setlist_response['response']['count'] == 1
        assert len(setlist_response['response']['data']) == 1
        assert setlist_response['response']['data'][0]['showid'] == 1252698446

        get_setlists_response = api.get_setlist(showdate='1997-12-29')
        assert get_setlists_response['response']['count'] == 1
        assert len(get_setlists_response['response']['data']) == 1
        assert get_setlists_response['response']['data'][0]['showid'] == 1252698446

    def test_get_latest_setlist(self, requests_mock):
        api = PhishNetAPI('apikey123456789test1')
        with open('tests/data/latest_setlist.json') as f:
            latest_setlist_json = json.load(f)
        requests_mock.post(api.base_url + "setlists/latest",
                           json=latest_setlist_json)

        latest_setlists_response = api.get_latest_setlist()
        assert latest_setlists_response['response']['count'] == 1
        assert len(latest_setlists_response['response']['data']) == 1
        assert latest_setlists_response['response']['data'][0]['showid'] == 1252698446

    def test_get_recent_setlists(self, requests_mock):
        api = PhishNetAPI('apikey123456789test1')
        with open('tests/data/recent_setlists.json') as f:
            get_recent_setlists_json = json.load(f)
        requests_mock.post(api.base_url + "setlists/recent",
                           json=get_recent_setlists_json)

        recent_setlists_response = api.get_recent_setlists()
        assert recent_setlists_response['response']['count'] == 10
        assert len(recent_setlists_response['response']['data']) == 10
        assert recent_setlists_response['response']['data'][0]['showid'] == 1470183033

    def test_get_tiph_setlist(self, requests_mock):
        api = PhishNetAPI('apikey123456789test1')
        with open('tests/data/tiph_setlist.json') as f:
            get_tiph_setlist_json = json.load(f)
        requests_mock.post(api.base_url + "setlists/tiph",
                           json=get_tiph_setlist_json)

        tiph_setlist_response = api.get_tiph_setlist()
        assert tiph_setlist_response['response']['count'] == 1
        assert len(tiph_setlist_response['response']['data']) == 1
        assert tiph_setlist_response['response']['data'][0]['showid'] == 1253165475

    def test_get_random_setlist(self, requests_mock):
        api = PhishNetAPI('apikey123456789test1')
        with open('tests/data/tiph_setlist.json') as f:
            get_random_setlist_json = json.load(f)
        requests_mock.post(api.base_url + "setlist/random",
                           json=get_random_setlist_json)

        random_setlist_response = api.get_random_setlist()
        assert random_setlist_response['response']['count'] == 1
        assert len(random_setlist_response['response']['data']) == 1
        assert random_setlist_response['response']['data'][0]['showid'] == 1253165475

    def test_get_show_links(self, requests_mock):
        api = PhishNetAPI('apikey123456789test1')
        with open('tests/data/get_show_links.json') as f:
            get_show_links_json = json.load(f)
        requests_mock.post(api.base_url + "shows/links",
                           json=get_show_links_json)

        show_links_response = api.get_show_links(1394573037)
        assert show_links_response['response']['count'] == 4
        assert len(show_links_response['response']['data']) == 4
        assert show_links_response['response']['data'][0]['type'] == "Photos"

    def test_get_upcoming_shows(self, requests_mock):
        api = PhishNetAPI('apikey123456789test1')
        with open('tests/data/get_upcoming_shows.json') as f:
            get_upcoming_shows_json = json.load(f)
        requests_mock.post(api.base_url + "shows/upcoming",
                           json=get_upcoming_shows_json)

        upcoming_shows_response = api.get_upcoming_shows()
        assert upcoming_shows_response['response']['count'] == 17
        assert len(upcoming_shows_response['response']['data']) == 17
        assert upcoming_shows_response['response']['data'][0]['showid'] == 1470182793

    def test_query_shows(self, requests_mock):
        api = PhishNetAPI('apikey123456789test1')
        with open('tests/data/query_shows.json') as f:
            query_shows_json = json.load(f)
        requests_mock.post(api.base_url + "shows/query",
                           json=query_shows_json)

        query_shows_response = api.query_shows(tourid=37)
        assert query_shows_response['response']['count'] == 14
        assert len(query_shows_response['response']['data']) == 14
        assert query_shows_response['response']['data'][0]['showid'] == 1252691618

        with pytest.raises(ParamValidationError):
            api.query_shows(year=1982)
        with pytest.raises(ParamValidationError):
            api.query_shows(month=13)
        with pytest.raises(ParamValidationError):
            api.query_shows(day=32)
        with pytest.raises(ParamValidationError):
            api.query_shows(showdate_gt=1982)

    def test_get_all_venues(self, requests_mock):
        api = PhishNetAPI('apikey123456789test1')
        with open('tests/data/all_venues.json') as f:
            all_venues_json = json.load(f)
        requests_mock.post(api.base_url + "venues/all", json=all_venues_json)

        venues_response = api.get_all_venues()
        assert venues_response['response']['count'] == 3
        assert len(venues_response['response']['data']) == 3
        assert venues_response['response']['data']['1']['venueid'] == 1

    def test_get_venue(self, requests_mock):
        api = PhishNetAPI('apikey123456789test1')
        with open('tests/data/get_venue.json') as f:
            get_venue_json = json.load(f)
        requests_mock.post(api.base_url + "venues/get", json=get_venue_json)

        venue_response = api.get_venue(1)
        assert venue_response['response']['count'] == 9
        assert venue_response['response']['data']['venueid'] == 1


# @pytest.mark.integration
class TestPhishNetAPI:
    '''
    These tests are live integration tests that require a valid apikey, appid, private_salt, and a 
    valid phish.net uid that has given authorization to run authorized api calls to api.phish.net
    for you application associated with the apikey. These are extracted from either OS environment 
    variables (APIKEY, APPID, PRIVATE_SALT, UID) or via a .env file at the root of this project 
    (see .env.SAMPLE for an example.) To run these test for this class pass --integration to pytest.
    '''

    def test_authorize(self):
        api = PhishNetAPI()
        api.authorize(os.getenv("UID"))

        assert api.uid == os.getenv("UID")
        assert api.apikey == os.getenv("APIKEY")
        assert api.appid == int(os.getenv("APPID"))
        assert api.private_salt == os.getenv("PRIVATE_SALT")
        assert 18 <= len(api.authkey) <= 19

    def test_get_recent_blogs(self):
        api = PhishNetAPI()
        blogs_response = api.get_recent_blogs()

        assert blogs_response['error_code'] == 0
        assert blogs_response['response']['count'] == len(
            blogs_response['response']['data'])

    def test_get_blogs(self):
        api = PhishNetAPI()
        blogs_response = api.get_blogs(year=2009)

        assert blogs_response['error_code'] == 0
        assert blogs_response['response']['count'] == len(
            blogs_response['response']['data'])

        with pytest.raises(ParamValidationError):
            api.get_blogs(year=2008)
            api.get_blogs(year=2020)

    def test_get_artists(self):
        api = PhishNetAPI()
        artists_response = api.get_artists()

        assert artists_response['error_code'] == 0
        assert artists_response['response']['count'] == len(
            artists_response['response']['data'])
        assert artists_response['response']['data']['1']['artistid'] == 1

    def test_get_show_attendees(self):
        api = PhishNetAPI()
        attendees_response = api.get_show_attendees(showdate='1991-07-19')

        assert attendees_response['error_code'] == 0
        assert attendees_response['response']['count'] == len(
            attendees_response['response']['data'])
        with pytest.raises(ParamValidationError):
            api.get_show_attendees(showdate='1991-13-19')
            api.get_show_attendees(showdate='1982-12-19')
            api.get_show_attendees(showid=0)

    def test_update_show_attendance(self):
        api = PhishNetAPI()
        api.uid = os.getenv('UID')
        update_attendance_response = api.update_show_attendance(
            api.uid, showid=1252691618, update='add')

        assert update_attendance_response['error_code'] == 0
        assert update_attendance_response['error_message'] == "Successfully added 1997-11-30"
        assert update_attendance_response['response']['data']['action'] == 'add'
        assert update_attendance_response['response']['data']['showdate'] == '1997-11-30'
        assert update_attendance_response['response']['data']['showid'] == 1252691618
        shows_seen_after_add = int(
            update_attendance_response['response']['data']['shows_seen'])

        update_attendance_response = api.update_show_attendance(
            api.uid, showid=1252691618, update='remove')

        assert update_attendance_response['error_code'] == 0
        assert update_attendance_response['error_message'] == "Successfully removed 1997-11-30"
        shows_seen_after_remove = int(
            update_attendance_response['response']['data']['shows_seen'])
        assert shows_seen_after_add > shows_seen_after_remove
        assert update_attendance_response['response']['data']['action'] == 'remove'
        assert update_attendance_response['response']['data']['showdate'] == '1997-11-30'
        assert update_attendance_response['response']['data']['showid'] == 1252691618

    def test_query_collections(self):
        api = PhishNetAPI()
        collections_response = api.query_collections(uid=1)

        assert collections_response['error_code'] == 0
        assert collections_response['response']['count'] == len(
            collections_response['response']['data'])

    def test_get_collection(self):
        api = PhishNetAPI()
        collection_response = api.get_collection(1294148902)

        assert collection_response['error_code'] == 0
        assert collection_response['response']['data']['show_count'] == len(
            collection_response['response']['data']['shows'])

    def test_get_all_jamcharts(self):
        api = PhishNetAPI()
        jamcharts_response = api.get_all_jamcharts()

        assert jamcharts_response['error_code'] == 0
        assert jamcharts_response['response']['count'] == len(
            jamcharts_response['response']['data'])

    def test_get_jamchart(self):
        api = PhishNetAPI()
        jamchart_response = api.get_jamchart(7)

        assert jamchart_response['error_code'] == 0
        assert jamchart_response['response']['data']['songid'] == 7
        assert jamchart_response['response']['count'] == len(
            jamchart_response['response']['data'])

    def test_get_all_people(self):
        api = PhishNetAPI()
        people_response = api.get_all_people()

        assert people_response['error_code'] == 0
        assert people_response['response']['count'] == len(
            people_response['response']['data'])

    def test_get_all_people_types(self):
        api = PhishNetAPI()
        people_types_response = api.get_all_people_types()

        assert people_types_response['error_code'] == 0
        assert people_types_response['response']['count'] == len(
            people_types_response['response']['data'].keys())
        assert people_types_response['response']['data']["1"] == "The Band"

    def test_get_appearances(self):
        api = PhishNetAPI()
        appearances_response = api.get_appearances(79)

        assert appearances_response['error_code'] == 0
        assert appearances_response['response']['count'] == len(
            appearances_response['response']['data'])
        assert appearances_response['response']['data'][0]['personid'] == 79

        with pytest.raises(ParamValidationError):
            api.get_appearances(79, 1982)

    def test_get_relationships(self):
        api = PhishNetAPI()
        relationships_response = api.get_relationships(1)

        assert relationships_response['error_code'] == 0
        assert relationships_response['response']['count'] == len(
            relationships_response['response']['data'].keys())

    def test_query_reviews(self):
        api = PhishNetAPI()
        reviews_response = api.query_reviews(showid=1394573037)

        assert reviews_response['error_code'] == 0
        assert reviews_response['response']['count'] == len(
            reviews_response['response']['data'])

    def test_get_latest_setlist(self):
        api = PhishNetAPI()
        latest_setlist_response = api.get_latest_setlist()

        assert latest_setlist_response['error_code'] == 0
        assert latest_setlist_response['response']['count'] == len(
            latest_setlist_response['response']['data'])

    def test_get_setlist(self):
        api = PhishNetAPI()
        setlist_response = api.get_setlist(showid=1252698446)

        assert setlist_response['error_code'] == 0
        assert setlist_response['response']['count'] == 1
        assert len(setlist_response['response']['data']) == 1
        assert setlist_response['response']['data'][0]['showid'] == 1252698446
        assert setlist_response['response']['data'][0]['showdate'] == '1997-12-29'
        assert setlist_response['response']['data'][0]['rating'] == '4.5907'
        assert setlist_response['response']['data'][0]['location'] == 'New York, NY, USA'

        get_setlists_response = api.get_setlist(showdate='1997-12-29')

        assert setlist_response['error_code'] == 0
        assert get_setlists_response['response']['count'] == 1
        assert len(get_setlists_response['response']['data']) == 1
        assert get_setlists_response['response']['data'][0]['showid'] == 1252698446
        assert setlist_response['response']['data'][0]['showdate'] == '1997-12-29'
        assert setlist_response['response']['data'][0]['rating'] == '4.5907'
        assert setlist_response['response']['data'][0]['location'] == 'New York, NY, USA'

    def test_get_recent_setlists(self):
        api = PhishNetAPI()
        recent_setlists_response = api.get_recent_setlists()

        assert recent_setlists_response['error_code'] == 0
        assert recent_setlists_response['response']['count'] == 10
        assert len(recent_setlists_response['response']['data']) == 10

    def test_get_tiph_setlist(self):
        api = PhishNetAPI()
        tiph_setlist_response = api.get_tiph_setlist()

        assert tiph_setlist_response['error_code'] == 0
        assert tiph_setlist_response['response']['count'] == 1
        assert len(tiph_setlist_response['response']['data']) == 1

    def test_get_random_setlist(self):
        api = PhishNetAPI()
        random_setlist_response = api.get_random_setlist()

        assert random_setlist_response['error_code'] == 0
        assert random_setlist_response['response']['count'] == 1
        assert len(random_setlist_response['response']['data']) == 1

    def test_get_show_links(self):
        api = PhishNetAPI()
        show_links_response = api.get_show_links(1394573037)

        assert show_links_response['error_code'] == 0
        assert show_links_response['response']['count'] == len(
            show_links_response['response']['data'])

    def test_get_upcoming_shows(self):
        api = PhishNetAPI()
        upcoming_shows_response = api.get_upcoming_shows()

        assert upcoming_shows_response['error_code'] == 0
        assert upcoming_shows_response['response']['count'] == len(
            upcoming_shows_response['response']['data'])

    def test_query_shows(self):
        api = PhishNetAPI()
        query_shows_response = api.query_shows(month=3, day=19)

        assert query_shows_response['error_code'] == 0
        assert query_shows_response['response']['count'] == 21
        assert len(query_shows_response['response']['data']) == 21
        assert query_shows_response['response']['data'][0]['showid'] == 1252697421

        with pytest.raises(ParamValidationError):
            api.query_shows(year=1982)
        with pytest.raises(ParamValidationError):
            api.query_shows(month=13)
        with pytest.raises(ParamValidationError):
            api.query_shows(day=32)
        with pytest.raises(ParamValidationError):
            api.query_shows(showdate_gt=1982)

    def test_get_all_venues(self):
        api = PhishNetAPI()
        venues_response = api.get_all_venues()

        assert venues_response['error_code'] == 0
        assert venues_response['response']['count'] == len(
            venues_response['response']['data'])
        assert venues_response['response']['data']['1']['venueid'] == 1

    def test_get_venue(self):
        api = PhishNetAPI()
        venue_response = api.get_venue(1)

        assert venue_response['error_code'] == 0
        assert venue_response['response']['count'] == 9
        assert venue_response['response']['data']['venueid'] == 1

    def test_get_user_details(self):
        api = PhishNetAPI()
        response = api.get_user_details(os.getenv('UID'))
        assert response['response']['count'] == 1
