import keyring as k

terna_client = k.get_password("terna_client", username = None)
terna_secret = k.get_password("terna_secret", username = None)
entsoe       = k.get_password("entsoe", username = None)
