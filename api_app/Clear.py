from Database import db
from a import api_app


@api_app.route("/db/api/clear/")
def clear_db():
	db.clear()
	return 'Lol'
