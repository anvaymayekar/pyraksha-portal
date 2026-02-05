import os
from dotenv import load_dotenv
from src.app import create_app
from src.core.extensions import socketio

load_dotenv()

config_name = os.environ.get("FLASK_ENV", "development")
app = create_app(config_name)


if __name__ == "__main__":
    socketio.run(app, host="0.0.0.0", port=5000, debug=True)
