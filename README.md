# Google Drive Manager
Simple Python script for uploading and downloading files and folders from Google Drive using the Drive API v3.  
For more information see:  
https://developers.google.com/drive/api/v3/quickstart/python  
You will also need to "ENABLE THE DRIVE API" and download the credentials.json file from there.  

## Commands:
**Upload** zips the folder/file and adds it to your drive with the name you add.  
**Remove** deletes a file with that name from your drive. (If there are multiple with the same name, it only deletes the first one it finds)  
**Download** downloads and extracts a zip file from your drive to the directory. (Can optionally extract it to a new folder)  
**LocalRemove** deletes a folder/file from your computer.  
**LocalMove** moves a folder/file on your computer to a new directory.  
**LocalAdd** creates a new folder in a directory.  
**Macro** runs commands from a .txt file:  
- By creating a .txt file and putting it in the program's working directory, you can add multiple commands for the program to run in a row. Each line will be interpreted as a command.  
