from app import db, app, make_response, jsonify
from Item import Item
from Event import Event
from Users import Users

from sqlalchemy.dialects.postgresql import UUID


class Reserved_item(db.Model):
    __tablename__ = "reserved_item"
    status = db.Column(db.Boolean, nullable=False)
    quantity = db.Column(db.Integer, nullable=False)
    reserved_on = db.Column(db.DateTime, nullable=False)
    reserved_by = db.Column(UUID, db.ForeignKey('users.id'))
    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), primary_key=True)

    r_users = db.relationship('Users', backref='reserved_users', cascade="save-update")
    r_event = db.relationship('Event', backref="reserved_event", cascade="save-update, delete")
    r_item = db.relationship(Item, backref="reserved_item", cascade="save-update, delete")

    def __repr__(self):
        return f'<Reserved_item {self.r_item}>'

    def json(self):
        item = Item.query.filter_by(id=self.item_id).first()
        ev = Event.query.filter_by(id=self.event_id).first()
        user = Users.query.filter_by(id=self.reserved_by).first()
        return {
            'status': self.status,
            'quantity': self.quantity,
            'created_on': self.reserved_on,
            'reserved_by': {'email': user.email},
            'id_event': {'name': ev.name},
            'id_item': {'name': item.name},
        }


@app.route('/reserved_item')
def get_reserved_item_data():
    try:
        reserved_item_list = Reserved_item.query.all()
        return make_response(jsonify([reserved_item.json() for reserved_item in reserved_item_list]), 200)
    except Exception as e:
        return make_response(jsonify({'message': f'Error getting reserved_items, {e}'}), 500)


@app.route('/reserved_item/<int:id>/')
def reserved_item(id):
    reserved_item = Reserved_item.query.get_or_404(id)
    return reserved_item.json()
