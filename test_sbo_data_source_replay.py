#!/usr/local/bin/python3.2
# coding: utf-8

"""This module tests the sbo_data_source_replay module."""

import unittest
import debug
import debug_flags

# Test specific imports.
import os
import time
import datetime

# Import the module of the class under test to access its constants.
import sbo_data_source_replay

# The class under test.
from sbo_data_source_replay import SboDataSourceReplay

# Individual tests can be skipped by setting the appropriate flag.
SKIP_TEST_01 = False
SKIP_TEST_02 = False
SKIP_TEST_03 = False
SKIP_TEST_04 = False
SKIP_TEST_05 = False

# General constants.
CAPTURE_FILE = 0
PLAYBACK_FILE = 1
LIVE_DATA_FRAME = 0
NON_LIVE_DATA_FRAME = 1
NORMAL_REPLAY_MODE = 0
FAST_REPLAY_MODE = 1
DEFAULT_REPLAY_MODE = FAST_REPLAY_MODE
MINIMUM_REQUEST_PERIOD_LIVE = 2
MINIMUM_REQUEST_PERIOD_NON_LIVE = 6
SAFETY_MARGIN = 0.1


class TestSboDataSourceReplay(unittest.TestCase): # pylint: disable-msg=R0904

    """This class tests the SboDataSourceReplay class."""

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

        debug.message(debug_flags.TEST_SBO_DATA_SOURCE_REPLAY, debug.TESTUNIT, "STARTING %s..." % TestSboDataSourceReplay.__name__)

        # Create an instance of SboDataSourceReplay class.
        cls.sbo_data_source_replay = SboDataSourceReplay()

        # Use the constants defined in the sbo_data_source_replay.py module to determine the current capture directory.
        base_directory = os.sys.path[0]
        capture_folder = sbo_data_source_replay.CAPTURE_FOLDER
        capture_current_subfolder = sbo_data_source_replay.CAPTURE_CURRENT_SUBFOLDER

        cls.capture_current_path = os.path.join(base_directory, capture_folder, capture_current_subfolder)


    @staticmethod
    def read_file(file_path):

        """This method reads the captured data from a replay file."""

        debug.message(debug_flags.TEST_SBO_DATA_SOURCE_REPLAY_EXTRA, debug.TESTUNIT, "reading file...")

        file_handle = open(file_path, "r")

        data_identifier = file_handle.readline().rstrip('\n')
        datestamp = file_handle.readline().rstrip('\n')
        raw_data = file_handle.readline()

        file_handle.close()

        return (data_identifier, datestamp, raw_data)


    def reset_playback(self, replay_folder_path, replay_mode, minimum_request_period):

        """This method allows playback to be reset during testing.
           Note: For testing purposes only, the parameters passed to the initalise_playback() method will keep changing.
           This method calls initalise_playback() followed by reinitalise_playback() to ensure these changes are applied.
        """

        debug.message(debug_flags.TEST_SBO_DATA_SOURCE_REPLAY_EXTRA, debug.TESTUNIT, "initialising playback...")

        self.sbo_data_source_replay.initalise_playback(replay_folder_path, replay_mode, minimum_request_period)
        self.sbo_data_source_replay.reinitialise_playback()


    @unittest.skipIf(SKIP_TEST_01, "in development")
    def test_01_object_creation(self):

        """Test the class initialiser method."""

        debug.message(debug_flags.TEST_SBO_DATA_SOURCE_REPLAY, debug.TESTUNIT, "STARTING %s:" % "test_01_object_creation")

        # A: Test that the instantiation of the class was successful.
        actual_object = self.sbo_data_source_replay
        expected_class = SboDataSourceReplay
        self.assertIsInstance(actual_object, expected_class, "[A] The tested object is not an instance of the SboDataSourceReplay class.")

        # B: Test that the base directory exists.
        actual_result = os.path.exists(self.sbo_data_source_replay.base_directory)
        self.assertTrue(actual_result, "[B] The base directory does not exist.")


    @unittest.skipIf(SKIP_TEST_02, "in development")
    def test_02_capture(self):

        """Test the capturing of raw data to file."""

        debug.message(debug_flags.TEST_SBO_DATA_SOURCE_REPLAY, debug.TESTUNIT, "STARTING %s:" % "test_02_capture")

        # Define valid parameters for the capture() method.
        valid_raw_data = "$Page.onUpdate([35210,0,1,[[[3,'TEST LEAGUE 1','','']],0],[[1158696,1158767],[],[1158767,1162975,1164090],0],[[],[],[]]]);"
        valid_frame_type = LIVE_DATA_FRAME

        # A: Test that the method can cope with invalid inputs by raising an exception.
        for number, invalid_raw_data in enumerate(self.test_types, start=1):

            # Test type 6 is a valid value of raw data.
            if number == 6:
                continue

            debug.message(debug_flags.TEST_SBO_DATA_SOURCE_REPLAY_EXTRA, debug.TESTUNIT, "Testing raw data with invalid type %s of %s." % (number, len(self.test_types)))
            self.assertRaises(SboDataSourceReplay.DataCaptureError, self.sbo_data_source_replay.capture, invalid_raw_data, valid_frame_type)

        # B: Test that the method can cope with invalid inputs by raising an exception.
        for number, invalid_frame_type in enumerate(self.test_types, start=1):

            # Test types 2 to 6 are valid values of frame types.
            if number in range(2, 6):
                continue

            debug.message(debug_flags.TEST_SBO_DATA_SOURCE_REPLAY_EXTRA, debug.TESTUNIT, "Testing frame type with invalid type %s of %s." % (number, len(self.test_types)))
            self.assertRaises(SboDataSourceReplay.DataCaptureError, self.sbo_data_source_replay.capture, valid_raw_data, invalid_frame_type)

        # Send the valid parameters to the capture() method.
        self.sbo_data_source_replay.capture(valid_raw_data, valid_frame_type)

        # This will be the first capture since the object was created, so it should attempt to check/create the capture directory structure.
        expected_capture_path = os.path.join(self.sbo_data_source_replay.base_directory, 'sbo_data_captured/current')

        # C: Test that the expected capture path exists.
        actual_result = os.path.exists(expected_capture_path)
        self.assertTrue(actual_result, "[C] The expected capture path does not exist.")

        # The first file should be numbered 1, padded with zeros to total 5 digits.
        expected_capture_file_path = os.path.join(expected_capture_path, 'today-double-data-00001.dat')

        # D: Test that the expected capture file exists.
        actual_result = os.path.exists(expected_capture_file_path)
        self.assertTrue(actual_result, "[D] The expected capture file does not exist.")

        # Read the contents of the captured file.
        data_identifier, datestamp, raw_data = self.read_file(expected_capture_file_path)

        # E: Test that the data identifier is as expected.
        actual_result = data_identifier
        expected_result = 'IN PLAY DATA'
        self.assertEqual(actual_result, expected_result, "[E] The actual result doesn't match the expected result.")

        # F: Test that the date stamp is as expected.
        actual_result = len(datestamp)
        expected_result = 26
        self.assertEqual(actual_result, expected_result, "[F] The actual result doesn't match the expected result.")

        # G: Test that the raw data is as expected.
        actual_result = raw_data
        expected_result = valid_raw_data
        self.assertEqual(actual_result, expected_result, "[G] The actual result doesn't match the expected result.")

        # Send non-live data to be captured.
        frame_type = NON_LIVE_DATA_FRAME
        self.sbo_data_source_replay.capture(valid_raw_data, frame_type)

        # H: Test that the expected capture file exists.
        expected_capture_file_path = os.path.join(expected_capture_path, 'today-double-data-00002.dat')
        actual_result = os.path.exists(expected_capture_file_path)
        self.assertTrue(actual_result, "[H] The expected capture file does not exist.")

        # Read the contents of the captured file.
        data_identifier, datestamp, raw_data = self.read_file(expected_capture_file_path)

        # I: Test that the data identifier is as expected.
        actual_result = data_identifier
        expected_result = 'NOT IN PLAY DATA'
        self.assertEqual(actual_result, expected_result, "[I] The actual result doesn't match the expected result.")

        # Send empty data to be captured.
        raw_data = ''
        self.sbo_data_source_replay.capture(raw_data, valid_frame_type)

        # J: Test that the expected capture file exists.
        expected_capture_file_path = os.path.join(expected_capture_path, 'today-double-data-00003.dat')
        actual_result = os.path.exists(expected_capture_file_path)
        self.assertTrue(actual_result, "[J] The expected capture file does not exist.")

        # Read the contents of the captured file.
        data_identifier, datestamp, raw_data = self.read_file(expected_capture_file_path)

        # K: Test that the data identifier is as expected.
        actual_result = data_identifier
        expected_result = 'CONNECTION TO SERVER LOST'
        self.assertEqual(actual_result, expected_result, "[K] The actual result doesn't match the expected result.")

        # Archived capture folders are date stamped to the nearest second.
        # Allow some time to pass before archiving again to avoid trying to overwrite previous results.
        seconds = 2
        debug.message(debug_flags.TEST_SBO_DATA_SOURCE_REPLAY, debug.TESTUNIT, "Waiting for %s seconds..." % seconds)
        time.sleep(seconds)

        # Create a temporary instance of the class.
        # Force the Capture file number to a high value to check how the class handles running out of numbers.
        temp_sbo_data_source_replay = SboDataSourceReplay()
        temp_sbo_data_source_replay.replay_file_number[CAPTURE_FILE] = 99997

        # Call the Capture method 4 times to ensure the class runs out of Capture file numbers.
        # On the first call, the start number will be incremented and filename 'today-double-data-99998.dat' should be used.
        # On the second call, 'today-double-data-99999.dat' should be used. This is the last available file name.
        # On any subsequent calls, data should not be captured.
        # A warning should be displayed on the console and the application should not crash.
        temp_sbo_data_source_replay.capture(valid_raw_data, valid_frame_type)
        temp_sbo_data_source_replay.capture(valid_raw_data, valid_frame_type)
        temp_sbo_data_source_replay.capture(valid_raw_data, valid_frame_type)
        temp_sbo_data_source_replay.capture(valid_raw_data, valid_frame_type)

        # Get a list of filenames in the current capture directory.
        current_filenames = os.listdir(self.capture_current_path)

        # L: Test that the current capture directory contains the expected files.
        actual_result = sorted(current_filenames)
        expected_result = ['today-double-data-99998.dat', 'today-double-data-99999.dat']
        self.assertListEqual(actual_result, expected_result, "[L] The actual result doesn't match the expected result.")


    @unittest.skipIf(SKIP_TEST_03, "in development")
    def test_03_initalise_playback(self):

        """Test the initialisation of playback."""

        debug.message(debug_flags.TEST_SBO_DATA_SOURCE_REPLAY, debug.TESTUNIT, "STARTING %s:" % "test_03_initalise_playback")

        # A: Test that playback is not available before initialisation.
        actual_result = self.sbo_data_source_replay.playback_initialised()
        expected_result = False
        self.assertEqual(actual_result, expected_result, "[A] The actual result doesn't match the expected result.")

        # B: Test that the playback() method raises an error when called before initialisation.
        self.assertRaises(SboDataSourceReplay.CallOrderError, self.sbo_data_source_replay.playback)

        # C: Test that the reinitialise_playback() method raises an error when called before initialisation.
        self.assertRaises(SboDataSourceReplay.CallOrderError, self.sbo_data_source_replay.reinitialise_playback)

        # Define valid parameters.
        replay_folder_path = 'test_data/playback_files/set_003'
        replay_mode = NORMAL_REPLAY_MODE
        minimum_request_period = [datetime.timedelta(seconds = MINIMUM_REQUEST_PERIOD_LIVE), datetime.timedelta(seconds = MINIMUM_REQUEST_PERIOD_NON_LIVE)]

        # D: Test that the method can cope with invalid inputs by raising an exception.
        for number, invalid_replay_folder_path in enumerate(self.test_types, start=1):

            # Test type 6 is a valid values of replay folder path.
            if number == 6:
                continue

            debug.message(debug_flags.TEST_SBO_DATA_SOURCE_REPLAY_EXTRA, debug.TESTUNIT, "Testing replay folder path with invalid type %s of %s." % (number, len(self.test_types)))
            self.assertRaises(SboDataSourceReplay.PlaybackInitialisationError, self.sbo_data_source_replay.initalise_playback, invalid_replay_folder_path, replay_mode, minimum_request_period)

        # Note: If an unexpected type is used for the replay mode parameter, it will be replaced with a default replay mode.
        # Skipping replay mode type test.

        # E: Test that the method can cope with invalid inputs by raising an exception.
        for number, invalid_minimum_request_period in enumerate(self.test_types, start=1):

            debug.message(debug_flags.TEST_SBO_DATA_SOURCE_REPLAY_EXTRA, debug.TESTUNIT, "Testing minimum request period with invalid type %s of %s." % (number, len(self.test_types)))
            self.assertRaises(SboDataSourceReplay.PlaybackInitialisationError, self.sbo_data_source_replay.initalise_playback, replay_folder_path, replay_mode, invalid_minimum_request_period)

        # F: Test that the method can cope with invalid inputs by raising an exception.
        for number, invalid_minimum_request_period_value in enumerate(self.test_types, start=1):

            # Initialise playback with invalid minimum request period values.
            invalid_minimum_request_period = [invalid_minimum_request_period_value, invalid_minimum_request_period_value]

            debug.message(debug_flags.TEST_SBO_DATA_SOURCE_REPLAY_EXTRA, debug.TESTUNIT, "Testing minimum request period value with invalid type %s of %s." % (number, len(self.test_types)))
            self.assertRaises(SboDataSourceReplay.PlaybackInitialisationError, self.sbo_data_source_replay.initalise_playback, replay_folder_path, replay_mode, invalid_minimum_request_period)

        # Attempt to successfully initialise the playback() method.
        self.sbo_data_source_replay.initalise_playback(replay_folder_path, replay_mode, minimum_request_period)

        # G: Test that the initialisation of playback was successful.
        actual_result = self.sbo_data_source_replay.playback_initialised()
        expected_result = True
        self.assertEqual(actual_result, expected_result, "[G] The actual result doesn't match the expected result.")


    @unittest.skipIf(SKIP_TEST_04, "in development")
    def test_04_playback_normal(self):

        """Test the playback of captured data files in normal replay mode."""

        debug.message(debug_flags.TEST_SBO_DATA_SOURCE_REPLAY, debug.TESTUNIT, "STARTING %s:" % "test_04_playback_normal")

        replay_mode = NORMAL_REPLAY_MODE
        minimum_request_period = [datetime.timedelta(seconds = MINIMUM_REQUEST_PERIOD_LIVE), datetime.timedelta(seconds = MINIMUM_REQUEST_PERIOD_NON_LIVE)]

        # Attempt to successfully initialise the playback() method.
        # Folder 'set_001' is empty.
        empty_replay_folder_path = 'test_data/playback_files/set_001'
        self.sbo_data_source_replay.initalise_playback(empty_replay_folder_path, replay_mode, minimum_request_period)

        # A: Test that trying to play back from an empty directory raises an exception.
        self.assertRaises(SboDataSourceReplay.EndOfReplay, self.sbo_data_source_replay.playback)

        # Attempt to successfully initialise the playback() method.
        # The file in the 'set_002' folder has a corrupt data identifier.
        corrupt_replay_folder_path = 'test_data/playback_files/set_002'
        self.reset_playback(corrupt_replay_folder_path, replay_mode, minimum_request_period)

        # B: Test that the method raises an error when reading a corrupt file.
        self.assertRaises(SboDataSourceReplay.PlaybackError, self.sbo_data_source_replay.playback)

        # After playback raises an error, it requires the initalise_playback() method to be called again.

        # C: Test that the playback() method raises an error when called before initialisation.
        self.assertRaises(SboDataSourceReplay.CallOrderError, self.sbo_data_source_replay.playback)

        # Attempt to successfully initialise the playback() method.
        # The 'set_003' folder contains a series of valid playback files.
        replay_folder_path = 'test_data/playback_files/set_003'
        self.reset_playback(replay_folder_path, replay_mode, minimum_request_period)

        # Attempt to playback data file 1.
        raw_data = self.sbo_data_source_replay.playback()

        # D: Test that the length of the returned raw data is as expected for data file 1.
        actual_result = len(raw_data)
        expected_result = 1003
        self.assertEqual(actual_result, expected_result, "[D] The actual result doesn't match the expected result.")

        # Attempt to playback data file 2.
        # This is the first file containing non-live data so can be played back straight away.
        # Note that if it contained live data, it could not be played back until the minimum request period had elapsed.
        raw_data = self.sbo_data_source_replay.playback()

        # E: Test that the length of the returned raw data is as expected for data file 2.
        actual_result = len(raw_data)
        expected_result = 59
        self.assertEqual(actual_result, expected_result, "[E] The actual result doesn't match the expected result.")

        # Attempt to playback data file 3.
        # This is a file containing live data and not enough time has elapsed since the last file was read.
        raw_data = self.sbo_data_source_replay.playback()

        # F: Test that no raw data is returned.
        actual_result = raw_data
        expected_result = None
        self.assertEqual(actual_result, expected_result, "[F] The actual result doesn't match the expected result.")

        # Wait the minimum required time, plus a safety margin and try again.
        seconds = MINIMUM_REQUEST_PERIOD_LIVE + SAFETY_MARGIN
        debug.message(debug_flags.TEST_SBO_DATA_SOURCE_REPLAY, debug.TESTUNIT, "Waiting for %s seconds..." % seconds)
        time.sleep(seconds)

        # Attempt to playback data file 3.
        raw_data = self.sbo_data_source_replay.playback()

        # G: Test that the length of the returned raw data is as expected for data file 3.
        actual_result = len(raw_data)
        expected_result = 50
        self.assertEqual(actual_result, expected_result, "[G] The actual result doesn't match the expected result.")

        # Get the last date stamp which should be for data file 3.
        datestamp_3 = self.sbo_data_source_replay.get_last_datestamp()

        # H: Test that the length of the returned raw data is as expected for data file 3.
        actual_result = len(datestamp_3)
        expected_result = 26
        self.assertEqual(actual_result, expected_result, "[H] The actual result doesn't match the expected result.")

        # Attempt to playback data file 4.
        # This is a file containing non-live data and not enough time has elapsed since the last file was read.
        raw_data = self.sbo_data_source_replay.playback()

        # I: Test that no raw data is returned.
        actual_result = raw_data
        expected_result = None
        self.assertEqual(actual_result, expected_result, "[I] The actual result doesn't match the expected result.")

        # Wait the minimum required time, plus a safety margin and try again.
        seconds = MINIMUM_REQUEST_PERIOD_NON_LIVE + SAFETY_MARGIN
        debug.message(debug_flags.TEST_SBO_DATA_SOURCE_REPLAY, debug.TESTUNIT, "Waiting for %s seconds..." % seconds)
        time.sleep(seconds)

        # Attempt to playback data file 4.
        raw_data = self.sbo_data_source_replay.playback()

        # J: Test that the length of the returned raw data is as expected for data file 4.
        actual_result = len(raw_data)
        expected_result = 67
        self.assertEqual(actual_result, expected_result, "[J] The actual result doesn't match the expected result.")

        # Get the last date stamp which should be for data file 4.
        datestamp_4 = self.sbo_data_source_replay.get_last_datestamp()

        # K: Test that the length of the returned raw data is as expected for data file 4.
        actual_result = len(datestamp_4)
        expected_result = 26
        self.assertEqual(actual_result, expected_result, "[K] The actual result doesn't match the expected result.")

        # L: Test the last two date stamps are not identical.
        self.assertNotEqual(datestamp_3, datestamp_4, "[L] The last two date stamps are identical.")

        # Attempt to playback data file 5.
        # This is a file containing no data and is marked with connection to server lost.

        # M: Test that a simulated connection error is raised.
        self.assertRaises(SboDataSourceReplay.SimulatedConnectionError, self.sbo_data_source_replay.playback)

        # N: Test that the previous connection error has cause playback to become unavailable.
        actual_result = self.sbo_data_source_replay.playback_initialised()
        expected_result = False
        self.assertEqual(actual_result, expected_result, "[N] The actual result doesn't match the expected result.")


    @unittest.skipIf(SKIP_TEST_05, "in development")
    def test_05_playback_fast(self):

        """Test the playback of captured data files in fast replay mode."""

        debug.message(debug_flags.TEST_SBO_DATA_SOURCE_REPLAY, debug.TESTUNIT, "STARTING %s:" % "test_05_playback_fast")

        # In Fast Replay Mode, the minimum request periods should be ignored.
        # This means that playback should always return data without having to wait.

        # Define the parameters for fast replay mode.
        replay_folder_path = 'test_data/playback_files/set_003'
        replay_mode = FAST_REPLAY_MODE
        minimum_request_period = [datetime.timedelta(seconds = MINIMUM_REQUEST_PERIOD_LIVE), datetime.timedelta(seconds = MINIMUM_REQUEST_PERIOD_NON_LIVE)]

        # Attempt to successfully initialise the playback() method.
        self.reset_playback(replay_folder_path, replay_mode, minimum_request_period)

        # Attempt to playback data file 1.
        raw_data = self.sbo_data_source_replay.playback()

        # A: Test that the length of the returned raw data is as expected for data file 1.
        actual_result = len(raw_data)
        expected_result = 1003
        self.assertEqual(actual_result, expected_result, "[A] The actual result doesn't match the expected result.")

        # Attempt to playback data file 2.
        raw_data = self.sbo_data_source_replay.playback()

        # B: Test that the length of the returned raw data is as expected for data file 2.
        actual_result = len(raw_data)
        expected_result = 59
        self.assertEqual(actual_result, expected_result, "[B] The actual result doesn't match the expected result.")

        # Attempt to playback data file 3.
        raw_data = self.sbo_data_source_replay.playback()

        # C: Test that the length of the returned raw data is as expected for data file 3.
        actual_result = len(raw_data)
        expected_result = 50
        self.assertEqual(actual_result, expected_result, "[C] The actual result doesn't match the expected result.")

        # Attempt to playback data file 4.
        raw_data = self.sbo_data_source_replay.playback()

        # D: Test that the length of the returned raw data is as expected for data file 4.
        actual_result = len(raw_data)
        expected_result = 67
        self.assertEqual(actual_result, expected_result, "[D] The actual result doesn't match the expected result.")

        # Create a temporary instance of the class.
        # Force the Playback file number to a high value to check how the class handles running out of numbers.
        temp_sbo_data_source_replay = SboDataSourceReplay()
        temp_sbo_data_source_replay.replay_file_number[PLAYBACK_FILE] = 99996

        # Define the parameters for fast replay mode.
        replay_folder_path = 'test_data/playback_files/set_004'
        replay_mode = FAST_REPLAY_MODE
        minimum_request_period = [datetime.timedelta(seconds = MINIMUM_REQUEST_PERIOD_LIVE), datetime.timedelta(seconds = MINIMUM_REQUEST_PERIOD_NON_LIVE)]

        # Attempt to successfully initialise the playback() method.
        temp_sbo_data_source_replay.initalise_playback(replay_folder_path, replay_mode, minimum_request_period)

        # Attempt to playback data file 99997.
        raw_data = temp_sbo_data_source_replay.playback()

        # E: Test that the length of the returned raw data is as expected for data file 99997.
        actual_result = len(raw_data)
        expected_result = 1115
        self.assertEqual(actual_result, expected_result, "[E] The actual result doesn't match the expected result.")

        # Attempt to playback data file 99998.
        raw_data = temp_sbo_data_source_replay.playback()

        # F: Test that the length of the returned raw data is as expected for data file 99998.
        actual_result = len(raw_data)
        expected_result = 59
        self.assertEqual(actual_result, expected_result, "[F] The actual result doesn't match the expected result.")

        # Attempt to playback data file 99999.
        raw_data = temp_sbo_data_source_replay.playback()

        # G: Test that the length of the returned raw data is as expected for data file 99999.
        actual_result = len(raw_data)
        expected_result = 60
        self.assertEqual(actual_result, expected_result, "[G] The actual result doesn't match the expected result.")

        # H: Test that trying to read again after reaching the limit raises an EndOfReplay exception.
        self.assertRaises(SboDataSourceReplay.EndOfReplay, temp_sbo_data_source_replay.playback)


if __name__ == "__main__":
    unittest.main()
