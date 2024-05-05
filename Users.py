from app import db, app, make_response, jsonify
import uuid
from sqlalchemy.dialects.postgresql import UUID


class Users(db.Model):
    __tablename__ = "users"

    id = db.Column(UUID, primary_key=True, unique=True, nullable=False, default=uuid.uuid4)
    email = db.Column(db.String(30), nullable=False)

    def __repr__(self):
        return f'<User {self.email}>'

    def json(self):
        return {
            'id': self.id,
            'email': self.email,
        }


@app.route('/users')
def get_user_data():
    try:
        users_list = Users.query.all()
        return make_response(jsonify([user.json() for user in users_list]), 200)
    except Exception as e:
        return make_response(jsonify({'message': f'Error getting users, {e}'}), 500)


@app.route('/users/<int:id>/')
def user(id):
    user = Users.query.get_or_404(id)
    return user.json()
