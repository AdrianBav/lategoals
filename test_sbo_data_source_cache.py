#!/usr/local/bin/python3.2
# coding: utf-8
# pylint: disable-msg=C0302

"""This module tests the sbo_data_source_cache module."""

import unittest
import debug
import debug_flags

# Test specific imports.
import datetime
from data_source_base import DataSourceBase

# The class under test.
from sbo_data_source_cache import SboDataSourceCache

# Individual tests can be skipped by setting the appropriate flag.
SKIP_TEST_01 = False
SKIP_TEST_02 = False
SKIP_TEST_03 = False
SKIP_TEST_04 = False
SKIP_TEST_05 = False
SKIP_TEST_06 = False
SKIP_TEST_07 = False
SKIP_TEST_08 = False
SKIP_TEST_09 = False
SKIP_TEST_10 = False
SKIP_TEST_11 = False
SKIP_TEST_12 = False
SKIP_TEST_13 = False
SKIP_TEST_14 = False

# SBO betting site details.
SBO_ID = 2
GMT_OFFSET = 8

# Data frames.
LIVE_DATA_FRAME = 0
NON_LIVE_DATA_FRAME = 1
FRAME_TYPE_DESCRIPTION = ['live', 'non-live']
NUMBER_OF_FRAMES = 2

# Update Cache result indexes.
CREATED_EVENTS = 0
UPDATED_EVENTS = 1
DELETED_EVENTS = 2


class TestSboDataSourceCache(unittest.TestCase): # pylint: disable-msg=R0904

    """This class tests the SboDataSourceCache class."""

    # A list of types for testing.
    test_types = [
        None,                   # 01 None.
        False,                  # 02 Boolean.
        0,                      # 03 Numeric type; Integer.
        0.0,                    # 04 Numeric type; Floating point.
        0j,                     # 05 Numeric type; Complex number.
        '',                     # 06 Empty sequence; String.
        (),                     # 07 Empty sequence; Tuple.
        [],                     # 08 Empty sequence; List.
        {},                     # 09 Empty mapping; Dictionary.
        set(),                  # 10 Empty Set.
        float('NaN'),           # 11 Not a number.
        float('inf')            # 12 Infinity.
    ]


    @classmethod
    def setUpClass(cls): # pylint: disable-msg=C0103

        """This method is executed once at the start of this Unit Test."""

        debug.message(debug_flags.TEST_SBO_DATA_SOURCE_CACHE, debug.TESTUNIT, "STARTING %s..." % TestSboDataSourceCache.__name__)

        # Create two instances of SboDataSourceCache class, one for each frame type.
        live_cache = SboDataSourceCache(LIVE_DATA_FRAME, SBO_ID, GMT_OFFSET)
        non_live_cache = SboDataSourceCache(NON_LIVE_DATA_FRAME, SBO_ID, GMT_OFFSET)

        cls.sbo_data_source_cache = [live_cache, non_live_cache]


    def _populate_cache(self, frame_type):

        """This method populates the cache with the default data set."""

        debug.message(debug_flags.TEST_SBO_DATA_SOURCE_CACHE_EXTRA, debug.TESTUNIT, "STARTING %s:" % "_populate_cache")

        tournaments = [
            [307,'Torneo Viareggio','',''],
            [3868,'Bahrain Premier League','','']
        ]
        events = [
            [1193897,1,307,'Torino U19','AS Roma U19','1.374',10,'02/19/2013 22:00',1,'',5],
            [1193898,1,307,'Juventus U19','Juve Stabia U19','1.377',10,'02/19/2013 22:00',1,'',3],
            [1193902,1,307,'Lazio U19','Anderlecht U19','1.389',10,'02/19/2013 22:00',1,'',3],
            [1195114,1,3868,'Muharraq','Busaiteen','1.407',10,'02/19/2013 23:00',1,'',6]
        ]
        event_results = [
            [189006,1193897,0,1,1,4],
            [190850,1193897,126,2,3,1],
            [189007,1193898,0,0,1,3],
            [189011,1193902,0,0,0,3],
            [190800,1195114,0,0,0,6]
        ]
        event_result_extra = [
            [189006,1,2,20,45,0,0,0],
            [190850,1,2,20,45,0,0,0],
            [189007,1,2,12,45,1,0,0],
            [189011,1,2,10,45,0,0,0],
            [190800,1,1,12,45,0,0,0]
        ]
        event_results_to_delete = [
        ]
        odds = [
            [12800915,[189006,1,1,1000.00,0.25],[2.2,1.67]],
            [12800917,[189006,3,1,1000.00,2.75],[1.77,2.05]],
            [12800919,[189006,5,1,500.00,0],[2.85,1.94,3.95]],
            [12800920,[190850,3,1,400.00,12.00],[3.55,6.65]],
            [12800934,[189007,1,1,2000.00,0.25],[2.09,1.75]],
            [12800936,[189007,3,1,2000.00,1.75],[1.72,2.11]],
            [12800938,[189007,5,1,500.00,0],[9.5,2.9,1.5]],
            [12801010,[189011,1,1,2000.00,0.25],[2.16,1.7]],
            [12801012,[189011,3,1,2000.00,1.25],[2.07,1.75]],
            [12801014,[189011,5,1,500.00,0],[2.59,2.14,3.75]],
            [12816830,[190800,1,1,1000.00,0.00],[1.68,2.25]],
            [12816832,[190800,3,1,1000.00,2.25],[2.01,1.85]],
            [12816834,[190800,5,1,500.00,0],[2.21,3,3]],
            [12816831,[190800,7,1,500.00,0.00],[1.77,2.12]],
            [12816835,[190800,8,1,500.00,0],[3.15,1.86,3.75]],
            [12816833,[190800,9,1,500.00,0.75],[1.8,2.06]]
        ]
        odds_to_delete = [
        ]
        market_groups = [
            [126,'Total Corners','_{home}_','_{away}_',1,0,0],
            [128,'Total Goals','_{home}_','_{away}_',1,0,0]
        ]

        # Clear any existing data from the cache before populating with the default data set.
        self.sbo_data_source_cache[frame_type].clear_cache()

        frame_cache_data = [tournaments, events, event_results, event_result_extra, event_results_to_delete, odds, odds_to_delete, market_groups]
        update_cache_result = self.sbo_data_source_cache[frame_type].update_cache(frame_cache_data)

        return update_cache_result


    @unittest.skipIf(SKIP_TEST_01, "in development")
    def test_01_object_creation(self):

        """Test the class initialiser method."""

        debug.message(debug_flags.TEST_SBO_DATA_SOURCE_CACHE, debug.TESTUNIT, "STARTING %s:" % "test_01_object_creation")

        # Test both instances of the class.
        for frame_type in range(NUMBER_OF_FRAMES):

            debug.message(debug_flags.TEST_SBO_DATA_SOURCE_CACHE_EXTRA, debug.TESTUNIT, "Testing %s data frame..." % FRAME_TYPE_DESCRIPTION[frame_type])

            # A: Test that the instantiation of the class was successful.
            actual_object = self.sbo_data_source_cache[frame_type]
            expected_class = SboDataSourceCache
            self.assertIsInstance(actual_object, expected_class, "[A] The tested object is not an instance of the SboDataSourceCache class.")

            # B: Test that the Tournament Dictionary is of the correct type and empty.
            actual_result = self.sbo_data_source_cache[frame_type].tournament_dictionary
            expected_result = {}
            self.assertDictEqual(actual_result, expected_result, "[B] The actual result doesn't match the expected result.")

            # C: Test that the Event Dictionary is of the correct type and empty.
            actual_result = self.sbo_data_source_cache[frame_type].event_dictionary
            expected_result = {}
            self.assertDictEqual(actual_result, expected_result, "[C] The actual result doesn't match the expected result.")

            # D: Test that the Event Result Dictionary is of the correct type and empty.
            actual_result = self.sbo_data_source_cache[frame_type].event_result_dictionary
            expected_result = {}
            self.assertDictEqual(actual_result, expected_result, "[D] The actual result doesn't match the expected result.")

            # E: Test that the Event Result Extra Dictionary is of the correct type and empty.
            actual_result = self.sbo_data_source_cache[frame_type].event_result_extra_dictionary
            expected_result = {}
            self.assertDictEqual(actual_result, expected_result, "[E] The actual result doesn't match the expected result.")

            # F: Test that the Odds Dictionary is of the correct type and empty.
            actual_result = self.sbo_data_source_cache[frame_type].odds_dictionary
            expected_result = {}
            self.assertDictEqual(actual_result, expected_result, "[F] The actual result doesn't match the expected result.")

            # G: Test that the Market Group Dictionary is of the correct type and empty.
            actual_result = self.sbo_data_source_cache[frame_type].market_group_dictionary
            expected_result = {}
            self.assertDictEqual(actual_result, expected_result, "[G] The actual result doesn't match the expected result.")


    @unittest.skipIf(SKIP_TEST_02, "in development")
    def test_02_clear_cache(self):

        """Test the method for updating the cache can handle invalid inputs and that it returns the correct structure."""

        debug.message(debug_flags.TEST_SBO_DATA_SOURCE_CACHE, debug.TESTUNIT, "STARTING %s:" % "test_02_clear_cache")

        # Fill the some of the Dictionaries with data.
        self.sbo_data_source_cache[LIVE_DATA_FRAME].tournament_dictionary = {307: 'Torneo Viareggio', 3868: 'Bahrain Premier League'}
        self.sbo_data_source_cache[LIVE_DATA_FRAME].event_dictionary = {
            1193897: {'home_team_name': 'Torino U19', 'show_time': '02/19/2013 22:00', 'event_sort_code': '1.374', 'away_team_name': 'AS Roma U19', 'show_time_type': 10, 'tornament_id': 307}
        }

        # A: Test that the Tournament Dictionary is not empty.
        actual_result = self.sbo_data_source_cache[LIVE_DATA_FRAME].tournament_dictionary
        unexpected_result = {}
        self.assertIsNot(actual_result, unexpected_result, "[A] The actual result matches the unexpected result.")

        # B: Test that the Event Dictionary is not empty.
        actual_result = self.sbo_data_source_cache[LIVE_DATA_FRAME].event_dictionary
        unexpected_result = {}
        self.assertIsNot(actual_result, unexpected_result, "[B] The actual result matches the unexpected result.")

        # Call the Clear Cache method.
        self.sbo_data_source_cache[LIVE_DATA_FRAME].clear_cache()

        # C: Test that the Tournament Dictionary is empty.
        actual_result = self.sbo_data_source_cache[LIVE_DATA_FRAME].tournament_dictionary
        expected_result = {}
        self.assertDictEqual(actual_result, expected_result, "[C] The actual result doesn't match the expected result.")

        # D: Test that the Event Dictionary is empty.
        actual_result = self.sbo_data_source_cache[LIVE_DATA_FRAME].event_dictionary
        expected_result = {}
        self.assertDictEqual(actual_result, expected_result, "[D] The actual result doesn't match the expected result.")


    @unittest.skipIf(SKIP_TEST_03, "in development")
    def test_03_update_cache(self):

        """Test the method for updating the cache can handle invalid inputs and that it returns the correct structure."""

        debug.message(debug_flags.TEST_SBO_DATA_SOURCE_CACHE, debug.TESTUNIT, "STARTING %s:" % "test_03_update_cache")

        # A: Test that the method can cope with invalid frame cache data types by raising an exception.
        for number, invalid_frame_cache_data in enumerate(self.test_types, start=1):

            debug.message(debug_flags.TEST_SBO_DATA_SOURCE_CACHE_EXTRA, debug.TESTUNIT, "Testing frame cache data with invalid type %s of %s." % (number, len(self.test_types)))
            self.assertRaises(SboDataSourceCache.UnexpectedDataError, self.sbo_data_source_cache[LIVE_DATA_FRAME].update_cache, invalid_frame_cache_data)

        # Frame Cache Data is a list of data retrieved from the SBO server.
        # Start by sending an empty list and checking the return structure is as expected.
        empty_frame_cache_data = [None, None, None, None, None, None, None, None]
        update_cache_result = self.sbo_data_source_cache[LIVE_DATA_FRAME].update_cache(empty_frame_cache_data)

        # B: Test that the result of the cache update is a tuple.
        actual_type = update_cache_result
        expected_type = tuple
        self.assertIsInstance(actual_type, expected_type, "[B] The actual result is not of the expected type.")

        # C: Test that the tuple has a length of 3.
        actual_result = len(update_cache_result)
        expected_result = 3
        self.assertEqual(actual_result, expected_result, "[C] The actual result doesn't match the expected result.")

        # D: Test that the first element is an empty list.
        actual_result = update_cache_result[0]
        expected_result = []
        self.assertListEqual(actual_result, expected_result, "[D] The actual result doesn't match the expected result.")

        # E: Test that the second element is an empty dictionary.
        actual_result = update_cache_result[1]
        expected_result = {}
        self.assertDictEqual(actual_result, expected_result, "[E] The actual result doesn't match the expected result.")

        # F: Test that the third element is an empty list.
        actual_result = update_cache_result[2]
        expected_result = []
        self.assertListEqual(actual_result, expected_result, "[F] The actual result doesn't match the expected result.")


    @unittest.skipIf(SKIP_TEST_04, "in development")
    def test_04_update_cache_tournaments(self):

        """Test the updating of cached Tournament data."""

        debug.message(debug_flags.TEST_SBO_DATA_SOURCE_CACHE, debug.TESTUNIT, "STARTING %s:" % "test_04_update_cache_tournaments")

        # A: Test that the method can cope with invalid tournament data types by raising an exception.
        for number, invalid_tournament_data in enumerate(self.test_types, start=1):

            # Skip the Test types numbered 1 and 6 to 10 as these are as valid parameters for tournament data.
            if number == 1 or number in range(6, 11):
                continue

            frame_cache_data = [invalid_tournament_data, None, None, None, None, None, None, None]

            debug.message(debug_flags.TEST_SBO_DATA_SOURCE_CACHE_EXTRA, debug.TESTUNIT, "Testing tournament data with invalid type %s of %s." % (number, len(self.test_types)))
            self.assertRaises(SboDataSourceCache.UnexpectedDataError, self.sbo_data_source_cache[LIVE_DATA_FRAME].update_cache, frame_cache_data)

        # B: Test that the method can cope with invalid Tournament data types by raising an exception.
        invalid_tournament_data = [None, None, None]
        frame_cache_data = [invalid_tournament_data, None, None, None, None, None, None, None]
        self.assertRaises(SboDataSourceCache.UnexpectedDataError, self.sbo_data_source_cache[LIVE_DATA_FRAME].update_cache, frame_cache_data)

        # C: Test that the method can cope with invalid Tournament data types by raising an exception.
        invalid_tournament_data = [
            [307],
            [3868],
            [0]
        ]
        frame_cache_data = [invalid_tournament_data, None, None, None, None, None, None, None]
        self.assertRaises(SboDataSourceCache.UnexpectedDataError, self.sbo_data_source_cache[LIVE_DATA_FRAME].update_cache, frame_cache_data)

        # D: Test that the Tournament Dictionary is empty.
        actual_result = self.sbo_data_source_cache[LIVE_DATA_FRAME].tournament_dictionary
        expected_result = {}
        self.assertDictEqual(actual_result, expected_result, "[D] The actual result doesn't match the expected result.")

        # Update the cache with some valid Tournament data.
        tournaments = [
            [307,'Torneo Viareggio','',''],
            [3868,'Bahrain Premier League','','']
        ]
        frame_cache_data = [tournaments, None, None, None, None, None, None, None]
        self.sbo_data_source_cache[LIVE_DATA_FRAME].update_cache(frame_cache_data)

        # E: Test that the Tournament Dictionary contains the expected data.
        actual_result = self.sbo_data_source_cache[LIVE_DATA_FRAME].tournament_dictionary
        expected_result = {307: 'Torneo Viareggio', 3868: 'Bahrain Premier League'}
        self.assertDictEqual(actual_result, expected_result, "[E] The actual result doesn't match the expected result.")


    @unittest.skipIf(SKIP_TEST_05, "in development")
    def test_05_update_cache_events(self):

        """Test the updating of cached event data."""

        debug.message(debug_flags.TEST_SBO_DATA_SOURCE_CACHE, debug.TESTUNIT, "STARTING %s:" % "test_05_update_cache_events")

        # A: Test that the method can cope with invalid Event data types by raising an exception.
        for number, invalid_event_data in enumerate(self.test_types, start=1):

            # Skip the Test types numbered 1 and 6 to 10 as these are as valid parameters for Event data.
            if number == 1 or number in range(6, 11):
                continue

            frame_cache_data = [None, invalid_event_data, None, None, None, None, None, None]

            debug.message(debug_flags.TEST_SBO_DATA_SOURCE_CACHE_EXTRA, debug.TESTUNIT, "Testing event data with invalid type %s of %s." % (number, len(self.test_types)))
            self.assertRaises(SboDataSourceCache.UnexpectedDataError, self.sbo_data_source_cache[LIVE_DATA_FRAME].update_cache, frame_cache_data)

        # B: Test that the method can cope with invalid Event data types by raising an exception.
        invalid_event_data = [None, None, None]
        frame_cache_data = [None, invalid_event_data, None, None, None, None, None, None]
        self.assertRaises(SboDataSourceCache.UnexpectedDataError, self.sbo_data_source_cache[LIVE_DATA_FRAME].update_cache, frame_cache_data)

        # C: Test that the method can cope with invalid Event data types by raising an exception.
        invalid_event_data = [
            [1193897],
            [1193898],
            [0]
        ]
        frame_cache_data = [None, invalid_event_data, None, None, None, None, None, None]
        self.assertRaises(SboDataSourceCache.UnexpectedDataError, self.sbo_data_source_cache[LIVE_DATA_FRAME].update_cache, frame_cache_data)

        # D: Test that the Event Dictionary is empty.
        actual_result = self.sbo_data_source_cache[LIVE_DATA_FRAME].event_dictionary
        expected_result = {}
        self.assertDictEqual(actual_result, expected_result, "[D] The actual result doesn't match the expected result.")

        # Update the cache with valid Event data.
        events = [
            [1193897,1,307,'Torino U19','AS Roma U19','1.374',10,'02/19/2013 22:00',1,'',3],
            [1193898,1,307,'Juventus U19','Juve Stabia U19','1.377',10,'02/19/2013 22:00',1,'',3],
            [1193902,1,307,'Lazio U19','Anderlecht U19','1.389',10,'02/19/2013 22:00',1,'',3],
            [1195114,1,3868,'Muharraq','Busaiteen','1.407',10,'02/19/2013 23:00',1,'',6]
        ]
        frame_cache_data = [None, events, None, None, None, None, None, None]
        self.sbo_data_source_cache[LIVE_DATA_FRAME].update_cache(frame_cache_data)

        # E: Test that the Event Dictionary contains the expected data.
        actual_result = self.sbo_data_source_cache[LIVE_DATA_FRAME].event_dictionary
        expected_result = {
            1193897: {'home_team_name': 'Torino U19', 'show_time': '02/19/2013 22:00', 'event_sort_code': '1.374', 'away_team_name': 'AS Roma U19', 'show_time_type': 10, 'tornament_id': 307},
            1193898: {'home_team_name': 'Juventus U19', 'show_time': '02/19/2013 22:00', 'event_sort_code': '1.377', 'away_team_name': 'Juve Stabia U19', 'show_time_type': 10, 'tornament_id': 307},
            1193902: {'home_team_name': 'Lazio U19', 'show_time': '02/19/2013 22:00', 'event_sort_code': '1.389', 'away_team_name': 'Anderlecht U19', 'show_time_type': 10, 'tornament_id': 307},
            1195114: {'home_team_name': 'Muharraq', 'show_time': '02/19/2013 23:00', 'event_sort_code': '1.407', 'away_team_name': 'Busaiteen', 'show_time_type': 10, 'tornament_id': 3868}
        }
        self.assertDictEqual(actual_result, expected_result, "[E] The actual result doesn't match the expected result.")


    @unittest.skipIf(SKIP_TEST_06, "in development")
    def test_06_update_cache_event_results(self): # pylint: disable-msg=C0103

        """Test the updating of cached event result data."""

        debug.message(debug_flags.TEST_SBO_DATA_SOURCE_CACHE, debug.TESTUNIT, "STARTING %s:" % "test_06_update_cache_event_results")

        # A: Test that the method can cope with invalid Event Result data types by raising an exception.
        for number, invalid_event_result_data in enumerate(self.test_types, start=1):

            # Skip the Test types numbered 1 and 6 to 10 as these are as valid parameters for Event Result data.
            if number == 1 or number in range(6, 11):
                continue

            frame_cache_data = [None, None, invalid_event_result_data, None, None, None, None, None]

            debug.message(debug_flags.TEST_SBO_DATA_SOURCE_CACHE_EXTRA, debug.TESTUNIT, "Testing event result data with invalid type %s of %s." % (number, len(self.test_types)))
            self.assertRaises(SboDataSourceCache.UnexpectedDataError, self.sbo_data_source_cache[LIVE_DATA_FRAME].update_cache, frame_cache_data)

        # B: Test that the method can cope with invalid Event Result data types by raising an exception.
        invalid_event_result_data = [None, None, None]
        frame_cache_data = [None, None, invalid_event_result_data, None, None, None, None, None]
        self.assertRaises(SboDataSourceCache.UnexpectedDataError, self.sbo_data_source_cache[LIVE_DATA_FRAME].update_cache, frame_cache_data)

        # C: Test that the method can cope with invalid Event Result data types by raising an exception.
        invalid_event_result_data = [
            [189006],
            [189007],
            [0]
        ]
        frame_cache_data = [None, None, invalid_event_result_data, None, None, None, None, None]
        self.assertRaises(SboDataSourceCache.UnexpectedDataError, self.sbo_data_source_cache[LIVE_DATA_FRAME].update_cache, frame_cache_data)

        # D: Test that the method can cope with invalid Event Result for deletion data types by raising an exception.
        for number, invalid_event_result_for_deletion_data in enumerate(self.test_types, start=1):

            # Skip the Test types numbered 1 and 6 to 10 as these are as valid parameters for Event Result for deletion data.
            if number == 1 or number in range(6, 11):
                continue

            frame_cache_data = [None, None, None, None, invalid_event_result_for_deletion_data, None, None, None]

            debug.message(debug_flags.TEST_SBO_DATA_SOURCE_CACHE_EXTRA, debug.TESTUNIT, "Testing event result for deletion data with invalid type %s of %s." % (number, len(self.test_types)))
            self.assertRaises(SboDataSourceCache.UnexpectedDataError, self.sbo_data_source_cache[LIVE_DATA_FRAME].update_cache, frame_cache_data)

        # E: Test that the Event Result Dictionary is empty.
        actual_result = self.sbo_data_source_cache[LIVE_DATA_FRAME].event_result_dictionary
        expected_result = {}
        self.assertDictEqual(actual_result, expected_result, "The actual result doesn't match the expected result.")

        # Update the cache with valid Event data.
        event_results = [
            [189006,1193897,0,1,1,3],
            [189007,1193898,0,0,1,3],
            [189011,1193902,0,0,0,3],
            [190800,1195114,0,0,0,6],
            [182282,1190361,0,0,1,6],
            [169108,1182861,0,0,0,3]
        ]
        frame_cache_data = [None, None, event_results, None, None, None, None, None]
        update_cache_result = self.sbo_data_source_cache[LIVE_DATA_FRAME].update_cache(frame_cache_data)

        # F: Test that the created elements list contains the six Element Result IDs that were created above.
        actual_result = update_cache_result[CREATED_EVENTS]
        expected_result = [189006, 189007, 189011, 190800, 182282, 169108]
        self.assertListEqual(actual_result, expected_result, "[F] The actual result doesn't match the expected result.")

        # Specify non-existent Event Result IDs.
        event_results_to_delete = [123, 456]
        frame_cache_data = [None, None, None, None, event_results_to_delete, None, None, None]
        update_cache_result = self.sbo_data_source_cache[LIVE_DATA_FRAME].update_cache(frame_cache_data)

        # G: Test that the deleted elements list is empty, as the two Event Result IDs were non-existent.
        actual_result = update_cache_result[DELETED_EVENTS]
        expected_result = []
        self.assertListEqual(actual_result, expected_result, "[G] The actual result doesn't match the expected result.")

        # H: Test that the Event Result Dictionary contains the expected data.
        # Note: Specifying Event Result IDs that are valid but do not exist, should not raise any exceptions.
        actual_result = self.sbo_data_source_cache[LIVE_DATA_FRAME].event_result_dictionary
        expected_result = {
            182282: {'event_id': 1190361, 'odds_count': 6, 'market_group_id': 0, 'home_score': 0, 'away_score': 1},
            189006: {'event_id': 1193897, 'odds_count': 3, 'market_group_id': 0, 'home_score': 1, 'away_score': 1},
            189007: {'event_id': 1193898, 'odds_count': 3, 'market_group_id': 0, 'home_score': 0, 'away_score': 1},
            190800: {'event_id': 1195114, 'odds_count': 6, 'market_group_id': 0, 'home_score': 0, 'away_score': 0},
            189011: {'event_id': 1193902, 'odds_count': 3, 'market_group_id': 0, 'home_score': 0, 'away_score': 0},
            169108: {'event_id': 1182861, 'odds_count': 3, 'market_group_id': 0, 'home_score': 0, 'away_score': 0}
        }
        self.assertDictEqual(actual_result, expected_result, "[H] The actual result doesn't match the expected result.")

        # Delete two Events Results.
        event_results_to_delete = [182282, 169108]
        frame_cache_data = [None, None, None, None, event_results_to_delete, None, None, None]
        update_cache_result = self.sbo_data_source_cache[LIVE_DATA_FRAME].update_cache(frame_cache_data)

        # I: Test that the deleted elements list contains the Event Result IDs of the deleted elements.
        actual_result = update_cache_result[DELETED_EVENTS]
        expected_result = [182282, 169108]
        self.assertListEqual(actual_result, expected_result, "[I] The actual result doesn't match the expected result.")

        # J: Test that the Event Dictionary contains the expected data.
        actual_result = self.sbo_data_source_cache[LIVE_DATA_FRAME].event_result_dictionary
        expected_result = {
            189006: {'event_id': 1193897, 'odds_count': 3, 'market_group_id': 0, 'home_score': 1, 'away_score': 1},
            189007: {'event_id': 1193898, 'odds_count': 3, 'market_group_id': 0, 'home_score': 0, 'away_score': 1},
            190800: {'event_id': 1195114, 'odds_count': 6, 'market_group_id': 0, 'home_score': 0, 'away_score': 0},
            189011: {'event_id': 1193902, 'odds_count': 3, 'market_group_id': 0, 'home_score': 0, 'away_score': 0}
        }
        self.assertDictEqual(actual_result, expected_result, "[J] The actual result doesn't match the expected result.")


    @unittest.skipIf(SKIP_TEST_07, "in development")
    def test_07_update_cache_event_result_extra(self): # pylint: disable-msg=C0103

        """Test the updating of cached event result extra data."""

        debug.message(debug_flags.TEST_SBO_DATA_SOURCE_CACHE, debug.TESTUNIT, "STARTING %s:" % "test_07_update_cache_event_result_extra")

        # A: Test that the method can cope with invalid Event Result Extra data types by raising an exception.
        for number, invalid_event_result_extra_data in enumerate(self.test_types, start=1):

            # Skip the Test types numbered 1 and 6 to 10 as these are as valid parameters for Event Result Extra data.
            if number == 1 or number in range(6, 11):
                continue

            frame_cache_data = [None, None, None, invalid_event_result_extra_data, None, None, None, None]

            debug.message(debug_flags.TEST_SBO_DATA_SOURCE_CACHE_EXTRA, debug.TESTUNIT, "Testing event result extra data with invalid type %s of %s." % (number, len(self.test_types)))
            self.assertRaises(SboDataSourceCache.UnexpectedDataError, self.sbo_data_source_cache[LIVE_DATA_FRAME].update_cache, frame_cache_data)

        # B: Test that the method can cope with invalid Event Result Extra data types by raising an exception.
        invalid_event_result_extra_data = [None, None, None]
        frame_cache_data = [None, None, None, invalid_event_result_extra_data, None, None, None, None]
        self.assertRaises(SboDataSourceCache.UnexpectedDataError, self.sbo_data_source_cache[LIVE_DATA_FRAME].update_cache, frame_cache_data)

        # C: Test that the method can cope with invalid Event Result Extra data types by raising an exception.
        invalid_event_result_extra_data = [
            [189006],
            [189007],
            [0]
        ]
        frame_cache_data = [None, None, None, invalid_event_result_extra_data, None, None, None, None]
        self.assertRaises(SboDataSourceCache.UnexpectedDataError, self.sbo_data_source_cache[LIVE_DATA_FRAME].update_cache, frame_cache_data)

        # D: Test that the Event Result Extra Dictionary is empty.
        actual_result = self.sbo_data_source_cache[LIVE_DATA_FRAME].event_result_extra_dictionary
        expected_result = {}
        self.assertDictEqual(actual_result, expected_result, "[D] The actual result doesn't match the expected result.")

        # Update the cache with valid Event Result Extra data.
        event_result_extra = [
            [189006,1,2,20,45,0,0,0],
            [189007,1,2,12,45,1,0,0],
            [189011,1,2,10,45,0,0,0],
            [190800,1,1,12,45,0,0,0]
        ]
        frame_cache_data = [None, None, None, event_result_extra, None, None, None, None]
        self.sbo_data_source_cache[LIVE_DATA_FRAME].update_cache(frame_cache_data)

        # E: Test that the Event Result Extra Dictionary contains the expected data.
        actual_result = self.sbo_data_source_cache[LIVE_DATA_FRAME].event_result_extra_dictionary
        expected_result = {
            190800: {'away_red_card_count': 0, 'home_red_card_count': 0, 'current_minutes': 12, 'total_minutes': 45, 'period': 1, 'injury_time': 0, 'row_count': 1},
            189011: {'away_red_card_count': 0, 'home_red_card_count': 0, 'current_minutes': 10, 'total_minutes': 45, 'period': 2, 'injury_time': 0, 'row_count': 1},
            189006: {'away_red_card_count': 0, 'home_red_card_count': 0, 'current_minutes': 20, 'total_minutes': 45, 'period': 2, 'injury_time': 0, 'row_count': 1},
            189007: {'away_red_card_count': 0, 'home_red_card_count': 1, 'current_minutes': 12, 'total_minutes': 45, 'period': 2, 'injury_time': 0, 'row_count': 1}
        }

        self.assertDictEqual(actual_result, expected_result, "[E] The actual result doesn't match the expected result.")


    @unittest.skipIf(SKIP_TEST_08, "in development")
    def test_08_update_cache_odds(self):

        """Test the updating of cached odds data."""

        debug.message(debug_flags.TEST_SBO_DATA_SOURCE_CACHE, debug.TESTUNIT, "STARTING %s:" % "test_08_update_cache_odds")

        # A: Test that the method can cope with invalid Odds data types by raising an exception.
        for number, invalid_odds_data in enumerate(self.test_types, start=1):

            # Skip the Test types numbered 1 and 6 to 10 as these are as valid parameters for Event Result Extra data.
            if number == 1 or number in range(6, 11):
                continue

            frame_cache_data = [None, None, None, None, None, invalid_odds_data, None, None]

            debug.message(debug_flags.TEST_SBO_DATA_SOURCE_CACHE_EXTRA, debug.TESTUNIT, "Testing odds data with invalid type %s of %s." % (number, len(self.test_types)))
            self.assertRaises(SboDataSourceCache.UnexpectedDataError, self.sbo_data_source_cache[LIVE_DATA_FRAME].update_cache, frame_cache_data)

        # B: Test that the method can cope with invalid Odds data types by raising an exception.
        invalid_odds_data = [None, None, None]
        frame_cache_data = [None, None, None, None, None, invalid_odds_data, None, None]
        self.assertRaises(SboDataSourceCache.UnexpectedDataError, self.sbo_data_source_cache[LIVE_DATA_FRAME].update_cache, frame_cache_data)

        # C: Test that the method can cope with invalid Odds data types by raising an exception.
        invalid_odds_data = [12800915, None, None]
        frame_cache_data = [None, None, None, None, None, invalid_odds_data, None, None]
        self.assertRaises(SboDataSourceCache.UnexpectedDataError, self.sbo_data_source_cache[LIVE_DATA_FRAME].update_cache, frame_cache_data)

        # D: Test that the method can cope with invalid Odds data types by raising an exception.
        invalid_odds_data = [12800915, [0], [0]]
        frame_cache_data = [None, None, None, None, None, invalid_odds_data, None, None]
        self.assertRaises(SboDataSourceCache.UnexpectedDataError, self.sbo_data_source_cache[LIVE_DATA_FRAME].update_cache, frame_cache_data)

        # E: Test that the method can cope with invalid Odds data for deletion types by raising an exception.
        for number, invalid_odds_data_for_deletion in enumerate(self.test_types, start=1):

            # Skip the Test types numbered 1 and 6 to 10 as these are as valid parameters for Event Result Extra data.
            if number == 1 or number in range(6, 11):
                continue

            frame_cache_data = [None, None, None, None, None, None, invalid_odds_data_for_deletion, None]

            debug.message(debug_flags.TEST_SBO_DATA_SOURCE_CACHE_EXTRA, debug.TESTUNIT, "Testing odds data for deletion with invalid type %s of %s." % (number, len(self.test_types)))
            self.assertRaises(SboDataSourceCache.UnexpectedDataError, self.sbo_data_source_cache[LIVE_DATA_FRAME].update_cache, frame_cache_data)

        # F: Test that the Odds Dictionary is empty.
        actual_result = self.sbo_data_source_cache[LIVE_DATA_FRAME].odds_dictionary
        expected_result = {}
        self.assertDictEqual(actual_result, expected_result, "[F] The actual result doesn't match the expected result.")

        # Update the cache with valid Odds data.
        odds = [
            [12800915,[189006,1,1,1000.00,0.25],[2.2,1.67]],
            [12800917,[189006,3,1,1000.00,2.75],[1.77,2.05]],
            [12800919,[189006,5,1,500.00,0],[2.85,1.94,3.95]],
            [12800934,[189007,1,1,2000.00,0.25],[2.09,1.75]],
            [12800936,[189007,3,1,2000.00,1.75],[1.72,2.11]],
            [12800938,[189007,5,1,500.00,0],[9.5,2.9,1.5]],
            [12801010,[189011,1,1,2000.00,0.25],[2.16,1.7]],
            [12801012,[189011,3,1,2000.00,1.25],[2.07,1.75]],
            [12801014,[189011,5,1,500.00,0],[2.59,2.14,3.75]],
            [12816830,[190800,1,1,1000.00,0.00],[1.68,2.25]],
            [12816832,[190800,3,1,1000.00,2.25],[2.01,1.85]],
            [12816834,[190800,5,1,500.00,0],[2.21,3,3]],
            [12816831,[190800,7,1,500.00,0.00],[1.77,2.12]],
            [12816835,[190800,8,1,500.00,0],[3.15,1.86,3.75]],
            [12816833,[190800,9,1,500.00,0.75],[1.8,2.06]],
            [12743315,[182282,1,1,3000.00,0.50],[2.11,1.78]],
            [12743317,[182282,3,1,3000.00,2.50],[1.86,2]],
            [12743319,[182282,5,1,500.00,0],[4.8,2.84,1.79]]
        ]
        frame_cache_data = [None, None, None, None, None, odds, None, None]
        self.sbo_data_source_cache[LIVE_DATA_FRAME].update_cache(frame_cache_data)

        # Specify two non-existent Odds IDs to delete.
        odds_to_delete = [123, 456]
        frame_cache_data = [None, None, None, None, None, None, odds_to_delete, None]
        self.sbo_data_source_cache[LIVE_DATA_FRAME].update_cache(frame_cache_data)

        # G: Test that the Event Result Extra Dictionary contains the expected data.
        # Note: Specifying Odds IDs that are valid but do not exist, should not raise any exceptions.
        actual_result = self.sbo_data_source_cache[LIVE_DATA_FRAME].odds_dictionary
        expected_result = {
            12816832: {'prices': [2.01, 1.85], 'line_number': 1, 'odds_data': [190800, 3, 1, 1000.0, 2.25]},
            12816833: {'prices': [1.8, 2.06], 'line_number': 1, 'odds_data': [190800, 9, 1, 500.0, 0.75]},
            12816834: {'prices': [2.21, 3, 3], 'line_number': 1, 'odds_data': [190800, 5, 1, 500.0, 0]},
            12816835: {'prices': [3.15, 1.86, 3.75], 'line_number': 1, 'odds_data': [190800, 8, 1, 500.0, 0]},
            12800934: {'prices': [2.09, 1.75], 'line_number': 1, 'odds_data': [189007, 1, 1, 2000.0, 0.25]},
            12800936: {'prices': [1.72, 2.11], 'line_number': 1, 'odds_data': [189007, 3, 1, 2000.0, 1.75]},
            12800938: {'prices': [9.5, 2.9, 1.5], 'line_number': 1, 'odds_data': [189007, 5, 1, 500.0, 0]},
            12801010: {'prices': [2.16, 1.7], 'line_number': 1, 'odds_data': [189011, 1, 1, 2000.0, 0.25]},
            12800915: {'prices': [2.2, 1.67], 'line_number': 1, 'odds_data': [189006, 1, 1, 1000.0, 0.25]},
            12801012: {'prices': [2.07, 1.75], 'line_number': 1, 'odds_data': [189011, 3, 1, 2000.0, 1.25]},
            12800917: {'prices': [1.77, 2.05], 'line_number': 1, 'odds_data': [189006, 3, 1, 1000.0, 2.75]},
            12801014: {'prices': [2.59, 2.14, 3.75], 'line_number': 1, 'odds_data': [189011, 5, 1, 500.0, 0]},
            12800919: {'prices': [2.85, 1.94, 3.95], 'line_number': 1, 'odds_data': [189006, 5, 1, 500.0, 0]},
            12816830: {'prices': [1.68, 2.25], 'line_number': 1, 'odds_data': [190800, 1, 1, 1000.0, 0.0]},
            12816831: {'prices': [1.77, 2.12], 'line_number': 1, 'odds_data': [190800, 7, 1, 500.0, 0.0]},
            12743315: {'prices': [2.11,1.78], 'line_number': 1, 'odds_data': [182282,1,1,3000.00,0.50]},
            12743317: {'prices': [1.86,2], 'line_number': 1, 'odds_data': [182282,3,1,3000.00,2.50]},
            12743319: {'prices': [4.8,2.84,1.79], 'line_number': 1, 'odds_data': [182282,5,1,500.00,0]}
        }
        self.assertDictEqual(actual_result, expected_result, "[G] The actual result doesn't match the expected result.")

        # Delete three Odds.
        odds_to_delete = [12743315, 12743317, 12743319]
        frame_cache_data = [None, None, None, None, None, None, odds_to_delete, None]
        self.sbo_data_source_cache[LIVE_DATA_FRAME].update_cache(frame_cache_data)

        # I: Test that the Event Dictionary contains the expected data.
        actual_result = self.sbo_data_source_cache[LIVE_DATA_FRAME].odds_dictionary
        expected_result = {
            12816832: {'prices': [2.01, 1.85], 'line_number': 1, 'odds_data': [190800, 3, 1, 1000.0, 2.25]},
            12816833: {'prices': [1.8, 2.06], 'line_number': 1, 'odds_data': [190800, 9, 1, 500.0, 0.75]},
            12816834: {'prices': [2.21, 3, 3], 'line_number': 1, 'odds_data': [190800, 5, 1, 500.0, 0]},
            12816835: {'prices': [3.15, 1.86, 3.75], 'line_number': 1, 'odds_data': [190800, 8, 1, 500.0, 0]},
            12800934: {'prices': [2.09, 1.75], 'line_number': 1, 'odds_data': [189007, 1, 1, 2000.0, 0.25]},
            12800936: {'prices': [1.72, 2.11], 'line_number': 1, 'odds_data': [189007, 3, 1, 2000.0, 1.75]},
            12800938: {'prices': [9.5, 2.9, 1.5], 'line_number': 1, 'odds_data': [189007, 5, 1, 500.0, 0]},
            12801010: {'prices': [2.16, 1.7], 'line_number': 1, 'odds_data': [189011, 1, 1, 2000.0, 0.25]},
            12800915: {'prices': [2.2, 1.67], 'line_number': 1, 'odds_data': [189006, 1, 1, 1000.0, 0.25]},
            12801012: {'prices': [2.07, 1.75], 'line_number': 1, 'odds_data': [189011, 3, 1, 2000.0, 1.25]},
            12800917: {'prices': [1.77, 2.05], 'line_number': 1, 'odds_data': [189006, 3, 1, 1000.0, 2.75]},
            12801014: {'prices': [2.59, 2.14, 3.75], 'line_number': 1, 'odds_data': [189011, 5, 1, 500.0, 0]},
            12800919: {'prices': [2.85, 1.94, 3.95], 'line_number': 1, 'odds_data': [189006, 5, 1, 500.0, 0]},
            12816830: {'prices': [1.68, 2.25], 'line_number': 1, 'odds_data': [190800, 1, 1, 1000.0, 0.0]},
            12816831: {'prices': [1.77, 2.12], 'line_number': 1, 'odds_data': [190800, 7, 1, 500.0, 0.0]}
        }
        self.assertDictEqual(actual_result, expected_result, "[I] The actual result doesn't match the expected result.")


    @unittest.skipIf(SKIP_TEST_09, "in development")
    def test_09_update_cache_market_groups(self):

        """Test the updating of cached Market Group data."""

        debug.message(debug_flags.TEST_SBO_DATA_SOURCE_CACHE, debug.TESTUNIT, "STARTING %s:" % "test_09_update_cache_market_groups")

        # A: Test that the method can cope with invalid Market Group data types by raising an exception.
        for number, invalid_market_group_data in enumerate(self.test_types, start=1):

            # Skip the Test types numbered 1 and 6 to 10 as these are as valid parameters for tournament data.
            if number == 1 or number in range(6, 11):
                continue

            frame_cache_data = [None, None, None, None, None, None, None, invalid_market_group_data]

            debug.message(debug_flags.TEST_SBO_DATA_SOURCE_CACHE_EXTRA, debug.TESTUNIT, "Testing market group data with invalid type %s of %s." % (number, len(self.test_types)))
            self.assertRaises(SboDataSourceCache.UnexpectedDataError, self.sbo_data_source_cache[LIVE_DATA_FRAME].update_cache, frame_cache_data)

        # B: Test that the method can cope with invalid Market Group data types by raising an exception.
        invalid_market_group_data = [None, None, None]
        frame_cache_data = [None, None, None, None, None, None, None, invalid_market_group_data]
        self.assertRaises(SboDataSourceCache.UnexpectedDataError, self.sbo_data_source_cache[LIVE_DATA_FRAME].update_cache, frame_cache_data)

        # C: Test that the method can cope with invalid Market Group data types by raising an exception.
        invalid_market_group_data = [
            [126],
            [128],
            [0]
        ]
        frame_cache_data = [None, None, None, None, None, None, None, invalid_market_group_data]
        self.assertRaises(SboDataSourceCache.UnexpectedDataError, self.sbo_data_source_cache[LIVE_DATA_FRAME].update_cache, frame_cache_data)

        # D: Test that the Market Group Dictionary is empty.
        actual_result = self.sbo_data_source_cache[LIVE_DATA_FRAME].market_group_dictionary
        expected_result = {}
        self.assertDictEqual(actual_result, expected_result, "[D] The actual result doesn't match the expected result.")

        # Update the cache with some valid Market Group data.
        market_groups = [
            [126,'Total Corners','_{home}_','_{away}_',1,0,0],
            [128,'Total Goals','_{home}_','_{away}_',1,0,0]
        ]
        frame_cache_data = [None, None, None, None, None, None, None, market_groups]
        self.sbo_data_source_cache[LIVE_DATA_FRAME].update_cache(frame_cache_data)

        # E: Test that the Market Group Dictionary contains the expected data.
        actual_result = self.sbo_data_source_cache[LIVE_DATA_FRAME].market_group_dictionary
        expected_result = {126: 'Total Corners', 128: 'Total Goals'}
        self.assertDictEqual(actual_result, expected_result, "[E] The actual result doesn't match the expected result.")


    @unittest.skipIf(SKIP_TEST_10, "in development")
    def test_10_update_cache_modify_data(self):

        """Test the updating of cached data."""

        debug.message(debug_flags.TEST_SBO_DATA_SOURCE_CACHE, debug.TESTUNIT, "STARTING %s:" % "test_10_update_cache_modify_data")

        # Populating the cache with the default data set.
        update_cache_result = self._populate_cache(LIVE_DATA_FRAME)

        # A: Test that the created elements list contains the four Element Result IDs that were created in the default data set.
        actual_result = update_cache_result[CREATED_EVENTS]
        expected_result = [189006, 190850, 189007, 189011, 190800]
        self.assertListEqual(actual_result, expected_result, "[A] The actual result doesn't match the expected result.")

        # B: Test that the updated elements list is an empty dictionary.
        actual_result = update_cache_result[UPDATED_EVENTS]
        expected_result = {}
        self.assertDictEqual(actual_result, expected_result, "[B] The actual result doesn't match the expected result.")

        # C: Test that the deleted elements list is an empty list.
        actual_result = update_cache_result[DELETED_EVENTS]
        expected_result = []
        self.assertListEqual(actual_result, expected_result, "[C] The actual result doesn't match the expected result.")

        # Modify a Tournament name.
        tournaments = [
            [307,'Egypt Premier League','','']
        ]
        frame_cache_data = [tournaments, None, None, None, None, None, None, None]
        update_cache_result = self.sbo_data_source_cache[LIVE_DATA_FRAME].update_cache(frame_cache_data)

        # D: Test that the Tournament Dictionary contains the expected data.
        actual_result = self.sbo_data_source_cache[LIVE_DATA_FRAME].tournament_dictionary
        expected_result = {307: 'Egypt Premier League', 3868: 'Bahrain Premier League'}
        self.assertDictEqual(actual_result, expected_result, "[D] The actual result doesn't match the expected result.")

        # E: Test that all Event Results that are associated with the modified Tournament are updated.
        # Note: This tests the private '_get_affected_event_ids()' and '_get_affected_event_result_ids()' methods.
        actual_result = update_cache_result[UPDATED_EVENTS]
        expected_result = {
            189006: {'event_details': True},
            190850: {'event_details': True},
            189007: {'event_details': True},
            190800: {'event_details': True},
            189011: {'event_details': True}
        }
        self.assertDictEqual(actual_result, expected_result, "[E] The actual result doesn't match the expected result.")

        # Modify some Events.
        events = [
            [1193897,1,307,'Torino U19','AS Roma U19','1.363',10,'02/19/2013 22:00',1,'',3],
            [1193902,1,307,'Lazio U19','Anderlecht U19','1.389',10,'02/19/2013 22:30',1,'',3]
        ]
        frame_cache_data = [None, events, None, None, None, None, None, None]
        update_cache_result = self.sbo_data_source_cache[LIVE_DATA_FRAME].update_cache(frame_cache_data)

        # F: Test that the Event Dictionary contains the expected data.
        actual_result = self.sbo_data_source_cache[LIVE_DATA_FRAME].event_dictionary
        expected_result = {
            1193897: {'home_team_name': 'Torino U19', 'show_time': '02/19/2013 22:00', 'event_sort_code': '1.363', 'away_team_name': 'AS Roma U19', 'show_time_type': 10, 'tornament_id': 307},
            1193898: {'home_team_name': 'Juventus U19', 'show_time': '02/19/2013 22:00', 'event_sort_code': '1.377', 'away_team_name': 'Juve Stabia U19', 'show_time_type': 10, 'tornament_id': 307},
            1193902: {'home_team_name': 'Lazio U19', 'show_time': '02/19/2013 22:30', 'event_sort_code': '1.389', 'away_team_name': 'Anderlecht U19', 'show_time_type': 10, 'tornament_id': 307},
            1195114: {'home_team_name': 'Muharraq', 'show_time': '02/19/2013 23:00', 'event_sort_code': '1.407', 'away_team_name': 'Busaiteen', 'show_time_type': 10, 'tornament_id': 3868}
        }
        self.assertDictEqual(actual_result, expected_result, "[F] The actual result doesn't match the expected result.")

        # G: Test that all Event Results that are associated with the modified Events are updated.
        actual_result = update_cache_result[UPDATED_EVENTS]
        expected_result = {
            189006: {'event_details': True},
            190850: {'event_details': True},
            189007: {'event_details': True},
            190800: {'event_details': True},
            189011: {'event_details': True}
        }
        self.assertDictEqual(actual_result, expected_result, "[G] The actual result doesn't match the expected result.")

        # Modify some Event Results.
        event_results = [
            [189006,1193897,0,1,2,3],
            [189011,1193902,0,1,0,3],
            [190800,1195114,0,0,0,7]
        ]
        frame_cache_data = [None, None, event_results, None, None, None, None, None]
        update_cache_result = self.sbo_data_source_cache[LIVE_DATA_FRAME].update_cache(frame_cache_data)

        # H: Test that the Event Result Dictionary contains the expected data.
        actual_result = self.sbo_data_source_cache[LIVE_DATA_FRAME].event_result_dictionary
        expected_result = {
            189006: {'event_id': 1193897, 'odds_count': 3, 'market_group_id': 0, 'home_score': 1, 'away_score': 2},
            190850: {'event_id': 1193897, 'odds_count': 1, 'market_group_id': 126, 'home_score': 2, 'away_score': 3},
            189007: {'event_id': 1193898, 'odds_count': 3, 'market_group_id': 0, 'home_score': 0, 'away_score': 1},
            190800: {'event_id': 1195114, 'odds_count': 7, 'market_group_id': 0, 'home_score': 0, 'away_score': 0},
            189011: {'event_id': 1193902, 'odds_count': 3, 'market_group_id': 0, 'home_score': 1, 'away_score': 0}
        }
        self.assertDictEqual(actual_result, expected_result, "[H] The actual result doesn't match the expected result.")

        # I: Test that all Event Results that were modified are updated.
        actual_result = update_cache_result[UPDATED_EVENTS]
        expected_result = {
            189006: {'event_details': True},
            189011: {'event_details': True},
            190850: {'event_details': True},
            189007: {'event_details': True},
            190800: {'event_details': True}
        }
        self.assertDictEqual(actual_result, expected_result, "[I] The actual result doesn't match the expected result.")

        # Modify some Event Result Extra data.
        event_result_extra = [
            [190800,1,1,14,45,0,0,0]
        ]
        frame_cache_data = [None, None, None, event_result_extra, None, None, None, None]
        update_cache_result = self.sbo_data_source_cache[LIVE_DATA_FRAME].update_cache(frame_cache_data)

        # J: Test that the Event Result Extra Dictionary contains the expected data.
        actual_result = self.sbo_data_source_cache[LIVE_DATA_FRAME].event_result_extra_dictionary
        expected_result = {
            190800: {'away_red_card_count': 0, 'home_red_card_count': 0, 'current_minutes': 14, 'total_minutes': 45, 'period': 1, 'injury_time': 0, 'row_count': 1},
            189011: {'away_red_card_count': 0, 'home_red_card_count': 0, 'current_minutes': 10, 'total_minutes': 45, 'period': 2, 'injury_time': 0, 'row_count': 1},
            189006: {'away_red_card_count': 0, 'home_red_card_count': 0, 'current_minutes': 20, 'total_minutes': 45, 'period': 2, 'injury_time': 0, 'row_count': 1},
            190850: {'away_red_card_count': 0, 'home_red_card_count': 0, 'current_minutes': 20, 'total_minutes': 45, 'period': 2, 'injury_time': 0, 'row_count': 1},
            189007: {'away_red_card_count': 0, 'home_red_card_count': 1, 'current_minutes': 12, 'total_minutes': 45, 'period': 2, 'injury_time': 0, 'row_count': 1}
        }
        self.assertDictEqual(actual_result, expected_result, "[J] The actual result doesn't match the expected result.")

        # K: Test that all Event Results that were modified are updated.
        actual_result = update_cache_result[UPDATED_EVENTS]
        expected_result = {
            189006: {'event_details': True},
            189011: {'event_details': True},
            190850: {'event_details': True},
            189007: {'event_details': True},
            190800: {'event_details': True}
        }
        self.assertDictEqual(actual_result, expected_result, "[K] The actual result doesn't match the expected result.")

        # Modify some Odds data.
        odds = [
            [12800915,None,[2.4,1.37]],
            [12800917,None,[None,2.15]],
            [12801010,None,[3.42]],
            [12816835,[190800,8,1,500.00,-0.25],[None,None,2.75]],
            [12816833,[190800,9,1,500.00]]
        ]
        frame_cache_data = [None, None, None, None, None, odds, None, None]
        update_cache_result = self.sbo_data_source_cache[LIVE_DATA_FRAME].update_cache(frame_cache_data)

        # L: Test that the Odds Dictionary contains the expected data.
        actual_result = self.sbo_data_source_cache[LIVE_DATA_FRAME].odds_dictionary
        expected_result = {
            12816832: {'prices': [2.01, 1.85], 'line_number': 1, 'odds_data': [190800, 3, 1, 1000.0, 2.25]},
            12816833: {'prices': [1.8, 2.06], 'line_number': 1, 'odds_data': [190800, 9, 1, 500.0, 0.75]},
            12816834: {'prices': [2.21, 3, 3], 'line_number': 1, 'odds_data': [190800, 5, 1, 500.0, 0]},
            12816835: {'prices': [3.15, 1.86, 2.75], 'line_number': 1, 'odds_data': [190800, 8, 1, 500.0, -0.25]},
            12800934: {'prices': [2.09, 1.75], 'line_number': 1, 'odds_data': [189007, 1, 1, 2000.0, 0.25]},
            12800936: {'prices': [1.72, 2.11], 'line_number': 1, 'odds_data': [189007, 3, 1, 2000.0, 1.75]},
            12800938: {'prices': [9.5, 2.9, 1.5], 'line_number': 1, 'odds_data': [189007, 5, 1, 500.0, 0]},
            12801010: {'prices': [3.42, 1.7], 'line_number': 1, 'odds_data': [189011, 1, 1, 2000.0, 0.25]},
            12800915: {'prices': [2.4, 1.37], 'line_number': 1, 'odds_data': [189006, 1, 1, 1000.0, 0.25]},
            12801012: {'prices': [2.07, 1.75], 'line_number': 1, 'odds_data': [189011, 3, 1, 2000.0, 1.25]},
            12800917: {'prices': [1.77, 2.15], 'line_number': 1, 'odds_data': [189006, 3, 1, 1000.0, 2.75]},
            12801014: {'prices': [2.59, 2.14, 3.75], 'line_number': 1, 'odds_data': [189011, 5, 1, 500.0, 0]},
            12800919: {'prices': [2.85, 1.94, 3.95], 'line_number': 1, 'odds_data': [189006, 5, 1, 500.0, 0]},
            12800920: {'prices': [3.55, 6.65], 'line_number': 1, 'odds_data': [190850, 3, 1, 400.0, 12.0]},
            12816830: {'prices': [1.68, 2.25], 'line_number': 1, 'odds_data': [190800, 1, 1, 1000.0, 0.0]},
            12816831: {'prices': [1.77, 2.12], 'line_number': 1, 'odds_data': [190800, 7, 1, 500.0, 0.0]}
        }
        self.assertDictEqual(actual_result, expected_result, "[L] The actual result doesn't match the expected result.")

        # M: Test that all Event Results that are associated with the modified Odds are updated.
        actual_result = update_cache_result[UPDATED_EVENTS]

        expected_result = {
            190800: {'event_details': True, 'event_odds': [12816835, 12816833]},
            190850: {'event_details': True},
            189011: {'event_details': True, 'event_odds': [12801010]},
            189006: {'event_details': True, 'event_odds': [12800915, 12800917]},
            189007: {'event_details': True}
        }
        self.assertDictEqual(actual_result, expected_result, "[M] The actual result doesn't match the expected result.")

        # Modify a Market Group name.
        market_groups = [
            [126,'Total Corners Tonight','_{home}_','_{away}_',1,0,0],
        ]
        frame_cache_data = [None, None, None, None, None, None, None, market_groups]
        update_cache_result = self.sbo_data_source_cache[LIVE_DATA_FRAME].update_cache(frame_cache_data)

        # N: Test that the Market Group Dictionary contains the expected data.
        actual_result = self.sbo_data_source_cache[LIVE_DATA_FRAME].market_group_dictionary
        expected_result = {126: 'Total Corners Tonight', 128: 'Total Goals'}
        self.assertDictEqual(actual_result, expected_result, "[N] The actual result doesn't match the expected result.")

        # O: Test that no Event Results are updated as none of them reference any of the Market Groups in the dictionary.
        actual_result = update_cache_result[UPDATED_EVENTS]
        expected_result = {
            190800: {'event_details': True},
            190850: {'event_details': True},
            189011: {'event_details': True},
            189006: {'event_details': True},
            189007: {'event_details': True}
        }
        self.assertDictEqual(actual_result, expected_result, "[O] The actual result doesn't match the expected result.")

        # Modify some Event data and Odds data simultaneously.
        events = [
            [1193897,1,307,'Torino FC U19','AS Roma U19','1.363',10,'02/19/2013 22:00',1,'',3]
        ]
        odds = [
            [12800915,None,[3.5,2.87]],
            [12800917,None,[2.32,4.57]],
            [12800919,[189006,5,1,500.0,0.25],[3.45,3.24,1.75]],
            [12816840,[189006,3,1,800.0,1.75],[3.22,5.76]]
        ]
        frame_cache_data = [None, events, None, None, None, odds, None, None]
        update_cache_result = self.sbo_data_source_cache[LIVE_DATA_FRAME].update_cache(frame_cache_data)

        # P: Test that the Event Dictionary contains the expected data.
        actual_result = self.sbo_data_source_cache[LIVE_DATA_FRAME].event_dictionary
        expected_result = {
            1193897: {'home_team_name': 'Torino FC U19', 'show_time': '02/19/2013 22:00', 'event_sort_code': '1.363', 'away_team_name': 'AS Roma U19', 'show_time_type': 10, 'tornament_id': 307},
            1193898: {'home_team_name': 'Juventus U19', 'show_time': '02/19/2013 22:00', 'event_sort_code': '1.377', 'away_team_name': 'Juve Stabia U19', 'show_time_type': 10, 'tornament_id': 307},
            1193902: {'home_team_name': 'Lazio U19', 'show_time': '02/19/2013 22:30', 'event_sort_code': '1.389', 'away_team_name': 'Anderlecht U19', 'show_time_type': 10, 'tornament_id': 307},
            1195114: {'home_team_name': 'Muharraq', 'show_time': '02/19/2013 23:00', 'event_sort_code': '1.407', 'away_team_name': 'Busaiteen', 'show_time_type': 10, 'tornament_id': 3868}
        }
        self.assertDictEqual(actual_result, expected_result, "[P] The actual result doesn't match the expected result.")

        # Q: Test that the Odds Dictionary contains the expected data.
        actual_result = self.sbo_data_source_cache[LIVE_DATA_FRAME].odds_dictionary
        expected_result = {
            12816832: {'prices': [2.01, 1.85], 'line_number': 1, 'odds_data': [190800, 3, 1, 1000.0, 2.25]},
            12816833: {'prices': [1.8, 2.06], 'line_number': 1, 'odds_data': [190800, 9, 1, 500.0, 0.75]},
            12816834: {'prices': [2.21, 3, 3], 'line_number': 1, 'odds_data': [190800, 5, 1, 500.0, 0]},
            12816835: {'prices': [3.15, 1.86, 2.75], 'line_number': 1, 'odds_data': [190800, 8, 1, 500.0, -0.25]},
            12800934: {'prices': [2.09, 1.75], 'line_number': 1, 'odds_data': [189007, 1, 1, 2000.0, 0.25]},
            12800936: {'prices': [1.72, 2.11], 'line_number': 1, 'odds_data': [189007, 3, 1, 2000.0, 1.75]},
            12800938: {'prices': [9.5, 2.9, 1.5], 'line_number': 1, 'odds_data': [189007, 5, 1, 500.0, 0]},
            12816840: {'prices': [3.22, 5.76], 'line_number': 1, 'odds_data': [189006, 3, 1, 800.0, 1.75]},
            12801010: {'prices': [3.42, 1.7], 'line_number': 1, 'odds_data': [189011, 1, 1, 2000.0, 0.25]},
            12800915: {'prices': [3.5, 2.87], 'line_number': 1, 'odds_data': [189006, 1, 1, 1000.0, 0.25]},
            12801012: {'prices': [2.07, 1.75], 'line_number': 1, 'odds_data': [189011, 3, 1, 2000.0, 1.25]},
            12800917: {'prices': [2.32, 4.57], 'line_number': 1, 'odds_data': [189006, 3, 1, 1000.0, 2.75]},
            12801014: {'prices': [2.59, 2.14, 3.75], 'line_number': 1, 'odds_data': [189011, 5, 1, 500.0, 0]},
            12800919: {'prices': [3.45, 3.24, 1.75], 'line_number': 1, 'odds_data': [189006, 5, 1, 500.0, 0.25]},
            12800920: {'prices': [3.55, 6.65], 'line_number': 1, 'odds_data': [190850, 3, 1, 400.0, 12.0]},
            12816830: {'prices': [1.68, 2.25], 'line_number': 1, 'odds_data': [190800, 1, 1, 1000.0, 0.0]},
            12816831: {'prices': [1.77, 2.12], 'line_number': 1, 'odds_data': [190800, 7, 1, 500.0, 0.0]}
        }
        self.assertDictEqual(actual_result, expected_result, "[Q] The actual result doesn't match the expected result.")

        # R: Test that all Event Results that are associated with the modified Odds are updated.
        actual_result = update_cache_result[UPDATED_EVENTS]
        expected_result = {
            190800: {'event_details': True},
            190850: {'event_details': True},
            189011: {'event_details': True},
            189006: {'event_details': True, 'event_odds': [12800915, 12800917, 12800919, 12816840]},
            189007: {'event_details': True}
        }
        self.assertDictEqual(actual_result, expected_result, "[R] The actual result doesn't match the expected result.")


    @unittest.skipIf((SKIP_TEST_10 or SKIP_TEST_11), "in development")
    def test_11_update_cache_delete_data(self):

        """Test the deleting of Event Results also removes the entries from the Event Result Extra dictionary."""

        debug.message(debug_flags.TEST_SBO_DATA_SOURCE_CACHE, debug.TESTUNIT, "STARTING %s:" % "test_11_update_cache_delete_data")

        # A: Test that the Event Result Dictionary contains the expected data.
        actual_result = self.sbo_data_source_cache[LIVE_DATA_FRAME].event_result_dictionary
        expected_result = {
            189006: {'event_id': 1193897, 'odds_count': 3, 'market_group_id': 0, 'home_score': 1, 'away_score': 2},
            190850: {'event_id': 1193897, 'odds_count': 1, 'market_group_id': 126, 'home_score': 2, 'away_score': 3},
            189007: {'event_id': 1193898, 'odds_count': 3, 'market_group_id': 0, 'home_score': 0, 'away_score': 1},
            190800: {'event_id': 1195114, 'odds_count': 7, 'market_group_id': 0, 'home_score': 0, 'away_score': 0},
            189011: {'event_id': 1193902, 'odds_count': 3, 'market_group_id': 0, 'home_score': 1, 'away_score': 0}
        }
        self.assertDictEqual(actual_result, expected_result, "[A] The actual result doesn't match the expected result.")

        # B: Test that the Event Result Extra Dictionary contains the expected data.
        actual_result = self.sbo_data_source_cache[LIVE_DATA_FRAME].event_result_extra_dictionary
        expected_result = {
            189006: {'away_red_card_count': 0, 'home_red_card_count': 0, 'current_minutes': 20, 'total_minutes': 45, 'period': 2, 'injury_time': 0, 'row_count': 1},
            190850: {'away_red_card_count': 0, 'home_red_card_count': 0, 'current_minutes': 20, 'total_minutes': 45, 'period': 2, 'injury_time': 0, 'row_count': 1},
            189007: {'away_red_card_count': 0, 'home_red_card_count': 1, 'current_minutes': 12, 'total_minutes': 45, 'period': 2, 'injury_time': 0, 'row_count': 1},
            190800: {'away_red_card_count': 0, 'home_red_card_count': 0, 'current_minutes': 14, 'total_minutes': 45, 'period': 1, 'injury_time': 0, 'row_count': 1},
            189011: {'away_red_card_count': 0, 'home_red_card_count': 0, 'current_minutes': 10, 'total_minutes': 45, 'period': 2, 'injury_time': 0, 'row_count': 1}
        }
        self.assertDictEqual(actual_result, expected_result, "[B] The actual result doesn't match the expected result.")

        # Delete three Events Results.
        event_results_to_delete = [189006, 190850, 189011]
        frame_cache_data = [None, None, None, None, event_results_to_delete, None, None, None]
        update_cache_result = self.sbo_data_source_cache[LIVE_DATA_FRAME].update_cache(frame_cache_data)

        # C: Test that the deleted elements list contains the Event Result IDs of the deleted elements.
        actual_result = update_cache_result[DELETED_EVENTS]
        expected_result = [189006, 190850, 189011]
        self.assertListEqual(actual_result, expected_result, "[C] The actual result doesn't match the expected result.")

        # D: Test that the Event Result Dictionary contains the expected data.
        actual_result = self.sbo_data_source_cache[LIVE_DATA_FRAME].event_result_dictionary
        expected_result = {
            189007: {'event_id': 1193898, 'odds_count': 3, 'market_group_id': 0, 'home_score': 0, 'away_score': 1},
            190800: {'event_id': 1195114, 'odds_count': 7, 'market_group_id': 0, 'home_score': 0, 'away_score': 0}
        }
        self.assertDictEqual(actual_result, expected_result, "[D] The actual result doesn't match the expected result.")

        # E: Test that the Event Result Extra Dictionary contains the expected data.
        actual_result = self.sbo_data_source_cache[LIVE_DATA_FRAME].event_result_extra_dictionary
        expected_result = {
            189007: {'away_red_card_count': 0, 'home_red_card_count': 1, 'current_minutes': 12, 'total_minutes': 45, 'period': 2, 'injury_time': 0, 'row_count': 1},
            190800: {'away_red_card_count': 0, 'home_red_card_count': 0, 'current_minutes': 14, 'total_minutes': 45, 'period': 1, 'injury_time': 0, 'row_count': 1}
        }
        self.assertDictEqual(actual_result, expected_result, "[E] The actual result doesn't match the expected result.")


    @unittest.skipIf(SKIP_TEST_12, "in development")
    def test_12_fetch_event(self):

        """Test that the details of recently created events can be fetched successfully."""

        debug.message(debug_flags.TEST_SBO_DATA_SOURCE_CACHE, debug.TESTUNIT, "STARTING %s:" % "test_12_fetch_event")

        # A: Test that the method can cope with invalid Event Result ID types by raising an exception.
        for number, invalid_event_result_id in enumerate(self.test_types, start=1):

            debug.message(debug_flags.TEST_SBO_DATA_SOURCE_CACHE_EXTRA, debug.TESTUNIT, "Testing event result id with invalid type %s of %s." % (number, len(self.test_types)))
            self.assertRaises(DataSourceBase.EventIndexError, self.sbo_data_source_cache[LIVE_DATA_FRAME].fetch_event, invalid_event_result_id)

        # B: Test that the method can cope with a valid, but non-existent Event Result ID types by raising an exception.
        non_existant_event_result_id = 123
        self.assertRaises(DataSourceBase.EventIndexError, self.sbo_data_source_cache[LIVE_DATA_FRAME].fetch_event, non_existant_event_result_id)

        # Populating the live cache with the default data set.
        update_cache_result = self._populate_cache(LIVE_DATA_FRAME)
        created_events = update_cache_result[CREATED_EVENTS]

        # Fetch the Event details for each Event Result ID.
        events = []

        for event_result_id in created_events:

            event = self.sbo_data_source_cache[LIVE_DATA_FRAME].fetch_event(event_result_id)
            events.append(event)

        # C: Test that the Created Events array contains the expected data.
        actual_result = events
        expected_result = [
            (537059918, 537059918, ('Torneo Viareggio', 1374, ('Torino U19', 'AS Roma U19'), datetime.datetime(2013, 2, 19, 14, 0), 1, (None, 20), 3, 0, 0, (1, 1), (0, 0)), [
                [(0.0, 0.0, 0.0, 0), ('0-0.5', 2.2, 1.67, 1), (0.0, 0.0, 0.0), ('2.5-3', 1.77, 2.05)],
                [None, None, None, None],
                [None, None, None, None]
            ]),
            (537061762, 537061762, ('Torneo Viareggio - Total Corners', 1374, ('Torino U19', 'AS Roma U19'), datetime.datetime(2013, 2, 19, 14, 0), 1, (None, 20), 3, 0, 0, (2, 3), (0, 0)), [
                [(0.0, 0.0, 0.0, 0), (0.0, 0.0, 0.0, 0), (0.0, 0.0, 0.0), ('12.0', 3.55, 6.65)],
                [None, None, None, None],
                [None, None, None, None]
            ]),
            (537059919, 537059919, ('Torneo Viareggio', 1377, ('Juventus U19', 'Juve Stabia U19'), datetime.datetime(2013, 2, 19, 14, 0), 1, (None, 12), 3, 0, 0, (0, 1), (1, 0)), [
                [(0.0, 0.0, 0.0, 0), ('0-0.5', 2.09, 1.75, 1), (0.0, 0.0, 0.0), ('1.5-2', 1.72, 2.11)],
                [None, None, None, None],
                [None, None, None, None]
            ]),
            (537059923, 537059923, ('Torneo Viareggio', 1389, ('Lazio U19', 'Anderlecht U19'), datetime.datetime(2013, 2, 19, 14, 0), 1, (None, 10), 3, 0, 0, (0, 0), (0, 0)), [
                [(0.0, 0.0, 0.0, 0), ('0-0.5', 2.16, 1.7, 1), (0.0, 0.0, 0.0), ('1-1.5', 2.07, 1.75)],
                [None, None, None, None],
                [None, None, None, None]
            ]),
            (537061712, 537061712, ('Bahrain Premier League', 1407, ('Muharraq', 'Busaiteen'), datetime.datetime(2013, 2, 19, 15, 0), 1, (12, None), 1, 0, 0, (0, 0), (0, 0)), [
                [('0.0', 1.77, 2.12, 0), ('0.0', 1.68, 2.25, 0), ('0.5-1', 1.8, 2.06), ('2-2.5', 2.01, 1.85)],
                [None, None, None, None],
                [None, None, None, None]
            ])
        ]
        self.assertListEqual(actual_result, expected_result, "[C] The actual result doesn't match the expected result.")

        # Populating the non-live cache with the default data set.
        update_cache_result = self._populate_cache(NON_LIVE_DATA_FRAME)
        created_events = update_cache_result[CREATED_EVENTS]

        # Fetch the Event details for each Event Result ID.
        events = []

        for event_result_id in created_events:

            event = self.sbo_data_source_cache[NON_LIVE_DATA_FRAME].fetch_event(event_result_id)
            events.append(event)

        # D: Test that the Created Events array contains the expected data.
        actual_result = events
        expected_result = [
            (538059918, 537059918, ('Torneo Viareggio', 1374, ('Torino U19', 'AS Roma U19'), datetime.datetime(2013, 2, 19, 14, 0), 1, (None, 20), 3, 0, 0, (1, 1), (0, 0)), [
                [(0.0, 0.0, 0.0, 0), ('0-0.5', 2.2, 1.67, 1), (0.0, 0.0, 0.0), ('2.5-3', 1.77, 2.05)],
                [None, None, None, None],
                [None, None, None, None]
            ]),
            (538061762, 537061762, ('Torneo Viareggio - Total Corners', 1374, ('Torino U19', 'AS Roma U19'), datetime.datetime(2013, 2, 19, 14, 0), 1, (None, 20), 3, 0, 0, (2, 3), (0, 0)), [
                [(0.0, 0.0, 0.0, 0), (0.0, 0.0, 0.0, 0), (0.0, 0.0, 0.0), ('12.0', 3.55, 6.65)],
                [None, None, None, None],
                [None, None, None, None]
            ]),
            (538059919, 537059919, ('Torneo Viareggio', 1377, ('Juventus U19', 'Juve Stabia U19'), datetime.datetime(2013, 2, 19, 14, 0), 1, (None, 12), 3, 0, 0, (0, 1), (1, 0)), [
                [(0.0, 0.0, 0.0, 0), ('0-0.5', 2.09, 1.75, 1), (0.0, 0.0, 0.0), ('1.5-2', 1.72, 2.11)],
                [None, None, None, None],
                [None, None, None, None]
            ]),
            (538059923, 537059923, ('Torneo Viareggio', 1389, ('Lazio U19', 'Anderlecht U19'), datetime.datetime(2013, 2, 19, 14, 0), 1, (None, 10), 3, 0, 0, (0, 0), (0, 0)), [
                [(0.0, 0.0, 0.0, 0), ('0-0.5', 2.16, 1.7, 1), (0.0, 0.0, 0.0), ('1-1.5', 2.07, 1.75)],
                [None, None, None, None],
                [None, None, None, None]
            ]),
            (538061712, 537061712, ('Bahrain Premier League', 1407, ('Muharraq', 'Busaiteen'), datetime.datetime(2013, 2, 19, 15, 0), 1, (12, None), 1, 0, 0, (0, 0), (0, 0)), [
                [('0.0', 1.77, 2.12, 0), ('0.0', 1.68, 2.25, 0), ('0.5-1', 1.8, 2.06), ('2-2.5', 2.01, 1.85)],
                [None, None, None, None],
                [None, None, None, None]
            ])
        ]
        self.assertListEqual(actual_result, expected_result, "[D] The actual result doesn't match the expected result.")


    @unittest.skipIf((SKIP_TEST_12 or SKIP_TEST_13), "in development")
    def test_13_fetch_modified_event(self):

        """Test that the details of recently created events can be fetched successfully."""

        debug.message(debug_flags.TEST_SBO_DATA_SOURCE_CACHE, debug.TESTUNIT, "STARTING %s:" % "test_13_fetch_modified_event")

        # Define valid parameters.
        valid_event_result_id = 182282
        valid_modified_property = {'event_details': True, 'event_odds': [12743320, 12743318]}

        # A: Test that the method can cope with invalid Event Result ID types by raising an exception.
        for number, invalid_event_result_id in enumerate(self.test_types, start=1):

            debug.message(debug_flags.TEST_SBO_DATA_SOURCE_CACHE_EXTRA, debug.TESTUNIT, "Testing event result id with invalid type %s of %s." % (number, len(self.test_types)))
            self.assertRaises(DataSourceBase.EventIndexError, self.sbo_data_source_cache[LIVE_DATA_FRAME].fetch_modified_event, invalid_event_result_id, valid_modified_property)

        # B: Test that the method can cope with invalid modified parameters types by raising an exception.
        for number, invalid_modified_property in enumerate(self.test_types, start=1):

            # Skip the Test types numbered 6 to 10 as these are as valid parameters for modified parameters.
            if number in range(6, 11):
                continue

            debug.message(debug_flags.TEST_SBO_DATA_SOURCE_CACHE_EXTRA, debug.TESTUNIT, "Testing modified parameters with invalid type %s of %s." % (number, len(self.test_types)))
            self.assertRaises(DataSourceBase.EventIndexError, self.sbo_data_source_cache[LIVE_DATA_FRAME].fetch_modified_event, valid_event_result_id, invalid_modified_property)

        # C: Test that the method can cope with a valid, but non-existent Event Result ID types by raising an exception.
        non_existant_event_result_id = 123
        self.assertRaises(DataSourceBase.EventIndexError, self.sbo_data_source_cache[LIVE_DATA_FRAME].fetch_modified_event, non_existant_event_result_id, valid_modified_property)

        # D: Test that the method can cope with a valid, but non-existent Odds ID types by raising an exception.
        invalid_odds_id = 123
        non_existant_modified_property = {'event_details': True, 'event_odds': [12743320, invalid_odds_id]}
        self.assertRaises(DataSourceBase.EventIndexError, self.sbo_data_source_cache[LIVE_DATA_FRAME].fetch_modified_event, valid_event_result_id, non_existant_modified_property)

        # E: Test that the method can cope with invalid Odds ID types by raising an exception.
        for number, invalid_odds_id in enumerate(self.test_types, start=1):

            non_existant_modified_property = {'event_details': True, 'event_odds': [12743320, invalid_odds_id]}

            debug.message(debug_flags.TEST_SBO_DATA_SOURCE_CACHE_EXTRA, debug.TESTUNIT, "Testing Odds ID with invalid type %s of %s." % (number, len(self.test_types)))
            self.assertRaises(DataSourceBase.EventIndexError, self.sbo_data_source_cache[LIVE_DATA_FRAME].fetch_modified_event, valid_event_result_id, non_existant_modified_property)

        # Modify some data.
        event_result = [
            [190800,1195114,0,0,1,6]
        ]
        event_result_extra = [
            [190800,1,2,17,45,0,0,0]
        ]
        odds = [
            [12816832,None,[1.6,2.33]],
            [12816833,None,[3.67,1.15]],
            [12816834,None,[2.42,0.11]],
            [12816835,[190800,8,1,500.0,0],[2.15,2.86,2.75]],
            [12801010,[189011,1,1,2000.0,0.5],None]
        ]
        frame_cache_data = [None, None, event_result, event_result_extra, None, odds, None, None]
        update_cache_result = self.sbo_data_source_cache[LIVE_DATA_FRAME].update_cache(frame_cache_data)

        modified_event_result_properties = update_cache_result[UPDATED_EVENTS]

        # Fetch the Event details for each Event Result ID.
        events_updated = []

        for event_result_id, modified_properties in modified_event_result_properties.items():

            event = self.sbo_data_source_cache[LIVE_DATA_FRAME].fetch_modified_event(event_result_id, modified_properties)
            events_updated.append(event)

        # F: Test that the Updated Events array contains the expected data.
        actual_result = events_updated
        expected_result = [
            (537061712, 537061712, ('Bahrain Premier League', 1407, ('Muharraq', 'Busaiteen'), datetime.datetime(2013, 2, 19, 15, 0), 1, (None, 17), 3, 0, 0, (0, 1), (0, 0)), [
                [None, None, ('0.5-1', 3.67, 1.15), ('2-2.5', 1.6, 2.33)],
                [None, None, None, None],
                [None, None, None, None]
            ]),
            (537061762, 537061762, ('Torneo Viareggio - Total Corners', 1374, ('Torino U19', 'AS Roma U19'), datetime.datetime(2013, 2, 19, 14, 0), 1, (None, 20), 3, 0, 0, (2, 3), (0, 0)), [
                [None, None, None, None],
                [None, None, None, None],
                [None, None, None, None]
            ]),
            (537059923, 537059923, ('Torneo Viareggio', 1389, ('Lazio U19', 'Anderlecht U19'), datetime.datetime(2013, 2, 19, 14, 0), 1, (None, 10), 3, 0, 0, (0, 0), (0, 0)), [
                [None, ('0.50', 2.16, 1.7, 1), None, None],
                [None, None, None, None],
                [None, None, None, None]
            ]),
            (537059918, 537059918, ('Torneo Viareggio', 1374, ('Torino U19', 'AS Roma U19'), datetime.datetime(2013, 2, 19, 14, 0), 1, (None, 20), 3, 0, 0, (1, 1), (0, 0)), [
                [None, None, None, None],
                [None, None, None, None],
                [None, None, None, None]
            ]),
            (537059919, 537059919, ('Torneo Viareggio', 1377, ('Juventus U19', 'Juve Stabia U19'), datetime.datetime(2013, 2, 19, 14, 0), 1, (None, 12), 3, 0, 0, (0, 1), (1, 0)), [
                [None, None, None, None],
                [None, None, None, None],
                [None, None, None, None]
            ])
        ]
        self.assertListEqual(actual_result, expected_result, "[F] The actual result doesn't match the expected result.")


    @unittest.skipIf(SKIP_TEST_14, "in development")
    def test_14_corrupt_data(self):

        """Test the method can cope with corrupted data."""

        debug.message(debug_flags.TEST_SBO_DATA_SOURCE_CACHE, debug.TESTUNIT, "STARTING %s:" % "test_14_corrupt_data")

        # Populating the cache with the default data set.
        self._populate_cache(LIVE_DATA_FRAME)

        # The Period parameter is the only input to the _get_match_stage_details() function.
        # The function can be tested by setting the Period parameter to different values.

        # A: Test that the method can cope with invalid Period types by raising an exception.
        for number, invalid_period in enumerate(self.test_types, start=1):

            # Skip the Test types numbered 2 to 4 and 11 to 12, as these are as valid parameters for Period.
            if number in range(2, 5) or number in range(11, 13):
                continue

            debug.message(debug_flags.TEST_SBO_DATA_SOURCE_CACHE_EXTRA, debug.TESTUNIT, "Testing period with invalid type %s of %s." % (number, len(self.test_types)))

            event_result_extra = [[190800, 1, invalid_period, 11, 45, 0, 0, 0]]
            frame_cache_data = [None, None, None, event_result_extra, None, None, None, None]

            # Update the cache with the corrupt data.
            update_cache_result = self.sbo_data_source_cache[LIVE_DATA_FRAME].update_cache(frame_cache_data)
            modified_event_result_properties = update_cache_result[UPDATED_EVENTS]

            for event_result_id, modified_properties in modified_event_result_properties.items():

                # Even though only one event has been modified, other events may have been modified by the system, so filter for the required event.
                if event_result_id == 190800:
                    self.assertRaises(DataSourceBase.EventIndexError, self.sbo_data_source_cache[LIVE_DATA_FRAME].fetch_modified_event, event_result_id, modified_properties)

        # The Show Time parameter is the only input to the _format_show_time() function.
        # The function can be tested by setting the Show Time parameter to different values.

        # Create a new Event for use with the temporary instance of SboDataSourceCache.
        tournaments = [[307, 'Torneo Viareggio', '', '']]
        events = [[1193897, 1, 307, 'Torino U19', 'AS Roma U19', '1.374', 10, '02/19/2013 22:00', 1, '', 1]]
        event_results = [[189006, 1193897, 0, 1, 1, 1]]
        event_result_extra = [[189006, 1, 2, 20, 45, 0, 0, 0]]
        event_results_to_delete = []
        odds = [[12800915, [189006, 1, 1, 1000.00, 0.25], [2.2, 1.67]]]
        odds_to_delete = []
        market_groups = []
        frame_cache_data = [tournaments, events, event_results, event_result_extra, event_results_to_delete, odds, odds_to_delete, market_groups]

        # B: Test that the method can cope with invalid Show Time types by generating a warning.
        for number, invalid_showtime in enumerate(self.test_types, start=1):

            debug.message(debug_flags.TEST_SBO_DATA_SOURCE_CACHE_EXTRA, debug.TESTUNIT, "Testing show time with invalid type %s of %s." % (number, len(self.test_types)))

            event = [[1193898, 1, 307, 'Juventus U19', 'Juve Stabia U19', '1.377', 10, invalid_showtime, 1, '', 3]]
            frame_cache_data = [None, event, None, None, None, None, None, None]

            # Update the cache with the corrupt data.
            update_cache_result = self.sbo_data_source_cache[LIVE_DATA_FRAME].update_cache(frame_cache_data)
            modified_event_result_properties = update_cache_result[UPDATED_EVENTS]

            for event_result_id, modified_properties in modified_event_result_properties.items():

                # Even though only one event has been modified, other events may have been modified by the system, so filter for the required event.
                if event_result_id == 189006:
                    self.sbo_data_source_cache[LIVE_DATA_FRAME].fetch_modified_event(event_result_id, modified_properties)

        # C: Test that the method can cope with invalid Show Time types by generating a warning
        invalid_showtime = '02/19/2013'
        event = [[1193898, 1, 307, 'Juventus U19', 'Juve Stabia U19', '1.377', 10, invalid_showtime, 1, '', 3]]
        frame_cache_data = [None, event, None, None, None, None, None, None]

        # Update the cache with the corrupt data.
        update_cache_result = self.sbo_data_source_cache[LIVE_DATA_FRAME].update_cache(frame_cache_data)
        modified_event_result_properties = update_cache_result[UPDATED_EVENTS]

        for event_result_id, modified_properties in modified_event_result_properties.items():

            # Even though only one event has been modified, other events may have been modified by the system, so filter for the required event.
            if event_result_id == 189006:
                self.sbo_data_source_cache[LIVE_DATA_FRAME].fetch_modified_event(event_result_id, modified_properties)

        # D: Test that the method can cope with invalid Show Time types by generating a warning
        invalid_showtime = 'aa/bb/cccc dd:ee'
        event = [[1193898, 1, 307, 'Juventus U19', 'Juve Stabia U19', '1.377', 10, invalid_showtime, 1, '', 3]]
        frame_cache_data = [None, event, None, None, None, None, None, None]

        # Update the cache with the corrupt data.
        update_cache_result = self.sbo_data_source_cache[LIVE_DATA_FRAME].update_cache(frame_cache_data)
        modified_event_result_properties = update_cache_result[UPDATED_EVENTS]

        for event_result_id, modified_properties in modified_event_result_properties.items():

            # Even though only one event has been modified, other events may have been modified by the system, so filter for the required event.
            if event_result_id == 189006:
                self.sbo_data_source_cache[LIVE_DATA_FRAME].fetch_modified_event(event_result_id, modified_properties)

        # E: Test that the show time can be interpretted with the leading zeros missing.
        invalid_showtime = '2/6/2013 7:11'
        event = [[1193898, 1, 307, 'Juventus U19', 'Juve Stabia U19', '1.377', 10, invalid_showtime, 1, '', 3]]
        frame_cache_data = [None, event, None, None, None, None, None, None]

        # Update the cache with the corrupt data.
        update_cache_result = self.sbo_data_source_cache[LIVE_DATA_FRAME].update_cache(frame_cache_data)
        modified_event_result_properties = update_cache_result[UPDATED_EVENTS]

        for event_result_id, modified_properties in modified_event_result_properties.items():

            # Even though only one event has been modified, other events may have been modified by the system, so filter for the required event.
            if event_result_id == 189007:
                updated_event = self.sbo_data_source_cache[LIVE_DATA_FRAME].fetch_modified_event(event_result_id, modified_properties)

        # Check the updated event details are as expected.
        actual_result = updated_event
        expected_result = (
            537059919, 537059919, ('Torneo Viareggio', 1377, ('Juventus U19', 'Juve Stabia U19'), datetime.datetime(2013, 2, 5, 23, 11), 1, (None, 12), 3, 0, 0, (0, 1), (1, 0)), [
                [None, None, None, None],
                [None, None, None, None],
                [None, None, None, None]
            ])

        self.assertTupleEqual(actual_result, expected_result, "[E] The actual result doesn't match the expected result.")

        # The Point parameter is the only input to the _format_point_value() function.
        # The function can be tested by setting the Point parameter to different values.

        # F: Create a new Event with a corrupt Odds Point Parameter.
        event_results = [[190851, 1193897, 128, 1, 3, 1]]
        event_result_extra = [[190851, 1, 2, 33, 45, 0, 0, 0]]
        invalid_point = '0.75'
        odds = [[12816844, [190851, 3, 1, 450.00, invalid_point], [1.25, 3.2]]]
        frame_cache_data = [None, None, event_results, event_result_extra, None, odds, None, None]

        # Update the cache with the corrupt data.
        update_cache_result = self.sbo_data_source_cache[LIVE_DATA_FRAME].update_cache(frame_cache_data)
        created_events = update_cache_result[CREATED_EVENTS]

        # As only one Event has been created, this loop will only have one itteration.
        for event_result_id in created_events:

            self.assertRaises(DataSourceBase.EventIndexError, self.sbo_data_source_cache[LIVE_DATA_FRAME].fetch_event, event_result_id)

        # G: Update an Event with a corrupt Odds Point Parameter.
        invalid_point = '0.85'
        odds = [[12800920, [190850, 3, 1, 400.00, invalid_point], [3.55, 6.65]]]
        frame_cache_data = [None, None, None, None, None, odds, None, None]

        # Update the cache with the corrupt data.
        update_cache_result = self.sbo_data_source_cache[LIVE_DATA_FRAME].update_cache(frame_cache_data)
        modified_event_result_properties = update_cache_result[UPDATED_EVENTS]

        for event_result_id, modified_properties in modified_event_result_properties.items():

            # Even though only one event has been modified, other events may have been modified by the system, so filter for the required event.
            if event_result_id == 190850:
                self.assertRaises(DataSourceBase.EventIndexError, self.sbo_data_source_cache[LIVE_DATA_FRAME].fetch_modified_event, event_result_id, modified_properties)


if __name__ == "__main__":
    unittest.main()
