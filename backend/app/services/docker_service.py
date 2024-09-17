from flask import jsonify
from threading import Thread
import docker
import socket
import os
import time
import logging
import queue
import shutil
import re

# Initialize Docker client
client = docker.from_env()

# Set up logging to be pushed to a queue
log_queue = queue.Queue()

# Logging handler that pushes logs to a queue
class QueueHandler(logging.Handler):
    def emit(self, record):
        # Filter out Flask's default access logs
        if not record.name.startswith('werkzeug'):
            log_queue.put(self.format(record))

# Custom logger for our application
logger = logging.getLogger('app')
logger.setLevel(logging.INFO)
logger.addHandler(QueueHandler())

def clean_dangling_images(logger,client):
    # Find all dangling images (images with none:none)
    dangling_images = client.images.list(filters={"dangling": True})
    # Stop and remove any containers using dangling images
    for dangling_image in dangling_images:
        # Find containers using this dangling image
        containers_using_dangling = client.containers.list(all=True, filters={"ancestor": dangling_image.id})
        for cont in containers_using_dangling:
            cont.stop()  # Stop the container
            cont.remove()  # Remove the container
    # Now safely remove dangling images
    for dangling_image in dangling_images:
        try:
            client.images.remove(image=dangling_image.id, force=True)
        except Exception as e:
            logger.error(f"Could not remove dangling image {dangling_image.id}: {e}")   

def stream_logs():
    """
    Stream logs from the log queue to the client using Server-Sent Events (SSE).

    This function continuously retrieves logs from the log queue and yields them
    as SSE data. It handles the case where the queue is empty by simply passing.

    Yields:
        str: A formatted string containing the log data.
    """
    while True:
        try:
            log = log_queue.get()  # Wait for 1 second for a new log
            yield f"data: {log}\n\n"
        except queue.Empty:
            pass 

def build_and_run_docker(file_path, data):
    """
    Build and run a Docker container based on the provided Dockerfile and zip contents.

    Args:
        file_path (str): The path to the directory containing the Dockerfile and extracted zip contents.
        data (RunContainerRequest): The validated request data containing image name and endpoint.

    Returns:
        Response: JSON response indicating success or failure of the operation.
    """
    try:
        # Build Docker image
        logger.info("-> Building Docker image...")
        image, build_logs = client.images.build(path=file_path, tag=data.image_name)
        
        # Log Docker build process
        for line in build_logs:
            if 'stream' in line:
                logger.info(f"Build log: {line['stream'].strip()}")
            elif 'error' in line:
                logger.error(f"Build error: {line['error'].strip()}")
        logger.info(f"-> Docker image {data.image_name} built successfully.")

        # Define regex pattern to search for port in Dockerfile
        pattern = r'--port\",?\"(\d+)'
        dockerfile_path = os.path.join(file_path, 'Dockerfile')

        # Check if Dockerfile exists
        if not os.path.isfile(dockerfile_path):
            raise FileNotFoundError(f"Dockerfile not found at {dockerfile_path}")

        # Read Dockerfile contents
        with open(dockerfile_path, 'r') as file:
            dockerfile_text = file.read()

        # Search for the port pattern in Dockerfile
        match = re.search(pattern, dockerfile_text)
        local_endpoint = match.group(1) if match else data.endpoint

        # Run Docker container
        logger.info(f"-> Running Docker container {data.image_name}...")
        container = client.containers.run(
            data.image_name,
            name=data.image_name,
            detach=True,
            ports={f'{local_endpoint}/tcp': data.endpoint}
        )

        # Wait for a few seconds to let the container start
        time.sleep(1)

        # Check if the container is still running
        container.reload()  # Refresh the container status
        if container.status != 'running':
            logs = container.logs().decode('utf-8')  # Get container logs for debugging
            time.sleep(1)
            logger.error(f"Container {data.image_name} exited unexpectedly. Logs: {logs}")
            # Stop and remove all containers created from the image
            containers = client.containers.list(all=True, filters={"ancestor": data.image_name})
            for cont in containers:
                cont.stop()  # Stop the container
                cont.remove()  # Remove the container 
            # Reload the image
            image.reload()
            client.images.remove(image=data.image_name, force=True)
            # Clean up files and directory
            shutil.rmtree(file_path)  # Remove the directory containing the Dockerfile and zip
            return jsonify({"error": f"Container exited unexpectedly. Logs: {logs}", "status": 500}), 500

        # Log container runtime logs
        container_logs = container.logs().decode('utf-8')
        logger.info(f"Container logs: {str(container_logs)}")

        # Get container details
        container_info = client.api.inspect_container(container.id)
        ports = container_info['NetworkSettings']['Ports']
        hostname = socket.gethostname()
        ip_address = socket.gethostbyname(hostname)

        # Construct URLs for the running container
        urls = [f"http://{ip_address}:{binding[0]['HostPort']}" for port, binding in ports.items() if binding]
        logger.info(f"-> Container {data.image_name} started successfully.")
        
        # Clean up files and directory
        shutil.rmtree(file_path)  # Remove the directory containing the Dockerfile and zip

        return jsonify({"urls": urls, "status": 200})

    except Exception as e:
        logger.error(f"An error occurred: {str(e)}")
        return jsonify({"error": str(e), "status": 500}), 500
    finally:
        clean_dangling_images(logger,client)
        clean_dangling_images(logger,client)
        clean_dangling_images(logger,client)
        clean_dangling_images(logger,client)