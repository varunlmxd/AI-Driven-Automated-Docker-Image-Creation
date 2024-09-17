import os
import zipfile
import uuid

def extract_zip(zip_file_path, extract_to):
    """
    Extract the contents of the zip file to a given directory without creating extra folders.

    Args:
        zip_file_path (str): The path to the zip file to be extracted.
        extract_to (str): The directory where the contents of the zip file will be extracted.

    Returns:
        None
    """
    with zipfile.ZipFile(zip_file_path, 'r') as zip_ref:
        for file_info in zip_ref.infolist():
            # Construct the file path
            extracted_path = os.path.join(extract_to, os.path.basename(file_info.filename))
            # Extract the file
            with zip_ref.open(file_info) as source, open(extracted_path, 'wb') as target:
                target.write(source.read())
    # Delete the zip file
    os.remove(zip_file_path)

def create_unique_directory(base_path='./uploads'):
    """
    Create a unique directory for the user's session.

    Args:
        base_path (str): The base directory where the unique directory will be created. Defaults to './uploads'.

    Returns:
        str: The path to the created unique directory.
    """
    unique_id = str(uuid.uuid4())  # Generate a unique ID for each request
    user_upload_dir = os.path.join(base_path, unique_id)
    os.makedirs(user_upload_dir, exist_ok=True)
    return user_upload_dir