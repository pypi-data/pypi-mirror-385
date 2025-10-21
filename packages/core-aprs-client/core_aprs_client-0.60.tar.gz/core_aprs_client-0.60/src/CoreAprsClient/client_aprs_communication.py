#
# Core APRS Client
# Various APRS communication routines
# Author: Joerg Schultze-Lutter, 2025
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 3 of the License, or
# (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License along
# with this program; if not, write to the Free Software Foundation, Inc.,
# 51 Franklin Street, Fifth Floor, Boston, MA 02110-1301 USA.
#

import time
import types

from .client_configuration import program_config
from .client_utils import (
    make_pretty_aprs_messages,
    get_aprs_message_from_cache,
    add_aprs_message_to_cache,
    parse_bulletin_data,
    finalize_pretty_aprs_messages,
)
from ._version import __version__
from .client_aprsobject import APRSISObject
from . import client_shared
from .client_logger import logger
from .client_return_codes import CoreAprsClientInputParserStatus
from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.schedulers import base as apbase
import copy
import re

APRS_MSG_LEN_NOTRAILING = 67


def send_ack(
    myaprsis: APRSISObject,
    target_callsign: str,
    source_msg_no: str,
    source_callsign: str,
    tocall: str,
    packet_delay: float,
    simulate_send: bool = True,
):
    """
    Send acknowledgment for received package to APRS-IS if
    a message number was present
    If 'simulate_send'= True, we still prepare the message but only send it to our log file
    Parameters
    ==========
    myaprsis: aprslib.inet.IS
        Our aprslib object that we will use for the communication part
    target_callsign: str
        Call sign of the user that has sent us the message
    source_msg_no: str
        message number from user's request. Can be 'None'. In that case, we don't send a message acknowledgment to the user
        (normally, we should not enter this function at all if this value is 'None'. The safeguard will still stay in place)
    simulate_send: bool
        If True: Prepare string but only send it to logger
    source_callsign: str
        Our very own APRS callsign (e.g. COAC)
    packet_delay: float
        Delay after sending out our APRS acknowledgment request
    tocall: str
        This bot uses the default TOCALL ("APRS")

    Returns
    =======
    none
    """

    # only prepare an ack if the incoming message contained a message number
    if source_msg_no:
        logger.debug(msg="Preparing acknowledgment receipt")
        # build the ack string
        stringtosend = (
            f"{source_callsign}>{tocall}::{target_callsign:9}:ack{source_msg_no}"
        )
        if not simulate_send:
            logger.debug(msg=f"Sending acknowledgment receipt: {stringtosend}")
            # send the data to APRS-IS
            myaprsis.ais_send(aprsis_data=stringtosend)
            time.sleep(packet_delay)
        else:
            logger.debug(msg=f"Simulating acknowledgment receipt: {stringtosend}")


def send_aprs_message_list(
    myaprsis: APRSISObject,
    message_text_array: list,
    destination_call_sign: str,
    send_with_msg_no: bool,
    aprs_message_counter: int,
    external_message_number: str,
    simulate_send: bool = True,
    new_ackrej_format: bool = False,
    source_callsign: str = "COAC",
    packet_delay: float = 10.0,
    packet_delay_grace_period: float = 1.0,
    tocall: str = "APRS",
):
    """
    Send a pre-prepared message list to to APRS_IS
    All packages have a max len of 67 characters
    If 'simulate_send'= True, we still prepare the message but only send it to our log file
    Parameters
    ==========
    myaprsis: aprslib.inet.IS
        Our aprslib object that we will use for the communication part
    message_text_array: list
        Contains 1..n entries of the content that we want to send to the user
    destination_call_sign: str
        Target user call sign that is going to receive the message (usually, this
        is the user's call sign who has sent us the initial message)
    send_with_msg_no: bool
        If True, each outgoing message will have its own message ID attached to the outgoing content
        If False, no message ID is added
    aprs_message_counter: int
        message_counter for messages that require to be ack'ed
    simulate_send: bool
        If True: Prepare string but only send it to logger
    external_message_number: str
        only used if we deal with the new ackrej format
    new_ackrej_format: bool
        false: apply the old ack/rej logic as described in aprs101.pdf.
        We generate our own message id. The user's message ID
        (from the original request) will NOT be added to the
        outgoing message
        ---
        True: apply the new ack/rej logic as described
        in www.aprs.org/aprs11/replyacks.txt
        We generate our own message id. The user's message ID
        (from the original request) WILL be added to the
        outgoing message
    source_callsign: str
        Our very own APRS callsign (e.g. COAC)
    packet_delay: float
        Delay after sending out our APRS acknowledgment request
        Applied in case there are still remaining messages
    packet_delay_grace_period: float
        Delay after sending out our APRS acknowledgment request
        Applied in case there no more still remaining messages
    tocall: str
        This bot uses the default TOCALL ("APRS"). You need to apply
        for your very own TOCALL, see program documentation

    Returns
    =======
    aprs_message_counter: int
        new value for message_counter for messages that require to be ack'ed
    """

    # Send our message list
    for index, single_message in enumerate(message_text_array, start=1):
        # Build the output string
        stringtosend = (
            f"{source_callsign}>{tocall}::{destination_call_sign:9}:{single_message}"
        )
        # Does the outgoing message require to have a message number? (Read:
        # did our INCOMING message request contain a message number, thus requiring
        # us to honor this behavior with our OUTGOING message by adding a message no)?
        if send_with_msg_no:
            # Build the alphanumeric message number
            alpha_counter = get_alphanumeric_counter_value(aprs_message_counter)
            stringtosend = stringtosend + "{" + alpha_counter
            if new_ackrej_format:
                stringtosend = stringtosend + "}" + external_message_number[:2]
            aprs_message_counter = aprs_message_counter + 1
            # reset the message number if we have exceeded the maximum count
            if (
                aprs_message_counter > 676 or alpha_counter == "ZZ"
            ):  # for the alphanumeric counter AA..ZZ, this is equal to "ZZ"
                aprs_message_counter = 0
        # Check if we need to send the message for real or have to simulate it
        if not simulate_send:
            logger.debug(msg=f"Sending response message '{stringtosend}'")
            myaprsis.ais_send(aprsis_data=stringtosend)
        else:
            logger.debug(msg=f"Simulating response message '{stringtosend}'")
        # Apply the regular sleep cycle if there are still messages to be sent
        # Otherwise, use the shorter sleep cycle
        if index < len(message_text_array):
            time.sleep(packet_delay)
        else:
            time.sleep(packet_delay_grace_period)
    return aprs_message_counter


def get_alphanumeric_counter_value(numeric_counter: int):
    """
    Calculate an alphanumeric
    Parameters
    ==========
    numeric_counter: int
        numeric counter that is used for calculating the start value
    Returns
    =======
    alphanumeric_counter: str
        alphanumeric counter that is based on the numeric counter
        Range from AA to ZZ
    """
    first_char = int(numeric_counter / 26)
    second_char = int(numeric_counter % 26)
    alphanumeric_counter = chr(first_char + 65) + chr(second_char + 65)
    return alphanumeric_counter


def send_beacon_and_status_msg(
    class_instance: object,
    myaprsis: APRSISObject,
    aprs_beacon_messages: list,
    simulate_send: bool = True,
):
    """
    Send beacon message list to APRS_IS
    If 'simulate_send'= True, we still prepare the message but only send it to our log file

    Parameters
    ==========
    class_instance: object
        Instance of the main class
    myaprsis: APRSISObject
        Our aprslib object that we will use for the communication part
    aprs_beacon_messages: list
        List of pre-defined APRS beacon messages
    simulate_send: bool
        If True: Prepare string but only send it to logger

    Returns
    =======
    none
    """
    logger.debug(msg="Reached beacon interval; sending beacons")

    # Generate some local variables because the 'black' beautifier seems
    # to choke on multi-dimensional dictionaries
    _aprsis_callsign = program_config["coac_client_config"]["aprsis_callsign"]
    _aprsis_tocall = program_config["coac_client_config"]["aprsis_tocall"]

    # Build and send the list of beacons
    for index, bcn in enumerate(aprs_beacon_messages, start=1):
        # build the beacon string
        stringtosend = f"{_aprsis_callsign}>{_aprsis_tocall}:{bcn}"
        # simulate sending yes/no
        if not simulate_send:
            logger.debug(msg=f"Sending beacon: {stringtosend}")
            # send the beacon to APRS-IS
            myaprsis.ais_send(aprsis_data=stringtosend)
        else:
            logger.debug(msg=f"Simulating beacons: {stringtosend}")
        # apply sleep cycle(s)
        # do we still have messages in our queue?
        # Yes, apply the regular beacon sleep cycle
        if index < len(aprs_beacon_messages):
            time.sleep(program_config["coac_message_delay"]["packet_delay_beacon"])
        else:
            # Otherwise, apply the shorter sleep cycle after sending out
            # our very last beacon message
            time.sleep(
                program_config["coac_message_delay"]["packet_delay_grace_period"]
            )


def send_bulletin_messages(
    class_instance: object,
    myaprsis: APRSISObject,
    bulletin_dict: dict,
    simulate_send: bool = True,
):
    """
    Sends bulletin message list to APRS_IS
    'Recipient' is 'BLNxxx' and is predefined in the bulletin's dict 'key'. The actual message
    itself is stored in the dict's 'value'.
    If 'simulate_send'= True, we still prepare the message but only send it to our log file

    Parameters
    ==========
    class_instance: object
        Instance of the main class
    myaprsis: APRSISObject
        Our aprslib object that we will use for the communication part
    bulletin_dict: dict
        The bulletins that we are going to send upt to the user. Key = BLNxxx, Value = Bulletin Text
    simulate_send: bool
        If True: Prepare string but only send it to logger

    Returns
    =======
    none
    """
    logger.debug(msg="reached bulletin interval; sending bulletins")

    # create our target dictionary which may contain both static
    # and dynamic bulletin messages. First, copy the content from the static
    # bulletin settings - we don't need to check this data again.
    target_dict = copy.deepcopy(bulletin_dict)

    if type(class_instance.dynamic_aprs_bulletins) is types.MappingProxyType:
        # Get the key and value from our configuration file's bulletin messages section
        for key, value in class_instance.dynamic_aprs_bulletins.items():
            # Message populated and less than max APRS message length?
            # note: we do not use message enumeration for bulletins
            # therefore, the max length requirement is always fixed (67 bytes)
            if 0 < len(value) <= APRS_MSG_LEN_NOTRAILING:
                # Check if the identifier follows these APRS requirements:
                # 1) must start with fixed "BLN" string OR "NWS-" string
                # 2) needs to be followed by 1..6 (NWS: 1..5) ASCII-7 characters and/or digits
                # We do not need to look for "finalized" entries, read: the dictionary's key is
                # not required to have keys with 9 chars in total length
                match = re.match(
                    pattern=r"^(bln[a-z0-9]{1,6})|(nws-[a-z0-9]{1,5})$",
                    string=key,
                    flags=re.IGNORECASE,
                )
                if match:
                    # We found a match. As a precaution, let's check if the user has
                    # used characters in the actual message which are special to APRS
                    match = re.findall(r"[{}|~]+", value)
                    if match:
                        logger.debug(
                            msg=f"APRS dynamic bulletin message '{key}': removing special APRS characters from 'value' setting"
                        )
                        # Let's get rid of those control characters from the message
                        value = re.sub(r"[{}|~]+", "", value)
                    # Convert the bulletin identifier to upperkey
                    key = key.upper()
                    # and add it to our dictionary in case it does not exist
                    # and its lenght (after potential character replacements)
                    # is still greater than zero
                    if key not in target_dict and len(value) > 0:
                        target_dict[key] = value
            else:
                logger.debug(
                    f"Ignoring dynamic bulletin setting for '{key}'; value is either empty or exceeds {APRS_MSG_LEN_NOTRAILING} characters. Check your input data"
                )

    # Generate some local variables because the 'black' beautifier seems
    # to choke on multi-dimensional dictionaries
    _aprsis_callsign = program_config["coac_client_config"]["aprsis_callsign"]
    _aprsis_tocall = program_config["coac_client_config"]["aprsis_tocall"]

    # Build and send the list of bulletins
    # Note that we iterate over the unified dictionary of APRS bulletins
    for index, (recipient_id, bln) in enumerate(target_dict.items(), start=1):
        # build the bulletin string
        stringtosend = f"{_aprsis_callsign}>{_aprsis_tocall}::{recipient_id:9}:{bln}"
        # simulate sending yes/no
        if not simulate_send:
            logger.debug(msg=f"Sending bulletin: {stringtosend}")
            # send the bulletin to APRS-IS
            myaprsis.ais_send(aprsis_data=stringtosend)
        else:
            logger.debug(msg=f"simulating bulletins: {stringtosend}")
        # apply sleep cycle(s)
        # do we still have messages in our queue?
        # Yes, apply the regular bulletin sleep cycle
        if index < len(bulletin_dict):
            time.sleep(program_config["coac_message_delay"]["packet_delay_bulletin"])
        else:
            # Otherwise, apply the shorter sleep cycle after sending out
            # our very last bulletin message
            time.sleep(
                program_config["coac_message_delay"]["packet_delay_grace_period"]
            )


# APRSlib callback
# Extract the fields from the APRS message, start the parsing process,
# execute the command and send the command output back to the user
def aprs_callback(
    raw_aprs_packet: dict, parser: types.FunctionType, generator: types.FunctionType
):
    """
    aprslib callback; this is the core process that takes care of everything
    Parameters
    ==========
    raw_aprs_packet: dict
        dict object, containing the raw APRS data
    parser: types.FunctionType
        input parser function
    generator: types.FunctionType
        output generator function
    Returns
    =======
    """
    # Get our relevant fields from the APRS message
    addresse_string = raw_aprs_packet.get("addresse")
    message_text_string = raw_aprs_packet.get("message_text")
    response_string = raw_aprs_packet.get("response")
    msgno_string = raw_aprs_packet.get("msgNo")
    from_callsign = raw_aprs_packet.get("from")
    format_string = raw_aprs_packet.get("format")
    ack_msgno_string = raw_aprs_packet.get("ackMsgNo")

    # lower the response in case we received one
    if response_string:
        response_string = response_string.lower()

    # Check if we need to deal with the old vs the new message format
    new_ackrej_format = True if ack_msgno_string else False

    # Check if this request supports a msgno
    msg_no_supported = True if msgno_string else False

    # User's call sign. read: who has sent us this message?
    if from_callsign:
        from_callsign = from_callsign.upper()

    if addresse_string:
        # Lets examine what we've got:
        # 1. Message format should always be 'message'.
        #    This is even valid for ack/rej responses
        # 2. Message text should contain content
        # 3. response text should NOT be ack/rej
        # Continue if both assumptions are correct
        if (
            format_string == "message"
            and message_text_string
            and response_string not in ["ack", "rej"]
        ):
            # This is a message that belongs to us
            #
            # Check if the message is present in our decaying message cache
            # If the message can be located, then we can assume that we have
            # processed (and potentially acknowledged) that message request
            # within the last e.g. 5 minutes and that this is a delayed / dupe
            # request, thus allowing us to ignore this request.
            aprs_message_key = get_aprs_message_from_cache(
                message_text=message_text_string,
                message_no=msgno_string,
                target_callsign=from_callsign,
                aprs_cache=client_shared.aprs_message_cache,
            )
            if aprs_message_key:
                logger.debug(
                    msg="DUPLICATE APRS PACKET - this message is still in our decaying message cache"
                )
                logger.debug(
                    msg=f"Ignoring duplicate APRS packet raw_aprs_packet: {raw_aprs_packet}"
                )
            else:
                logger.debug(msg=f"Received raw_aprs_packet: {raw_aprs_packet}")

                # Send an ack if we DID receive a message number
                # and we DID NOT have received a request in the
                # new ack/rej format
                # see aprs101.pdf pg. 71ff.
                if msg_no_supported and not new_ackrej_format:
                    send_ack(
                        myaprsis=client_shared.AIS,
                        simulate_send=program_config["coac_testing"][
                            "aprsis_simulate_send"
                        ],
                        source_callsign=program_config["coac_client_config"][
                            "aprsis_callsign"
                        ],
                        tocall=program_config["coac_client_config"]["aprsis_tocall"],
                        target_callsign=from_callsign,
                        source_msg_no=msgno_string,
                        packet_delay=program_config["coac_message_delay"][
                            "packet_delay_ack"
                        ],
                    )
                #
                # This is where the magic happens: Try to figure out what the user
                # wants from us. If we were able to understand the user's message,
                # 'success' will be true. In any case, the 'response_parameters'
                # dictionary will give us a hint about what to do next (and even
                # contains the parser's error message if 'success' != True)
                # input parameters: the actual message, the user's call sign and
                # the aprs.fi API access key for location lookups
                #
                # Note: we call the function which was passed along with the
                # callback object
                retcode, input_parser_error_message, response_parameters = parser(
                    aprs_message=message_text_string,
                    from_callsign=from_callsign,
                )
                logger.debug(msg=f"Input parser result: {retcode}")
                logger.debug(msg=response_parameters)

                # this is our future output message object
                output_message = []

                #
                # parsing successful?
                #
                # We support three possible return codes from the input parser:
                # PARSE_OK     - Input processor has identified keyword and is ready
                #                to continue. This is the desired default state
                #                Whenever the return code is PARSE_OK, then we should know
                #                by now what the user wants from us. Now, we'll leave it to
                #                another module to generate the output data of what we want
                #                to send to the user (client_output_generatpr.py).
                #                The result to this post-processor will be a general success
                #                status code and the message that is to be sent to the user.
                # PARSE_ERROR  - an error has occurred. Most likely, the external
                #                input processor was either unable to identify a
                #                keyword from the message OR a follow-up process has
                #                failed; e.g. the user has defined a wx keyword,
                #                requiring the sender to supply mandatory location info
                #                which was missing from the message. In any way, this signals
                #                the callback function that we are unable to process the
                #                message any further
                # PARSE_IGNORE - The message was ok but we are being told to ignore it. This
                #                might be the case if the user's input processor has a dupe
                #                check that is additional to the one provided by the
                #                core-aprs-client framework. Similar to PARSE_ERROR, we
                #                are not permitted to process this request any further BUT
                #                instead of sending an error message, we will simply ignore
                #                the request. Note that the core-aprs-client framework has
                #                already ack'ed the request at this point, thus preventing it
                #                from getting resend by APRS-IS over and over again.
                #
                # Note that you should refrain from using PARSE_IGNORE whenever possible - a
                # polite inquiry should always trigger a polite response :-) Nevertheless, there
                # might be use cases where you simply need to ignore a (technically valid) request
                # in your custom code.
                #
                #
                match retcode:
                    case CoreAprsClientInputParserStatus.PARSE_OK:
                        # Generate the output message for the requested keyword
                        #
                        # Note: we call the function which was passed along with the
                        # callback object
                        success, output_string = generator(
                            input_parser_response_object=response_parameters
                        )
                        if success:
                            output_message = make_pretty_aprs_messages(
                                message_to_add=output_string
                            )
                        else:
                            # This code branch should never be reached unless there is a
                            # discrepancy between the action determined by the input parser
                            # and the responsive counter-action from the output processor
                            output_message = make_pretty_aprs_messages(
                                message_to_add=program_config["coac_client_config"][
                                    "aprs_input_parser_default_error_message"
                                ],
                            )
                    # This is the branch where the input parser failed to understand
                    # the message. A possible reason: you sent a keyword which requires
                    # an additional parameter but failed to send that one, too.
                    # As we only parse but never process data in that input
                    # parser, we sinply don't know what to do with the user's message
                    # and get back to him with a generic response.
                    case CoreAprsClientInputParserStatus.PARSE_ERROR:
                        # Dump the human readable message to the user if we have one
                        if input_parser_error_message:
                            output_message = make_pretty_aprs_messages(
                                message_to_add=f"{input_parser_error_message}",
                            )
                        # If not, just dump the link to the instructions
                        # This is the default branch which dumps generic information
                        # to the client whenever there is no generic error text from the input parser
                        else:
                            output_message = make_pretty_aprs_messages(
                                message_to_add=program_config["coac_client_config"][
                                    "aprs_input_parser_default_error_message"
                                ],
                            )
                            logger.debug(
                                msg=f"Unable to process APRS packet {raw_aprs_packet}"
                            )
                    # default branch for anything else, including PARSE_IGNORE
                    case _:
                        pass

                # Ultimately, finalize the outgoing message(s) and add the message
                # numbers if the user has requested this in his configuration
                # settings
                output_message = finalize_pretty_aprs_messages(
                    mylistarray=output_message
                )

                # Send our message(s) to APRS-IS
                _aprs_msg_count = send_aprs_message_list(
                    myaprsis=client_shared.AIS,
                    simulate_send=program_config["coac_testing"][
                        "aprsis_simulate_send"
                    ],
                    message_text_array=output_message,
                    destination_call_sign=from_callsign,
                    send_with_msg_no=msg_no_supported,
                    aprs_message_counter=client_shared.aprs_message_counter.get_counter(),
                    external_message_number=msgno_string,
                    new_ackrej_format=new_ackrej_format,
                    packet_delay=program_config["coac_message_delay"][
                        "packet_delay_message"
                    ],
                    packet_delay_grace_period=program_config["coac_message_delay"][
                        "packet_delay_grace_period"
                    ],
                )

                # And store the new APRS message number in our counter object
                client_shared.aprs_message_counter.set_counter(_aprs_msg_count)

                # We've finished processing this message. Update the decaying
                # cache with our message.
                # Store the core message data in our decaying APRS message cache
                # Dupe detection is applied regardless of the message's
                # processing status
                client_shared.aprs_message_cache = add_aprs_message_to_cache(
                    message_text=message_text_string,
                    message_no=msgno_string,
                    target_callsign=from_callsign,
                    aprs_cache=client_shared.aprs_message_cache,
                )


def init_scheduler_jobs(class_instance: object):
    """
    Initializes the scheduler jobs for APRS bulletins and / or beacons.

    Parameters
    ==========

    Returns
    =======
    my_scheduler: BackgroundScheduler object or 'None' if no scheduler was initialized.
    """

    if (
        program_config["coac_beacon_config"]["aprsis_broadcast_beacon"]
        or program_config["coac_bulletin_config"]["aprsis_broadcast_bulletins"]
    ):
        # If we reach this position in the code, we have at least one
        # task that needs to be scheduled (bulletins and/or position messages
        #
        # Create the scheduler
        my_scheduler = BackgroundScheduler()

        # Install two schedulers tasks, if requested by the user
        # The first task is responsible for sending out beacon messages
        # to APRS; it will be triggered every 30 mins
        #

        # The 2nd task is responsible for sending out bulletin messages
        # to APRS; it will be triggered every 4 hours
        #

        if program_config["coac_beacon_config"]["aprsis_broadcast_beacon"]:
            # Send initial beacon after establishing the connection to APRS_IS
            logger.debug(
                msg="Send initial beacon after establishing the connection to APRS_IS"
            )

            #
            # APRS_IS beacon messages (will be sent every 30 mins)
            # - APRS Position (first line) needs to have 63 characters or less
            # - APRS Status can have 67 chars (as usual)
            # Details: see aprs101.pdf chapter 8
            #
            # The client will NOT check the content and send it out 'as is'
            #
            # This message is a position report; format description can be found on pg. 23ff and pg. 94ff.
            # of aprs101.pdf. Message symbols: see http://www.aprs.org/symbols/symbolsX.txt and aprs101.pdf
            # on page 104ff.
            # Format is as follows: =Lat primary-symbol-table-identifier lon symbol-identifier test-message
            # Lat/lon from the configuration have to be valid or the message will not be accepted by aprs-is
            #
            # Example nessage: COAC>APRS:=5150.34N/00819.60E?COAC 0.01
            # results in
            # lat = 5150.34N
            # primary symbol identifier = /
            # lon = 00819.60E
            # symbol identifier = ?
            # plus some text.
            # The overall total symbol code /? refers to a server icon - see list of symbols
            #
            # as all of our parameters are stored in a dictionary, we need to construct

            # create a couple of local variables as the 'black' prettifier seems to
            # choke on multi-dimensional dictionaries

            # fmt:off
            _aprsis_latitude = program_config["coac_beacon_config"]["aprsis_latitude"]
            _aprsis_longitude = program_config["coac_beacon_config"]["aprsis_longitude"]
            _aprsis_table = program_config["coac_beacon_config"]["aprsis_table"]
            _aprsis_symbol = program_config["coac_beacon_config"]["aprsis_symbol"]
            _aprsis_callsign = program_config["coac_client_config"]["aprsis_callsign"]
            _aprsis_beacon_altitude_ft = program_config["coac_beacon_config"]["aprsis_beacon_altitude_ft"]
            # fmt:on

            # check if altitude data is present
            #
            # default assumption: User has provided a numeric value which is then
            # transposed to altitude settings; the config file importer has already
            # done this job for us by now. However, if the variable's type is "str",
            # there is a chance that the user did not provide us with altitude information
            # so we need to check on whether we have to include this field in our
            # beacon or not
            #
            # Assume the default case first (user HAS provided altitude)
            _altitude_present = True
            # field type = 'str'? Then check if the field is empty
            if type(_aprsis_beacon_altitude_ft) is str:
                # Note that this should ALWAYS return "false" - otherwise,
                # we might have encountered a cfg value in the config file
                # which did not consist of purely numeric content
                _altitude_present = len(_aprsis_beacon_altitude_ft) > 0
                if _altitude_present:
                    if not bool(re.fullmatch(r"\d+", _aprsis_beacon_altitude_ft)):
                        raise ValueError(
                            "Invalid 'altitude' setting in configuration file; value must either be numeric or empty"
                        )

            # Build the proper altitude string if altitude data is present
            _aprsis_beacon_altitude_ft = (
                f" /A={str(_aprsis_beacon_altitude_ft).zfill(6)[:6]}"
                if _altitude_present
                else ""
            )

            # generate the APRS beacon string
            _beacon = f"={_aprsis_latitude}{_aprsis_table}{_aprsis_longitude}{_aprsis_symbol}{_aprsis_callsign} {__version__}{_aprsis_beacon_altitude_ft}"

            # and store it in a list item
            aprs_beacon_messages: list = [_beacon]

            # Ultimately, send the initial beacon message
            send_beacon_and_status_msg(
                class_instance=class_instance,
                myaprsis=client_shared.AIS,
                aprs_beacon_messages=aprs_beacon_messages,
                simulate_send=program_config["coac_testing"]["aprsis_simulate_send"],
            )

            # Now let's add position beaconing to scheduler
            my_scheduler.add_job(
                send_beacon_and_status_msg,
                "interval",
                id="aprsbeacon",
                minutes=program_config["coac_beacon_config"][
                    "aprsis_beacon_interval_minutes"
                ],
                args=[
                    class_instance,
                    client_shared.AIS,
                    aprs_beacon_messages,
                    program_config["coac_testing"]["aprsis_simulate_send"],
                ],
                max_instances=1,
                coalesce=True,
            )

        if program_config["coac_bulletin_config"]["aprsis_broadcast_bulletins"]:
            # prepare the bulletin data
            aprs_bulletin_messages = parse_bulletin_data()

            # Install scheduler task 2 - send standard bulletins (advertising the program instance)
            # The bulletin messages consist of fixed content and are defined at the beginning of
            # this program code
            my_scheduler.add_job(
                send_bulletin_messages,
                "interval",
                id="aprsbulletin",
                minutes=program_config["coac_bulletin_config"][
                    "aprsis_bulletin_interval_minutes"
                ],
                args=[
                    class_instance,
                    client_shared.AIS,
                    aprs_bulletin_messages,
                    program_config["coac_testing"]["aprsis_simulate_send"],
                ],
                max_instances=1,
                coalesce=True,
            )

        # Ultimately, start the scheduler
        my_scheduler.start()
    # Default handler in case we neither want bulletins nor beacons
    else:
        my_scheduler = None

    return my_scheduler


def remove_scheduler(aprs_scheduler: BackgroundScheduler):
    """
    Shuts down and the scheduler whereas present.

    Parameters
    ==========
    aprs_scheduler: BackgroundScheduler object or None if no scheduler was initialized.

    Returns
    =======

    """
    # If the scheduler object exists, then try to pause it before it gets destroyed
    if type(aprs_scheduler) is BackgroundScheduler:
        logger.debug(msg="Pausing aprs_scheduler")
        aprs_scheduler.pause()
        aprs_scheduler.remove_all_jobs()
        logger.debug(msg="Shutting down aprs_scheduler")
        if aprs_scheduler.state != apbase.STATE_STOPPED:
            try:
                aprs_scheduler.shutdown()
            except:
                logger.debug(msg="Exception during scheduler shutdown SystemExit loop")


if __name__ == "__main__":
    pass
