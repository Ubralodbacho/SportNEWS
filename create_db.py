from ext import app, db
from models import User
from werkzeug.security import generate_password_hash

with app.app_context():
    db.drop_all()
    db.create_all()

    admin_username = 'ubralodbacho'
    admin_password = 'bacho1'
    admin_role = 'Admin'

    existing_admin = User.query.filter_by(username=admin_username).first()

    if not existing_admin:
        new_admin = User(username=admin_username, password=admin_password, role=admin_role)
        db.session.add(new_admin)
        db.session.commit()
        print("ადმინი წარმატებით დაემატა.")
    else:
        print("ადმინი უკვე არსებობს.")
