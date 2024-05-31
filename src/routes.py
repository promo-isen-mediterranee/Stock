from datetime import datetime, timedelta
from functools import wraps
from os import environ
from flask import request, session, abort, current_app
from flask_login import current_user
from .models import Item, Event, Reserved_item, Item_location, Users, Location, Category, empty, User_role, Role_permissions
from sqlalchemy.sql.expression import func, text

db = current_app.db
login_manager = current_app.login_manager
logger = current_app.logger


def response(obj=None, message=None, status_code=200):
    dictionary = {}

    if status_code >= 400:
        dictionary["error"] = message
    else:
        if obj is not None:
            dictionary = obj
        elif message is not None:
            dictionary["message"] = message

    return dictionary, status_code


def permissions_required(*permissions):
    def wrapper(fn):
        @wraps(fn)
        def decorated_view(*args, **kwargs):
            bypass_token = request.headers.get("X-BYPASS")
            if bypass_token == environ.get("BYPASS_TOKEN"):
                return fn(*args, **kwargs)

            if not current_user and not current_user.is_authenticated:
                return login_manager.unauthorized()

            if not permissions:
                return fn(*args, **kwargs)

            user_roles = User_role.query.filter_by(user_id=current_user.id).all()
            roles = [user_role.r_role for user_role in user_roles]
            has_permission = any(
                Role_permissions.query.filter_by(role_id=role.id, permission_id=permission).first()
                for role in roles for permission in permissions
            )

            if has_permission:
                return fn(*args, **kwargs)
            return abort(403)

        return decorated_view

    return wrapper


@login_manager.user_loader
def user_loader(userId):
    return Users.query.get(userId)


@current_app.errorhandler(400)
def bad_request(e):
    return response(message='Requête incorrecte', status_code=400)


@current_app.errorhandler(401)
def unauthorized(e):
    return response(message='Non autorisé', status_code=401)


@current_app.errorhandler(403)
def forbidden(e):
    return response(message='Accès interdit', status_code=403)


@current_app.errorhandler(404)
def page_not_found(e):
    return response(message='Resource introuvable', status_code=404)


@current_app.errorhandler(405)
def method_not_allowed(e):
    return response(message='Méthode non autorisée', status_code=405)


@current_app.errorhandler(409)
def conflict(e):
    return response(message='Conflit', status_code=409)


@current_app.errorhandler(429)
def too_many_requests(e):
    return response(message=e, status_code=429)


@current_app.errorhandler(500)
def internal_server_error(e):
    return response(message='Erreur interne du serveur', status_code=500)


@current_app.get('/stock/item/getAll')
@permissions_required(5)
def get_items():
    items = Item_location.query.all()
    return response(obj=[item.json() for item in items])


@current_app.post('/stock/category/create')
@permissions_required(10)
def create_category():
    request_form = request.form
    label = request_form['label']
    category = Category.query.filter_by(label=label).first()

    if category:
        abort(409)

    if empty(label):
        abort(400)

    categoryId = db.session.query(func.max(Category.id) + 1).first()[0]
    new_category = Category(id=categoryId, label=label)
    db.session.add(new_category)
    db.session.commit()

    return response(message="Catégorie créée", status_code=201)


@current_app.get('/stock/category/getAll')
@permissions_required(9)
def get_categories():
    categories = Category.query.all()
    return response(obj=[category.json() for category in categories])


@current_app.get('/stock/category/<int:categoryId>')
@permissions_required(9)
def get_category(categoryId):
    category = Category.query.get(categoryId)
    return response(obj=category.json())


@current_app.put('/stock/category/<int:categoryId>')
@permissions_required(10)
def update_category(categoryId):
    request_form = request.form
    label = request_form['label']

    if empty(label):
        abort(400)

    category = Category.query.filter_by(id=categoryId).first()
    if category is None:
        abort(404)

    category.label = label
    db.session.commit()

    return response(message="Catégorie mise à jour", status_code=201)


@current_app.delete('/stock/category/<int:categoryId>')
@permissions_required(10)
def delete_category(categoryId):
    category = Category.query.filter_by(id=categoryId).first()

    if not category:
        abort(404)
    db.session.delete(category)
    db.session.commit()

    return response(message="Item supprimé", status_code=204)


@current_app.post('/stock/item/create')
@permissions_required(6)
def create_item():
    request_form = request.form
    name = request_form['name']
    item = Item.query.filter_by(name=name).first()
    if item:
        abort(409)

    quantity = int(request_form['quantity'])
    label = request_form['category']
    locationId = int(request_form['location.id'])

    if empty(name) or quantity <= 0 or empty(label):
        abort(400)

    category = Category.query.filter_by(label=label).first()
    category_id = category.id
    itemId = db.session.query(func.max(Item.id) + 1).first()[0]
    item = Item(id=itemId, name=name, category_id=category_id)
    item_location = Item_location(item_id=itemId,
                                  location_id=locationId,
                                  quantity=quantity)

    db.session.add(item)
    db.session.add(item_location)
    db.session.commit()

    return response(message="Item créé", status_code=201)


@current_app.get('/stock/item/<int:itemId>/<int:locationId>')
@permissions_required(5)
def get_item(itemId, locationId):
    item = Item.query.get(itemId)
    location = Location.query.get(locationId)
    quantity = Item_location.query.filter_by(item_id=itemId, location_id=locationId).first().quantity
    if not item or not location:
        abort(404)
    return response(obj={"item": item.json(), "location": location.json(), "quantity": quantity})


@current_app.put('/stock/item/<int:itemId>/<locationId>')
@permissions_required(6)
def update_item(itemId, locationId):
    request_form = request.form

    name = request_form['name']
    quantity = int(request_form['quantity'])
    label = request_form['category']
    locationId = request_form['location.id']

    nb_to_order =request_form['nb_to_order'] if 'nb_to_order' in request_form else 0

    if empty(name) or quantity <= 0 or empty(label):
        abort(400)

    category = Category.query.filter_by(label=label).first()
    if category is None:
        new_category = Category(id=db.session.query(func.max(Category.id) + 1).first()[0], label=label)
        db.session.add(new_category)
        db.session.commit()
        category_id = new_category.id
    else:
        category_id = category.id

    item = Item.query.filter_by(id=itemId)
    item_location = Item_location.query.filter_by(item_id=itemId, location_id=locationId).first()
    if not item or not item_location:
        abort(404)
    item.name = name
    item.nb_to_order = nb_to_order
    item.category_id = category_id
    item_location.quantity = quantity
    item_location.location_id = locationId

    db.session.commit()

    return response(message='Item mis à jour', status_code=201)


@current_app.delete('/stock/item/<int:itemId>/<int:locationId>')
@permissions_required(6)
def delete_item(itemId, locationId):
    item_location = Item_location.query.filter_by(item_id=itemId, location_id=locationId).first()

    if not item_location:
        abort(404)
    db.session.delete(item_location)
    db.session.commit()

    return response(message='Item supprimé', status_code=204)


@current_app.get('/stock/location/getAll')
@permissions_required(7)
def get_locations():
    locations = Location.query.all()
    return response(obj=[location.json() for location in locations])


@current_app.post('/stock/location/create')
@permissions_required(8)
def create_location():
    request_form = request.form
    address = request_form["address"]
    city = request_form["city"]
    if empty(address) or empty(city):
        abort(400)

    room = request_form['room'] if 'room' in request_form else ''
    new_id = db.session.query(func.max(Location.id) + 1).first()[0]
    location = Location(id=new_id, address=address, city=city, room=room)
    db.session.add(location)
    db.session.commit()

    return response(message='Emplacement créé', status_code=203)


@current_app.get('/stock/location/<int:locationId>/')
@permissions_required(7)
def get_location(locationId):
    location = Location.query.get(locationId)
    return response(obj=location.json())


@current_app.put('/stock/location/<int:locationId>/')
@permissions_required(8)
def update_location(locationId):
    request_form = request.form
    address = request_form["address"]
    city = request_form["city"]
    room = request_form['room'] if 'room' in request_form else ''

    if empty(address) or empty(city):
        abort(400)

    location = Location.query.filter_by(id=locationId).first()

    if not location:
        abort(404)

    location.address = address
    location.city = city
    location.room = room

    db.session.commit()

    return response(message='Emplacement mis à jour', status_code=201)


@current_app.delete('/stock/location/<int:locationId>')
@permissions_required(8)
def delete_location(locationId):
    location = Location.query.filter_by(id=locationId).first()
    item_loc = Item_location.query.filter_by(location_id=locationId).first()
    event = Event.query.filter_by(location_id=locationId).first()
    if event or item_loc:
        abort(409)
    if not location:
        abort(404)
    db.session.delete(location)
    db.session.commit()

    return response(message='Emplacement supprimé', status_code=204)


@current_app.post('/stock/reserveItem')
@permissions_required(11)
def reserve_item():
    request_form = request.form
    event_id = request_form["eventId"]
    item_location_id = request_form['item_locationId']

    event = Event.query.filter_by(id=event_id).first()
    item_location = Item_location.query.filter_by(id=item_location_id).first()

    if not item_location or not event:
        abort(404)

    quantity = request_form['quantity']
    if empty(quantity):
        abort(400)

    status = request_form.get('status', False, bool)
    reserved_on = func.now().op('AT TIME ZONE')(text("'Europe/Paris'"))
    reserved_by = None
    if current_user and current_user.is_authenticated:
        reserved_by = current_user.id

    check = Reserved_item.query.filter_by(event_id=event_id, item_location_id=item_location_id).first()
    if check:
        abort(409)

    reserved_item = Reserved_item(event_id=event.id, item_location_id=item_location_id, status=status,
                                  quantity=quantity, reserved_on=reserved_on, reserved_by=reserved_by)
    db.session.add(reserved_item)
    db.session.commit()

    return response(message='Item réservé', status_code=201)


@current_app.put('/stock/reservedItem/edit/<int:eventId>/<int:item_locationId>')
@permissions_required(11)
def update_reserved_item(eventId, item_locationId):
    request_form = request.form
    event_id = request_form["eventId"]
    event = Event.query.filter_by(id=event_id).first()

    item_location_id = request_form['item_locationId']
    item_location = Item_location.query.filter_by(id=item_location_id).first()

    quantity = request_form['quantity']
    status = bool(request_form['status']) if 'status' in request_form else False

    if not event or not item_location:
        abort(404)

    if empty(event_id) or empty(item_location_id) or empty(quantity):
        abort(400)

    reserved_item = Reserved_item.query.filter_by(event_id=eventId, item_location_id=item_locationId).first()

    reserved_item.event_id = event_id
    reserved_item.item_location_id = item_location_id
    reserved_item.quantity = quantity
    reserved_item.status = status

    db.session.commit()

    return response(message='Emplacement mis à jour', status_code=201)


@current_app.delete('/stock/unreserveItem/<int:eventId>/<int:item_locationId>')
@permissions_required(11)
def unreserve_item(eventId, item_locationId):
    reserved_item = Reserved_item.query.filter_by(event_id=eventId, item_location_id=item_locationId).first()
    if not reserved_item:
        abort(404)

    db.session.delete(reserved_item)
    db.session.commit()

    return response(message='Item unreserved', status_code=204)


@current_app.get('/stock/reservedItem/getAll')
@permissions_required(12)
def get_reserved_items():
    date_start = request.form['date_start'] if 'date_start' in request.form else ''
    date_end = request.form['date_end'] if 'date_end' in request.form else ''
    if not empty(date_start) and not empty(date_end):
        date_start = datetime.strptime(date_start, '%Y-%m-%d')
        date_end = datetime.strptime(date_end, '%Y-%m-%d')
        reserved_items = Reserved_item.query.filter(
            Reserved_item.reserved_on >= date_start,
            Reserved_item.reserved_on <= date_end
        ).all()
        return response(obj=[reserved_item.json() for reserved_item in reserved_items])
    elif not empty(date_start):
        date_start = datetime.strptime(date_start, '%Y-%m-%d')
        reserved_items = Reserved_item.query.filter(
            Reserved_item.reserved_on >= date_start
        ).all()
        return response(obj=[reserved_item.json() for reserved_item in reserved_items])
    elif not empty(date_end):
        date_end = datetime.strptime(date_end, '%Y-%m-%d')
        reserved_items = Reserved_item.query.filter(
            Reserved_item.reserved_on <= date_end
        ).all()
        return response(obj=[reserved_item.json() for reserved_item in reserved_items])
    else:
        reserved_items = Reserved_item.query.all()
        return response(obj=[reserved_item.json() for reserved_item in reserved_items])


@current_app.get('/stock/reservedItem/getAll/<int:eventId>')
@permissions_required(12)
def get_reserved_items_event(eventId):
    reserved_items = Reserved_item.query.filter_by(event_id=eventId).all()
    return response(obj=[reserved_item.json() for reserved_item in reserved_items])
