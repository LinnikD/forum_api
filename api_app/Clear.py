from api_app.Database import db
from api_app import api_app


@api_app.route("/db/api/clear/")
def clear_db():
	db.clear()
	return 'Lol'