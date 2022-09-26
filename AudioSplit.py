from googleapiclient.discovery import build
import io
from google.oauth2 import service_account
from googleapiclient.http import MediaIoBaseDownload, MediaFileUpload
from pydub import AudioSegment
import datetime
SCOPES = ['https://www.googleapis.com/auth/drive']
#token.json generated from google drive
SERVICE_ACCOUNT_FILE = 'token.json'
credentials=None
credentials = service_account.Credentials.from_service_account_file(
        SERVICE_ACCOUNT_FILE, scopes=SCOPES)
#Google drive file Id's
SAMPLE_SPREADSHEET_ID = '1UoxRl3c8x5zSvv4nTPF5OjKfY2Zmo-gEXqYoKJlYKrE'
SPLITED_AUDIO_FOLDER_ID = '1wNjtUugfIf3vYe7qpG_fUOAz0bcQInCA'
BIG_AUDIO_FILE='15IjK6M5KsAJ0Ibu__q5gFDh8tMLRO7-A'
service = build('sheets', 'v4', credentials=credentials)
# Call the Sheets API
sheet = service.spreadsheets()
result = sheet.values().get(spreadsheetId=SAMPLE_SPREADSHEET_ID,
                            range="Sheet1!A1:B100").execute()
rows = result.get('values', [])
print(result)
aservice = build('drive', "v3", credentials=credentials)
request = aservice.files().get_media(fileId=BIG_AUDIO_FILE)
file = io.BytesIO()
downloader = MediaIoBaseDownload(file, request)
done = False
while done is False:
    status, done = downloader.next_chunk()
    print(F'Download {int(status.progress() * 100)}.')
mp3File=file.getvalue()
t1 = 0
pod_date=datetime.datetime.strptime(rows[1][0], '%b %d, %Y').date()
uploadService = build('drive', "v3", credentials=credentials)
arr = ["Timestamp", "0:00"]
for count,row in enumerate(rows):
    if row[1] not in arr:
        # split time calculation
        timestamp1 = row[1]
        tArray = timestamp1.split(":")
        minutes = int(tArray[0]) * 1000 * 60
        seconds = 0
        if len(tArray) > 1:
            seconds = (int(tArray[1]))* 1000
        t2 = minutes + seconds
        # split big audio file based on timestamp
        song = AudioSegment.from_mp3(io.BytesIO(mp3File))
        Output_MP3 = song[t1:t2]
        if t1==0:
            fileName = str(pod_date)+ "_ITN_Podcast_Intro.mp3"
        else:
            fileName = str(pod_date) + "_ITN_Podcast_Story_"+str(count-2)+ ".mp3"
        Output_MP3.export(fileName, format="mp3")

        # upload file
        file_metadata = {'name': fileName, "parents": [SPLITED_AUDIO_FOLDER_ID]}
        media = MediaFileUpload(fileName)
        file = uploadService.files().create(body=file_metadata, media_body=media,fields='id').execute()
        print(F'File ID: {file.get("id")}')
        t1 = t2
