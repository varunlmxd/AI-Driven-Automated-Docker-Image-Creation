class ProductionConfig:
    """
    Configuration class for the production environment.

    Attributes:
        DEBUG (bool): Enable or disable debug mode.
        UPLOAD_FOLDER (str): The directory where uploaded files will be stored.
    """
    DEBUG = False
    UPLOAD_FOLDER = '/var/uploads'