import zipfile
import os

def unzip_file(zip_filepath, dest_dir):
    """
    Unzips a zip file to a destination directory.
    """
    if not os.path.exists(zip_filepath):
        print(f"Error: Zip file not found at {zip_filepath}")
        return

    if not os.path.exists(dest_dir):
        os.makedirs(dest_dir)

    with zipfile.ZipFile(zip_filepath, 'r') as zip_ref:
        zip_ref.extractall(dest_dir)
        print(f"Successfully extracted {zip_filepath} to {dest_dir}")

if __name__ == '__main__':
    zip_file = 'simplemaps_uscities_basicv1.91.zip'
    destination_directory = 'data'
    unzip_file(zip_file, destination_directory) 