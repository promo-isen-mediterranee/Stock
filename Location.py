from app import db, app, make_response, jsonify
from sqlalchemy.sql.expression import func

class Location(db.Model):
    __tablename__ = "location"

    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    room = db.Column(db.String(10), nullable=True)

    def __repr__(self):
        return f'<Location {self.city}>'

    def json(self):
        return {
            'id': self.id,
            'address': self.address,
            'city': self.city,
            'room': self.room,
        }


@app.route('/location')
def get_location_data():
    try:
        location_list = Location.query.all()
        return make_response(jsonify([loc.json() for loc in location_list]), 200)
    except Exception as e:
        return make_response(jsonify({'message': f'Error getting locations, {e}'}), 500)


@app.route('/location/<int:id>/')
def location(id):
    location = Location.query.get_or_404(id)
    return location.json()


def get_location_id(address, city, room):
    loc = Location.query.filter_by(address=address, city=city, room=room).first()
    if loc is None:
        new_loc = Location(id=db.session.query(func.max(Location.id) + 1), address=address, city=city, room=room)
        db.session.add(new_loc)
        db.session.commit()
        return new_loc.id
    else:
        return loc.id
