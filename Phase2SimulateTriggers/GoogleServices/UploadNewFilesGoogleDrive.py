from builtins import print

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

gauth = GoogleAuth()
#gauth.LocalWebserverAuth() # client_secrets.json need to be in the same directory as the script

# Try to load saved client credentials
gauth.LoadCredentialsFile("mycreds.txt")
if gauth.credentials is None:
    # Authenticate if they're not there
    gauth.LocalWebserverAuth()
elif gauth.access_token_expired:
    # Refresh them if expired
    gauth.Refresh()
else:
    # Initialize the saved creds
    gauth.Authorize()
# Save the current credentials to a file
gauth.SaveCredentialsFile("mycreds.txt")


drive = GoogleDrive(gauth)
fileList = drive.ListFile({'q': "'root' in parents and trashed=false"}).GetList()
for file in fileList:
  #print('Title: %s, ID: %s' % (file['title'], file['id']))
  # Get the folder ID that you want
  if(file['title'] == "IFTTT"):
      fileID = file['id']
      file1 = drive.CreateFile({"mimeType": "image/gif", "parents": [{"kind": "drive#fileLink", "id": fileID}]})
      file1.SetContentFile("/home/TATester/ImpTATester/Taifu/Phase2SimulateTriggers/media/IFTTTestPhoto.gif")
      #file1.Upload()  # Upload the Photo.
      print('Created photo file %s with mimeType %s' % (file1['title'], file1['mimeType']))

      file2 = drive.CreateFile({"mimeType": "video/mp4", "parents": [{"kind": "drive#fileLink", "id": fileID}]})
      file2.SetContentFile("/home/TATester/ImpTATester/Taifu/Phase2SimulateTriggers/media/IFTTTestVideo.mp4")
      #file2.Upload()  # Upload the Video.
      print('Created video file %s with mimeType %s' % (file2['title'], file2['mimeType']))

      file3 = drive.CreateFile({"mimeType": "application/vnd.ms-excel",  "convert": True ,"parents": [{"kind": "drive#fileLink", "id": fileID}]})
      file3.SetContentFile("/home/TATester/ImpTATester/Taifu/Phase2SimulateTriggers/media/IFTTTestSheet.xlsx")
      #file3.Upload()  # Upload the Google Sheet.
      print('Created Google Sheet file %s with mimeType %s' % (file3['title'], file3['mimeType']))

      file4 = drive.CreateFile({"mimeType": "application/vnd.openxmlformats-officedocument.wordprocessingml.document",  "starred": "true" ,"parents": [{"kind": "drive#file", "id": fileID}]})
      file4.SetContentFile("/home/TATester/ImpTATester/Taifu/Phase2SimulateTriggers/media/IFTTTestDoc.docx")
      file4['title'] = 'IFTTTestDoc.docx'
      # file4['starred'] = 'true'# ')#"labels.starred":"true"
      # file4['starred'] = 'True'
      file4.Upload()  # Upload the Google Doc.
      print('Created Google Doc file %s with mimeType %s' % (file4['title'], file4['mimeType']))


