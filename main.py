from flask import request, jsonify, make_response
from app import db, app
from sqlalchemy.sql.expression import func

from Location import Location, get_location_id
from Item import Item
from Item_location import Item_location
from Event import Event
from Reserved_item import Reserved_item


@app.route('/items', methods=['POST'])
def create_new_item():
    try:
        request_form = request.get_json()

        name = request_form['name']
        quantity = int(request_form['quantity'])
        address = request_form['address']
        city = request_form['city']
        room = request_form['room']
        location_id = get_location_id(address, city, room)

        item_id = db.session.query(func.max(Item.id) + 1).first()[0]
        item = Item(id=item_id,
                    name=name)
        item_location = Item_location(item_id=item_id,
                                      location_id=location_id,
                                      quantity=quantity)
        db.session.add(item)
        db.session.add(item_location)
        db.session.commit()
        return make_response(jsonify({'message': 'Item created'}), 201)
    except Exception as e:
        return make_response(jsonify({'message': f'Error creating item, {e}'}), 500)


@app.route('/items/<int:item_id>/<int:location_id>', methods=['PUT'])
def add_stock(item_id, location_id):
    try:
        item = Item.query.get_or_404(item_id)
        loc = Location.query.get_or_404(location_id)
        if item and loc:
            request_form = request.get_json()
            item_loc = Item_location.query.get((item_id, location_id))
            quantity = request_form['quantity']
            item_loc.quantity = quantity
            db.session.commit()
            return make_response(jsonify({'message': 'Item updated'}), 200)
        return make_response(jsonify({'message': 'Item not found'}), 404)
    except Exception as e:
        return make_response(jsonify({'message': f'Error updating item, {e}'}), 500)


@app.route('/items/<int:item_id>/', methods=['DELETE'])
def delete_item(item_id):
    try:
        item = Item.query.get_or_404(item_id)
        item_location = Item_location.query.filter_by(item_id=item_id).all()
        if item and item_location:
            db.session.delete(item)
            [db.session.delete(item_loc) for item_loc in item_location]
            db.session.commit()
            return make_response(jsonify({'message': 'Item deleted'}), 200)

        return make_response(jsonify({'message': 'Item not found'}), 404)
    except Exception as e:
        return make_response(jsonify({'message': f'Error deleting item, {e}'}), 404)


# @app.route('/reserved_item/<int:item_id>/', methods=['POST'])
# def reserve_item(item_id): -> TODO
#     try:
#         request_form = request.get_json()
#
#         event_name = request_form["event_name"]
#         date_event = request_form["date_event"]
#         event_address = request_form['event_address']
#         city_event = request_form['city_event']
#         room_event = ""  # pas de salle spécifiée pour les events
#         event_location_id = get_location_id(event_address, city_event, room_event)
#         event = Event.query.filter_by(name=event_name, date_event=date_event, location_id=event_location_id)
#
#         status = request_form["status"]
#         quantity = request_form['quantity']
#         reserved_on = request_form["reserved_on"]
#         reserved_by = request_form["reserved_by"]
#
#         # item_location = Item_location(item_id=item_id,
#         #                               location_id=event_location_id,
#         #                               quantity=quantity)
#         reserved_item = Reserved_item(status=status, quantity=quantity, reserved_on=reserved_on,
#                                       reserved_by=reserved_by, event_id=event.id, location_id=event_location_id)
#         db.session.add(reserved_item)
#         db.commit()
#
#         return make_response(jsonify({'message': 'Item reserved'}), 201)
#     except Exception as e:
#         return make_response(jsonify({'message': f'Error reserving item, {e}'}), 201)


with app.app_context():
    db.create_all()
    app.run()
