# Copyright 2018 Google LLC
#
# Licensed under the Apache License, Version 2.0 (the "License");
# you may not use this file except in compliance with the License.
# You may obtain a copy of the License at
#
#     http://www.apache.org/licenses/LICENSE-2.0
#
# Unless required by applicable law or agreed to in writing, software
# distributed under the License is distributed on an "AS IS" BASIS,
# WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
# See the License for the specific language governing permissions and
# limitations under the License.

# [START sheets_quickstart]
from __future__ import print_function
import pickle
import os.path
from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

#TRIGGERS =>
#New spreadsheet added to folder
#New worksheet in spreadsheet
#New row added to spreadsheet
#Cell updated in spreadsheet



# If modifying these scopes, delete the file token.pickle.
SCOPES = ['https://www.googleapis.com/auth/drive']#spreadsheets.readonly']

# The ID and range of a sample spreadsheet.

def auth():
    #Authorize to create and edit all files in Google Drive
    creds = None
    # The file token.pickle stores the user's access and refresh tokens, and is
    # created automatically when the authorization flow completes for the first
    # time.
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    # If there are no (valid) credentials available, let the user log in.
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        # Save the credentials for the next run
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)

    service = build('sheets', 'v4', credentials=creds)
    drive = build('drive', 'v3', credentials=creds)
    return service,drive


def main():
    # Authentication and Authorization
    #################################################################
    service,drive = auth()
    # Call the Sheets API
    sheet = service.spreadsheets()

    # Create a new Google Sheet (Method 1) using Google Drive API, inside an existing folder
    ##################################################################
    file_metadata = {
        'name': 'IFTTTsheet',
        'parents': ['1U0KcbcQWcmbaHkmI81YlvlivxU52-U1H'], # - id of folder 'IFTTT'
        'mimeType': 'application/vnd.google-apps.spreadsheet',
    }
    res = drive.files().create(body=file_metadata).execute()
    print(res)

    spreadsheet_id = res['id']

    # Create a new Google Sheet (Method 2) using Google Sheets API
    ##################################################################
    # spreadsheet = {
    #     'properties': {
    #         'title': "IFTTTsheet"
    #     }
    # }
    # spreadsheet = service.spreadsheets().create(body=spreadsheet,
    #                                             fields='spreadsheetId').execute()
    # print('Spreadsheet ID: {0}'.format(spreadsheet.get('spreadsheetId')))
    # spreadsheet_id = spreadsheet.get('spreadsheetId')


    # Append ROWS of the created Google Sheet
    ###################################################################
    values = [
    # Cell values ...
    ["IFTTTItem", "IFTTTCost", "IFTTTStocked", "IFTTTDate"],
    ["IFTTTWheel", "$20.50", "4", "3/1/2016"],
    ["IFTTTDoor", "$15", "2", "3/15/2016"],
    ["IFTTTEngine", "$100", "1", "3/20/2016"],
    ]
    body = {
        'values': values
    }
    result = service.spreadsheets().values().append(
        spreadsheetId=spreadsheet_id, range="Sheet1!A1:D5",
        valueInputOption='USER_ENTERED', body=body).execute()
    print('{0} cells appended.'.format(result \
                                       .get('updates') \
                                       .get('updatedCells')))

    # Read an existing Google Sheet
    #################################################################
    result = sheet.values().get(spreadsheetId=spreadsheet_id,
                                range="Sheet1!A1:D5").execute()
    values = result.get('values', [])

    if not values:
        print('No data found.')
    else:
        print('Name, Major:')
        for row in values:
            # Print columns A and D, which correspond to indices 0 and 4.
            print('%s, %s' % (row[0], row[3]))

    # Update the created Google Sheet
    ###################################################################
    # Find and replace text
    requests = []
    requests.append({
        'findReplace': {
            'find': 'IFTTTItem',
            'replacement': 'IFTTTItemEditedCell',
            'allSheets': True
        }
    })
    # Add additional requests (operations) ...

    body = {
        'requests': requests
    }
    response = service.spreadsheets().batchUpdate(
        spreadsheetId=spreadsheet_id,
        body=body).execute()
    find_replace_response = response.get('replies')[0].get('findReplace')
    print('{0} replacements made.'.format(
        find_replace_response.get('occurrencesChanged')))

#######################################################################
#
# Begin Main
#
#######################################################################

if __name__ == '__main__':
    main()
# [END sheets_quickstart]