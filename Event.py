from app import db, app, make_response, jsonify
from Location import Location
from Event_status import Event_status
from Person import Person
from sqlalchemy.dialects.postgresql import UUID


class Event(db.Model):
    __tablename__ = "event"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(265), nullable=False)
    stand_size = db.Column(db.Integer, nullable=False)
    contact_objective = db.Column(db.Integer, nullable=False)
    date_event = db.Column(db.Date, nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey('event_status.id'))
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    item_manager = db.Column(UUID, db.ForeignKey('person.id'))

    r_stat = db.relationship(Event_status, backref="event_status", cascade="save-update")
    r_loc = db.relationship(Location, backref="location", cascade="save-update")
    r_item_manager = db.relationship(Person, backref="person", cascade="save-update")

    def __repr__(self):
        return f'<Event {self.name}>'

    def json(self):
        loc = Location.query.filter_by(id=self.location_id).first()
        person = Person.query.filter_by(id=self.item_manager).first()
        return {
            'id': self.id,
            'name': self.name,
            'stand_size': self.stand_size,
            'contact_objective': self.contact_objective,
            'date_event': self.date_event.strftime('%Y-%m-%d'),
            'status_id': Event_status.query.filter_by(id=self.status_id).first().label,
            'item_manager': {'name': person.last_name,
                             'surname': person.first_name},
            'location_id': {'address': loc.address,
                            'city': loc.city,
                            'room': loc.room}
        }


@app.route('/events')
def get_event_data():
    try:
        event_list = Event.query.all()
        return make_response(jsonify([event.json() for event in event_list]), 200)
    except Exception as e:
        return make_response(jsonify({'message': f'Error getting events, {e}'}), 500)


@app.route('/events/<int:id>/')
def event(id):
    event = Event.query.get_or_404(id)
    return event.json()
