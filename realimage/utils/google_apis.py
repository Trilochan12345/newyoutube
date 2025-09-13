import os
import pickle
import google_auth_oauthlib.flow
import googleapiclient.discovery
import googleapiclient.errors

def create_service(client_secret_file, api_name, api_version, *scopes):
    print("Creating service...")

    creds = None
    working_dir = os.getcwd()
    token_dir = os.path.join(working_dir, 'tokens')
    if not os.path.exists(token_dir):
        os.mkdir(token_dir)

    token_file = os.path.join(token_dir, f'token_{api_name}_{api_version}.pickle')

    if os.path.exists(token_file):
        with open(token_file, 'rb') as token:
            creds = pickle.load(token)

    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = google_auth_oauthlib.flow.InstalledAppFlow.from_client_secrets_file(
                client_secret_file, scopes)
            creds = flow.run_local_server(port=0)

        with open(token_file, 'wb') as token:
            pickle.dump(creds, token)

    try:
        service = googleapiclient.discovery.build(api_name, api_version, credentials=creds)
        print(f"{api_name} service created successfully")
        return service
    except Exception as e:
        print(f"Error creating service: {e}")
        return None
