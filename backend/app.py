from flask_cors import CORS
import sys
from dotenv import load_dotenv
import os
load_dotenv()
sys.path.append(os.environ.get("HOME"))

from backend.server import create_app

app = create_app()
CORS(app, supports_credentials=True,)

if __name__ == '__main__':
    try:
        app.run(debug=True,host='192.168.1.4',port=5000)     
    finally:
        app.db_thread.stop()    