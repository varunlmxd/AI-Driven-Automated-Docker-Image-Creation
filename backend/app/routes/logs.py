from flask import Blueprint,Response
from app.services.docker_service import stream_logs

# Create a new Flask Blueprint for log streaming
logs_bp = Blueprint('logs', __name__)

@logs_bp.route('/api/v1/logs')
def logs():
    """
    Stream logs to the client using Server-Sent Events (SSE).

    Args:
        None

    Returns:
        Response: A streaming response with log data.
    """
    return Response(stream_logs(), mimetype='text/event-stream')