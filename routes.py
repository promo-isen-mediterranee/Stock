from flask import request
from models import Item, Event, Reserved_item, Item_location, Users, Location, Category, get_location_id
from app import app, db
from sqlalchemy.sql.expression import func, text


@app.route('/stock/item/create', methods=['POST'])
def create_item():
    try:
        request_form = request.form
        name = request_form['name']
        item = Item.query.filter_by(name=name).first()
        if item:
            return 'Item already exists', 409
        
        quantity = int(request_form['quantity'])
        label = request_form['category']
        address = request_form['location.address']
        city = request_form['location.city']
        room = request_form['location.room'] if 'location.room' in request_form else ''
        category = Category.query.filter_by(label=label).first()
        if category is None:
            new_category = Category(id=db.session.query(func.max(Category.id) + 1).first()[0], label=label)
            db.session.add(new_category)
            db.session.commit()
            category_id = new_category.id
        else:
            category_id = category.id

        locationId = get_location_id(address, city, room)
        itemId = db.session.query(func.max(Item.id) + 1).first()[0]
        item = Item(id=itemId, name=name, category_id=category_id)
        item_location = Item_location(item_id=itemId,
                                      location_id=locationId,
                                      quantity=quantity)
        
        db.session.add(item)
        db.session.add(item_location)
        db.session.commit()

        return 'Item créé', 201
    except Exception as e:
        return f'Erreur lors de la création de l item, {e}', 500


@app.route('/stock/item/<int:itemId>/<int:locationId>', methods=['GET'])
def get_item(itemId, locationId):
    item = Item.query.get(itemId)
    location = Location.query.get(locationId)
    quantity = Item_location.query.filter_by(item_id=itemId, location_id=locationId).first().quantity
    if not item:
        return 'Item introuvable', 404
    elif not location:
        return 'Location introuvable', 404
    return {"item": item.json(), "location": location.json(), "quantity": quantity}, 200


@app.route('/stock/item/<int:itemId>/<locationId>', methods=['PUT'])
def update_item(itemId, locationId):
    try:
        request_form = request.form

        name = request_form['name']
        quantity = int(request_form['quantity'])
        label = request_form['category']
        address = request_form['location.address']
        city = request_form['location.city']
        room = request_form['location.room'] if 'location.room' in request_form else ''
        new_location_id = get_location_id(address, city, room)

        category = Category.query.filter_by(label=label).first()
        if category is None:
            new_category = Category(id=db.session.query(func.max(Category.id) + 1).first()[0], label=label)
            db.session.add(new_category)
            db.session.commit()
            category_id = new_category.id
        else:
            category_id = category.id
        
        item = Item.query.filter_by(id = itemId, category_id = category_id)
        item_location = Item_location.query.filter_by(item_id=itemId, location_id=locationId).first()
        if not item:
            return 'Item introuvable', 404
        elif not item_location:
            return 'Localisation de l objet introuvable'

        item.name = name
        item.category_id = category_id
        item_location.quantity = quantity
        item_location.location_id = new_location_id

        db.session.commit()

        return 'Item mis à jour', 201
    except Exception as e:
        return f'Erreur lors de la mise à jour de l item, {e}', 500


@app.route('/stock/item/<int:itemId>/<int:locationId>', methods=['DELETE'])
def delete_item(itemId, locationId):
    try:
        item_location = Item_location.query.filter_by(item_id=itemId, location_id=locationId).first()
        
        if not item_location:
            return 'Objet à localiser introuvable', 404
        db.session.delete(item_location)
        db.session.commit()

        return 'Item supprimé', 204
    except Exception as e:
        return f'Erreur lors de la suppression de l item, {e}', 500


@app.route('/stock/location/getAll')
def get_locations():
    try:
        locations = Location.query.all()
        return [location.json() for location in locations]
    except Exception as e:
        return f'Erreur lors de la récupération des emplacements, {e}', 500


@app.route('/stock/location/create', methods=['POST'])
def create_location():
    try:
        request_form = request.form
        address = request_form["address"]
        city = request_form["city"]
        room = request_form['room'] if 'room' in request_form else ''
        new_id = db.session.query(func.max(Location.id) + 1).first()[0]
        location = Location(id=new_id, address=address, city=city, room=room)
        print(location)
        db.session.add(location)
        db.session.commit()

        return 'Emplacement créé', 203 
    except Exception as e:
       return f'Erreur lors de la création d un emplacement, {e}', 500


@app.route('/stock/location/<int:locationId>/')
def get_location(locationId):
    try:
        location = Location.query.get(locationId)
        return location.json()
    except Exception as e:
        return f'Erreur lors de la récupération d un emplacement, {e}', 500


@app.route('/stock/location/<int:locationId>/', methods = ['PUT'])
def update_location(locationId):
    try:
        request_form = request.form
        address = request_form["address"]
        city = request_form["city"]
        room = request_form['room'] if 'room' in request_form else ''
        
        location = Location.query.filter_by(id=locationId).first()

        if not location:
            return 'Emplacement introuvable', 404

        location.address = address
        location.city = city
        location.room = room

        db.session.commit()

        return 'Emplacement mis à jour', 201
    except Exception as e:
        return f'Erreur lors de la mise à jour de l emplacement, {e}', 500
    

@app.route('/stock/location/<int:locationId>', methods=['DELETE'])
def delete_location(locationId):
    try:
        location = Location.query.filter_by(id=locationId).first()
        
        if not location:
            return 'Localisation introuvable', 404
        db.session.delete(location)
        db.session.commit()

        return 'Emplacement supprimé', 204
    except Exception as e:
        return f'Erreur lors de la suppression de l emplacement, {e}', 500
    

@app.route('/stock/reserveItem', methods=['POST'])
def reserve_item():
    try:
        request_form = request.form
        event_id = request_form["eventId"]
        event = Event.query.filter_by(id=event_id).first()
        
        item_location_id = request_form['item_locationId']
        item_location = Item_location.query.filter_by(id=item_location_id).first()

        if not item_location:
            return 'Emplacement de l item introuvable', 404
        elif not event:
            return 'Event introuvable', 404
        quantity = request_form['quantity']
        status = bool(request_form['status'])
        reserved_on = func.now().op('AT TIME ZONE')(text("'Europe/Paris'"))
        # TODO -> reserved_by = user authentifié
        reserved_by = Users.query.filter_by(email="definir.a@isen.yncrea.fr").first().id

        reserved_item = Reserved_item(event_id=event.id, item_location_id=item_location_id, status=status,
                                      quantity=quantity, reserved_on=reserved_on, reserved_by=reserved_by)
        # TODO -> update quantity item 
        db.session.add(reserved_item)
        db.session.commit()

        return 'Item réservé', 201
    except Exception as e:
        return f'Erreur lors de la réservation de l item, {e}', 500



@app.route('/stock/unreserveItem/<int:eventId>/<int:item_locationId>', methods=['DELETE'])
def unreserve_item(eventId, item_locationId):
    try:
        reserved_item = Reserved_item.query.filter_by(event_id=eventId, item_location_id=item_locationId).first()
        if not reserved_item:
            return 'Reserved item not found', 404

        db.session.delete(reserved_item)
        db.session.commit()

        return 'Item unreserved', 204
    except Exception as e:
        return f'Erreur lors de la suppression de la réservation, {e}', 500
