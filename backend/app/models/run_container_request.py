from pydantic import BaseModel

class RunContainerRequest(BaseModel):
    """
    Pydantic model for validating the request data for running a Docker container.

    Attributes:
        endpoint (int): The port number on which the container will be exposed.
        image_name (str): The name of the Docker image to be built and run.
    """
    endpoint: int
    image_name: str