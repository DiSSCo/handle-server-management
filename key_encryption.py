import base64
import os
import connection_values as cv

# RSA
from Crypto.PublicKey import RSA
from Crypto.Signature import PKCS1_v1_5
from Crypto.Hash import SHA256
import Crypto.Signature


# RNG
from _cffi_backend import buffer


def create_authorisation_header(response):
    key_file = cv.key_file
    auth_id = cv.admin_id

    authenticate_header = response.headers['www-authenticate']
    authenticate_header_dict = parse_authenticate_header(authenticate_header)
    server_nonce_bytes = base64.b64decode(authenticate_header_dict['nonce'])
    session_id = authenticate_header_dict['sessionId']

    # Generate a client number once (cnonce)
    client_nonce_bytes = generate_client_nonce_bytes()
    client_nonce_string = base64.b64encode(client_nonce_bytes).decode('UTF-8')

    # Our response has to be the signature of server nonce + client nonce
    combined_nonce_bytes = server_nonce_bytes + client_nonce_bytes
    signature_bytes = sign_bytes_SHA256(combined_nonce_bytes)

    signature_string = base64.b64encode(signature_bytes).decode('UTF-8')

    # Build the authorisation header to send with the request
    authorization_header_string = build_complex_auth_str(signature_string, session_id, client_nonce_string)

    return authorization_header_string


def generate_client_nonce_bytes():
    return bytearray(os.urandom(16))


def sign_bytes_SHA256(byte_array):
    key = open(cv.key_file, "r").read()
    rsa_key = RSA.importKey(key)
    signer = PKCS1_v1_5.new(rsa_key)

    digest = SHA256.new()
    digest.update(byte_array)
    sign = signer.sign(digest)
    return sign


def sign_bytes_rsa(byte_array):
    # Use this method for RSA keys
    key = open(cv.key_file, 'r').read()
    rsa_key = RSA.importKey(key)

    signer = PKCS1_v1_5.new(rsa_key)
    buf = buffer(byte_array)

    digest = SHA256.new(buf)
    digest.update(buffer(byte_array))

    sign = signer.sign(digest)

    return sign


def build_complex_auth_str(signature_string, session_id, client_nonce_string):
    auth_id = cv.admin_id
    result = ('handle sessionID=\"' + session_id + "\"," +
              "id=\"" + auth_id + "\"," +
              "type=\"HS_PUBKEY\"," +
              "cnonce=\"" + client_nonce_string + "\"," +
              "alg=\"SHA256\"," +
              "signature=\""+signature_string+"\""
              )
    return result

create_authorisation_header
def parse_authenticate_header(authenticate_header):
    result = {}
    tokens = authenticate_header.split(', ')

    for token in tokens:
        first_equals = token.find('=')
        key = token[0:first_equals]
        # quick and dirty parsing of the expected WWW-Authenticate headers
        if key == 'Basic realm':
            continue

        if key == 'Handle sessionId':
            key = 'sessionId'

        value = token[first_equals + 2: len(token) - 1]
        result[key] = value

    return result
