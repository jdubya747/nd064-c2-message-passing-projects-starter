import os
import logging
from app import create_app

logging.basicConfig(format='%(levelname)s: %(asctime)s %(message)s', level=logging.DEBUG)
app = create_app(os.getenv("FLASK_ENV") or "test")
if __name__ == "__main__":
    app.run(debug=True)
