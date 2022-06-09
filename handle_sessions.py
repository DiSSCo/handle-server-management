import base64
import requests

import key_encryption
import connection_values as cv


def setup_session():
    headers = {
        'Content-Type': 'application/json;charset=UTF-8'
    }
    url = 'https://' + cv.ip + ':' + str(cv.port) + '/api/sessions/'

    r = requests.post(url, verify=False)
    json_response = r.json()

    headers['Authorization'] = create_authorisation_header_from_json(json_response)

    # Send the request again with a valid correctly signed Authorization header
    r2 = requests.put(url + 'this', headers=headers, verify=False)

    json_response2 = r2.json()
    print(json_response2)
    print(r2.status_code, r2.reason)
    if json_response2['authenticated']:
        return json_response2["sessionId"]
    else:
        return ""


def create_authorisation_header_from_json(json_response):
    # Unpick number once (nonce) and session id from server response (this is the challenge)
    server_nonce_bytes = base64.b64decode(json_response['nonce'])
    session_id = json_response['sessionId']

    # Generate a client number once (cnonce)
    client_nonce_bytes = key_encryption.generate_client_nonce_bytes()
    client_nonce_string = base64.b64encode(client_nonce_bytes).decode('UTF-8')

    # Our response has to be the signature of server nonce + client nonce
    combined_nonce_bytes = server_nonce_bytes + client_nonce_bytes
    signature_bytes = key_encryption.sign_bytes_SHA256(combined_nonce_bytes)
    signature_string = base64.b64encode(signature_bytes).decode('UTF-8')

    # Build the authorisation header to send with the request
    authorization_header_string = build_complex_auth_str_session(signature_string, session_id,
                                                                        client_nonce_string)


    return authorization_header_string


def build_complex_auth_str_session(signature_string, session_id, client_nonce_string):
    result = ('Handle ' +
              'version="0", ' +
              'sessionId="' + session_id + '", '
              'cnonce="' + client_nonce_string + '", '
              'id="' + cv.admin_id + '", '
              "type=\"HS_PUBKEY\"," +
              "alg=\"SHA256\"," +
              'signature="' + signature_string + '"')

    return result



