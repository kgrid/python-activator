import urllib.request
import zipfile


# Step 1: Download the file
url = "https://github.com/kgrid-objects/example-collection/releases/download/4.2.1/python-simple-v1.0.zip"  # Replace with the URL of the file you want to download
filename = "python-simple-v1.0.zip"  # Specify the name you want to give to the downloaded file

urllib.request.urlretrieve(url, "test"+filename)

# Step 2: Unzip the file
with zipfile.ZipFile(filename, "r") as zip_ref:
    zip_ref.extractall("destination_folder")  # Specify the destination folder where you want to extract the files