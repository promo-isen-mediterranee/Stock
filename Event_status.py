from app import db, app, make_response, jsonify


class Event_status(db.Model):
    __tablename__ = "event_status"

    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(30), nullable=False)

    def __repr__(self):
        return f'<Event_status {self.label}>'

    def json(self):
        return {
            'id': self.id,
            'label': self.label,
        }


@app.route('/events_status')
def get_status_data():
    try:
        event__status_list = Event_status.query.all()
        return make_response(jsonify([status.json() for status in event__status_list]), 200)
    except Exception as e:
        return make_response(jsonify({'message': f'Error getting status, {e}'}), 500)


@app.route('/events_status/<int:id>/')
def status(id):
    event_status = Event_status.query.get_or_404(id)
    return event_status.json()
