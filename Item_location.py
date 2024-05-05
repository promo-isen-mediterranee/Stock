from app import db, app, make_response, jsonify
from Item import Item
from Location import Location


class Item_location(db.Model):
    __tablename__ = "item_location"

    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), primary_key=True)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)

    r_item = db.relationship(Item, backref="item", cascade="save-update, delete")
    r_location = db.relationship('Location', backref="item_location", cascade="save-update")

    def __repr__(self):
        return f'<Item_location {self.r_item, self.r_location}>'

    def json(self):
        item = Item.query.filter_by(id=self.item_id).first()
        loc = Location.query.filter_by(id=self.location_id).first()
        return {
            'name': item.name,
            'city': loc.city, 'room': loc.room,
            'quantity': self.quantity,
        }


@app.route('/items_location')
def get_item_location_data():
    try:
        item_loc_list = Item_location.query.all()
        return make_response(jsonify([item_loc.json() for item_loc in item_loc_list]), 200)
    except Exception as e:
        return make_response(jsonify({'message': f'Error getting items location, {e}'}), 500)


@app.route('/items_location/<int:item_id>/')
def get_item_location_item_id(item_id):
    try:
        item_loca_list = Item_location.query.filter_by(item_id=item_id).all()
        return make_response(jsonify([item_loc.json() for item_loc in item_loca_list]), 200)
    except Exception as e:
        return make_response(jsonify({'message': f'Error getting items location using item id, {e}'}), 500)


@app.route('/items_location/<int:item_id>/<int:location_id>/')
def get_item_location_both_id(item_id, location_id):
    item_loc = Item_location.query.get_or_404((item_id, location_id))
    return item_loc.json()
