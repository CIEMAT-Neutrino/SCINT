# I want to create a function that will allow me to read in a file from my Google Drive and return it as a pandas dataframe.

import os
import pandas as pd

from pydrive.auth import GoogleAuth
from pydrive.drive import GoogleDrive

def read_file_from_drive(file_id, file_name):
    # Authenticate and create the PyDrive client.
    gauth = GoogleAuth()
    gauth.LocalWebserverAuth() # Creates local webserver and auto handles authentication.
    drive = GoogleDrive(gauth)

    # Download the file
    downloaded = drive.CreateFile({'id': file_id})
    downloaded.GetContentFile(file_name)

    # Read the file into a pandas dataframe
    df = pd.read_csv(file_name)

    # Return the dataframe
    return df
