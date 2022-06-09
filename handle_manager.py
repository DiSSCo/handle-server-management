import json
import requests
from datetime import datetime
import base32_lib as b32
from pprint import pprint

import handle_sessions
import key_encryption
import connection_values as cv

sessions_mode = True  # True to authenticate via sessions, false to authenticate using key pairs

# In this program, "handle" refers only to the suffix. The prefix (20.5000.1025/) is appended automatically

# This file contains functions for:
    # Minting new handle ids
    # Creating (publishing) handle records
    # Retrieving handle records
    # Deleting handle records
    # Updating handle records

# Operations can either be authenticated using keys for each operation (sessions_mode = False)
# or by establishing a session for the program (sessions_mode = True)


def gen_basic_record(handle=""):
    # Returns sample handle body as a dictionary
    current_date = datetime.now()
    current_date_format = current_date.strftime('%Y-%m-%dT%H:%M:%SZ')
    handle_record = {u'values': [
        {u'index': 1, u'ttl': 86400, u'type': u'URL', u'timestamp': current_date_format,
         u'data': {u'value': u'https://sandbox.dissco.tech/', u'format': u'string'}},
        {u'index': 2, u'ttl': 86400, u'type': u'EMAIL', u'timestamp': current_date_format,
         u'data': {u'value': u'info@naturalis.nl', u'format': u'string'}},
        {u'index': 3, u'ttl': 86400, u'type': u'ROR', u'timestamp': current_date_format,
         u'data': {u'value': u'https://ror.org/019wvm592', u'format': u'string'}},
        {u'index': 100, u'ttl': 86400, u'type': u'HS_ADMIN', u'timestamp': current_date_format,
         u'data': {u'value': {u'index': 200, u'handle': cv.admin_id, u'permissions': u'011111110011'},
                   u'format': u'admin'}}
    ], u'handle': cv.prefix + handle, u'responseCode': 1}

    return handle_record


def new_handle_id():
    # Mints a new handleID, checks if it is available.

    hid = str(b32.generate(8, 4, False))  # generates an 8-character long 32-bit encoded string, no checksum
    while handle_exists(hid):  # checks if handle is taken
        hid = str(b32.generate(8, 4, False))

    return hid


def handle_exists(hid):
    # Attempts to retrieve handle record based on HID. If no record exists, returns false

    url = cv.base_url + hid
    r = requests.get(url, verify=False)
    if r.status_code == 404:  # if this HID is not found, handle id is not taken
        return False
    return True

    # If true: this handle query returned a record; the handle is taken
    # If false: this handle did not return a record; the handle id is available


def get_auth_type_headers(session_id="", url="", body="", d=False):
    # Returns headers appropriate for authentication type (either sessions or key pairs
    # If it's key-pairs, we need to check if it's a delete operation to formulate the first request

    if sessions_mode:  # If we're authenticating by sessions
        headers = {
            'Content-Type': 'application/json;charset=UTF-8',
            'Authorization': 'Handle version="0", sessionId="' + str(session_id) + '"'
        }
    else:
        headers = {
            'Content-Type': 'application/json;charset=UTF-8'
        }
        # Send the request expecting a response with a WWW-Authenticate header
        # The server will give us a 401 error and challenge us

        if d:  # If we're deleting, the request should be a delete operation, otherwise it's a put request
            r_key = requests.delete(url, headers=headers, verify=False)
        else:
            r_key = requests.put(url, headers=headers, verify=False, data=body)

        # Build the authorisation header that will respond to the server challenge
        headers['Authorization'] = key_encryption.create_authorisation_header(r_key)
    return headers


def create_handle_record(record_str, handle="", session_id=""):
    # Takes a handle record string, creates a handle record, and pushes it to the server
    # If handle is not provided, mint a new one. If handle is provided, assume body is up to-date

    # todo: this should push jobs to a queue, processing service to execute
    if not handle:  # if no HID is provided, mint a new one
        handle = new_handle_id()
        record_str["handle"] = cv.prefix + handle  # assigns HID here, right before posting it to server

    # Setup values to post to handle server
    url = cv.base_url + handle
    body = json.dumps(record_str)

    headers = get_auth_type_headers(session_id=session_id, url=url, body=body)

    r = requests.put(url, headers=headers, verify=False, data=body)
    print("Operation: Create, Handle: ", cv.prefix+handle, ", Status: ", r.status_code, r.reason)
    return r, handle


def delete_handle_record(handle, session_id=""):
    url = cv.base_url + handle
    headers = get_auth_type_headers(session_id=session_id, url=url, d=True)  # Get headers for a delete request

    # Send the request with a valid correctly signed Authorization header
    r = requests.delete(url, headers=headers, verify=False)
    print("Operation: Delete\t Handle: ", cv.prefix + handle, "\tStatus: ", r.status_code, r.reason)
    return r


def get_handle_record(handle):
    url = cv.base_url + handle
    # Turn off certificate verification as most handle servers have self-signed certificates
    r = requests.get(url, verify=False)
    handle_record = r.json()
    print("Operation: Retrieve\t Handle: ", cv.prefix + handle, "\tStatus: ", r.status_code, r.reason)
    return handle_record


def update_handle_record(handle, idx, new_val, session_id=""):
    # Note: handle record indices start at 1; python arrays start at 0. We are using py indices, not handle records here
    # Note: "handle" here just refers to the suffix (i.e. ../123-456). Prefix is appended by other functions

    # Get the handle record
    handle_record = get_handle_record(handle)

    # Update record body with new_val
    handle_record["values"][idx]["data"]["value"] = new_val
    body = json.dumps(handle_record)

    # Update the handle server
    url = cv.base_url + handle  # generate url to POST to
    if sessions_mode:
        headers = get_auth_type_headers(session_id=session_id)
    else:
        headers = get_auth_type_headers(url=url, body=body)

    r = requests.put(url, headers=headers, verify=False, data=body)

    print("Operation: Update\t Handle: ", cv.prefix+handle, "\tStatus: ", r.status_code, r.reason)
    return r


def demo():
    if sessions_mode:
        session_id = handle_sessions.setup_session()
    else:
        session_id = ""

    # Publish a record using a pre-determined HID
    hid = "abc-123"
    record_test = gen_basic_record(hid)
    create_handle_record(record_test, hid, session_id)
    #pprint(get_handle_record(hid))
    update_handle_record(hid, 1, "stheo@naturalis.nl",session_id=session_id)
    #pprint(get_handle_record(hid))
    delete_handle_record(hid, session_id)

    # Publish a record using an HID minted on-the-fly (at posting time)
    record_test = gen_basic_record()
    r, hid = create_handle_record(record_test, session_id=session_id)
    #pprint(get_handle_record(hid))
    update_handle_record(hid, 1, "stheo@naturalis.nl", session_id=session_id)
    #pprint(get_handle_record(hid))
    delete_handle_record(hid, session_id)


demo()

