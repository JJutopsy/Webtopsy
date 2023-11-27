from flask_cors import CORS
import sys
from dotenv import load_dotenv
import os
load_dotenv()
sys.path.append(os.environ.get("HOME"))

from backend.server import create_app

app = create_app()
CORS(app, supports_credentials=True)

if __name__ == '__main__':
    try:
        app.run(debug=True)     
    finally:
        app.db_thread.stop()