from payload_structure.credentials_manager import CredentialsManager
from controllers.RESTController import APIController

credentialManagetr = CredentialsManager(APIController())



credenciales = credentialManagetr.get_credentials_by_user('MTK861014317')
print(credenciales)