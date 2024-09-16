from app import create_app

# Provide a default config if none is specified
app = create_app('development')

if __name__ == '__main__':
    """
    Entry point for running the Flask application.

    The application will run on all available IP addresses (0.0.0.0) and listen on port 5000.
    """
    app.run(host='0.0.0.0', port=5000)