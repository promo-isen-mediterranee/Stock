import uuid
from app import db
from sqlalchemy.sql.expression import func, text



class Users(db.Model):
    __tablename__ = "users"

    id = db.Column(db.UUID, primary_key=True, unique=True, nullable=False, default=uuid.uuid4)
    email = db.Column(db.String(30), nullable=False)


class Item(db.Model):
    __tablename__ = "item"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)
    category = db.Column(db.String(50), nullable=False)

    def json(self):
        return {
            'id': self.id,
            'name': self.name,
            'category': self.category
        }


class Location(db.Model):
    __tablename__ = "location"

    id = db.Column(db.Integer, primary_key=True)
    address = db.Column(db.String(100), nullable=False)
    city = db.Column(db.String(100), nullable=False)
    room = db.Column(db.String(10), nullable=True)


class Item_location(db.Model):
    __tablename__ = "item_location"

    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), primary_key=True)
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'), primary_key=True)
    quantity = db.Column(db.Integer, nullable=False)

    r_item = db.relationship(Item, backref="item", cascade="save-update, delete")
    r_location = db.relationship('Location', backref="item_location", cascade="save-update")


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
    date_start = db.Column(db.DateTime, nullable=False)
    date_end = db.Column(db.DateTime, nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey('event_status.id'))
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    item_manager = db.Column(db.UUID, db.ForeignKey('person.id'))

    r_stat = db.relationship(Event_status, backref="event_status", cascade="save-update")
    r_loc = db.relationship(Location, backref="location", cascade="save-update")
    r_item_manager = db.relationship(Person, backref="person", cascade="save-update")


class Reserved_item(db.Model):
    __tablename__ = "reserved_item"

    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), primary_key=True)
    item_id = db.Column(db.Integer, db.ForeignKey('item.id'), primary_key=True)
    status = db.Column(db.Boolean, nullable=False, default=False)
    quantity = db.Column(db.Integer, nullable=False)
    reserved_on = db.Column(db.DateTime, nullable=False,
                            server_default=db.func.now().op('AT TIME ZONE')(text("'Europe/Paris'")))
    reserved_by = db.Column(db.UUID, db.ForeignKey('users.id'))

    r_users = db.relationship(Users, backref='reserved_users', cascade="save-update")
    r_event = db.relationship(Event, backref="reserved_event", cascade="save-update")
    r_item = db.relationship(Item, backref="reserved_item", cascade="save-update")


def get_location_id(address, city, room):
    loc = Location.query.filter_by(address=address, city=city, room=room).first()
    if loc is None:
        new_loc = Location(id=db.session.query(func.max(Location.id) + 1), address=address, city=city, room=room)
        db.session.add(new_loc)
        db.session.commit()
        return new_loc.id
    else:
        return loc.id