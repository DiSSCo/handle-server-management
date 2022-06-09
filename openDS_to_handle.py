# This file queries the DiSSCo API and publishes handle records for each digital specimen

import requests
from datetime import datetime
import connection_values as cv

import handle_manager

# Records to be created
pageSize = '100'
pageCount = 15
pageStart = 16  # June 9, 2022: We've done the first 15 pages (first 1500 specimens)


def retrieve_json_data():
    # Pulls JSON data from sandbox
    url_base = "https://sandbox.dissco.tech/api/v1/specimen/?pageSize=" + pageSize
    records = []
    for i in range(pageStart, pageCount):
        url = url_base + "&pageNumber=" + str(i)
        records = requests.get(url).json() + records
    return records


def make_handle_record_string(record_list):
    # This function takes the data retrieved from the API, extracts data needed for the Minimum PID Record, and formats
    # the data into the handle record format. The HID is not minted in this step; that will be done right before the
    # record is pushed to the server.

    # Minimum PID Record Metadata:
    #   1. URL
    #   2. OBJECT_TYPE - @type. Each FDO should have a type
    #   3. CURATED_OBJECT_ID - ods:physicalSpecimenId. Could be media without physical specimen.
    #   4. CURATED_OBJECT_ID_TYPE - "Physical Specimen" for all entries now (defines above's Type)
    #   5. SPECIMEN_NAME - ods:name
    #   6. INSTITUTION_NAME - ods:institutionCode
    #   7. INSTITUTION_ID - ods:institution
    #   8. RECORD_ID - @id #possibly temporary whomst knows
    #   100. HS_ADMIN

    # The returned value is a tricky data structure.
    # It is a list of dictionaries; each dictionary is a handle record to be created.
    # Each dictionary has its metadata entries under one key: "values"
    # Inside "values" is another list of dictionaries, which makes up the minimum handle record
    # Also inside the handle record dictionary is its handle (suffix to be minted at time of posting) and authorization

    handle_record_list = []  # list of all records to be added
    timestamp = datetime.today().strftime('%Y-%m-%dT%H:%M:%SZ')

    for elem in record_list:
        do_url = cv.digital_object_url + elem["@id"]

        handle_record = {u'values': [
            {u'index': 1, u'ttl': 86400, u'type': u'URL', u'timestamp': timestamp,
             u'data': {u'value': do_url, u'format': u'string'}},

            {u'index': 2, u'ttl': 86400, u'type': u'OBJECT_TYPE', u'timestamp': timestamp,
             u'data': {u'value': elem["@type"], u'format': u'string'}},

            {u'index': 3, u'ttl': 86400, u'type': u'CURATED_OBJECT_ID', u'timestamp': timestamp,
             u'data': {u'value': elem["ods:authoritative"]["ods:physicalSpecimenId"], u'format': u'string'}},

            {u'index': 4, u'ttl': 86400, u'type': u'CURATED_OBJECT_ID_TYPE', u'timestamp': timestamp,
             u'data': {u'value': "Physical Specimen ID", u'format': u'string'}},

            {u'index': 5, u'ttl': 86400, u'type': u'SPECIMEN_NAME', u'timestamp': timestamp,
             u'data': {u'value': elem["ods:authoritative"]["ods:name"], u'format': u'string'}},

            {u'index': 6, u'ttl': 86400, u'type': u'ORGANIZATION_CODE', u'timestamp': timestamp,  # Human-readable
             u'data': {u'value': elem["ods:authoritative"]["ods:institution"], u'format': u'string'}},

            {u'index': 7, u'ttl': 86400, u'type': u'ORGANIZATION_ID', u'timestamp': timestamp,
             u'data': {u'value': elem["ods:authoritative"]["ods:institutionCode"], u'format': u'string'}},  # ROR

            {u'index': 8, u'ttl': 86400, u'type': u'RECORD_ID', u'timestamp': timestamp,
             u'data': {u'value': elem["@id"], u'format': u'string'}},

            {u'index': 100, u'ttl': 86400, u'type': u'HS_ADMIN', u'timestamp': timestamp,
             u'data': {u'value': {u'index': 200, u'handle': cv.admin_id, u'permissions': u'011111110011'},
                       u'format': u'admin'}}
        ], u'handle': 'HANDLE', u'responseCode': 1}  # "HANDLE" Here will be updated upon posting to handle server

        handle_record_list.append(handle_record)

    return handle_record_list


def batch_handle_records(handle_record_list):
    # Takes list of handle record strings and makes a separate handle for each of them

    for record_str in handle_record_list:
        response, hid = handle_manager.create_handle_record(record_str)
        print(response.status_code, response.reason)
        # todo: should do some error catching here


def search_json(test_id, query_field):
    # Query field should be exactly what we're looking for
    # This isn't a very generic function; will only search under "ods:authoritative" for now
    # Hopefully we don't need to use it

    query_url = "https://sandbox.dissco.tech/search?query=" + test_id
    print(query_url)
    record = requests.get(query_url).json()
    result = record["results"][0]["content"]["ods:authoritative"][query_field]
    return result


def publish_records():
    # Retrieve digital specimens, store in list of dicts
    records = retrieve_json_data()
    # Extract kernel information metadata profile from each entry and store it in a handle-ingestible format
    handle_ready_strings = make_handle_record_string(records)
    # Publish list of records
    batch_handle_records(handle_ready_strings)
