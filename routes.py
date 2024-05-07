from flask import request
from models import Item, Event, Reserved_item, Item_location, Person, get_location_id
from app import app, db
from sqlalchemy.sql.expression import func, text


@app.route('/stock/item/<int:itemId>', methods=['GET'])
def get_item(itemId):
    item = Item.query.get(itemId)

    if not item:
        return 'Item introuvable', 404

    return item.json(), 200


@app.route('/stock/item/create', methods=['POST'])
def create_item():
    try:
        request_form = request.form
        name = request_form['name']
        item = Item.query.filter_by(name=name).first()
        if item:
            return 'Item already exists', 409
        
        quantity = int(request_form['quantity'])
        category = request_form['category']
        address = request_form['location.address']
        city = request_form['location.city']
        room = request_form['location.room'] if 'location.room' else ''

        locationId = get_location_id(address, city, room)
        itemId = db.session.query(func.max(Item.id) + 1).first()[0]
        item = Item(id=itemId, name=name, category=category)
        item_location = Item_location(item_id=itemId,
                                      location_id=locationId,
                                      quantity=quantity)
        
        db.session.add(item)
        db.session.add(item_location)
        db.session.commit()

        return 'Item créé', 201
    except Exception as e:
        return f'Erreur lors de la création de l item, {e}', 500


@app.route('/stock/item/<int:itemId>/<locationId>', methods=['PUT'])
def update_item(itemId, locationId):
    try:
        request_form = request.form

        name = request_form['name']
        quantity = int(request_form['quantity'])
        category = request_form['category']
        address = request_form['location.address']
        city = request_form['location.city']
        room = request_form['location.room'] if 'location.room' else ''
        new_location_id = get_location_id(address, city, room)
        
        item = Item.query.get(itemId)
        item_location = Item_location.query.filter_by(item_id=itemId, location_id=locationId).first()
        print(item_location)
        if not item:
            return 'Item introuvable', 404
        elif not item_location:
            return 'Localisation de l objet introuvable'

        item.name = name
        item.category = category
        item_location.quantity = quantity
        item_location.location_id = new_location_id

        db.session.commit()

        return 'Item mis à jour', 201
    except Exception as e:
        return f'Erreur lors de la mise à jour de l item, {e}', 500


@app.route('/stock/item/<int:itemId>', methods=['DELETE'])
def delete_item(itemId):
    try:
        item = Item.query.get(itemId)
        item_location = Item_location.query.filter_by(item_id=itemId).all()
            
        if not item:
            return 'Item introuvable', 404
        elif not item_location:
            return 'Localisation de l objet introuvable', 404

        db.session.delete(item)
        [db.session.delete(item_loc) for item_loc in item_location]
        db.session.commit()

        return 'Item supprimé', 204
    except Exception as e:
        return f'Erreur lors de la suppression de l item, {e}', 500


@app.route('/stock/reserveItem', methods=['POST'])
def reserve_item():
    try:
        request_form = request.get_json()

        ev = request_form["event"]

        event_name = ev["name"]
        date_start = ev["date_start"]
        date_end = ev["date_end"]
        event_location = ev["location"]
        event_address = event_location['address']
        city_event = event_location['city']
        room_event = '' if 'room' not in event_location else event_location['room']
        event_location_id = get_location_id(event_address, city_event, room_event)
        event = Event.query.filter_by(name=event_name, date_start=date_start, date_end=date_end, locationId=event_location_id)

        it = request_form['item']
        item_name = it['name']
        item_category = it['category']
        item = Item.query.filter_by(name=item_name, category=item_category)

        if not item:
            return 'Item not found', 404
        elif not event:
            return 'Event not found', 404
        
        quantity = request_form['quantity']
        status = request_form['status']
        reserved_on = func.now().op('AT TIME ZONE')(text("'Europe/Paris'"))
        # TODO -> reserved_by = user authentifié
        reserved_by = Person.query.filter_by(last_name = "A", first_name="Definir")

        reserved_item = Reserved_item(event_id=event.id, itemId=item.id, status=status,
                                      quantity=quantity, reserved_on=reserved_on, reserved_by=reserved_by)
        
        db.session.add(reserved_item)
        db.session.commit()

        return 'Item réservé', 201
    except Exception as e:
        return f'Erreur lors de la réservation de l item, {e}', 500



@app.route('/stock/item/unreserveItem', methods=['POST'])
def unreserve_item():
    itemId = request.form.get('item')
    event_id = request.form.get('event')

    reserved_item = Reserved_item.query.filter_by(itemId=itemId, event_id=event_id).first()

    if not reserved_item:
        return 'Reserved item not found', 404

    db.session.delete(reserved_item)
    db.session.commit()

    return 'Item unreserved', 204
