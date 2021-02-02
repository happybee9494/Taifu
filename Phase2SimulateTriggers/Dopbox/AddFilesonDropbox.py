import dropbox
import os

#TRIGGERS =>
#New file in your folder
#New text file in your folder
#New photo in your folder

#https://www.dropbox.com/developers/documentation/python#tutorial
mytoken = 'tIrGv6ETBFAAAAAAAAAAy9_8jPVBpPXEltu1b2I3JGkwhl6SgCljkBStRWfvokbX'

dbx = dropbox.Dropbox(mytoken)

dbx.users_get_current_account()

# for entry in dbx.files_list_folder('').entries:
#     print(entry.name)
# OUTPUT:
# Cavs vs Warriors

file_path_photo = '/home/TATester/ImpTATester/Taifu/Phase2SimulateTriggers/media/IFTTTestPhoto.gif'
file_path_video = '/home/TATester/ImpTATester/Taifu/Phase2SimulateTriggers/media/IFTTTestVideo.mp4'
file_path_text = '/home/TATester/ImpTATester/Taifu/Phase2SimulateTriggers/media/IFTTTestText.txt'


with open(file_path_photo, "rb") as f:
    dbx.files_upload(f.read(), '/myfolder/IFTTTestPhoto.gif', mute=True)


with open(file_path_video, "rb") as f:
    dbx.files_upload(f.read(), '/myfolder/IFTTTestVideo.mp4', mute=True)

with open(file_path_text, "rb") as f:
    dbx.files_upload(f.read(), '/myfolder/IFTTTestText.txt', mute=True)
