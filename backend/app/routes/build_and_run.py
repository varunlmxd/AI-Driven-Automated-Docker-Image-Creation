from flask import Blueprint, jsonify, request
from pydantic import ValidationError
from werkzeug.utils import secure_filename
import os
from app.models.run_container_request import RunContainerRequest
from app.utils.file_utils import extract_zip, create_unique_directory
from app.services.docker_service import build_and_run_docker

# Create a new Flask Blueprint for build and run operations
build_and_run_bp = Blueprint('build_and_run', __name__)

@build_and_run_bp.route('/api/v1/build_and_run', methods=['POST'])
def build_and_run():
    """
    Handle the build and run request for Docker containers.

    Args:
        zip_file (File): A zip file containing the source code of the application.
        Dockerfile (File): The Dockerfile to build the Docker image.
        image_name (str): The name of the Docker image.
        endpoint (int): The port to expose the Docker container.

    Returns:
        Response: JSON response indicating success or failure of the operation.
    """
    # Check for uploaded zip file and Dockerfile
    if 'zip_file' not in request.files:
        return jsonify({"error": "Missing Zip File", "status": 400}), 400
    if 'Dockerfile' not in request.files:
        return jsonify({"error": "Missing Dockerfile", "status": 400}), 400

    try:
        # Validate the request form data using Pydantic model
        data = RunContainerRequest(**request.form)
    except ValidationError as e:
        return jsonify({"error": "Invalid request", "message": e.errors(), "status": 400}), 400

    zip_file = request.files['zip_file']
    dockerfile = request.files['Dockerfile']

    # Check if any file is not selected
    if zip_file.filename == '':
        return jsonify({"error": "No zip file selected", "status": 400}), 400
    if dockerfile.filename == '':
        return jsonify({"error": "No Dockerfile selected", "status": 400}), 400

    # Check if zip file is valid
    if not zip_file.filename.lower().endswith('.zip'):
        return jsonify({"error": "File must be a zip file (.zip)", "status": 400}), 400

    # Create a unique directory for this user's session
    user_upload_dir = create_unique_directory()

    # Save the zip file
    zip_filename = secure_filename(zip_file.filename)
    zip_file_path = os.path.join(user_upload_dir, zip_filename)
    zip_file.save(zip_file_path)

    # Extract the zip file in the current directory
    extract_zip(zip_file_path, user_upload_dir)

    # Save the Dockerfile
    dockerfile_filename = secure_filename(dockerfile.filename)
    dockerfile_path = os.path.join(user_upload_dir, dockerfile_filename)
    dockerfile.save(dockerfile_path)

    # Check if the Dockerfile exists in the current directory
    if not os.path.exists(dockerfile_path):
        return jsonify({"error": "Dockerfile not found in extracted contents", "status": 400}), 400

    # Delegate Docker build and run logic to the service
    return build_and_run_docker(user_upload_dir, data)