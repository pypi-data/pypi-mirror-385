# !/usr/bin/env python3
# -*- coding: utf-8 -*-
#
# Revision and Development: Enno Henn (henn@ipfdd.de), Leibniz Institute of Polymer Research Dresden
# IPF GitLab: https://gitlab.ipfdd.de/Henn/pyatmoweb
# for further information consult the documentation of the AtmoWeb Rest API by Memmert at:
# https://www.memmert.com/index.php?eID=dumpFile&t=f&f=5708&token=e46b35fe2d26d6e83f1db73c13c9314db165a9f0

# Disclaimer
# This software is an independent product and is not developed, maintained, or endorsed by Memmert. 
# All trademarks, brand names, and product names referenced in this software are the property of their respective owners.
# This software is designed to interface with machines manufactured by Memmert, but it is not affiliated with, authorized by, 
# or supported byMemmert in any way. Use of this software is at the user's own risk. 
# The developers of this software make no warranties, express or implied, regarding compatibility, functionality, or reliability when # used in conjunction with Memmert’s hardware or software.
# By using this software, you acknowledge that Memmert is not responsible for any damage, malfunction, or loss resulting from its use.

import requests
import json
import logging

"""
TEMPERATURES
"""


def get_temp_1(ip_address):
    """
    The function queries the AtmoWeb API using requests for Temperature 1 and extracts the
    value (1 decimal) from the response json.
    :param ip_address: Address of the oven that needs to be connected via ethernet
    :return: Temperature 1 Value Type: Float
    """

    url = "http://" + ip_address + "/atmoweb?Temp1Read="
    r = requests.get(url)

    if r.status_code == 200:
        try:
            text = str(r.text)
            text = text.strip(", ")
            json_text = "{" + text + "}"
            json_data = json.loads(json_text)

            # reading value from json
            return_value = float(json_data["Temp1Read"])

        except json.JSONDecodeError as e:
            logging.error(f"error while decoding JSON-Response: {e}")
            return_value = None
    else:
        logging.error(f"error while querying the REST-API: {r.status_code}")
        return_value = None

    return return_value


def get_temp_2(ip_address):
    """
    The function queries the AtmoWeb API using requests for Temperature 2 and extracts the
    value (1 decimal) from the response json.
    :param ip_address: Address of the Oven that needs to be connected via ethernet
    :return: Temperature 2 Value Type: Float
    """
    url = "http://" + ip_address + "/atmoweb?Temp2Read="
    r = requests.get(url)

    if r.status_code == 200:
        try:
            text = str(r.text)
            text = text.strip(", ")
            json_text = "{" + text + "}"
            json_data = json.loads(json_text)

            value = json_data["Temp2Read"]

            if value not in ["N/A"]:
                return_value = float(value)
            else:
                return_value = None

        except json.JSONDecodeError as e:
            logging.error(f"error while decoding JSON-Response: {e}")
            return_value = None
    else:
        logging.error(f"error while querying the REST-API: {r.status_code}")
        return_value = None

    return return_value


def get_temp_3(ip_address):
    """
    The function queries the AtmoWeb API using requests for Temperature 3 and extracts the
    value (1 decimal) from the response json.
    :param ip_address: Address of the Oven that needs to be connected via ethernet
    :return: Temperature 3 Value Type: Float
    """
    url = "http://" + ip_address + "/atmoweb?Temp3Read="
    r = requests.get(url)

    if r.status_code == 200:
        try:
            text = str(r.text)
            text = text.strip(", ")
            json_text = "{" + text + "}"
            json_data = json.loads(json_text)

            value = json_data["Temp3Read"]

            if value not in ["N/A"]:
                return_value = float(value)
            else:
                return_value = None

        except json.JSONDecodeError as e:
            logging.error(f"error while decoding JSON-Response: {e}")
            return_value = None
    else:
        logging.error(f"error while querying the REST-API: {r.status_code}")
        return_value = None

    return return_value


def get_temp_4(ip_address):
    """
    The function queries the AtmoWeb API using requests for Temperature 4 and extracts the
    value (1 decimal) from the response json.
    :param ip_address: Address of the Oven that needs to be connected via ethernet
    :return: Temperature 4 Value Type: Float
    """
    url = "http://" + ip_address + "/atmoweb?Temp4Read="
    r = requests.get(url)

    if r.status_code == 200:
        try:
            text = str(r.text)
            text = text.strip(", ")
            json_text = "{" + text + "}"
            json_data = json.loads(json_text)

            value = json_data["Temp4Read"]

            if value not in ["N/A"]:
                return_value = float(value)
            else:
                return_value = None

        except json.JSONDecodeError as e:
            logging.error(f"error while decoding JSON-Response: {e}")
            return_value = None
    else:
        logging.error(f"error while querying the REST-API: {r.status_code}")
        return_value = None

    return return_value


def get_low_temp_alarm(ip_address):
    """
    The function queries the AtmoWeb API using requests for the lower Temperature to trigger an alarm
    from the response json.
    :param ip_address: Address of the Oven that needs to be connected via ethernet
    :return: Lower Temperature limit for an alarm: Float
    """
    url = "http://" + ip_address + "/atmoweb?AlTempLo="
    r = requests.get(url)

    if r.status_code == 200:
        try:
            text = str(r.text)
            text = text.strip(", ")
            json_text = "{" + text + "}"
            json_data = json.loads(json_text)

            value = json_data["AlTempLo"]

            if value not in ["N/A"]:
                return_value = float(value)
            else:
                return_value = None

        except json.JSONDecodeError as e:
            logging.error(f"error while decoding JSON-Response: {e}")
            return_value = None
    else:
        logging.error(f"error while querying the REST-API: {r.status_code}")
        return_value = None

    return return_value


def get_high_temp_alarm(ip_address):
    """
    The function queries the AtmoWeb API using requests for the high Temperature to trigger an alarm
    from the response json.
    :param ip_address: Address of the Oven that needs to be connected via ethernet
    :return: Lower Temperature limit for an alarm: Float
    """
    url = "http://" + ip_address + "/atmoweb?AlTempHi="
    r = requests.get(url)

    if r.status_code == 200:
        try:
            text = str(r.text)
            text = text.strip(", ")
            json_text = "{" + text + "}"
            json_data = json.loads(json_text)

            value = json_data["AlTempHi"]

            if value not in ["N/A"]:
                return_value = float(value)
            else:
                return_value = None

        except json.JSONDecodeError as e:
            logging.error(f"error while decoding JSON-Response: {e}")
            return_value = None
    else:
        logging.error(f"error while querying the REST-API: {r.status_code}")
        return_value = None

    return return_value


def get_low_temp_alarm_range(ip_address):
    """
    The function queries the AtmoWeb API using requests for the lower Temperature alarm range
    from the response json.
    :param ip_address: Address of the Oven that needs to be connected via ethernet
    :return: Lower Temperature limit for an alarm: Float
    """
    url = "http://" + ip_address + "/atmoweb?AlTempLo_Range="
    r = requests.get(url)

    if r.status_code == 200:
        try:
            text = str(r.text)
            text = text.strip(", ")
            json_text = "{" + text + "}"
            json_data = json.loads(json_text)

            value = json_data["AlTempLo_Range"]

            if value not in ["N/A"]:
                return_value = value
            else:
                return_value = None

        except json.JSONDecodeError as e:
            logging.error(f"error while decoding JSON-Response: {e}")
            return_value = None
    else:
        logging.error(f"error while querying the REST-API: {r.status_code}")
        return_value = None

    return return_value


def get_high_temp_alarm_range(ip_address):
    """
    The function queries the AtmoWeb API using requests for the higher Temperature alarm range
    from the response json.
    :param ip_address: Address of the Oven that needs to be connected via ethernet
    :return: higher Temperature limit for an alarm: Float
    """
    url = "http://" + ip_address + "/atmoweb?AlTempHi_Range="
    r = requests.get(url)

    if r.status_code == 200:
        try:
            text = str(r.text)
            text = text.strip(", ")
            json_text = "{" + text + "}"
            json_data = json.loads(json_text)

            value = json_data["AlTempHi_Range"]

            if value not in ["N/A"]:
                return_value = value
            else:
                return_value = None

        except json.JSONDecodeError as e:
            logging.error(f"error while decoding JSON-Response: {e}")
            return_value = None
    else:
        logging.error(f"error while querying the REST-API: {r.status_code}")
        return_value = None

    return return_value


"""
HUMIDITY
"""


def get_humidity(ip_address):
    """
    The function queries the AtmoWeb API using requests for getting the humidity
    from the response json.
    :param ip_address: Address of the Oven that needs to be connected via ethernet
    :return: humidity in r.h.: Float
    """
    url = "http://" + ip_address + "/atmoweb?HumRead="
    r = requests.get(url)

    if r.status_code == 200:
        try:
            text = str(r.text)
            text = text.strip(", ")
            json_text = "{" + text + "}"
            json_data = json.loads(json_text)

            value = json_data["HumRead"]

            if value not in ["N/A"]:
                return_value = float(value)
            else:
                return_value = None

        except json.JSONDecodeError as e:
            logging.error(f"error while decoding JSON-Response: {e}")
            return_value = None
    else:
        logging.error(f"error while querying the REST-API: {r.status_code}")
        return_value = None

    return return_value


def get_humidity_set_range(ip_address):
    """
    The function queries the AtmoWeb API using requests for getting the set humidity
    range from the response json.
    :param ip_address: Address of the Oven that needs to be connected via ethernet
    :return: humidity range in %: Float
    """
    url = "http://" + ip_address + "/atmoweb?HumSet_Range="
    r = requests.get(url)

    if r.status_code == 200:
        try:
            text = str(r.text)
            text = text.strip(", ")
            json_text = "{" + text + "}"
            json_data = json.loads(json_text)

            value = json_data["HumSet_Range"]

            if value not in ["N/A"]:
                return_value = value
            else:
                return_value = None

        except json.JSONDecodeError as e:
            logging.error(f"error while decoding JSON-Response: {e}")
            return_value = None
    else:
        logging.error(f"error while querying the REST-API: {r.status_code}")
        return_value = None

    return return_value


def get_low_humidity_alarm(ip_address):
    """
    The function queries the AtmoWeb API using requests for the low humidity to trigger an alarm
    from the response json.
    :param ip_address: Address of the Oven that needs to be connected via ethernet
    :return: Lower humidity limit for an alarm: Float
    """
    url = "http://" + ip_address + "/atmoweb?AlHumLo="
    r = requests.get(url)

    if r.status_code == 200:
        try:
            text = str(r.text)
            text = text.strip(", ")
            json_text = "{" + text + "}"
            json_data = json.loads(json_text)

            value = json_data["AlHumLo"]

            if value not in ["N/A"]:
                return_value = float(value)
            else:
                return_value = None

        except json.JSONDecodeError as e:
            logging.error(f"error while decoding JSON-Response: {e}")
            return_value = None
    else:
        logging.error(f"error while querying the REST-API: {r.status_code}")
        return_value = None

    return return_value


def get_high_humidity_alarm(ip_address):
    """
    The function queries the AtmoWeb API using requests for the high humidity to trigger an alarm
    from the response json.
    :param ip_address: Address of the Oven that needs to be connected via ethernet
    :return: higher humidity limit for an alarm: Float
    """
    url = "http://" + ip_address + "/atmoweb?AlHumHi="
    r = requests.get(url)

    if r.status_code == 200:
        try:
            text = str(r.text)
            text = text.strip(", ")
            json_text = "{" + text + "}"
            json_data = json.loads(json_text)

            value = json_data["AlHumHi"]

            if value not in ["N/A"]:
                return_value = float(value)
            else:
                return_value = None

        except json.JSONDecodeError as e:
            logging.error(f"error while decoding JSON-Response: {e}")
            return_value = None
    else:
        logging.error(f"error while querying the REST-API: {r.status_code}")
        return_value = None

    return return_value


def get_high_humidity_alarm_range(ip_address):
    """
    The function queries the AtmoWeb API using requests for the high humidity range to trigger an alarm
    from the response json.
    :param ip_address: Address of the Oven that needs to be connected via ethernet
    :return: higher humidity range for an alarm: Float
    """
    url = "http://" + ip_address + "/atmoweb?AlHumHi_Range="
    r = requests.get(url)

    if r.status_code == 200:
        try:
            text = str(r.text)
            text = text.strip(", ")
            json_text = "{" + text + "}"
            json_data = json.loads(json_text)

            value = json_data["AlHumHi_Range"]

            if value not in ["N/A"]:
                return_value = value
            else:
                return_value = None

        except json.JSONDecodeError as e:
            logging.error(f"error while decoding JSON-Response: {e}")
            return_value = None
    else:
        logging.error(f"error while querying the REST-API: {r.status_code}")
        return_value = None

    return return_value


def get_low_humidity_alarm_range(ip_address):
    """
    The function queries the AtmoWeb API using requests for the low humidity range to trigger an alarm
    from the response json.
    :param ip_address: Address of the Oven that needs to be connected via ethernet
    :return: higher humidity range for an alarm: Float
    """
    url = "http://" + ip_address + "/atmoweb?AlHumLo_Range="
    r = requests.get(url)

    if r.status_code == 200:
        try:
            text = str(r.text)
            text = text.strip(", ")
            json_text = "{" + text + "}"
            json_data = json.loads(json_text)

            value = json_data["AlHumLo_Range"]

            if value not in ["N/A"]:
                return_value = value
            else:
                return_value = None

        except json.JSONDecodeError as e:
            logging.error(f"error while decoding JSON-Response: {e}")
            return_value = None
    else:
        logging.error(f"error while querying the REST-API: {r.status_code}")
        return_value = None

    return return_value


"""
VACUUM
"""


def get_vacuum_set_point(ip_address):
    """
    The function queries the AtmoWeb API using requests for the vacuum set point
    from the response json.
    :param ip_address: Address of the Oven that needs to be connected via ethernet
    :return: vacuum set point: Float
    """
    url = "http://" + ip_address + "/atmoweb?VacSet="
    r = requests.get(url)

    if r.status_code == 200:
        try:
            text = str(r.text)
            text = text.strip(", ")
            json_text = "{" + text + "}"
            json_data = json.loads(json_text)

            value = json_data["VacSet"]

            if value not in ["N/A"]:
                return_value = float(value)
            else:
                return_value = None

        except json.JSONDecodeError as e:
            logging.error(f"error while decoding JSON-Response: {e}")
            return_value = None
    else:
        logging.error(f"error while querying the REST-API: {r.status_code}")
        return_value = None

    return return_value


def get_vacuum_set_point_range(ip_address):
    """
    The function queries the AtmoWeb API using requests for the vacuum set point
    range from the response json.
    :param ip_address: Address of the Oven that needs to be connected via ethernet
    :return: vacuum set point range: Float
    """
    url = "http://" + ip_address + "/atmoweb?VacSet_Range="
    r = requests.get(url)

    if r.status_code == 200:
        try:
            text = str(r.text)
            text = text.strip(", ")
            json_text = "{" + text + "}"
            json_data = json.loads(json_text)

            value = json_data["VacSet_Range"]

            if value not in ["N/A"]:
                return_value = value
            else:
                return_value = None

        except json.JSONDecodeError as e:
            logging.error(f"error while decoding JSON-Response: {e}")
            return_value = None
    else:
        logging.error(f"error while querying the REST-API: {r.status_code}")
        return_value = None

    return return_value


def get_vacuum(ip_address):
    """
    The function queries the AtmoWeb API using requests for current vacuum value
    from the response json.
    :param ip_address: Address of the Oven that needs to be connected via ethernet
    :return: low vacuum range for an alarm: Float
    """
    url = "http://" + ip_address + "/atmoweb?VacRead="
    r = requests.get(url)

    if r.status_code == 200:
        try:
            text = str(r.text)
            text = text.strip(", ")
            json_text = "{" + text + "}"
            json_data = json.loads(json_text)

            value = json_data["VacRead"]

            if value not in ["N/A"]:
                return_value = float(value)
            else:
                return_value = None

        except json.JSONDecodeError as e:
            logging.error(f"error while decoding JSON-Response: {e}")
            return_value = None
    else:
        logging.error(f"error while querying the REST-API: {r.status_code}")
        return_value = None

    return return_value


def get_high_vacuum_alarm(ip_address):
    """
    The function queries the AtmoWeb API using requests for the high vacuum to trigger an alarm
    from the response json.
    :param ip_address: Address of the Oven that needs to be connected via ethernet
    :return: higher vacuum limit for an alarm: Float
    """
    url = "http://" + ip_address + "/atmoweb?AlVacHi="
    r = requests.get(url)

    if r.status_code == 200:
        try:
            text = str(r.text)
            text = text.strip(", ")
            json_text = "{" + text + "}"
            json_data = json.loads(json_text)

            value = json_data["AlVacHi"]

            if value not in ["N/A"]:
                return_value = float(value)
            else:
                return_value = None

        except json.JSONDecodeError as e:
            logging.error(f"error while decoding JSON-Response: {e}")
            return_value = None
    else:
        logging.error(f"error while querying the REST-API: {r.status_code}")
        return_value = None

    return return_value


def get_low_vacuum_alarm(ip_address):
    """
    The function queries the AtmoWeb API using requests for the low vacuum to trigger an alarm
    from the response json.
    :param ip_address: Address of the Oven that needs to be connected via ethernet
    :return: low vacuum limit for an alarm: Float
    """
    url = "http://" + ip_address + "/atmoweb?AlVacLo="
    r = requests.get(url)

    if r.status_code == 200:
        try:
            text = str(r.text)
            text = text.strip(", ")
            json_text = "{" + text + "}"
            json_data = json.loads(json_text)

            value = json_data["AlVacLo"]

            if value not in ["N/A"]:
                return_value = float(value)
            else:
                return_value = None

        except json.JSONDecodeError as e:
            logging.error(f"error while decoding JSON-Response: {e}")
            return_value = None
    else:
        logging.error(f"error while querying the REST-API: {r.status_code}")
        return_value = None

    return return_value


def get_low_vacuum_alarm_range(ip_address):
    """
    The function queries the AtmoWeb API using requests for the low vacuum range to trigger an alarm
    from the response json.
    :param ip_address: Address of the Oven that needs to be connected via ethernet
    :return: low vacuum range for an alarm: Float
    """
    url = "http://" + ip_address + "/atmoweb?AlVacLo_Range="
    r = requests.get(url)

    if r.status_code == 200:
        try:
            text = str(r.text)
            text = text.strip(", ")
            json_text = "{" + text + "}"
            json_data = json.loads(json_text)

            value = json_data["AlVacLo_Range"]

            if value not in ["N/A"]:
                return_value = value
            else:
                return_value = None

        except json.JSONDecodeError as e:
            logging.error(f"error while decoding JSON-Response: {e}")
            return_value = None
    else:
        logging.error(f"error while querying the REST-API: {r.status_code}")
        return_value = None

    return return_value


def get_high_vacuum_alarm_range(ip_address):
    """
    The function queries the AtmoWeb API using requests for the low vacuum range to trigger an alarm
    from the response json.
    :param ip_address: Address of the Oven that needs to be connected via ethernet
    :return: high vacuum range for an alarm: Float
    """
    url = "http://" + ip_address + "/atmoweb?AlVacHi_Range="
    r = requests.get(url)

    if r.status_code == 200:
        try:
            text = str(r.text)
            text = text.strip(", ")
            json_text = "{" + text + "}"
            json_data = json.loads(json_text)

            value = json_data["AlVacHi_Range"]

            if value not in ["N/A"]:
                return_value = value
            else:
                return_value = None

        except json.JSONDecodeError as e:
            logging.error(f"error while decoding JSON-Response: {e}")
            return_value = None
    else:
        logging.error(f"error while querying the REST-API: {r.status_code}")
        return_value = None

    return return_value


"""
CO2 GAS
"""


def get_co2_set_point(ip_address):
    """
    The function queries the AtmoWeb API using requests for the co2 set point
    from the response json.
    :param ip_address: Address of the Oven that needs to be connected via ethernet
    :return: co2 set point: Float
    """
    url = "http://" + ip_address + "/atmoweb?CO2Set="
    r = requests.get(url)

    if r.status_code == 200:
        try:
            text = str(r.text)
            text = text.strip(", ")
            json_text = "{" + text + "}"
            json_data = json.loads(json_text)

            value = json_data["CO2Set"]

            if value not in ["N/A"]:
                return_value = float(value)
            else:
                return_value = None

        except json.JSONDecodeError as e:
            logging.error(f"error while decoding JSON-Response: {e}")
            return_value = None
    else:
        logging.error(f"error while querying the REST-API: {r.status_code}")
        return_value = None

    return return_value


def get_co2_set_point_range(ip_address):
    """
    The function queries the AtmoWeb API using requests for the co2 set point
    range from the response json.
    :param ip_address: Address of the Oven that needs to be connected via ethernet
    :return: co2 set point range: Float
    """
    url = "http://" + ip_address + "/atmoweb?CO2Set_Range="
    r = requests.get(url)

    if r.status_code == 200:
        try:
            text = str(r.text)
            text = text.strip(", ")
            json_text = "{" + text + "}"
            json_data = json.loads(json_text)

            value = json_data["CO2Set_Range"]

            if value not in ["N/A"]:
                return_value = value
            else:
                return_value = None

        except json.JSONDecodeError as e:
            logging.error(f"error while decoding JSON-Response: {e}")
            return_value = None
    else:
        logging.error(f"error while querying the REST-API: {r.status_code}")
        return_value = None

    return return_value


def get_co2(ip_address):
    """
    The function queries the AtmoWeb API using requests for current co2 value
    from the response json.
    :param ip_address: Address of the Oven that needs to be connected via ethernet
    :return: current co2 value: Float
    """
    url = "http://" + ip_address + "/atmoweb?CO2Read="
    r = requests.get(url)

    if r.status_code == 200:
        try:
            text = str(r.text)
            text = text.strip(", ")
            json_text = "{" + text + "}"
            json_data = json.loads(json_text)

            value = json_data["CO2Read"]

            if value not in ["N/A"]:
                return_value = float(value)
            else:
                return_value = None

        except json.JSONDecodeError as e:
            logging.error(f"error while decoding JSON-Response: {e}")
            return_value = None
    else:
        logging.error(f"error while querying the REST-API: {r.status_code}")
        return_value = None

    return return_value


def get_high_co2_alarm(ip_address):
    """
    The function queries the AtmoWeb API using requests for the high co2 to trigger an alarm
    from the response json.
    :param ip_address: Address of the Oven that needs to be connected via ethernet
    :return: higher co2 limit for an alarm: Float
    """
    url = "http://" + ip_address + "/atmoweb?AlCO2Hi="
    r = requests.get(url)

    if r.status_code == 200:
        try:
            text = str(r.text)
            text = text.strip(", ")
            json_text = "{" + text + "}"
            json_data = json.loads(json_text)

            value = json_data["AlCO2Hi"]

            if value not in ["N/A"]:
                return_value = float(value)
            else:
                return_value = None

        except json.JSONDecodeError as e:
            logging.error(f"error while decoding JSON-Response: {e}")
            return_value = None
    else:
        logging.error(f"error while querying the REST-API: {r.status_code}")
        return_value = None

    return return_value


def get_low_co2_alarm(ip_address):
    """
    The function queries the AtmoWeb API using requests for the low vacuum to trigger an alarm
    from the response json.
    :param ip_address: Address of the Oven that needs to be connected via ethernet
    :return: low co2 limit for an alarm: Float
    """
    url = "http://" + ip_address + "/atmoweb?AlCO2Lo="
    r = requests.get(url)

    if r.status_code == 200:
        try:
            text = str(r.text)
            text = text.strip(", ")
            json_text = "{" + text + "}"
            json_data = json.loads(json_text)

            value = json_data["AlCO2Lo"]

            if value not in ["N/A"]:
                return_value = float(value)
            else:
                return_value = None

        except json.JSONDecodeError as e:
            logging.error(f"error while decoding JSON-Response: {e}")
            return_value = None
    else:
        logging.error(f"error while querying the REST-API: {r.status_code}")
        return_value = None

    return return_value


def get_low_co2_alarm_range(ip_address):
    """
    The function queries the AtmoWeb API using requests for the low vacuum range to trigger an alarm
    from the response json.
    :param ip_address: Address of the Oven that needs to be connected via ethernet
    :return: low vacuum range for an alarm: Float
    """
    url = "http://" + ip_address + "/atmoweb?AlCO2Lo_Range="
    r = requests.get(url)

    if r.status_code == 200:
        try:
            text = str(r.text)
            text = text.strip(", ")
            json_text = "{" + text + "}"
            json_data = json.loads(json_text)

            value = json_data["AlCO2Lo_Range"]

            if value not in ["N/A"]:
                return_value = value
            else:
                return_value = None

        except json.JSONDecodeError as e:
            logging.error(f"error while decoding JSON-Response: {e}")
            return_value = None
    else:
        logging.error(f"error while querying the REST-API: {r.status_code}")
        return_value = None

    return return_value


def get_high_co2_alarm_range(ip_address):
    """
    The function queries the AtmoWeb API using requests for the low co2 range to trigger an alarm
    from the response json.
    :param ip_address: Address of the Oven that needs to be connected via ethernet
    :return: high co2 range for an alarm: Float
    """
    url = "http://" + ip_address + "/atmoweb?AlCO2Hi_Range="
    r = requests.get(url)

    if r.status_code == 200:
        try:
            text = str(r.text)
            text = text.strip(", ")
            json_text = "{" + text + "}"
            json_data = json.loads(json_text)

            value = json_data["AlCO2Hi_Range"]

            if value not in ["N/A"]:
                return_value = value
            else:
                return_value = None

        except json.JSONDecodeError as e:
            logging.error(f"error while decoding JSON-Response: {e}")
            return_value = None
    else:
        logging.error(f"error while querying the REST-API: {r.status_code}")
        return_value = None

    return return_value


"""
O2 GAS
"""


def get_o2_set_point(ip_address):
    """
    The function queries the AtmoWeb API using requests for the o2 set point
    from the response json.
    :param ip_address: Address of the Oven that needs to be connected via ethernet
    :return: o2 set point: Float
    """
    url = "http://" + ip_address + "/atmoweb?O2Set="
    r = requests.get(url)

    if r.status_code == 200:
        try:
            text = str(r.text)
            text = text.strip(", ")
            json_text = "{" + text + "}"
            json_data = json.loads(json_text)

            value = json_data["O2Set"]

            if value not in ["N/A"]:
                return_value = float(value)
            else:
                return_value = None

        except json.JSONDecodeError as e:
            logging.error(f"error while decoding JSON-Response: {e}")
            return_value = None
    else:
        logging.error(f"error while querying the REST-API: {r.status_code}")
        return_value = None

    return return_value


def get_o2_set_point_range(ip_address):
    """
    The function queries the AtmoWeb API using requests for the o2 set point
    range from the response json.
    :param ip_address: Address of the Oven that needs to be connected via ethernet
    :return: o2 set point range: Float
    """
    url = "http://" + ip_address + "/atmoweb?O2Set_Range="
    r = requests.get(url)

    if r.status_code == 200:
        try:
            text = str(r.text)
            text = text.strip(", ")
            json_text = "{" + text + "}"
            json_data = json.loads(json_text)

            value = json_data["O2Set_Range"]

            if value not in ["N/A"]:
                return_value = value
            else:
                return_value = None

        except json.JSONDecodeError as e:
            logging.error(f"error while decoding JSON-Response: {e}")
            return_value = None
    else:
        logging.error(f"error while querying the REST-API: {r.status_code}")
        return_value = None

    return return_value


def get_o2(ip_address):
    """
    The function queries the AtmoWeb API using requests for current o2 value
    from the response json.
    :param ip_address: Address of the Oven that needs to be connected via ethernet
    :return: current o2 value: Float
    """
    url = "http://" + ip_address + "/atmoweb?O2Read="
    r = requests.get(url)

    if r.status_code == 200:
        try:
            text = str(r.text)
            text = text.strip(", ")
            json_text = "{" + text + "}"
            json_data = json.loads(json_text)

            value = json_data["O2Read"]

            if value not in ["N/A"]:
                return_value = float(value)
            else:
                return_value = None

        except json.JSONDecodeError as e:
            logging.error(f"error while decoding JSON-Response: {e}")
            return_value = None
    else:
        logging.error(f"error while querying the REST-API: {r.status_code}")
        return_value = None

    return return_value


def get_high_o2_alarm(ip_address):
    """
    The function queries the AtmoWeb API using requests for the high o2 to trigger an alarm
    from the response json.
    :param ip_address: Address of the Oven that needs to be connected via ethernet
    :return: higher o2 limit for an alarm: Float
    """
    url = "http://" + ip_address + "/atmoweb?AlO2Hi="
    r = requests.get(url)

    if r.status_code == 200:
        try:
            text = str(r.text)
            text = text.strip(", ")
            json_text = "{" + text + "}"
            json_data = json.loads(json_text)

            value = json_data["AlO2Hi"]

            if value not in ["N/A"]:
                return_value = float(value)
            else:
                return_value = None

        except json.JSONDecodeError as e:
            logging.error(f"error while decoding JSON-Response: {e}")
            return_value = None
    else:
        logging.error(f"error while querying the REST-API: {r.status_code}")
        return_value = None

    return return_value


def get_low_o2_alarm(ip_address):
    """
    The function queries the AtmoWeb API using requests for the low o2 to trigger an alarm
    from the response json.
    :param ip_address: Address of the Oven that needs to be connected via ethernet
    :return: low o2 limit for an alarm: Float
    """
    url = "http://" + ip_address + "/atmoweb?AlO2Lo="
    r = requests.get(url)

    if r.status_code == 200:
        try:
            text = str(r.text)
            text = text.strip(", ")
            json_text = "{" + text + "}"
            json_data = json.loads(json_text)

            value = json_data["AlO2Lo"]

            if value not in ["N/A"]:
                return_value = float(value)
            else:
                return_value = None

        except json.JSONDecodeError as e:
            logging.error(f"error while decoding JSON-Response: {e}")
            return_value = None
    else:
        logging.error(f"error while querying the REST-API: {r.status_code}")
        return_value = None

    return return_value


def get_low_o2_alarm_range(ip_address):
    """
    The function queries the AtmoWeb API using requests for the low o2 range to trigger an alarm
    from the response json.
    :param ip_address: Address of the Oven that needs to be connected via ethernet
    :return: low o2 range for an alarm: Float
    """
    url = "http://" + ip_address + "/atmoweb?AlO2Lo_Range="
    r = requests.get(url)

    if r.status_code == 200:
        try:
            text = str(r.text)
            text = text.strip(", ")
            json_text = "{" + text + "}"
            json_data = json.loads(json_text)

            value = json_data["AlO2Lo_Range"]

            if value not in ["N/A"]:
                return_value = value
            else:
                return_value = None

        except json.JSONDecodeError as e:
            logging.error(f"error while decoding JSON-Response: {e}")
            return_value = None
    else:
        logging.error(f"error while querying the REST-API: {r.status_code}")
        return_value = None

    return return_value


def get_high_o2_alarm_range(ip_address):
    """
    The function queries the AtmoWeb API using requests for the low o2 range to trigger an alarm
    from the response json.
    :param ip_address: Address of the Oven that needs to be connected via ethernet
    :return: high o2 range for an alarm: Float
    """
    url = "http://" + ip_address + "/atmoweb?AlO2Hi_Range="
    r = requests.get(url)

    if r.status_code == 200:
        try:
            text = str(r.text)
            text = text.strip(", ")
            json_text = "{" + text + "}"
            json_data = json.loads(json_text)

            value = json_data["AlO2Hi_Range"]

            if value not in ["N/A"]:
                return_value = value
            else:
                return_value = None

        except json.JSONDecodeError as e:
            logging.error(f"error while decoding JSON-Response: {e}")
            return_value = None
    else:
        logging.error(f"error while querying the REST-API: {r.status_code}")
        return_value = None

    return return_value


"""
FAN
"""


def get_fan_set_point(ip_address):
    """
    The function queries the AtmoWeb API using requests for the Fan Speed set point
    :param ip_address: Address of the Oven that needs to be connected via ethernet
    :return: Fan Speed set point value: Float
    """
    url = "http://" + ip_address + "/atmoweb?FanSet="
    r = requests.get(url)

    if r.status_code == 200:
        try:
            text = str(r.text)
            text = text.strip(", ")
            json_text = "{" + text + "}"
            json_data = json.loads(json_text)

            value = json_data["FanSet"]

            if value not in ["N/A"]:
                return_value = float(value)
            else:
                return_value = None

        except json.JSONDecodeError as e:
            logging.error(f"error while decoding JSON-Response: {e}")
            return_value = None
    else:
        logging.error(f"error while querying the REST-API: {r.status_code}")
        return_value = None

    return return_value


def get_fan_speed(ip_address):
    """
    The function queries the AtmoWeb API using requests for the Fan Speed
    :param ip_address: Address of the Oven that needs to be connected via ethernet
    :return: current fan speed value: Float
    """
    url = "http://" + ip_address + "/atmoweb?FanRead="
    r = requests.get(url)

    if r.status_code == 200:
        try:
            text = str(r.text)
            text = text.strip(", ")
            json_text = "{" + text + "}"
            json_data = json.loads(json_text)

            value = json_data["FanRead"]

            if value not in ["N/A"]:
                return_value = float(value)
            else:
                return_value = None

        except json.JSONDecodeError as e:
            logging.error(f"error while decoding JSON-Response: {e}")
            return_value = None
    else:
        logging.error(f"error while querying the REST-API: {r.status_code}")
        return_value = None

    return return_value


def get_fan_set_range(ip_address):
    """
    The function queries the AtmoWeb API using requests for the Fan Speed set point range
    :param ip_address: Address of the Oven that needs to be connected via ethernet
    :return: Fan Speed set range values: Float
    """
    url = "http://" + ip_address + "/atmoweb?FanSet_Range="
    r = requests.get(url)

    if r.status_code == 200:
        try:
            text = str(r.text)
            text = text.strip(", ")
            json_text = "{" + text + "}"
            json_data = json.loads(json_text)

            value = json_data["FanSet_Range"]

            if value not in ["N/A"]:
                return_value = value
            else:
                return_value = None

        except json.JSONDecodeError as e:
            logging.error(f"error while decoding JSON-Response: {e}")
            return_value = None
    else:
        logging.error(f"error while querying the REST-API: {r.status_code}")
        return_value = None

    return return_value


"""
Switches
"""


def get_switch_A_state(ip_address):
    """
    The function queries the AtmoWeb API using requests for the stat of switch A
    0 represents open, 1 represents closed
    :param ip_address: Address of the Oven that needs to be connected via ethernet
    :return: state of switch A: Integer
    """
    url = "http://" + ip_address + "/atmoweb?SwASet="
    r = requests.get(url)

    if r.status_code == 200:
        try:
            text = str(r.text)
            text = text.strip(", ")
            json_text = "{" + text + "}"
            json_data = json.loads(json_text)

            value = json_data["SwASet"]

            if value not in ["N/A"]:
                return_value = int(value)
            else:
                return_value = None

        except json.JSONDecodeError as e:
            logging.error(f"error while decoding JSON-Response: {e}")
            return_value = None
    else:
        logging.error(f"error while querying the REST-API: {r.status_code}")
        return_value = None

    return return_value


def get_switch_B_state(ip_address):
    """
    The function queries the AtmoWeb API using requests for the stat of switch B
    0 represents open, 1 represents closed
    :param ip_address: Address of the Oven that needs to be connected via ethernet
    :return: state of switch B: Integer
    """
    url = "http://" + ip_address + "/atmoweb?SwBSet="
    r = requests.get(url)

    if r.status_code == 200:
        try:
            text = str(r.text)
            text = text.strip(", ")
            json_text = "{" + text + "}"
            json_data = json.loads(json_text)

            value = json_data["SwBSet"]

            if value not in ["N/A"]:
                return_value = int(value)
            else:
                return_value = None

        except json.JSONDecodeError as e:
            logging.error(f"error while decoding JSON-Response: {e}")
            return_value = None
    else:
        logging.error(f"error while querying the REST-API: {r.status_code}")
        return_value = None

    return return_value


def get_switch_C_state(ip_address):
    """
    The function queries the AtmoWeb API using requests for the stat of switch C
    0 represents open, 1 represents closed
    :param ip_address: Address of the Oven that needs to be connected via ethernet
    :return: state of switch C: Integer
    """
    url = "http://" + ip_address + "/atmoweb?SwCSet="
    r = requests.get(url)

    if r.status_code == 200:
        try:
            text = str(r.text)
            text = text.strip(", ")
            json_text = "{" + text + "}"
            json_data = json.loads(json_text)

            value = json_data["SwCSet"]

            if value not in ["N/A"]:
                return_value = int(value)
            else:
                return_value = None

        except json.JSONDecodeError as e:
            logging.error(f"error while decoding JSON-Response: {e}")
            return_value = None
    else:
        logging.error(f"error while querying the REST-API: {r.status_code}")
        return_value = None

    return return_value


def get_switch_D_state(ip_address):
    """
    The function queries the AtmoWeb API using requests for the stat of switch D
    0 represents open, 1 represents closed
    :param ip_address: Address of the Oven that needs to be connected via ethernet
    :return: state of switch D: Integer
    """
    url = "http://" + ip_address + "/atmoweb?SwDSet="
    r = requests.get(url)

    if r.status_code == 200:
        try:
            text = str(r.text)
            text = text.strip(", ")
            json_text = "{" + text + "}"
            json_data = json.loads(json_text)

            value = json_data["SwDSet"]

            if value not in ["N/A"]:
                return_value = int(value)
            else:
                return_value = None

        except json.JSONDecodeError as e:
            logging.error(f"error while decoding JSON-Response: {e}")
            return_value = None
    else:
        logging.error(f"error while querying the REST-API: {r.status_code}")
        return_value = None

    return return_value


"""
FLAP
"""


def get_flap_position(ip_address):
    """
    The function queries the AtmoWeb API using requests for the position of the
    flap position is in 10% steps
    :param ip_address: Address of the Oven that needs to be connected via ethernet
    :return: flap position in percents: Float
    """
    url = "http://" + ip_address + "/atmoweb?FlapSet="
    r = requests.get(url)

    if r.status_code == 200:
        try:
            text = str(r.text)
            text = text.strip(", ")
            json_text = "{" + text + "}"
            json_data = json.loads(json_text)

            value = json_data["FlapSet"]

            if value not in ["N/A"]:
                return_value = float(value)
            else:
                return_value = None

        except json.JSONDecodeError as e:
            logging.error(f"error while decoding JSON-Response: {e}")
            return_value = None
    else:
        logging.error(f"error while querying the REST-API: {r.status_code}")
        return_value = None

    return return_value


"""
DOOR
"""


def get_door_state(ip_address):
    """
    The function queries the AtmoWeb API using requests for the stat of oven door
    0 represents closed, 1 represents open
    :param ip_address: Address of the Oven that needs to be connected via ethernet
    :return: state of the oven door: Integer
    """
    url = "http://" + ip_address + "/atmoweb?DoorOpen="
    r = requests.get(url)

    if r.status_code == 200:
        try:
            text = str(r.text)
            text = text.strip(", ")
            json_text = "{" + text + "}"
            json_data = json.loads(json_text)

            value = json_data["DoorOpen"]

            if value not in ["N/A"]:
                return_value = int(value)
            else:
                return_value = None

        except json.JSONDecodeError as e:
            logging.error(f"error while decoding JSON-Response: {e}")
            return_value = None
    else:
        logging.error(f"error while querying the REST-API: {r.status_code}")
        return_value = None

    return return_value


def get_door_lock_state(ip_address):
    """
    The function queries the AtmoWeb API using requests for the stat of oven door lock
    0 represents unlocked, 1 represents locked
    :param ip_address: Address of the Oven that needs to be connected via ethernet
    :return: state of the oven door: Integer
    """
    url = "http://" + ip_address + "/atmoweb?DoorLock="
    r = requests.get(url)

    if r.status_code == 200:
        try:
            text = str(r.text)
            text = text.strip(", ")
            json_text = "{" + text + "}"
            json_data = json.loads(json_text)

            value = json_data["DoorLock"]

            if value not in ["N/A"]:
                return_value = int(value)
            else:
                return_value = None

        except json.JSONDecodeError as e:
            logging.error(f"error while decoding JSON-Response: {e}")
            return_value = None
    else:
        logging.error(f"error while querying the REST-API: {r.status_code}")
        return_value = None

    return return_value


"""
LIGHT
"""


def get_daylight_lamps_state(ip_address):
    """
    The function queries the AtmoWeb API using requests for the stat of the daylight lamps
    0 represents off, 1 represents on
    :param ip_address: Address of the Oven that needs to be connected via ethernet
    :return: state of the daylight lamps: Integer
    """
    url = "http://" + ip_address + "/atmoweb?LightDay="
    r = requests.get(url)

    if r.status_code == 200:
        try:
            text = str(r.text)
            text = text.strip(", ")
            json_text = "{" + text + "}"
            json_data = json.loads(json_text)

            value = json_data["LightDay"]

            if value not in ["N/A"]:
                return_value = int(value)
            else:
                return_value = None

        except json.JSONDecodeError as e:
            logging.error(f"error while decoding JSON-Response: {e}")
            return_value = None
    else:
        logging.error(f"error while querying the REST-API: {r.status_code}")
        return_value = None

    return return_value


def get_uv_light_lamps_state(ip_address):
    """
    The function queries the AtmoWeb API using requests for the stat of the uv light lamps
    0 represents off, 1 represents on
    :param ip_address: Address of the Oven that needs to be connected via ethernet
    :return: state of the uv light lamps: Integer
    """
    url = "http://" + ip_address + "/atmoweb?LightUV="
    r = requests.get(url)

    if r.status_code == 200:
        try:
            text = str(r.text)
            text = text.strip(", ")
            json_text = "{" + text + "}"
            json_data = json.loads(json_text)

            value = json_data["LightUV"]

            if value not in ["N/A"]:
                return_value = int(value)
            else:
                return_value = None

        except json.JSONDecodeError as e:
            logging.error(f"error while decoding JSON-Response: {e}")
            return_value = None
    else:
        logging.error(f"error while querying the REST-API: {r.status_code}")
        return_value = None

    return return_value


def get_dimmer_state(ip_address):
    """
    The function queries the AtmoWeb API using requests for the stat of the dimmer controlling lamps
    0 represents off, stat s transferd in 1% steps to 1 which represents fully on
    :param ip_address: Address of the Oven that needs to be connected via ethernet
    :return: dimmer status: Float
    """
    url = "http://" + ip_address + "/atmoweb?LightLED="
    r = requests.get(url)

    if r.status_code == 200:
        try:
            text = str(r.text)
            text = text.strip(", ")
            json_text = "{" + text + "}"
            json_data = json.loads(json_text)

            value = json_data["LightLED"]

            if value not in ["N/A"]:
                return_value = float(value)
            else:
                return_value = None

        except json.JSONDecodeError as e:
            logging.error(f"error while decoding JSON-Response: {e}")
            return_value = None
    else:
        logging.error(f"error while querying the REST-API: {r.status_code}")
        return_value = None

    return return_value


"""
PROGRAM
"""


def get_program_state(ip_address):
    """
    The function queries the AtmoWeb API using requests for the run or program state of the oven
    this states can be: „Program“, „Idle“, „Timer“, „Manual“
    :param ip_address: Address of the Oven that needs to be connected via ethernet
    :return: program state description: String
    """
    url = "http://" + ip_address + "/atmoweb?CurOp="
    r = requests.get(url)

    if r.status_code == 200:
        try:
            text = str(r.text)
            text = text.strip(", ")
            json_text = "{" + text + "}"
            json_data = json.loads(json_text)

            value = json_data["CurOp"]

            if value not in ["N/A"]:
                return_value = str(value)
            else:
                return_value = None

        except json.JSONDecodeError as e:
            logging.error(f"error while decoding JSON-Response: {e}")
            return_value = None
    else:
        logging.error(f"error while querying the REST-API: {r.status_code}")
        return_value = None

    return return_value


def get_temp_ramp_name(ip_address):
    """
    The function queries the AtmoWeb API using requests for the kind of set temperature ramp
    :param ip_address: Address of the Oven that needs to be connected via ethernet
    :return:  Name of the temperature ramp: String
    """
    url = "http://" + ip_address + "/atmoweb?InfoTemp="
    r = requests.get(url)

    if r.status_code == 200:
        try:
            text = str(r.text)
            text = text.strip(", ")
            json_text = "{" + text + "}"
            json_data = json.loads(json_text)

            value = json_data["InfoTemp"]

            if value not in ["N/A"]:
                return_value = str(value)
            else:
                return_value = None

        except json.JSONDecodeError as e:
            logging.error(f"error while decoding JSON-Response: {e}")
            return_value = None
    else:
        logging.error(f"error while querying the REST-API: {r.status_code}")
        return_value = None

    return return_value


def get_humid_ramp_name(ip_address):
    """
    The function queries the AtmoWeb API using requests for the kind of set humidity ramp
    :param ip_address: Address of the Oven that needs to be connected via ethernet
    :return:  Name of the humidity ramp: String
    """
    url = "http://" + ip_address + "/atmoweb?InfoHum="
    r = requests.get(url)

    if r.status_code == 200:
        try:
            text = str(r.text)
            text = text.strip(", ")
            json_text = "{" + text + "}"
            json_data = json.loads(json_text)

            value = json_data["InfoHum"]

            if value not in ["N/A"]:
                return_value = str(value)
            else:
                return_value = None

        except json.JSONDecodeError as e:
            logging.error(f"error while decoding JSON-Response: {e}")
            return_value = None
    else:
        logging.error(f"error while querying the REST-API: {r.status_code}")
        return_value = None

    return return_value


def get_vacuum_ramp_name(ip_address):
    """
    The function queries the AtmoWeb API using requests for the kind of set vacuum ramp
    :param ip_address: Address of the Oven that needs to be connected via ethernet
    :return:  Name of the vacuum ramp: String
    """
    url = "http://" + ip_address + "/atmoweb?InfoVac="
    r = requests.get(url)

    if r.status_code == 200:
        try:
            text = str(r.text)
            text = text.strip(", ")
            json_text = "{" + text + "}"
            json_data = json.loads(json_text)

            value = json_data["InfoVac"]

            if value not in ["N/A"]:
                return_value = str(value)
            else:
                return_value = None

        except json.JSONDecodeError as e:
            logging.error(f"error while decoding JSON-Response: {e}")
            return_value = None
    else:
        logging.error(f"error while querying the REST-API: {r.status_code}")
        return_value = None

    return return_value


def get_program_message(ip_address):
    """
    The function queries the AtmoWeb API using requests for the programmed message
    :param ip_address: Address of the Oven that needs to be connected via ethernet
    :return: message: String
    """
    url = "http://" + ip_address + "/atmoweb?InfoMsg="
    r = requests.get(url)

    if r.status_code == 200:
        try:
            text = str(r.text)
            text = text.strip(", ")
            json_text = "{" + text + "}"
            json_data = json.loads(json_text)

            value = json_data["InfoMsg"]

            if value not in ["N/A"]:
                return_value = str(value)
            else:
                return_value = None

        except json.JSONDecodeError as e:
            logging.error(f"error while decoding JSON-Response: {e}")
            return_value = None
    else:
        logging.error(f"error while querying the REST-API: {r.status_code}")
        return_value = None

    return return_value


def get_program_name(ip_address):
    """
    The function queries the AtmoWeb API using requests for the current program name
    :param ip_address: Address of the Oven that needs to be connected via ethernet
    :return: current program name: String
    """
    url = "http://" + ip_address + "/atmoweb?Info="
    r = requests.get(url)

    if r.status_code == 200:
        try:
            text = str(r.text)
            text = text.strip(", ")
            json_text = "{" + text + "}"
            json_data = json.loads(json_text)

            value = json_data["Info"]

            if value not in ["N/A"]:
                return_value = str(value)
            else:
                return_value = None

        except json.JSONDecodeError as e:
            logging.error(f"error while decoding JSON-Response: {e}")
            return_value = None
    else:
        logging.error(f"error while querying the REST-API: {r.status_code}")
        return_value = None

    return return_value


def get_current_program(ip_address):
    """
    The function queries the AtmoWeb API using requests for the name of the current running program
    :param ip_address: Address of the Oven that needs to be connected via ethernet
    :return: name of current running program: String
    """
    url = "http://" + ip_address + "/atmoweb?ProgCurrent="
    r = requests.get(url)

    if r.status_code == 200:
        try:
            text = str(r.text)
            text = text.strip(", ")
            json_text = "{" + text + "}"
            json_data = json.loads(json_text)

            value = json_data["ProgCurrent"]

            if value not in ["N/A"]:
                return_value = str(value)
            else:
                return_value = None

        except json.JSONDecodeError as e:
            logging.error(f"error while decoding JSON-Response: {e}")
            return_value = None
    else:
        logging.error(f"error while querying the REST-API: {r.status_code}")
        return_value = None

    return return_value


def get_name_of_program_to_start(ip_address):
    """
    The function queries the AtmoWeb API using requests for the name of the program about to start
    :param ip_address: Address of the Oven that needs to be connected via ethernet
    :return: name of program about to start: String
    """
    url = "http://" + ip_address + "/atmoweb?ProgStart="
    r = requests.get(url)

    if r.status_code == 200:
        try:
            text = str(r.text)
            text = text.strip(", ")
            json_text = "{" + text + "}"
            json_data = json.loads(json_text)

            value = json_data["ProgStart"]

            if value not in ["N/A"]:
                return_value = str(value)
            else:
                return_value = None

        except json.JSONDecodeError as e:
            logging.error(f"error while decoding JSON-Response: {e}")
            return_value = None
    else:
        logging.error(f"error while querying the REST-API: {r.status_code}")
        return_value = None

    return return_value


def get_total_program_duration(ip_address):
    """
    The function queries the AtmoWeb API using requests for the total duration of the current program
    the duration is displayed in the format: [days] [hours]:[min]:[sec]
    if no program is loaded “-00:00:01” is returned.
    :param ip_address: Address of the Oven that needs to be connected via ethernet
    :return: total duration of the current program: String
    """
    url = "http://" + ip_address + "/atmoweb?ProgDuration="
    r = requests.get(url)

    if r.status_code == 200:
        try:
            text = str(r.text)
            text = text.strip(", ")
            json_text = "{" + text + "}"
            json_data = json.loads(json_text)

            value = json_data["ProgDuration"]

            if value not in ["N/A"]:
                return_value = str(value)
            else:
                return_value = None

        except json.JSONDecodeError as e:
            logging.error(f"error while decoding JSON-Response: {e}")
            return_value = None
    else:
        logging.error(f"error while querying the REST-API: {r.status_code}")
        return_value = None

    return return_value


def get_remaining_program_duration(ip_address):
    """
    The function queries the AtmoWeb API using requests for the remaining duration of the current program
    the duration is displayed in the format: [days] [hours]:[min]:[sec]
    if no program is loaded “-00:00:01” is returned.
    :param ip_address: Address of the oven that needs to be connected via ethernet
    :return: remaining duration of the current program: String
    """
    url = "http://" + ip_address + "/atmoweb?ProgRemain="
    r = requests.get(url)

    if r.status_code == 200:
        try:
            text = str(r.text)
            text = text.strip(", ")
            json_text = "{" + text + "}"
            json_data = json.loads(json_text)

            value = json_data["ProgRemain"]

            if value not in ["N/A"]:
                return_value = str(value)
            else:
                return_value = None

        except json.JSONDecodeError as e:
            logging.error(f"error while decoding JSON-Response: {e}")
            return_value = None
    else:
        logging.error(f"error while querying the REST-API: {r.status_code}")
        return_value = None

    return return_value


def get_program_list(ip_address):
    """
    The function queries the AtmoWeb API using requests for a list of all programs on the sd card
    The List format is: “ProgList”: [“Test100”]
    :param ip_address: Address of the Oven that needs to be connected via ethernet
    :return: List of programs on the SD card: String
    """
    url = "http://" + ip_address + "/atmoweb?ProgList="
    r = requests.get(url)

    if r.status_code == 200:
        try:
            text = str(r.text)
            text = text.strip(", ")
            json_text = "{" + text + "}"
            json_data = json.loads(json_text)

            value = json_data["ProgList"]

            if value not in ["N/A"]:
                return_value = str(value)
            else:
                return_value = None

        except json.JSONDecodeError as e:
            logging.error(f"error while decoding JSON-Response: {e}")
            return_value = None
    else:
        logging.error(f"error while querying the REST-API: {r.status_code}")
        return_value = None

    return return_value


"""
MISCELLANEOUS
"""


def get_time(ip_address):
    """
    The function queries the AtmoWeb API using requests for the time what is set on the device
    Timestamp is returned according to ISO 8601
    :param ip_address: Address of the Oven that needs to be connected via ethernet
    :return: current time of device: String
    """
    url = "http://" + ip_address + "/atmoweb?Time="
    r = requests.get(url)

    if r.status_code == 200:
        try:
            text = str(r.text)
            text = text.strip(", ")
            json_text = "{" + text + "}"
            json_data = json.loads(json_text)

            value = json_data["Time"]

            if value not in ["N/A"]:
                return_value = str(value)
            else:
                return_value = None

        except json.JSONDecodeError as e:
            logging.error(f"error while decoding JSON-Response: {e}")
            return_value = None
    else:
        logging.error(f"error while querying the REST-API: {r.status_code}")
        return_value = None

    return return_value


def get_time_zone(ip_address):
    """
    The function queries the AtmoWeb API using requests for the time zone which is set on the device
    :param ip_address: Address of the Oven that needs to be connected via ethernet
    :return: time zone of device: String
    """
    url = "http://" + ip_address + "/atmoweb?TimeZone="
    r = requests.get(url)

    if r.status_code == 200:
        try:
            text = str(r.text)
            text = text.strip(", ")
            json_text = "{" + text + "}"
            json_data = json.loads(json_text)

            value = json_data["TimeZone"]

            if value not in ["N/A"]:
                return_value = str(value)
            else:
                return_value = None

        except json.JSONDecodeError as e:
            logging.error(f"error while decoding JSON-Response: {e}")
            return_value = None
    else:
        logging.error(f"error while querying the REST-API: {r.status_code}")
        return_value = None

    return return_value


def get_daylight_savings_time(ip_address):
    """
    The function queries the AtmoWeb API using requests for the daylight savings time of the device
    :param ip_address: Address of the Oven that needs to be connected via ethernet
    :return: Daylight savings time of device: String
    """
    url = "http://" + ip_address + "/atmoweb?TimeDST="
    r = requests.get(url)

    if r.status_code == 200:
        try:
            text = str(r.text)
            text = text.strip(", ")
            json_text = "{" + text + "}"
            json_data = json.loads(json_text)

            value = json_data["TimeDST"]

            if value not in ["N/A"]:
                return_value = str(value)
            else:
                return_value = None

        except json.JSONDecodeError as e:
            logging.error(f"error while decoding JSON-Response: {e}")
            return_value = None
    else:
        logging.error(f"error while querying the REST-API: {r.status_code}")
        return_value = None

    return return_value


def get_software_version(ip_address):
    """
    The function queries the AtmoWeb API using requests for the software version on the device
    :param ip_address: Address of the Oven that needs to be connected via ethernet
    :return: software version of device: String
    """
    url = "http://" + ip_address + "/atmoweb?SWRev="
    r = requests.get(url)

    if r.status_code == 200:
        try:
            text = str(r.text)
            text = text.strip(", ")
            json_text = "{" + text + "}"
            json_data = json.loads(json_text)

            value = json_data["SWRev"]

            if value not in ["N/A"]:
                return_value = str(value)
            else:
                return_value = None

        except json.JSONDecodeError as e:
            logging.error(f"error while decoding JSON-Response: {e}")
            return_value = None
    else:
        logging.error(f"error while querying the REST-API: {r.status_code}")
        return_value = None

    return return_value


def get_serial_number(ip_address):
    """
    The function queries the AtmoWeb API using requests for the serial number of the device
    :param ip_address: Address of the Oven that needs to be connected via ethernet
    :return: software version of device: String
    """
    url = "http://" + ip_address + "/atmoweb?SN="
    r = requests.get(url)

    if r.status_code == 200:
        try:
            text = str(r.text)
            text = text.strip(", ")
            json_text = "{" + text + "}"
            json_data = json.loads(json_text)

            value = json_data["SN"]

            if value not in ["N/A"]:
                return_value = str(value)
            else:
                return_value = None

        except json.JSONDecodeError as e:
            logging.error(f"error while decoding JSON-Response: {e}")
            return_value = None
    else:
        logging.error(f"error while querying the REST-API: {r.status_code}")
        return_value = None

    return return_value


def get_Device_Type(ip_address):
    """
    The function queries the AtmoWeb API using requests for the device type
    :param ip_address: Address of the Oven that needs to be connected via ethernet
    :return: device type: String
    """
    url = "http://" + ip_address + "/atmoweb?DevType="
    r = requests.get(url)

    if r.status_code == 200:
        try:
            text = str(r.text)
            text = text.strip(", ")
            json_text = "{" + text + "}"
            json_data = json.loads(json_text)

            value = json_data["DevType"]

            if value not in ["N/A"]:
                return_value = str(value)
            else:
                return_value = None

        except json.JSONDecodeError as e:
            logging.error(f"error while decoding JSON-Response: {e}")
            return_value = None
    else:
        logging.error(f"error while querying the REST-API: {r.status_code}")
        return_value = None

    return return_value


def get_remote_control_permissions(ip_address):
    """
    The function queries the AtmoWeb API using requests for remote control permissions
    r=read, w=write, a=alarm
    :param ip_address: Address of the Oven that needs to be connected via ethernet
    :return: permission type: String
    """
    url = "http://" + ip_address + "/atmoweb?RC="
    r = requests.get(url)

    if r.status_code == 200:
        try:
            text = str(r.text)
            text = text.strip(", ")
            json_text = "{" + text + "}"
            json_data = json.loads(json_text)

            value = json_data["RC"]

            if value not in ["N/A"]:
                return_value = str(value)
            else:
                return_value = None

        except json.JSONDecodeError as e:
            logging.error(f"error while decoding JSON-Response: {e}")
            return_value = None
    else:
        logging.error(f"error while querying the REST-API: {r.status_code}")
        return_value = None

    return return_value


def get_gas_type(ip_address):
    """
    The function queries the AtmoWeb API using requests for gas type in the oven
    Possible answers:“InertGas”, “FreshAir”, “N/A”
    :param ip_address: Address of the Oven that needs to be connected via ethernet
    :return: gas type: String
    """
    url = "http://" + ip_address + "/atmoweb?GasType="
    r = requests.get(url)

    if r.status_code == 200:
        try:
            text = str(r.text)
            text = text.strip(", ")
            json_text = "{" + text + "}"
            json_data = json.loads(json_text)

            value = json_data["GasType"]

            if value not in ["N/A"]:
                return_value = str(value)
            else:
                return_value = None

        except json.JSONDecodeError as e:
            logging.error(f"error while decoding JSON-Response: {e}")
            return_value = None
    else:
        logging.error(f"error while querying the REST-API: {r.status_code}")
        return_value = None

    return return_value
