#!/usr/local/bin/python3.2
# coding: utf-8

"""This module implements the SboDataSourceReplay class."""

import debug
import debug_flags
import os
import re
import datetime

# Capture folder paths and filenames.
CAPTURE_FOLDER = 'sbo_data_captured'
CAPTURE_CURRENT_SUBFOLDER = 'current'
CAPTURE_ARCHIVE_SUBFOLDER_PREFIX = 'up_to_restart_at_'
CAPTURE_FILENAME_TEMPLATE = 'today-double-data-nnnnn.dat'

# Data frames.
LIVE_DATA_FRAME = 0
NON_LIVE_DATA_FRAME = 1

# Data identifiers.
NO_DATA = 'CONNECTION TO SERVER LOST'
LIVE_DATA = 'IN PLAY DATA'
NON_LIVE_DATA = 'NOT IN PLAY DATA'

# Replay modes.
NORMAL_REPLAY_MODE = 0
FAST_REPLAY_MODE = 1
DEFAULT_REPLAY_MODE = FAST_REPLAY_MODE
REPLAY_MODE_DESCRIPTION = ['Normal Replay Mode', 'Fast Replay Mode']

# File types.
CAPTURE_FILE = 0
PLAYBACK_FILE = 1

# File contents indexes.
DATA_IDENTIFIER = 0
RAW_DATA = 1

# Initial states.
INITIAL_CAPTURE_FILE_NUMBER = 0
INITIAL_PLAYBACK_FILE_NUMBER = 0
INITIAL_LAST_LIVE_FILE_PLAYED_BACK = None
INITIAL_LAST_NON_LIVE_FILE_PLAYED_BACK = None
INITIAL_DATA_IDENTIFIER = None
INITIAL_RAW_DATA = None

# General constants.
FILE_NUMBER_DIGITS = 5
FILE_NUMBER_MAX = (10 ** FILE_NUMBER_DIGITS) - 1


class SboDataSourceReplay(object): # pylint: disable-msg=R0902

    """This class manages SboDataSourceReplay operations."""

    # Exceptions that this class may raise.
    class DataCaptureError(Exception):

        """Raised when an exception is encountered while trying to save raw data to a file."""
        pass

    class PlaybackInitialisationError(Exception):

        """Raised when an exception is encountered during the initialise_playback() method."""
        pass

    class CallOrderError(Exception):

        """Raised when a method is called out of order, usually before playback initialisation."""
        pass

    class FileReadError(Exception):

        """Raised when an exception is encountered during trying to read a captured replay file."""
        pass

    class EndOfReplay(Exception):

        """Raised when the next file in the specified path can not be found."""
        pass

    class PlaybackError(Exception):

        """Raised when an exception is encountered during playing back a captured data file."""
        pass

    class SimulatedConnectionError(Exception):

        """Raised when a data file is encountered with a data identifier indicating simulated connection failure."""
        pass


    # Class methods
    def __init__(self):

        debug.message(debug_flags.SBO_DATA_SOURCE_REPLAY_INFOS, debug.INFO, "%s: %s" % (SboDataSourceReplay.__name__, "__init__"))

        # The base directory contains the script that was used to invoke the Python interpreter.
        self.base_directory = os.sys.path[0]

        self.capture_limit = False
        self.first_capture = True

        self.replay_file_number = [INITIAL_CAPTURE_FILE_NUMBER, INITIAL_PLAYBACK_FILE_NUMBER]
        self.replay_folder_path = None
        self.replay_mode = None
        self.minimum_request_period_live = None
        self.minimum_request_period_non_live = None

        self.playback_previously_initialised_flag = False
        self.playback_initialised_flag = False
        self.last_file_played_back = [INITIAL_LAST_LIVE_FILE_PLAYED_BACK, INITIAL_LAST_NON_LIVE_FILE_PLAYED_BACK]
        self.load_next_file_for_playback = True
        self.file_contents = [INITIAL_DATA_IDENTIFIER, INITIAL_RAW_DATA]
        self.last_datestamp = None


    def _create_new_capture_folder(self):

        """This private method ensures that the necessary folder structure is in place for capturing raw data files.

        This simple method has no arguments or returns.
        It raises no errors.
        """
        debug.message(debug_flags.SBO_DATA_SOURCE_REPLAY_INFOS, debug.INFO, "%s: %s" % (SboDataSourceReplay.__name__, "_create_new_capture_folder"))

        # Ensure a folder exists to capture raw data to.
        capture_folder_path = os.path.join(self.base_directory, CAPTURE_FOLDER)

        if not os.path.exists(capture_folder_path):
            os.mkdir(capture_folder_path)

        debug.message(debug_flags.SBO_DATA_SOURCE_REPLAY_INFOS, debug.INFO, "Full path of capture root folder: '%s'" % capture_folder_path)

        # Ensure a sub-folder exists to capture raw data to.
        capture_current_path = os.path.join(capture_folder_path, CAPTURE_CURRENT_SUBFOLDER)

        if os.path.exists(capture_current_path):

            # If any raw data has previously been captured, the folder needs to be date stamped and archived.
            datestamp = datetime.datetime.now().strftime('%Y-%m-%d-%H-%M-%S')
            capture_archive_subfolder = CAPTURE_ARCHIVE_SUBFOLDER_PREFIX + datestamp

            capture_archive_path = os.path.join(capture_folder_path, capture_archive_subfolder)

            debug.message(debug_flags.SBO_DATA_SOURCE_REPLAY_INFOS, debug.INFO, "capture_archive_path: %s" % capture_archive_path)

            # Archive the previous folder.
            os.rename(capture_current_path, capture_archive_path)

        # Either the capture folder doesn't exist yet or it has just been archived.
        os.mkdir(capture_current_path)

        self.first_capture = False


    def _get_next_filename(self, file_type):

        """This private method keeps track of and returns the file name of the next capture or playback file that can be written to.

        Args: file_type(integer), eg: either CAPTURE_FILE or PLAYBACK_FILE.
        Returns: filename(string)
        Raises: EndOfReplay
        """
        debug.message(debug_flags.SBO_DATA_SOURCE_REPLAY_INFOS, debug.INFO, "%s: %s" % (SboDataSourceReplay.__name__, "_get_next_filename"))

        # Capture and Playback files are numbered sequentially starting at One.
        self.replay_file_number[file_type] = self.replay_file_number[file_type] + 1

        # Once the file number for a Capture file has reached the maximum allowed, set a flag.
        # With the flag is set, this method will return the last Capture filename to be used.
        if file_type == CAPTURE_FILE and self.replay_file_number[file_type] == FILE_NUMBER_MAX:
            self.capture_limit = True

        # Once the file number for a Playback file has gone over the maximum allowed, raise an exception.
        if file_type == PLAYBACK_FILE and self.replay_file_number[file_type] > FILE_NUMBER_MAX:
            raise SboDataSourceReplay.EndOfReplay("Can not playback more than %s files." % FILE_NUMBER_MAX)

        formatted_capture_file_number = str(self.replay_file_number[file_type]).zfill(FILE_NUMBER_DIGITS)

        # The capture filename template holds the filename of the capture data files with a dummy file number.
        # This statement replaces the 'nnnnn' in the dummy file with the real number, calculated above.
        filename = re.sub(r'n{5}', formatted_capture_file_number, CAPTURE_FILENAME_TEMPLATE)

        return filename


    def capture(self, raw_data, frame_type):

        """This public method writes the given raw data to a file.

        The next available capture file number is determined and the file is created.
        The raw data passed to this method is identified and a data identifier code is written to the file.
        After that, the current date and time is written and then the raw data its self.

        Args:
            raw_data: A string of raw data to be captured.
            frame_type: An integer which specifies if the raw data represents live or non-live betting data.

        Returns:
            None

        Raises:
            DataCaptureError: Raised on an error creating a new capture folder,
                an inability to identify the incoming raw data,
                the detection of invalid raw data
                or the failure to write a file to the server.
        """
        debug.message(debug_flags.SBO_DATA_SOURCE_REPLAY_INFOS, debug.INFO, "%s: %s" % (SboDataSourceReplay.__name__, "capture"))

        # The number of files captures has reached the limit.
        if self.capture_limit:
            debug.message(debug_flags.SBO_DATA_SOURCE_REPLAY_WARNINGS, debug.WARNING, "%s: Can not capture more than %s files." % (SboDataSourceReplay.__name__, FILE_NUMBER_MAX))
            return

        # The first capture flag is set on instantiation of this class.
        # After the new capture folder is created the flag is cleared.
        if self.first_capture:
            try:
                self._create_new_capture_folder()

            except OSError as exception_instance:
                raise SboDataSourceReplay.DataCaptureError("capture() experienced %s: %s" % (type(exception_instance).__name__, exception_instance))

        # The data identifier is useful when analysing the data files.
        if raw_data == '':
            data_identifier = NO_DATA

        elif frame_type == LIVE_DATA_FRAME:
            data_identifier = LIVE_DATA

        elif frame_type == NON_LIVE_DATA_FRAME:
            data_identifier = NON_LIVE_DATA

        else:
            raise SboDataSourceReplay.DataCaptureError("Unable to identify raw data.")

        # The date stamp is useful when analysing the data files.
        datestamp = str(datetime.datetime.now())

        try:
            file_contents = data_identifier + '\n' + datestamp + '\n' + raw_data

        except TypeError as exception_instance:
            raise SboDataSourceReplay.DataCaptureError("capture() experienced %s: %s" % (type(exception_instance).__name__, exception_instance))

        capture_filename = self._get_next_filename(CAPTURE_FILE)
        capture_file_path = os.path.join(self.base_directory, CAPTURE_FOLDER, CAPTURE_CURRENT_SUBFOLDER, capture_filename)

        try:
            file_handle = open(capture_file_path, mode='w', encoding='utf-8')

            debug.message(debug_flags.SBO_DATA_SOURCE_REPLAY_INFOS, debug.INFO, "Writing raw data to: '%s/%s'" % (CAPTURE_CURRENT_SUBFOLDER, capture_filename))

            try:
                # Any failure here will be caught by the outer except.
                file_handle.write(file_contents)

            finally:
                # The file will get closed even if the above try causes an exception.
                file_handle.close()

        except IOError as exception_instance:
            raise SboDataSourceReplay.DataCaptureError("capture() experienced %s: %s" % (type(exception_instance).__name__, exception_instance))


    def playback_initialised(self):

        """This public method returns the playback initialised flag which is set only when playback is initialised.

        Returns:
            playback_initialised_flag: A boolean representation of the initialised state of playback.

        This simple method has no arguments and raises no errors.
        """
        debug.message(debug_flags.SBO_DATA_SOURCE_REPLAY_INFOS, debug.INFO, "%s: %s (%s)" % (SboDataSourceReplay.__name__, "playback_initialised", self.playback_initialised_flag))

        return self.playback_initialised_flag


    def playback_previously_initalised(self):

        """This public method returns a flag which indicates weather playback has been successfully initialised at least once.

        Returns:
            playback_previously_initialised_flag: A boolean representation of the former initialisation of playback.

        This simple method has no arguments and raises no errors.
        """
        debug.message(debug_flags.SBO_DATA_SOURCE_REPLAY_INFOS, debug.INFO, "%s: %s (%s)" % (SboDataSourceReplay.__name__, "playback_previously_initalised", self.playback_previously_initialised_flag))

        return self.playback_previously_initialised_flag


    def initalise_playback(self, replay_folder_path, replay_mode, minimum_request_period):

        """This public method ensures that the object is initialised ready for the playback() method to be called.

        This method initialises the replay folder path, establishes the replay mode and stores the minimum request periods
        ready to the playback function to be called.

        Args:
            replay_folder_path: A string representing the path of the folder containing files to be replayed.
            replay_mode: An integer representing either Normal or Fast replay mode.
            minimum_request_period: A list of minimum request periods used during normal playback to limit the frequency in which the data is played back.

        Returns:
            None

        Raises:
            PlaybackInitialisationError: Raised if invalid arguments are passed to this method,
                preventing it from initialising the required parameters ready for playback.
        """
        debug.message(debug_flags.SBO_DATA_SOURCE_REPLAY_INFOS, debug.INFO, "%s: %s" % (SboDataSourceReplay.__name__, "initalise_playback"))

        try:
            # If the replay folder path does not exist then playback can not be initialised.
            replay_folder_path = os.path.join(self.base_directory, replay_folder_path)

        except AttributeError as exception_instance:
            raise SboDataSourceReplay.PlaybackInitialisationError("initalise_playback() experienced %s: %s" % (type(exception_instance).__name__, exception_instance))

        if not os.path.exists(replay_folder_path):
            self.playback_initialised_flag = False
            raise SboDataSourceReplay.PlaybackInitialisationError("Can not initialise playback, invalid replay folder given. '%s'" % replay_folder_path)

        # This folder specifies the path of the files to be played back.
        self.replay_folder_path = replay_folder_path
        debug.message(debug_flags.SBO_DATA_SOURCE_REPLAY_INFOS, debug.INFO, "Specified replay folder: '%s'" % self.replay_folder_path)

        # Fast replay mode allows the minimum request periods to be ignored during playback.
        if replay_mode == NORMAL_REPLAY_MODE:
            self.replay_mode = NORMAL_REPLAY_MODE

        elif replay_mode == FAST_REPLAY_MODE:
            self.replay_mode = FAST_REPLAY_MODE

        else:
            self.replay_mode = DEFAULT_REPLAY_MODE

        debug.message(debug_flags.SBO_DATA_SOURCE_REPLAY_INFOS, debug.INFO, "%s specified." % REPLAY_MODE_DESCRIPTION[self.replay_mode])

        try:
            # The minimum request periods are used during normal playback to limit the frequency in which the data can be played back.
            self.minimum_request_period_live = minimum_request_period[LIVE_DATA_FRAME]
            self.minimum_request_period_non_live = minimum_request_period[NON_LIVE_DATA_FRAME]

        except (TypeError, IndexError, KeyError) as exception_instance:
            raise SboDataSourceReplay.PlaybackInitialisationError("initalise_playback() experienced %s: %s" % (type(exception_instance).__name__, exception_instance))

        try:
            # Ensure that the minimum request periods are valid timedelta objects.
            # Attempt to call the total_seconds() attribute as this will only succeed on a timedelta object.
            self.minimum_request_period_live.total_seconds()
            self.minimum_request_period_non_live.total_seconds()

        except AttributeError as exception_instance:
            raise SboDataSourceReplay.PlaybackInitialisationError("initalise_playback() experienced %s: %s" % (type(exception_instance).__name__, exception_instance))

        self.playback_initialised_flag = True
        self.playback_previously_initialised_flag = True


    def reinitialise_playback(self):

        """This public method is called to re-initialise certain attributes ready for the playback() method to be called again.

        Raises:
            CallOrderError: Raised if playback has not previously been initialised.

        This simple method has no arguments and no returns.
        """
        debug.message(debug_flags.SBO_DATA_SOURCE_REPLAY_INFOS, debug.INFO, "%s: %s" % (SboDataSourceReplay.__name__, "reinitialise_playback"))

        if not self.playback_previously_initialised_flag:
            raise SboDataSourceReplay.CallOrderError("The reinitalise_playback() method was called before the initialise_playback() method.")

        # Re-initialise the playback attributes.
        self.last_file_played_back = [INITIAL_LAST_LIVE_FILE_PLAYED_BACK, INITIAL_LAST_NON_LIVE_FILE_PLAYED_BACK]
        self.replay_file_number[PLAYBACK_FILE] = INITIAL_PLAYBACK_FILE_NUMBER
        self.load_next_file_for_playback = True
        self.file_contents = [INITIAL_DATA_IDENTIFIER, INITIAL_RAW_DATA]

        self.playback_initialised_flag = True


    def playback(self):

        """This public method returns the contents of the next available replay file.

        The method looks in the replay folder setup during playback initialisation and attempts to read data from
        each file in turn. On reading the file data the data identifier that was encoded into the file during capture is
        read and the data is handled accordingly.
        The replay mode and minimum request periods specified during initialisation are observed.

        Args: None

        Returns:
            raw_data: A string of raw data retrieved from the replay file.

        Raises:
            CallOrderError: Raised if playback has not previously been initialised.
            EndOfReplay: Raised when all the replay files in the specified folder have been played back.
            FileReadError: Raised if an error is encountered while attempting to read the file contents of a replay file.
            SimulatedConnectionError: Raised when the data identifier of a replay file indicated no data. Used only during testing.
            PlaybackError: Raised when a reply file with an unknown data identifier is discovered.
        """
        debug.message(debug_flags.SBO_DATA_SOURCE_REPLAY_INFOS, debug.INFO, "%s: %s" % (SboDataSourceReplay.__name__, "playback"))

        if not self.playback_initialised_flag:
            raise SboDataSourceReplay.CallOrderError("The playback() method was called before the initialise_playback() method.")

        if self.load_next_file_for_playback:

            playback_filename = self._get_next_filename(PLAYBACK_FILE)
            replay_file_path = os.path.join(self.replay_folder_path, playback_filename)

            if not os.path.exists(replay_file_path):

                self.playback_initialised_flag = False
                raise SboDataSourceReplay.EndOfReplay("Can not find file '%s' in folder '%s'" % (playback_filename, self.replay_folder_path))

            try:
                file_handle = open(replay_file_path, mode='r', encoding='utf-8')

                debug.message(debug_flags.SBO_DATA_SOURCE_REPLAY_INFOS, debug.INFO, "Opening file for playback: '%s'" % replay_file_path)

                try:
                    # Any failure here will be caught by the outer except.

                    data_identifier = file_handle.readline().rstrip('\n')
                    datestamp = file_handle.readline().rstrip('\n')
                    captured_raw_data = file_handle.readline()

                    # If the file was captured with no raw data it should already have the No Data identifier.
                    # But if it has been modified it may not.
                    if captured_raw_data == '':
                        data_identifier = NO_DATA

                    # Raw data will only be returned form this function if certain conditions are met.
                    # If these conditions are not met this time, they may be met on future calls to this function.
                    # Store the data identifier and captured raw data until the next file is loaded.
                    self.file_contents = [data_identifier, captured_raw_data]

                finally:
                    # The file will get closed even if the above try causes an exception.
                    file_handle.close()

            except IOError as exception_instance:
                raise SboDataSourceReplay.FileReadError("playback() experienced %s: %s" % (type(exception_instance).__name__, exception_instance))

            debug.message(debug_flags.SBO_DATA_SOURCE_REPLAY_INFOS, debug.INFO, "Data Identifier: %s" % data_identifier)
            debug.message(debug_flags.SBO_DATA_SOURCE_REPLAY_INFOS, debug.INFO, "Date stamp: %s" % datestamp)

            # Keep track of the date stamp of the last valid raw data file to be opened.
            if data_identifier == LIVE_DATA or data_identifier == NON_LIVE_DATA:
                self.last_datestamp = datestamp

            self.load_next_file_for_playback = False

        # If non of the following conditions are met then raw data will be returned as None.
        raw_data = None

        # In Fast Replay Mode, data can be read at any time.
        # In Normal Replay Mode, data can not be read more frequent than the minimum request period.

        if self.file_contents[DATA_IDENTIFIER] == LIVE_DATA:

            if (self.replay_mode == FAST_REPLAY_MODE or
                self.replay_mode == NORMAL_REPLAY_MODE and
                (self.last_file_played_back[LIVE_DATA_FRAME] is None or
                 (datetime.datetime.now() - self.last_file_played_back[LIVE_DATA_FRAME]) > self.minimum_request_period_live)):

                raw_data = self.file_contents[RAW_DATA]

                # The date stamp makes it possible for the class to know when live raw data was last returned.
                self.last_file_played_back[LIVE_DATA_FRAME] = datetime.datetime.now()
                self.load_next_file_for_playback = True

            else:
                debug.message(debug_flags.SBO_DATA_SOURCE_REPLAY_INFOS, debug.INFO, "Tried to playback live replay data file before minimum request period expired.")

        elif self.file_contents[DATA_IDENTIFIER] == NON_LIVE_DATA:

            if (self.replay_mode == FAST_REPLAY_MODE or
                self.replay_mode == NORMAL_REPLAY_MODE and
                (self.last_file_played_back[NON_LIVE_DATA_FRAME] is None or
                 (datetime.datetime.now() - self.last_file_played_back[NON_LIVE_DATA_FRAME]) > self.minimum_request_period_non_live)):

                raw_data = self.file_contents[RAW_DATA]

                # The date stamp makes it possible for the class to know when non-live raw data was last returned.
                self.last_file_played_back[NON_LIVE_DATA_FRAME] = datetime.datetime.now()
                self.load_next_file_for_playback = True

            else:
                debug.message(debug_flags.SBO_DATA_SOURCE_REPLAY_INFOS, debug.INFO, "Tried to playback non-live replay data file before minimum request period expired.")

        elif self.file_contents[DATA_IDENTIFIER] == NO_DATA:

            # This identifier simulates a SBO server connection error.
            # This method must be re-initialised before it can be used again.
            self.playback_initialised_flag = False

            raise SboDataSourceReplay.SimulatedConnectionError("Simulated SBO server connection error.")

        else:

            # A file with an unknown Data Identifier will not be read.
            # This method must be re-initialised before it can be used again.
            self.playback_initialised_flag = False

            raise SboDataSourceReplay.PlaybackError("Unknown Data Identifier: '%s'" % self.file_contents[DATA_IDENTIFIER])

        return raw_data


    def get_last_datestamp(self):

        """This public method returns the date stamp of the last raw data replay file to be loaded for playback.

        Returns:
            last_datestamp: A string representing a date stamp of the the last valid raw data file to be opened.

        This simple method has no arguments and raises no errors.
        """
        debug.message(debug_flags.SBO_DATA_SOURCE_REPLAY_INFOS, debug.INFO, "%s: %s (%s)" % (SboDataSourceReplay.__name__, "get_last_datestamp", self.last_datestamp))

        return self.last_datestamp
