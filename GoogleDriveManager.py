from __future__ import print_function
import pickle
import os.path
import io

import shutil
import zipfile
from os.path import basename

import httplib2
import googleapiclient.http

from googleapiclient.discovery import build
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request

SCOPES = ['https://www.googleapis.com/auth/drive']
dir_name = "null"

def input_management(inputArray, drive_service):
    if (len(inputArray) < 2):
        print("Deleting all zips...")
        oldFiles = os.listdir(dir_name)
        for item in oldFiles:
            if (item.endswith(".zip")):
                os.remove(os.path.join(dir_name, item))
        print("Exiting...")
        return False
        
    newFolder = "null"
    if (len(inputArray) > 3):
        newFolder = inputArray[3]

    try:
        if (inputArray[0].lower() == "upload"):
            upload_file(drive_service, inputArray[1], inputArray[2])
            print("\nReady for the next command.")
        elif (inputArray[0].lower() == "remove"):
            remove_file(drive_service, inputArray[1])
            print("\nReady for the next command.")
        elif (inputArray[0].lower() == "download"):
            download_file(drive_service, inputArray[1], inputArray[2], newFolder)
            print("\nReady for the next command.")
        elif (inputArray[0].lower() == "localremove"):
            local_remove(inputArray[1])
            print("\nReady for the next command.")
        elif (inputArray[0].lower() == "localmove"):
            local_move(inputArray[1], inputArray[2])
            print("\nReady for the next command.")
        elif (inputArray[0].lower() == "localadd"):
            local_add(inputArray[1], inputArray[2])
            print("\nReady for the next command.")
        elif (inputArray[0].lower() == "macro"):
            if (macro(drive_service, inputArray[1]) == False):
                print("Unrecognizable commands in the macro file")
                return False
            print("\nReady for the next command.")
        else:
            print("The command \"" + inputArray[0] + "\" is not recognized. Press enter to exit, or try again with one of these formats.\n")
    except IndexError:
        print(inputArray[0] + " needs more than " + str(len(inputArray) - 1) + " commands after it.")

    return True

def main():
    global dir_name
    dir_name = os.getcwd()
    if (os.path.exists(os.path.join(dir_name, "credentials.json")) == False):
        print("There is no \"credentials.json file in \"" + dir_name + ".\nPlease download one from: https://developers.google.com/drive/api/v3/quickstart/python")
        input()
        return

    print("Deleting all zips...")
    oldFiles = os.listdir(dir_name)
    for item in oldFiles:
        if (item.endswith(".zip")):
            os.remove(os.path.join(dir_name, item))

    

    creds = None
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    if not creds or not creds.valid:
        print()
        if creds and creds.expired and creds.refresh_token:
            creds.refresh(Request())
        else:
            flow = InstalledAppFlow.from_client_secrets_file(
                'credentials.json', SCOPES)
            creds = flow.run_local_server(port=0)
        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
        print()

    drive_service = build('drive', 'v3', credentials=creds)

    

    goOn = True
    while goOn:
        print("\"upload *FileName* *FilePath*\"")
        print("\"remove *FileName*\"")
        print("\"download *FileName* *FilePath* (optional: *NewFolderToExtractTo*)\"")
        print("\"localRemove *FilePath*\"")
        print("\"localMove *FilePath* *DestinationPath*\"")
        print("\"localAdd *FolderName* *DestinationPath*\"")
        print("\"macro *TextFileName*\"\n")
        inputArray = str(input()).split()
        print("")

        goOn = input_management(inputArray, drive_service)

    
def get_fileID(drive_service, fileName):
    page_token = None
    
    while True:
        files = drive_service.files().list(q = "name='" + fileName + "'", 
        spaces = "drive",
        fields='nextPageToken, files(id, name)',
        pageToken = page_token).execute()
        
        for file in files.get("files", []):
            return file.get("id")

        page_token = files.get('nextPageToken', None)
        if page_token is None:
            break

    return "null"

def upload_file(drive_service, fileName, filePath):
    if (os.path.exists(filePath) == False):
        print(filePath + " doesn't exist")
        return

    newPath = os.path.join(os.getcwd(), fileName) + ".zip"
    if (os.path.exists(newPath)):
        print(newPath + " already exists")
        return

    try:
        shutil.make_archive(fileName, 'zip', filePath)
    except NotADirectoryError:
        zipfile.ZipFile(fileName + ".zip", mode='w').write(filePath, arcname = basename(filePath), compress_type = zipfile.ZIP_DEFLATED)

    body = {'name': fileName}
    media_body = googleapiclient.http.MediaFileUpload(newPath, resumable = True)
    drive_service.files().create(body = body, media_body = media_body).execute()


def remove_file(drive_service, fileName):
    fileID = get_fileID(drive_service, fileName)
    if (fileID == "null"):
        print("The file/folder " + fileName + " does not exist on your drive.")
        return
    
    drive_service.files().delete(fileId = fileID).execute()

def download_file(drive_service, fileName, filePath, newFolder):
    if (os.path.exists(filePath) == False):
        print(filePath + " doesn't exist")
        return

    newPath = filePath
    if (newFolder != "null"):
        newPath = os.path.join(filePath, newFolder)
        if (os.path.exists(newPath)):
            print(newPath + " already exists")
            return
        os.mkdir(newPath)

    fileID = get_fileID(drive_service, fileName)
    if (fileID == "null"):
        print("The file/folder " + fileName + " does not exist on your drive.")
        return

    try:
        request = drive_service.files().get_media(fileId=fileID)
        fh = io.BytesIO()
        downloader = googleapiclient.http.MediaIoBaseDownload(fh, request)
        done = False
        while done is False:
            status, done = downloader.next_chunk()
            print("Download %d%%." % int(status.progress() * 100))

        downloadedFile = zipfile.ZipFile(fh)
        downloadedFile.extractall(newPath)
    except:
        print("Make sure that the file you are trying to download is a .zip file.")
        return

    
def local_remove(filePath):
    if (os.path.exists(filePath) == False):
        print(filePath + " doesn't exist")
    else:
        try:
            shutil.rmtree(filePath)
        except NotADirectoryError:
            os.remove(filePath)
        

def local_move(filePath, destinationPath):
    if (os.path.exists(filePath) == False):
        print(filePath + " doesn't exist")
    elif (os.path.exists(destinationPath) == False):
        print(destinationPath + " doesn't exist")
    else:
        shutil.move(filePath, destinationPath)

def local_add(folderName, destinationPath):
    if (os.path.exists(destinationPath) == False):
        print(destinationPath + " doesn't exist")
        return
    
    newPath = os.path.join(destinationPath, folderName)
    if (os.path.exists(newPath)):
        print(newPath + " already exists")
    else:
        os.mkdir(newPath)

def macro(drive_service, textPath):
    if (textPath.endswith(".txt") == False):
        textPath += ".txt"
    
    if (os.path.exists(textPath) == False):
        print(textPath + " doesn't exist")
        return

    lines = [line.rstrip('\n') for line in open(textPath)]
    
    for line in lines:
        print("Next macro command: " + line)
        if (input_management(line.split(), drive_service) == False):
            return False

    return True


if __name__ == '__main__':
    main()