from app.main import create_app
from app.database.schema import init_db

init_db()
app = create_app()
