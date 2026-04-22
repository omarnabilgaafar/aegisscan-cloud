import os
from app.main import create_app
from app.database.schema import init_db

app = create_app()
init_db()

if __name__ == "__main__":
    port = int(os.environ.get("PORT", 5000))
    app.run(host="0.0.0.0", port=port, debug=False)