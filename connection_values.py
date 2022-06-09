# Global variables
key_file = '/home/ubuntu/hs/handle_svr/admpriv.pem'
admin_id = '300:0.NA/20.5000.1025'
prefix = '20.5000.1025/'
ip = '35.178.174.137'
port = 8000
base_url = "https://" + ip + ":" + str(port) + "/api/handles/" + prefix  # URL to POST handle records to
digital_object_url = "https://sandbox.dissco.tech/#objects/"  # where the digital specimen is stored on cordra atm