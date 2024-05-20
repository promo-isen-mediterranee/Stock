import uuid
from stock.database import get_db
from sqlalchemy.sql.expression import func, text

db = get_db()

class Users(db.Model):
    __tablename__ = "users"

    id = db.Column(db.UUID, primary_key=True, unique=True, nullable=False, default=uuid.uuid4)
    email = db.Column(db.String(30), nullable=False)


class Category(db.Model):
    __tablename__ = "category"

    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(50), nullable=False)

    def json(self):
        return {
            'id': self.id,
            'label': self.label
        }


class Item(db.Model):
    __tablename__ = "item"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    category_id = db.Column(db.String(50), db.ForeignKey("category.id"), nullable=False)

    r_category = db.relationship(Category, backref="category", cascade="save-update")


    def json(self):
        return {
            'id': self.id,
            'name': self.name,
            'category_id': self.r_category.json()
        }


class Location(db.Model):
    __tablename__ = "location"

    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    room = db.Column(db.String(10), nullable=True)
    def json(self):
        return {"id": self.id,
                "address": self.address,
                "city": self.city,
                "room": self.room} 


class Item_location(db.Model):
    __tablename__ = "item_location"
    id = db.Column(db.Integer, primary_key=True)

    item_id = db.Column(db.Integer, db.ForeignKey('item.id'))
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    quantity = db.Column(db.Integer, nullable=False)

    r_item = db.relationship(Item, backref="item", cascade="save-update, delete")
    r_location = db.relationship('Location', backref="item_location", cascade="save-update")

    def json(self):
        return {
            'id': self.id,
            'item_id': self.r_item.json(),
            'location_id': self.r_location.json(),
            'quantity': self.quantity
        }    


class Event_status(db.Model):
    __tablename__ = "event_status"

    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(30), nullable=False)


class Person(db.Model):
    __tablename__ = 'person'

    id = db.Column(db.UUID, primary_key=True, unique=True, nullable=False, default=uuid.uuid4)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))


class Event(db.Model):
    __tablename__ = "event"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(265), nullable=False)
    stand_size = db.Column(db.Integer, nullable=True)
    contact_objective = db.Column(db.Integer, nullable=False, default=100)
    date_start = db.Column(db.DateTime(timezone = True), nullable=False)
    date_end = db.Column(db.DateTime(timezone = True), nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey('event_status.id'))
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    item_manager = db.Column(db.UUID, db.ForeignKey('person.id'))

    r_stat = db.relationship(Event_status, backref="event_status", cascade="save-update")
    r_loc = db.relationship(Location, backref="location", cascade="save-update")
    r_item_manager = db.relationship(Person, backref="person", cascade="save-update")


class Reserved_item(db.Model):
    __tablename__ = "reserved_item"

    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), primary_key = True)
    item_location_id = db.Column(db.Integer, db.ForeignKey('item_location.id'), primary_key=  True)
    status = db.Column(db.Boolean, nullable=False, default=False)
    quantity = db.Column(db.Integer, nullable=False)
    reserved_on = db.Column(db.DateTime(timezone = True), nullable=False,
                            server_default=db.func.now().op('AT TIME ZONE')(text("'Europe/Paris'")))
    reserved_by = db.Column(db.UUID, db.ForeignKey('users.id'))

    r_users = db.relationship(Users, backref='reserved_users', cascade="save-update")
    r_event = db.relationship(Event, backref="reserved_event", cascade="save-update")
    r_item_location = db.relationship(Item_location, backref="reserved_item_location", cascade="save-update")


def empty(str):
    if str=="" or str.isspace():
        return 1
    return 0