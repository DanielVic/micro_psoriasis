import sys
import json
from .JWT import jwt_validator
import os

def auth_jwt(authHeader):
    with open('auth/security.conf') as config_file:
        config = json.loads(config_file.read())
        validator = jwt_validator(config['jwt_validator'])
        #authHeader = sys.argv[1]
        result = "False"
        aux = authHeader.split(' ')
        if aux[0] == 'Bearer':
            token = aux[1]
            decoded_token = validator.decode_token(token)
            if decoded_token is not None:
                print(decoded_token['sub'])
    return(decoded_token)


#if __name__ == "__main__":
#    from objects import tokens
#    tokens.server_token().get_token()
#    # Disposición de Headers
#    token = tokens.server_token().get_tokenDB()
#    #print(token['Data']['id_token'])
#    token = 'eyJhbGciOiJSUzI1NiIsInR5cCI6IkpXVCJ9.eyJpc3MiOiJNeU9wZW5JRCIsImlhdCI6MTUyMTEwMzY1Nywic3ViIjoiUHJvY2VzYWRvX2ltYWdlbiIsImV4cCI6MTUyMTEwNzI1Nywic2NvcGUiOiJvcGVuaWQifQ.VCA383Rkp_bJtGUG4bsNCZhJJoqfu4GDcY7Mg5Y3dQKvLqeMKBhGAeG5GnA4ojW19-BtZPVzFa7haeSLO1Yky9uZ7ynvPoBvUDng_8qtf8FqSGw8WdZourJBeKnpHK8nVokAqgiwX9wRoKjhj1lXTQXpCp-vRr8kInJmtpWfIIH0rsZaJOKxkoMQPoQBBxc3I5pcWIacbGrFOz6C8Q9U0ilp8Hc3IgsMnsZlgPUxZxUTIEPpaLO7sOYvgAefGvbAd5wTWXbeslaBWnGpqjt3zoZ-T94WKft8PWLkr4QHKQANMEn6gfCh3yfPnHJoi92gQQR4W_TWWUCNr_153ySgfg'
#
#    headers = {'Content-Type': 'application/json',
#               #'Authorization': 'Bearer ' + token['Data']['id_token']}
#               'Authorization': 'Bearer ' + token}
#
#    decodedtoken = auth_jwt(headers['Authorization'])
#    print(decodedtoken)
