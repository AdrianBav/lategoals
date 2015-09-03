#!/usr/local/bin/python3.2
# coding: utf-8

"""This module implements the SboDataSourceCache class."""

import debug
import debug_flags
import re
from datetime import datetime, timedelta
from data_source_base import DataSourceBase

# Data frames.
LIVE_DATA_FRAME = 0
NON_LIVE_DATA_FRAME = 1

# Frame Cache Data Array indexes.
TOURNAMENT_DICTIONARY = 0
EVENT_DICTIONARY = 1
EVENT_RESULT_DICTIONARY = 2
EVENT_RESULT_EXTRA_DICTIONARY = 3
EVENT_RESULT_LIST_FOR_DELETION = 4
ODDS_DICTIONARY = 5
ODDS_LIST_FOR_DELETION = 6
MARKET_GROUP_DICTIONARY = 7

# Tournament Dictionary indexes.
TORNAMENT_ID = 0
TORNAMENT_NAME = 1

# Event Dictionary indexes.
EVENT_ID = 0
EVENT_DICTIONARY_TORNAMENT_ID = 2
HOME_TEAM_NAME = 3
AWAY_TEAM_NAME = 4
EVENT_SORT_CODE = 5
SHOW_TIME_TYPE = 6
SHOW_TIME = 7

# Event Result Dictionary indexes.
EVENT_RESULT_ID = 0
EVENT_RESULT_DICTIONARY_EVENT_ID = 1
EVENT_RESULT_DICTIONARY_MARKET_GROUP_ID = 2
HOME_SCORE = 3
AWAY_SCORE = 4
ODDS_COUNT = 5

# Event Result Extra Dictionary indexes.
EVENT_RESULT_EXTRA_DICTIONARY_EVENT_RESULT_ID = 0
ROW_COUNT = 1
PERIOD = 2
CURRENT_MINUTES = 3
TOTAL_MINUTES = 4
HOME_RED_CARD_COUNT = 5
AWAY_RED_CARD_COUNT = 6
INJURY_TIME = 7

# Odds Dictionary indexes.
ODDS_ID = 0
ODDS_DATA_ARRAY = 1
PRICES_ARRAY = 2

# Market Group Dictionary indexes.
MARKET_GROUP_ID = 0
MARKET_GROUP_NAME = 1

# Odds Dictionary, Odds Data indexes.
ODDS_DICTIONARY_EVENT_RESULT_ID = 0
MARKET_DISPLAY_ID = 1
POINT = 4

# Odds Dictionary, Prices indexes.
PRICE_1 = 0
PRICE_2 = 1
PRICE_3 = 2

# Odds Dictionary, Odds Data, Market Display types.
FULL_TIME_HDP = 1
FULL_TIME_OU = 3
HALF_TIME_HDP = 7
HALF_TIME_OU = 9

# Match Stage states.
NOT_LIVE = 0
FIRST_HALF = 1
HALF_TIME = 2
SECOND_HALF = 3

# Match Stage Details indexes.
MATCH_STAGE = 0
FIRST_HALF_ELAPSED = 1
SECOND_HALF_ELAPSED = 2
#INJURY_TIME = 3

# Favourite Teams.
NEITHER_TEAM = 0
HOME_TEAM = 1
AWAY_TEAM = 2

# Show Time Types.
BLUE_LIVE = 0x8
RED_LIVE = 0x4
DATE_TIME = 0x2
DATE_STARS = 0x1

# Point Data indexes.
FORMATTED_POINT = 0
FAVOURITE_TEAM = 1

# Defaults
DEFAULT_EVENT_SORT_CODE = 0
DEFAULT_SHOW_TIME = datetime(1900, 1, 1)
DEFAULT_BETTING_AVAILABLE_IN_PLAY = 0

# Fetch Type.
FETCH_CREATED_EVENTS = 0
FETCH_MODIFIED_EVENTS = 1

# General Constants.
NEXT_LIST_ITEM = 0
NON_LIVE_SUB_EVENT_PREFIX = "1"
FAVOURITE_NOT_USED = 0
MARKET_GROUP_SEPERATOR = "-"
SECONDS_IN_A_MINUTE = 60

# Regular Expression Objects.
REGEX_SHOW_TIME = re.compile(r'(?P<month>\d{1,2})/(?P<day>\d{1,2})/(?P<year>\d{4}) (?P<hour>\d{1,2}):(?P<minute>\d{1,2})')


class SboDataSourceCache(object): # pylint: disable-msg=R0902

    """This class manages SboDataSourceCache operations.

    Notes:
      An SBO Tournament is equivalent to a JamBlob League.
      An SBO Event is equivalent to a JamBlob Match.
      An SBO Event Result ID is equivalent to a JamBlob Match ID.
    """

    class UnexpectedDataError(Exception):

        """Raised when trying to process unexpected data from the SBO server."""
        pass


    @staticmethod
    def _format_event_sort_code(event_sort_code):

        """This private method takes the event sort code parameter in its raw state and returns it in the required format.

        Args: event_sort_code(string)
        Returns: formatted_event_sort_code(integer)
        Raises: None
        """
        debug.message(debug_flags.SBO_DATA_SOURCE_CACHE_INFOS, debug.INFO, "%s: %s" % (SboDataSourceCache.__name__, "_format_event_sort_code"))

        formatted_event_sort_code = DEFAULT_EVENT_SORT_CODE

        # Only use the first five characters
        # Even codes can be in the form of, '1.304', '1.304F', '1.30435 A-', '1.30537 TIM'
        if len(event_sort_code) > 5:

            event_sort_code = event_sort_code[0:5]

        try:
            # The raw format of the event sort code is a number to 3 decimal places, represented as a string, ie: '1.789'
            formatted_event_sort_code = int(float(event_sort_code) * float(1000))

        except (TypeError, ValueError) as exception_instance:

            # Catch any TypeError or ValueErrors.
            debug.message(debug_flags.SBO_DATA_SOURCE_CACHE_WARNINGS, debug.WARNING, "_format_event_sort_code() experienced %s: %s" % (type(exception_instance).__name__, exception_instance))

        return formatted_event_sort_code


    @staticmethod
    def _format_point_value(point):

        """This private static method formats the point value and determines the favourite team.

        Args: point(integer)
        Returns: point_value(tuple), eg: (formatted_point, favourite_team)
        Raises: None
        """
        debug.message(debug_flags.SBO_DATA_SOURCE_CACHE_INFOS, debug.INFO, "%s: %s" % (SboDataSourceCache.__name__, "_format_point_value"))

        # The sign of the SBO servers Point parameter can be used to determine the favourite team.
        if point < 0:
            favourite_team = AWAY_TEAM

            # Now that the sign of the Point has been used, remove the minus sign so that it doesn't interfere with future calculations.
            point = abs(point)

        elif point == 0:
            favourite_team = NEITHER_TEAM

        else:
            favourite_team = HOME_TEAM

        # The Point parameter can represents a single number or a range of values.
        if (point % 0.5) == 0:

            # The resolution of the Point is 0.5 or more which means it represents a single value.
            formatted_point = str(point)

            # Ensure all single values end with a zero.
            if not formatted_point.endswith('0'):
                formatted_point += '0'

        else:

            # The SBO server can send Point values with a resolution 0.25.
            # These values represent a range plus or minus 0.25.
            min_point = str(point - 0.25)
            max_point = str(point + 0.25)

            # A range takes up more room to display and therefore values ending with .0 need to be trimmed.
            if min_point.endswith('.0'):
                min_point = min_point[:-2]

            if max_point.endswith('.0'):
                max_point = max_point[:-2]

            formatted_point = "%s-%s" % (min_point, max_point)

        return (formatted_point, favourite_team)


    @staticmethod
    def _get_betting_available_in_play(show_time_type):

        """This private method takes the show time parameter in its raw state and returns it in the required format.

        Args: show_time_type(integer)
        Returns: betting_available_in_play(integer)
        Raises: None
        """
        debug.message(debug_flags.SBO_DATA_SOURCE_CACHE_INFOS, debug.INFO, "%s: %s" % (SboDataSourceCache.__name__, "_get_betting_available_in_play"))

        betting_available_in_play = DEFAULT_BETTING_AVAILABLE_IN_PLAY

        try:
            if show_time_type & BLUE_LIVE:

                # The SBO site formats the TIME column as follows;
                # '_{showtime-hour}_:_{showtime-minute}_<br /><span class="NW">! <span class="Blue">Live </span></span>'

                # Essentially, live betting is allowed.
                betting_available_in_play = 1

            elif show_time_type & RED_LIVE:

                # The SBO site formats the TIME column as follows;
                # '_{showtime-hour}_:_{showtime-minute}_<br /><span class="NW">! <span class="Red">Live </span></span>'

                # Essentially, live betting is allowed.
                betting_available_in_play = 1

            elif show_time_type & DATE_TIME:

                # The SBO site formats the TIME column as follows;
                # '_{showtime-month}_/_{showtime-day}_<br />_{showtime-hour}_:_{showtime-minute}_'

                # Essentially, live betting is not allowed.
                betting_available_in_play = 0

            elif show_time_type & DATE_STARS:

                # The SBO site formats the TIME column as follows;
                # '_{showtime-month}_/_{showtime-day}_<br />**:**'

                # Essentially, live betting is not allowed.
                betting_available_in_play = 0

        except TypeError as exception_instance:

            # Catch any TypeErrors.
            debug.message(debug_flags.SBO_DATA_SOURCE_CACHE_WARNINGS, debug.WARNING, "_get_betting_available_in_play() experienced %s: %s" % (type(exception_instance).__name__, exception_instance))

        return betting_available_in_play


    @staticmethod
    def _get_next_line_number(line_number_dictionary, event_result_id, market_display_id):

        """This private method determines the next line number for a given Event ID and Market ID.

        Args: line_number_dict(dictionary), event_result_id(integer), event_result_id(integer)
        Returns: next_line_number(integer)
        Raises: None
        """
        debug.message(debug_flags.SBO_DATA_SOURCE_CACHE_INFOS, debug.INFO, "%s: %s" % (SboDataSourceCache.__name__, "_get_next_line_number"))

        # Generate a custom key unique to the event ID and market ID.
        event_market_key = str(event_result_id) + "-" + str(market_display_id)

        if event_market_key not in line_number_dictionary:
            next_line_number = 1

        else:
            next_line_number = line_number_dictionary[event_market_key] + 1

        # Store the current line number
        line_number_dictionary[event_market_key] = next_line_number

        return next_line_number


    # Class methods
    def __init__(self, frame_type, sbo_id, gmt_offset):

        debug.message(debug_flags.SBO_DATA_SOURCE_CACHE_INFOS, debug.INFO, "%s: %s" % (SboDataSourceCache.__name__, "__init__"))

        self.frame_type = frame_type
        self.sbo_id = sbo_id
        self.timedelta_gmt_offset = timedelta(hours = gmt_offset)

        self.current_minutes_cache = {}

        self.tournament_dictionary = {}
        self.event_dictionary = {}
        self.event_result_dictionary = {}
        self.event_result_extra_dictionary = {}
        self.odds_dictionary = {}
        self.market_group_dictionary = {}

        self.events_created = []
        self.events_updated = {}
        self.events_deleted = []


    def _get_affected_event_ids(self, tournament_id):

        """This private method returns a list of Event IDs that would be affected by an update to the specified Tournament ID.

        Args: tournament_id(integer)
        Returns: affected_event_ids(list)
        Raises: None
        """
        debug.message(debug_flags.SBO_DATA_SOURCE_CACHE_INFOS, debug.INFO, "%s: %s" % (SboDataSourceCache.__name__, "_get_affected_event_ids"))

        affected_event_ids = []

        # If an Event references the Tournament ID that is being updated, the Event is considered to be affected by the update.
        for event_id in self.event_dictionary:

            if self.event_dictionary[event_id]['tornament_id'] == tournament_id:
                affected_event_ids.append(event_id)

        return affected_event_ids


    def _get_affected_event_result_ids(self, id_index, id_value):

        """This private method returns a list of Event Result IDs that would be affected by an update to the specified Event Result.

        Args: id_index(string), id_value(integer)
        Returns: affected_event_result_ids(list)
        Raises: None
        """
        debug.message(debug_flags.SBO_DATA_SOURCE_CACHE_INFOS, debug.INFO, "%s: %s" % (SboDataSourceCache.__name__, "_get_affected_event_result_ids"))

        affected_event_result_ids = []

        # If an Event Result references the Event ID that is being updated, the Event Result is considered to be affected by the update.
        for event_result_id in self.event_result_dictionary:

            if self.event_result_dictionary[event_result_id][id_index] == id_value:
                affected_event_result_ids.append(event_result_id)

        return affected_event_result_ids


    def _update_tournament_dictionary(self, tournament_dictionary):

        """This private method updates the internal cache of tournament data.

        Args: tournament_dictionary(dictionary)
        Returns: None
        Raises: None
        """
        debug.message(debug_flags.SBO_DATA_SOURCE_CACHE_INFOS, debug.INFO, "%s: %s" % (SboDataSourceCache.__name__, "_update_tournament_dictionary"))

        for tournament in tournament_dictionary:

            tournament_id = tournament[TORNAMENT_ID]

            # Set a flag to indicate weather existing event details are being updated or new event details are being created.
            if tournament_id in self.tournament_dictionary:
                update_event_details = True
                debug.message(debug_flags.SBO_DATA_SOURCE_CACHE_INFOS, debug.INFO, "Updating Tournament ID: %s" % tournament_id)
            else:
                update_event_details = False
                debug.message(debug_flags.SBO_DATA_SOURCE_CACHE_INFOS, debug.INFO, "Creating Tournament ID: %s" % tournament_id)

            # Create or Update the dictionary with the received event details.
            self.tournament_dictionary[tournament_id] = tournament[TORNAMENT_NAME]

            if update_event_details:

                # Get a list of Event IDs affected by the update of this Tournament ID.
                affected_event_ids = self._get_affected_event_ids(tournament_id)

                for event_id in affected_event_ids:

                    # Get a list of Event Result IDs affected by the update of this Event ID.
                    affected_event_result_ids = self._get_affected_event_result_ids('event_id', event_id)

                    for event_result_id in affected_event_result_ids:

                        if event_result_id not in self.events_updated:
                            self.events_updated[event_result_id] = {}

                        # Set a flag to indicate that the event details for this event result have been updated.
                        self.events_updated[event_result_id]['event_details'] = True


    def _update_event_dictionary(self, event_dictionary):

        """This private method updates the internal cache of event data.

        Args: event_dictionary(dictionary)
        Returns: None
        Raises: None
        """
        debug.message(debug_flags.SBO_DATA_SOURCE_CACHE_INFOS, debug.INFO, "%s: %s" % (SboDataSourceCache.__name__, "_update_event_dictionary"))

        for event in event_dictionary:

            event_id = event[EVENT_ID]

            # Set a flag to indicate weather existing event details are being updated or new event details are being created.
            if event_id in self.event_dictionary:
                update_event_details = True
                debug.message(debug_flags.SBO_DATA_SOURCE_CACHE_INFOS, debug.INFO, "Updating Event ID: %s" % event_id)
            else:
                update_event_details = False
                debug.message(debug_flags.SBO_DATA_SOURCE_CACHE_INFOS, debug.INFO, "Creating Event ID: %s" % event_id)

            # Create or Update the dictionary with the received event details.
            self.event_dictionary[event_id] = {
                'tornament_id': event[EVENT_DICTIONARY_TORNAMENT_ID],
                'home_team_name': event[HOME_TEAM_NAME],
                'away_team_name': event[AWAY_TEAM_NAME],
                'event_sort_code': event[EVENT_SORT_CODE],
                'show_time_type': event[SHOW_TIME_TYPE],
                'show_time': event[SHOW_TIME]
            }

            if update_event_details:

                # Get a list of Event Result IDs affected by the update of this Event ID.
                affected_event_result_ids = self._get_affected_event_result_ids('event_id', event_id)

                for event_result_id in affected_event_result_ids:

                    if event_result_id not in self.events_updated:
                        self.events_updated[event_result_id] = {}

                    # Set a flag to indicate that the event details for this event result have been updated.
                    self.events_updated[event_result_id]['event_details'] = True


    def _update_event_result_dictionary(self, event_result_dictionary):

        """This private method updates the internal cache of event result data

        Args: event_result_dictionary(dictionary)
        Returns: None
        Raises: None
        """
        debug.message(debug_flags.SBO_DATA_SOURCE_CACHE_INFOS, debug.INFO, "%s: %s" % (SboDataSourceCache.__name__, "_update_event_result_dictionary"))

        for event_result in event_result_dictionary:

            event_result_id = event_result[EVENT_RESULT_ID]

            # Set a flag to indicate weather existing event details are being updated or new event details are being created.
            if event_result_id in self.event_result_dictionary:
                update_event_details = True
                debug.message(debug_flags.SBO_DATA_SOURCE_CACHE_INFOS, debug.INFO, "Updating Event Result ID: %s" % event_result_id)
            else:
                update_event_details = False
                debug.message(debug_flags.SBO_DATA_SOURCE_CACHE_INFOS, debug.INFO, "Creating Event Result ID: %s" % event_result_id)

            # Create or Update the dictionary with the received event details.
            self.event_result_dictionary[event_result_id] = {
                'event_id': event_result[EVENT_RESULT_DICTIONARY_EVENT_ID],
                'market_group_id': event_result[EVENT_RESULT_DICTIONARY_MARKET_GROUP_ID],
                'home_score': event_result[HOME_SCORE],
                'away_score': event_result[AWAY_SCORE],
                'odds_count': event_result[ODDS_COUNT]
            }

            if update_event_details:

                if event_result_id not in self.events_updated:
                    self.events_updated[event_result_id] = {}

                # Set a flag to indicate that the event details for this event result have been updated.
                self.events_updated[event_result_id]['event_details'] = True

            else:

                # Add the Event Result ID to the list of events that have been created.
                # Note: A new Event is only considered to be created once the Event Result Dictionary is updated.
                self.events_created.append(event_result_id)


    def _update_event_result_extra_dictionary(self, event_result_extra_dictionary): # pylint: disable-msg=C0103

        """This private method updates the internal cache of event result extra data.

        Args: event_result_extra_dictionary(dictionary)
        Returns: None
        Raises: None
        """
        debug.message(debug_flags.SBO_DATA_SOURCE_CACHE_INFOS, debug.INFO, "%s: %s" % (SboDataSourceCache.__name__, "_update_event_result_extra_dictionary"))

        current_minutes_just_cached = []

        if event_result_extra_dictionary is not None:

            for event_result_extra in event_result_extra_dictionary:

                event_result_id = event_result_extra[EVENT_RESULT_EXTRA_DICTIONARY_EVENT_RESULT_ID]

                # Set a flag to indicate weather existing event details are being updated or new event details are being created.
                if event_result_id in self.event_result_extra_dictionary:
                    update_event_details = True
                    debug.message(debug_flags.SBO_DATA_SOURCE_CACHE_INFOS, debug.INFO, "Updating Event Result (Extra) ID: %s" % event_result_id)
                else:
                    update_event_details = False
                    debug.message(debug_flags.SBO_DATA_SOURCE_CACHE_INFOS, debug.INFO, "Creating Event Result (Extra) ID: %s" % event_result_id)

                # Create or Update the dictionary with the received event details.
                self.event_result_extra_dictionary[event_result_id] = {
                    'row_count': event_result_extra[ROW_COUNT],
                    'period': event_result_extra[PERIOD],
                    'current_minutes': event_result_extra[CURRENT_MINUTES],
                    'total_minutes': event_result_extra[TOTAL_MINUTES],
                    'home_red_card_count': event_result_extra[HOME_RED_CARD_COUNT],
                    'away_red_card_count': event_result_extra[AWAY_RED_CARD_COUNT],
                    'injury_time': event_result_extra[INJURY_TIME]
                }

                if update_event_details:

                    if event_result_id not in self.events_updated:
                        self.events_updated[event_result_id] = {}

                    # Set a flag to indicate that the event details for this event result have been updated.
                    self.events_updated[event_result_id]['event_details'] = True

                # A new value for current minutes has just been received from the server.
                # Cache or re-cache the start date and time of the match.
                if event_result_id not in self.current_minutes_cache:
                    self.current_minutes_cache[event_result_id] = {}

                self.current_minutes_cache[event_result_id]['current_minutes'] = self.event_result_extra_dictionary[event_result_id]['current_minutes']
                self.current_minutes_cache[event_result_id]['cache_time'] = datetime.now()

                # Keep track of which events have just had their current minutes cached to save immediately calculating their new
                # current minutes below. The start time will not have elapsed more than a minute and the calculation will be wasted.
                current_minutes_just_cached.append(event_result_id)

        if self.event_result_extra_dictionary is not None:

            for event_result_id in self.event_result_extra_dictionary:

                # Any events which have not just had their current minutes cached have not received an updated current minutes from the server.
                # In this case we need to check how long has elapsed since the cache time and update the current minutes as necessary.
                if event_result_id not in current_minutes_just_cached:

                    now = datetime.now()
                    cached_time = self.current_minutes_cache[event_result_id]['cache_time']
                    cached_current_minutes = self.current_minutes_cache[event_result_id]['current_minutes']
                    current_minutes_cap = self.event_result_extra_dictionary[event_result_id]['total_minutes']

                    # Calculate the value for current minutes, based on the time elapsed since they were cached.
                    time_since_cache = now - cached_time
                    elapsed_minutes = time_since_cache.total_seconds() / SECONDS_IN_A_MINUTE                        # pylint: disable-msg=E1103
                    calculated_current_minutes = int(cached_current_minutes + elapsed_minutes)

                    if calculated_current_minutes > current_minutes_cap:
                        calculated_current_minutes = current_minutes_cap

                    # In the absence of a value for current minutes from the server, use the calculated value.
                    self.event_result_extra_dictionary[event_result_id]['current_minutes'] = calculated_current_minutes

                    if event_result_id not in self.events_updated:
                        self.events_updated[event_result_id] = {}

                    # Set a flag to indicate that the event details for this event result have been updated.
                    self.events_updated[event_result_id]['event_details'] = True


    def _update_odds_dictionary(self, odds_dictionary):

        """This private method updates the internal cache of odds data.

        Args: odds_dictionary(dictionary)
        Returns: None
        Raises: None
        """
        debug.message(debug_flags.SBO_DATA_SOURCE_CACHE_INFOS, debug.INFO, "%s: %s" % (SboDataSourceCache.__name__, "_update_odds_dictionary"))

        # A temporary dictionary used only within the scope of this method to keep track of which line number each odds belongs to.
        line_number_dictionary = {}

        for odds in odds_dictionary:

            # This flag is required because Odds that are passed to this function do not need to be reported in the
            # Updated Odds array if they are being added as part of a new Event.
            # If they are isolated Odds updated then they will be reported in the Updated Odds array as normal.
            add_to_updated_odds = False

            odds_id = odds[ODDS_ID]

            if odds_id not in self.odds_dictionary:

                # Create a new dictionary entry with the received odds details.

                # Look-up the Event Result ID that is associated with this set of Odds.
                event_result_id = odds[ODDS_DATA_ARRAY][ODDS_DICTIONARY_EVENT_RESULT_ID]
                market_display_id = odds[ODDS_DATA_ARRAY][MARKET_DISPLAY_ID]

                # Store the odds with a reference to the line number they belong to which is determined from the raw order of odds.
                line_number = self._get_next_line_number(line_number_dictionary, event_result_id, market_display_id)

                # Note: The entire Odds Data Array and Prices Array are stored in cache.
                # As the Odds type isn't checked at this stage, some odds my ultimately go unused.
                # However, this method supports the updating of all Odds types.
                self.odds_dictionary[odds_id] = {
                    'odds_data': odds[ODDS_DATA_ARRAY],
                    'prices': odds[PRICES_ARRAY],
                    'line_number': line_number
                }

                debug.message(debug_flags.SBO_DATA_SOURCE_CACHE_INFOS, debug.INFO, "Creating Odds ID: %s" % odds_id)

                # Determine if this set of Odds is being added as part of a new Event.
                # If they are not covered by the creation of an associated Event then they need to be added to the Updated Odds array.
                if event_result_id not in self.events_created:
                    add_to_updated_odds = True

            else:

                # Update the dictionary with the received odds details.

                # All Odds Updates are automatically added to the Updated Odds array.
                add_to_updated_odds = True

                debug.message(debug_flags.SBO_DATA_SOURCE_CACHE_INFOS, debug.INFO, "Updating Odds ID: %s" % odds_id)

                # Update the individual elements of the Odds Data Array and Prices Array, as SBO server updates
                # may not contain a full copy of the array.

                if odds[ODDS_DATA_ARRAY] is not None:

                    # The point information is not always included in an odds update.
                    # Only attempt to update the point value if the odds data array is large enough to include it.
                    if len(odds[ODDS_DATA_ARRAY]) > 4:
                        if odds[ODDS_DATA_ARRAY][POINT] is not None:
                            self.odds_dictionary[odds_id]['odds_data'][POINT] = odds[ODDS_DATA_ARRAY][POINT]

                if len(odds) > 2:
                    if odds[PRICES_ARRAY] is not None:

                        if odds[PRICES_ARRAY][PRICE_1] is not None:
                            self.odds_dictionary[odds_id]['prices'][PRICE_1] = odds[PRICES_ARRAY][PRICE_1]

                        # Price 2 is not always present in the Prices array, so check if there is more than one price.
                        if len(odds[PRICES_ARRAY]) > 1:
                            if odds[PRICES_ARRAY][PRICE_2] is not None:
                                self.odds_dictionary[odds_id]['prices'][PRICE_2] = odds[PRICES_ARRAY][PRICE_2]

                        # Price 3 is not always present in the Prices array, so check if there are more than two prices.
                        # Note: The JabBlob system doesn't require the Odds type that uses Price 3.
                        # This method supports the Price 3 parameter for possible future use.
                        if len(odds[PRICES_ARRAY]) > 2:
                            if odds[PRICES_ARRAY][PRICE_3] is not None:
                                self.odds_dictionary[odds_id]['prices'][PRICE_3] = odds[PRICES_ARRAY][PRICE_3]

            # Add the new or updated Odds set to the Updated Odds array.
            # If the Odds set is new, it will be associated with an existing Event.
            if add_to_updated_odds:

                # Look-up the Event Result ID that is associated with this set of Odds.
                event_result_id = self.odds_dictionary[odds_id]['odds_data'][ODDS_DICTIONARY_EVENT_RESULT_ID]

                if event_result_id not in self.events_updated:
                    self.events_updated[event_result_id] = {}

                # The updated odds list is a list of Odds IDs that have had their Odds updated.
                if 'event_odds' not in self.events_updated[event_result_id]:
                    updated_odds = []
                else:
                    updated_odds = self.events_updated[event_result_id]['event_odds']

                # Add the Odds ID to a list that indicates the odds data for this Event Result has been updated.
                updated_odds.append(odds_id)
                self.events_updated[event_result_id]['event_odds'] = updated_odds


    def _update_market_group_dictionary(self, market_group_dictionary):

        """This private method updates the internal cache of market group data.

        Args: market_group_dictionary(dictionary)
        Returns: None
        Raises: None
        """
        debug.message(debug_flags.SBO_DATA_SOURCE_CACHE_INFOS, debug.INFO, "%s: %s" % (SboDataSourceCache.__name__, "_update_market_group_dictionary"))

        for market_group in market_group_dictionary:

            market_group_id = market_group[MARKET_GROUP_ID]

            # Set a flag to indicate weather existing event details are being updated or new event details are being created.
            if market_group_id in self.market_group_dictionary:
                update_event_details = True
                debug.message(debug_flags.SBO_DATA_SOURCE_CACHE_INFOS, debug.INFO, "Updating Market Group ID: %s" % market_group_id)
            else:
                update_event_details = False
                debug.message(debug_flags.SBO_DATA_SOURCE_CACHE_INFOS, debug.INFO, "Creating Market Group ID: %s" % market_group_id)

            # Create or Update the dictionary with the received event details.
            self.market_group_dictionary[market_group_id] = market_group[MARKET_GROUP_NAME]

            if update_event_details:

                # Get a list of Event Result IDs affected by the update of this Market Group ID.
                affected_event_result_ids = self._get_affected_event_result_ids('market_group_id', market_group_id)

                for event_result_id in affected_event_result_ids:

                    if event_result_id not in self.events_updated:
                        self.events_updated[event_result_id] = {}

                    # Set a flag to indicate that the event details for this event result have been updated.
                    self.events_updated[event_result_id]['event_details'] = True


    def _delete_from_event_result_dictionary(self, event_results_to_delete):

        """This private method deletes from the internal cache of event result data.

        Args: event_results_to_delete(list)
        Returns: None
        Raises: None
        """
        debug.message(debug_flags.SBO_DATA_SOURCE_CACHE_INFOS, debug.INFO, "%s: %s" % (SboDataSourceCache.__name__, "_delete_from_event_result_dictionary"))

        for event_result_id in event_results_to_delete:

            debug.message(debug_flags.SBO_DATA_SOURCE_CACHE_INFOS, debug.INFO, "Attempting to delete Event Result ID: %s" % event_result_id)

            # Delete the Event Result ID from the Event Result Dictionary if the entry exists.
            if event_result_id in self.event_result_dictionary:

                debug.message(debug_flags.SBO_DATA_SOURCE_CACHE_INFOS, debug.INFO, "Deleting Event Result: %s" % self.event_result_dictionary[event_result_id])

                del self.event_result_dictionary[event_result_id]

                # Add the Event Result ID to the list of events that have been deleted.
                # Note: An Event is only considered to be deleted once it has been removed from the Event Result Dictionary.
                self.events_deleted.append(event_result_id)

            # Delete the Event Result ID from the Event Result Extra Dictionary if the entry exists.
            # Note: The SBO server does not explicitly request the deletion from this dictionary, but delete anyway to keep things tidy.
            if event_result_id in self.event_result_extra_dictionary:

                debug.message(debug_flags.SBO_DATA_SOURCE_CACHE_INFOS, debug.INFO, "Deleting Event Result Extra: %s" % self.event_result_extra_dictionary[event_result_id])

                del self.current_minutes_cache[event_result_id]
                del self.event_result_extra_dictionary[event_result_id]


    def _delete_from_odds_dictionary(self, odds_to_delete):

        """This private method deletes from the internal cache of odds data.

        Args: odds_to_delete(list)
        Returns: None
        Raises: None
        """
        debug.message(debug_flags.SBO_DATA_SOURCE_CACHE_INFOS, debug.INFO, "%s: %s" % (SboDataSourceCache.__name__, "_delete_from_odds_dictionary"))

        for odds_id in odds_to_delete:

            debug.message(debug_flags.SBO_DATA_SOURCE_CACHE_INFOS, debug.INFO, "Attempting to delete Odds ID: %s" % odds_id)

            # Delete the Odds ID from the Odds Dictionary if the entry exists.
            if odds_id in self.odds_dictionary:

                debug.message(debug_flags.SBO_DATA_SOURCE_CACHE_INFOS, debug.INFO, "Deleting Odds: %s" % self.odds_dictionary[odds_id])

                del self.odds_dictionary[odds_id]


    def _get_match_stage_details(self, event_result_id):

        """This private method uses the SBO servers Period parameter to determine the JamBlob match stage.

        Args: event_result_id(integer)
        Returns: match_stage_details(tuple), eg: (match_stage, first_half_elapsed, second_half_elapsed, injury_time)
        Raises: None
        """
        debug.message(debug_flags.SBO_DATA_SOURCE_CACHE_INFOS, debug.INFO, "%s: %s" % (SboDataSourceCache.__name__, "_get_match_stage_details"))

        match_stage = None
        first_half_elapsed = None
        second_half_elapsed = None
        injury_time = None

        # Some Events (usually non-live), do not have any Event Result Extra data.
        if event_result_id not in self.event_result_extra_dictionary:

            debug.message(debug_flags.SBO_DATA_SOURCE_CACHE_INFOS, debug.INFO, "Event Result ID %s has no Event Result Extra data." % event_result_id)

            match_stage = NOT_LIVE
            first_half_elapsed = 0
            second_half_elapsed = 0
            injury_time = 0

            return (match_stage, first_half_elapsed, second_half_elapsed, injury_time)

        # The match stage is a JamBlob parameter that indicates the current stage of the match.
        # The SBO servers Period and time related parameters can be used to determine the match stage.
        period = self.event_result_extra_dictionary[event_result_id]['period']
        current_minutes = self.event_result_extra_dictionary[event_result_id]['current_minutes']
        total_minutes = self.event_result_extra_dictionary[event_result_id]['total_minutes']

        if period == 1:

            # A Period of exactly One indicates the first half of the match is in play.
            match_stage = FIRST_HALF
            first_half_elapsed = current_minutes
            second_half_elapsed = None
            injury_time = 0

        elif period == 5:

            # A Period of exactly Five indicates that it is half time.
            match_stage = HALF_TIME
            first_half_elapsed = None
            second_half_elapsed = None
            injury_time = 0

        elif period == 2:

            # A Period of exactly Two indicates the second half of the match is in play.
            match_stage = SECOND_HALF
            first_half_elapsed = None
            second_half_elapsed = current_minutes
            injury_time = 0

        elif period > 2:

            # A Period of more than Two indicates that the match has gone into injury time.
            match_stage = SECOND_HALF
            first_half_elapsed = None
            second_half_elapsed = current_minutes
            injury_time = current_minutes - total_minutes

        return (match_stage, first_half_elapsed, second_half_elapsed, injury_time)


    def _format_show_time(self, show_time):

        """This private method takes the show time parameter in its raw state and returns it in the required format.

        Args: show_time(string)
        Returns: formatted_show_time(datetime)
        Raises: None
        """
        debug.message(debug_flags.SBO_DATA_SOURCE_CACHE_INFOS, debug.INFO, "%s: %s" % (SboDataSourceCache.__name__, "_format_show_time"))

        formatted_show_time = DEFAULT_SHOW_TIME

        try:
            # Extract the date and time details from the raw string.
            # eg: 02/19/2013 13:44
            regex_match = REGEX_SHOW_TIME.match(show_time)

        except TypeError as exception_instance:

            # Catch any TypeErrors.
            debug.message(debug_flags.SBO_DATA_SOURCE_CACHE_WARNINGS, debug.WARNING, "_format_show_time() experienced %s: %s" % (type(exception_instance).__name__, exception_instance))
            return formatted_show_time

        if not regex_match:

            debug.message(debug_flags.SBO_DATA_SOURCE_CACHE_WARNINGS, debug.WARNING, "_format_show_time() can not extract time and date details from show time string: %s" % show_time)
            return formatted_show_time

        # The Regular Expression will only match digits so it is safe to convert the matches to integers.
        year = int(regex_match.group('year'))
        month = int(regex_match.group('month'))
        day = int(regex_match.group('day'))
        hour = int(regex_match.group('hour'))
        minute = int(regex_match.group('minute'))

        try:
            # Subtracting the GMT offset from the show time ensures all show times are displayed in GMT.
            formatted_show_time = datetime(year, month, day, hour, minute) - self.timedelta_gmt_offset

        except (TypeError, ValueError, OverflowError) as exception_instance:
            debug.message(debug_flags.SBO_DATA_SOURCE_CACHE_WARNINGS, debug.WARNING, "_format_show_time() experienced %s: %s" % (type(exception_instance).__name__, exception_instance))

        return formatted_show_time


    def _get_red_cards(self, event_result_id):

        """This private method returns the number of red cards for home and away, if the given Event Result ID has Event Result Extra data.

        Args: event_result_id(integer)
        Returns: red_cards(tuple), eg: (home_red_card_count, away_red_card_count)
        Raises: None
        """
        debug.message(debug_flags.SBO_DATA_SOURCE_CACHE_INFOS, debug.INFO, "%s: %s" % (SboDataSourceCache.__name__, "_get_red_cards"))

        home_red_card_count = None
        away_red_card_count = None

        # Some Events (usually non-live), do not have any Event Result Extra data.
        if event_result_id in self.event_result_extra_dictionary:

            home_red_card_count = self.event_result_extra_dictionary[event_result_id]['home_red_card_count']
            away_red_card_count = self.event_result_extra_dictionary[event_result_id]['away_red_card_count']

        return (home_red_card_count, away_red_card_count)


    def _get_tournament_name(self, event_id, event_result_id):

        """This private method returns the Tournament Name for a given Tournament ID.

        Args: event_id(integer), event_result_id(integer)
        Returns: tournament_name(string)
        Raises: None
        """
        debug.message(debug_flags.SBO_DATA_SOURCE_CACHE_INFOS, debug.INFO, "%s: %s" % (SboDataSourceCache.__name__, "_get_tournament_name"))

        tournament_id = self.event_dictionary[event_id]['tornament_id']
        tournament_name = self.tournament_dictionary[tournament_id]

        # Some Event Results are categorised under a special Market Group.
        # These are identified by a non-zero Market Group ID.
        market_group_id = self.event_result_dictionary[event_result_id]['market_group_id']

        if market_group_id != 0:

            # To differentiate between Event Results in a special Market Group,
            # the Market Group Name is appended to the end of the Tournament Name.
            market_group_name = self.market_group_dictionary[market_group_id]

            try:
                tournament_name = tournament_name + " " + MARKET_GROUP_SEPERATOR + " " + market_group_name

            except TypeError as exception_instance:
                debug.message(debug_flags.SBO_DATA_SOURCE_CACHE_WARNINGS, debug.WARNING, "_get_tournament_name() experienced a %s: %s" % (type(exception_instance).__name__, exception_instance))

        return tournament_name


    def _get_event_details(self, event_result_id):

        """This private method looks-up all the event details in cache for a given Event Result ID and returns them in a tuple.

        Args: event_result_id(integer)
        Returns: event_details(tuple)
        Raises: None
        """
        debug.message(debug_flags.SBO_DATA_SOURCE_CACHE_INFOS, debug.INFO, "%s: %s" % (SboDataSourceCache.__name__, "_get_event_details"))

        # Fetch the associated Event ID as it will be needed to extract many of the event details.
        event_id = self.event_result_dictionary[event_result_id]['event_id']

        # Look-up the Event Result Extra parameters required to determine the match stage details.
        match_stage_details = self._get_match_stage_details(event_result_id)

        # Use the Event Result ID to extract the following required elements from cache.

        tournament_name = self._get_tournament_name(event_id, event_result_id)

        event_sort_code = self._format_event_sort_code(self.event_dictionary[event_id]['event_sort_code'])

        team_names = (
            self.event_dictionary[event_id]['home_team_name'],
            self.event_dictionary[event_id]['away_team_name']
        )

        show_time = self._format_show_time(self.event_dictionary[event_id]['show_time'])

        betting_available_in_play = self._get_betting_available_in_play(self.event_dictionary[event_id]['show_time_type'])

        match_time_elapsed = (
            match_stage_details[FIRST_HALF_ELAPSED],
            match_stage_details[SECOND_HALF_ELAPSED]
        )

        match_stage = match_stage_details[MATCH_STAGE]

        favourite = FAVOURITE_NOT_USED

        if event_result_id not in self.event_result_extra_dictionary:
            # Some Events (usually non-live), do not have any Event Result Extra data.
            injury_time = 0
        else:
            injury_time = self.event_result_extra_dictionary[event_result_id]['injury_time']

        score = (
            self.event_result_dictionary[event_result_id]['home_score'],
            self.event_result_dictionary[event_result_id]['away_score']
        )

        red_cards = self._get_red_cards(event_result_id)

        # Package all of the extracted elements in a tuple and return.
        event_details = (
            tournament_name,
            event_sort_code,
            team_names,
            show_time,
            betting_available_in_play,
            match_time_elapsed,
            match_stage,
            favourite,
            injury_time,
            score,
            red_cards
        )

        return event_details


    def _get_event_odds(self, list_of_odds, fetch_type):

        """This method looks-up all the event odds in cache for a given list of Odds IDs and returns them in a list.

        Args: list_of_odds(list), fetch_type(int)
        Returns: event_odds(list)
        Raises: None
        """
        debug.message(debug_flags.SBO_DATA_SOURCE_CACHE_INFOS, debug.INFO, "%s: %s" % (SboDataSourceCache.__name__, "_get_event_odds"))

        event_odds = []

        half_time_hdps = [None, None, None]
        full_time_hdps = [None, None, None]
        half_time_ous = [None, None, None]
        full_time_ous = [None, None, None]

        for odds_id in list_of_odds:

            # The Market Display ID determines the type of Odds and how to deal with them.
            # Market Display IDs other than the Four types checked for will be ignored.

            if self.odds_dictionary[odds_id]['odds_data'][MARKET_DISPLAY_ID] == HALF_TIME_HDP:

                list_position = self.odds_dictionary[odds_id]['line_number'] - 1
                point_data = self._format_point_value(self.odds_dictionary[odds_id]['odds_data'][POINT])
                price_1 = self.odds_dictionary[odds_id]['prices'][PRICE_1]
                price_2 = self.odds_dictionary[odds_id]['prices'][PRICE_2]

                # The HDP Odds include a parameter to represent the favourite team.
                row = (point_data[FORMATTED_POINT], price_1, price_2, point_data[FAVOURITE_TEAM])
                half_time_hdps[list_position] = row

            elif self.odds_dictionary[odds_id]['odds_data'][MARKET_DISPLAY_ID] == FULL_TIME_HDP:

                list_position = self.odds_dictionary[odds_id]['line_number'] - 1
                point_data = self._format_point_value(self.odds_dictionary[odds_id]['odds_data'][POINT])
                price_1 = self.odds_dictionary[odds_id]['prices'][PRICE_1]
                price_2 = self.odds_dictionary[odds_id]['prices'][PRICE_2]

                # The HDP Odds include a parameter to represent the favourite team.
                row = (point_data[FORMATTED_POINT], price_1, price_2, point_data[FAVOURITE_TEAM])
                full_time_hdps[list_position] = row

            elif self.odds_dictionary[odds_id]['odds_data'][MARKET_DISPLAY_ID] == HALF_TIME_OU:

                list_position = self.odds_dictionary[odds_id]['line_number'] - 1
                point_data = self._format_point_value(self.odds_dictionary[odds_id]['odds_data'][POINT])
                price_1 = self.odds_dictionary[odds_id]['prices'][PRICE_1]
                price_2 = self.odds_dictionary[odds_id]['prices'][PRICE_2]

                row = (point_data[FORMATTED_POINT], price_1, price_2)
                half_time_ous[list_position] = row

            elif self.odds_dictionary[odds_id]['odds_data'][MARKET_DISPLAY_ID] == FULL_TIME_OU:

                list_position = self.odds_dictionary[odds_id]['line_number'] - 1
                point_data = self._format_point_value(self.odds_dictionary[odds_id]['odds_data'][POINT])
                price_1 = self.odds_dictionary[odds_id]['prices'][PRICE_1]
                price_2 = self.odds_dictionary[odds_id]['prices'][PRICE_2]

                row = (point_data[FORMATTED_POINT], price_1, price_2)
                full_time_ous[list_position] = row

        # Each Event can have between One and Three rows of Odds data.
        # The JamBlob data structure requires that Three sets are returned, regardless of the actual number of sets available.
        for line in range(3):

            half_time_hdp = half_time_hdps[line]
            full_time_hdp = full_time_hdps[line]
            half_time_ou = half_time_ous[line]
            full_time_ou = full_time_ous[line]

            # If fetching newly created events, substitute None's for mixed rows only.
            if fetch_type == FETCH_CREATED_EVENTS:

                # When there is a mixture of values and Nones, replace the None with an empty Tuple.
                if not (half_time_hdp is None and full_time_hdp is None and half_time_ou is None and full_time_ou is None):

                    if half_time_hdp is None:
                        half_time_hdp = (0.0, 0.0, 0.0, 0)

                    if full_time_hdp is None:
                        full_time_hdp = (0.0, 0.0, 0.0, 0)

                    if half_time_ou is None:
                        half_time_ou = (0.0, 0.0, 0.0)

                    if full_time_ou is None:
                        full_time_ou = (0.0, 0.0, 0.0)

            event_odds.append([half_time_hdp, full_time_hdp, half_time_ou, full_time_ou])

        # The Event Odds is in the form of a List of Lists.
        return event_odds


    def _get_sub_event_result_id(self, event_result_id):

        """This method generates and returns a Sub Event Result ID from the given Event Result ID.

        Args: event_result_id(integer)
        Returns: sub_event_result_id(integer)
        Raises: EventIndexError
        """
        debug.message(debug_flags.SBO_DATA_SOURCE_CACHE_INFOS, debug.INFO, "%s: %s" % (SboDataSourceCache.__name__, "_get_sub_event_result_id"))

        if self.frame_type == LIVE_DATA_FRAME:

            # The Sub Event Result ID for a Live Frame is the Event Result ID prepended with a Zero.
            # Note: As a leading Zero doesn't change the numeric value, simply return the Event Result ID.
            sub_event_result_id = event_result_id

        else:

            try:
                # The Sub Event Result ID for a Non-Live Frame is the Event Result ID prepended with a One.
                sub_event_result_id = int(NON_LIVE_SUB_EVENT_PREFIX + str(event_result_id))

            except ValueError as exception_instance:
                raise DataSourceBase.EventIndexError("_get_sub_event_result_id() experienced %s: %s" % (type(exception_instance).__name__, exception_instance))

        return sub_event_result_id


    def clear_cache(self):

        """This public method clears all cached data.

        This simple method has no arguments or returns.
        It raises no errors.
        """
        debug.message(debug_flags.SBO_DATA_SOURCE_CACHE_INFOS, debug.INFO, "%s: %s" % (SboDataSourceCache.__name__, "clear_cache"))

        self.current_minutes_cache = {}

        self.tournament_dictionary = {}
        self.event_dictionary = {}
        self.event_result_dictionary = {}
        self.event_result_extra_dictionary = {}
        self.odds_dictionary = {}
        self.market_group_dictionary = {}


    def update_cache(self, frame_cache_data):

        """This public method updates the internal data cache with the latest data received from the SBO server.

        This method should be called each time data is fetched from the SBO server.
        It will ensure that a complete up to date cache of event data is always available.
        Note: The SBO server deals with Event Results which are equivalent to what JamBlob refers to as Matches.

        Args:
            frame_cache_data: A dictionary of RAW event data from the SBO server.

        Returns:
            During the process of updating the cache, a record is kept of which Event Results were created, updated or deleted.
            This method returns a tuple of the three records:

            (Events Created, Events Updated, Events Deleted)

            The Events Created and Deleted hold a list of Event Result IDs and
            Events Updated holds a dictionary specifying which parameters were updated.

        Raises:
            UnexpectedDataError: This class is based on a known data structure for frame_cache_data.
                This error will be raised if the structure differs to an extent that the data can not be interpreted.
        """
        debug.message(debug_flags.SBO_DATA_SOURCE_CACHE_INFOS, debug.INFO, "%s: %s" % (SboDataSourceCache.__name__, "update_cache"))

        # These will hold a record of that was changed during the update.
        # Note: The Events Created and Deleted hold a list of Event Result IDs and
        # Events Updated holds a dictionary specifying which parameters were updated.
        self.events_created = []
        self.events_updated = {}
        self.events_deleted = []

        try:
            # At the top level, the frame cache data is a collection of specific dictionaries.
            tournament_dictionary = frame_cache_data[TOURNAMENT_DICTIONARY]
            event_dictionary = frame_cache_data[EVENT_DICTIONARY]
            event_result_dictionary = frame_cache_data[EVENT_RESULT_DICTIONARY]
            event_result_extra_dictionary = frame_cache_data[EVENT_RESULT_EXTRA_DICTIONARY]
            event_result_list_for_deletion = frame_cache_data[EVENT_RESULT_LIST_FOR_DELETION]
            odds_dictionary = frame_cache_data[ODDS_DICTIONARY]
            odds_list_for_deletion = frame_cache_data[ODDS_LIST_FOR_DELETION]
            market_group_dictionary = frame_cache_data[MARKET_GROUP_DICTIONARY]

        except (TypeError, IndexError, KeyError) as exception_instance:
            raise SboDataSourceCache.UnexpectedDataError("update_cache() experienced %s: %s" % (type(exception_instance).__name__, exception_instance))

        try:
            # Delete the internal data cache for any dictionaries containing data.

            if event_result_list_for_deletion is not None:
                self._delete_from_event_result_dictionary(event_result_list_for_deletion)

            if odds_list_for_deletion is not None:
                self._delete_from_odds_dictionary(odds_list_for_deletion)

        except (TypeError, IndexError) as exception_instance:
            raise SboDataSourceCache.UnexpectedDataError("update_cache() experienced %s: %s" % (type(exception_instance).__name__, exception_instance))

        try:
            # Update the internal data cache for any dictionaries containing data.

            if tournament_dictionary is not None:
                self._update_tournament_dictionary(tournament_dictionary)

            if event_dictionary is not None:
                self._update_event_dictionary(event_dictionary)

            if event_result_dictionary is not None:
                self._update_event_result_dictionary(event_result_dictionary)

            #if event_result_extra_dictionary is not None:
            # Update: The event result extra dictionary must now be updated regardless of data coming from the SBO server.
            # This is so that if there is no update to the match elapsed time, it can be simulated here
            self._update_event_result_extra_dictionary(event_result_extra_dictionary)

            if odds_dictionary is not None:
                self._update_odds_dictionary(odds_dictionary)

            if market_group_dictionary is not None:
                self._update_market_group_dictionary(market_group_dictionary)

        except (TypeError, IndexError) as exception_instance:
            raise SboDataSourceCache.UnexpectedDataError("update_cache() experienced %s: %s" % (type(exception_instance).__name__, exception_instance))

        # These lists and dictionaries return a record of what was created, updated and deleted.
        return (self.events_created, self.events_updated, self.events_deleted)


    def fetch_event(self, event_result_id):

        """This public method returns all event details for the given Event Result ID.

        Args:
            event_result_id: An ID number used to look-up an Event Result.

        Returns:
            event: A Tuple made up of an Events IDs, details and odds.
                eg: (sub_event_result_id, sbo_event_result_id, event_details, event_odds)

        Raises:
            EventIndexError: Raised on an invalid event_result_id or
                when the event_result_id provided does not match any record in the cache.
        """
        debug.message(debug_flags.SBO_DATA_SOURCE_CACHE_INFOS, debug.INFO, "%s: %s" % (SboDataSourceCache.__name__, "fetch_event"))

        # The Sub-Event Result ID is based on the Event Result ID, prefixed with the frame type.
        sub_event_result_id = self._get_sub_event_result_id(event_result_id)

        # Each data source class has a unique ID.
        # Encode the unique ID into the Event Result ID so that its source can be identified.
        sub_event_result_id = DataSourceBase.get_identifiable_id(self, self.sbo_id, sub_event_result_id)
        sbo_event_result_id = DataSourceBase.get_identifiable_id(self, self.sbo_id, event_result_id)

        # A list of Odds IDs that are associated with the given Event Result ID.
        associated_odds = []

        # The only way to find Odds that relate to the given Event Result ID is to cycle round
        # the whole Odds Dictionary looking for a matching Event Result ID.
        for odds_id in self.odds_dictionary:
            if self.odds_dictionary[odds_id]['odds_data'][ODDS_DICTIONARY_EVENT_RESULT_ID] == event_result_id:
                associated_odds.append(odds_id)

        try:
            # Use the Event Result ID to look-up all the required Event details from cache.
            event_details = self._get_event_details(event_result_id)

            # Use the list of Odds IDs associated with the Event Result ID, to look-up all the required Odds details from cache.
            event_odds = self._get_event_odds(associated_odds, FETCH_CREATED_EVENTS)

        except (KeyError, TypeError, IndexError) as exception_instance:
            raise DataSourceBase.EventIndexError("fetch_event() experienced %s: %s" % (type(exception_instance).__name__, exception_instance))

        # This tuple represents the required JamBlob match structure.
        event = (sub_event_result_id, sbo_event_result_id, event_details, event_odds)

        return event


    def fetch_modified_event(self, event_result_id, modified_properties):

        """This public method returns all modified event details for the given Event Result ID.

        Args:
            event_result_id: An ID number used to look-up an Event Result.
            modified_properties: A dictionary of Event IDs that have had their properties modified in the last cache update.

        Returns:
            event: A Tuple made up of an Events IDs, details and odds.
                eg: (sub_event_result_id, sbo_event_result_id, event_details, event_odds)

        Raises:
            EventIndexError: Raised on an invalid event_result_id or
                when the event_result_id provided does not match any record in the cache.
        """
        debug.message(debug_flags.SBO_DATA_SOURCE_CACHE_INFOS, debug.INFO, "%s: %s" % (SboDataSourceCache.__name__, "fetch_modified_event"))

        # The Sub-Event Result ID is based on the Event Result ID, prefixed with the frame type.
        sub_event_result_id = self._get_sub_event_result_id(event_result_id)

        # Each data source class has a unique ID.
        # Encode the unique ID into the Event Result ID so that its source can be identified.
        sub_event_result_id = DataSourceBase.get_identifiable_id(self, self.sbo_id, sub_event_result_id)
        sbo_event_result_id = DataSourceBase.get_identifiable_id(self, self.sbo_id, event_result_id)

        # These default states will be returned if there is no entry in the dictionary to indicate they have been modified.
        event_details = (None, None, (None, None), None, None, (None, None), None, None, None, (None, None), (None, None))
        event_odds = [[None, None, None, None], [None, None, None, None], [None, None, None, None]]

        try:
            if 'event_details' in modified_properties:

                # The dictionary will contain an 'event_details' key only if the event details have been modified.
                # Note: The value of the key will be set to True, but it can be ignored.
                event_details = self._get_event_details(event_result_id)

        except (KeyError, TypeError, IndexError) as exception_instance:
            raise DataSourceBase.EventIndexError("fetch_modified_event() experienced %s: %s" % (type(exception_instance).__name__, exception_instance))
            #debug.message(debug_flags.SBO_DATA_SOURCE_CACHE_WARNINGS, debug.WARNING, "fetch_modified_event() experienced %s: %s" % (type(exception_instance).__name__, exception_instance))

        try:
            if 'event_odds' in modified_properties:

                # The dictionary will contain an 'event_odds' key only if the event odds have been modified.
                # The value of the key is a list of all the Odds IDs that have been modified.
                modified_odds = modified_properties['event_odds']

                event_odds = self._get_event_odds(modified_odds, FETCH_MODIFIED_EVENTS)

        except (KeyError, TypeError, IndexError) as exception_instance:
            raise DataSourceBase.EventIndexError("fetch_modified_event() experienced %s: %s" % (type(exception_instance).__name__, exception_instance))
            #debug.message(debug_flags.SBO_DATA_SOURCE_CACHE_WARNINGS, debug.WARNING, "fetch_modified_event() experienced %s: %s" % (type(exception_instance).__name__, exception_instance))

        # This tuple represents the required JabBlob match structure.
        event = (sub_event_result_id, sbo_event_result_id, event_details, event_odds)

        return event
