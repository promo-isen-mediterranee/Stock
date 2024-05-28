import uuid

from flask import current_app
from sqlalchemy.sql.expression import func, text

db = current_app.db


class Users(db.Model):
    __tablename__ = "users"

    id = db.Column(db.UUID, primary_key=True, unique=True, nullable=False, default=uuid.uuid4)
    username = db.Column(db.String(101), nullable=False)
    mail = db.Column(db.String(50), nullable=False)
    nom = db.Column(db.String(50), nullable=False)
    prenom = db.Column(db.String(50), nullable=False)
    is_active = db.Column(db.Boolean, nullable=False, default=True)
    is_authenticated = db.Column(db.Boolean, nullable=False, default=False)

    def json(self):
        return {
            'id': self.id,
            'username': self.username,
            'mail': self.mail,
            'nom': self.nom,
            'prenom': self.prenom,
            'is_active': self.is_active
        }


class Roles(db.Model):
    __tablename__ = "role"

    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    label = db.Column(db.String(20), nullable=False)

    def json(self):
        return {
            "id": self.id,
            "label": self.label
        }


class User_role(db.Model):
    __tablename__ = "user_role"

    user_id = db.Column(db.UUID, db.ForeignKey('users.id', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    role_id = db.Column(db.Integer, db.ForeignKey('role.id', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)

    r_user = db.relationship(Users, backref="users_role")
    r_role = db.relationship(Roles, backref="role")

    def json(self):
        return {
            "user": self.r_user.json(),
            "role": self.r_role.json()
        }


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
    gain = db.Column(db.Integer, nullable=False)

    r_category = db.relationship(Category, backref="category", cascade="save-update")

    def json(self):
        return {
            'id': self.id,
            'name': self.name,
            'gain': self.gain,
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
    nb_to_order = db.Column(db.Integer, nullable=False, default = 0)

    r_item = db.relationship(Item, backref="item", cascade="save-update, delete")
    r_location = db.relationship('Location', backref="item_location", cascade="save-update")

    def json(self):
        return {
            'id': self.id,
            'item_id': self.r_item.json(),
            'location_id': self.r_location.json(),
            'quantity': self.quantity,
            'nb_to_order': self.nb_to_order
        }


class Event_status(db.Model):
    __tablename__ = "event_status"

    id = db.Column(db.Integer, primary_key=True)
    label = db.Column(db.String(30), nullable=False)

    def json(self):
        return {
            'id': self.id,
            'label': self.label
        }


class Person(db.Model):
    __tablename__ = 'person'

    id = db.Column(db.UUID, primary_key=True, unique=True, nullable=False, default=uuid.uuid4)
    first_name = db.Column(db.String(50))
    last_name = db.Column(db.String(50))

    def json(self):
        return {
            'id': self.id,
            'first_name': self.first_name,
            'last_name': self.last_name
        }


class Event(db.Model):
    __tablename__ = "event"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(265), nullable=False)
    stand_size = db.Column(db.Integer, nullable=True)
    contact_objective = db.Column(db.Integer, nullable=False, default=100)
    date_start = db.Column(db.DateTime(timezone=True), nullable=False)
    date_end = db.Column(db.DateTime(timezone=True), nullable=False)
    status_id = db.Column(db.Integer, db.ForeignKey('event_status.id'))
    location_id = db.Column(db.Integer, db.ForeignKey('location.id'))
    item_manager = db.Column(db.UUID, db.ForeignKey('person.id'))

    r_stat = db.relationship(Event_status, backref="event_status", cascade="save-update")
    r_loc = db.relationship(Location, backref="location", cascade="save-update")
    r_item_manager = db.relationship(Person, backref="person", cascade="save-update")

    def json(self):
        return {
            'id': self.id,
            'name': self.name,
            'stand_size': self.stand_size,
            'contact_objective': self.contact_objective,
            'date_start': self.date_start,
            'date_end': self.date_end,
            'status_id': self.r_stat.json(),
            'location_id': self.r_loc.json(),
            'item_manager': self.r_item_manager.json()
        }


class Reserved_item(db.Model):
    __tablename__ = "reserved_item"

    event_id = db.Column(db.Integer, db.ForeignKey('event.id'), primary_key=True)
    item_location_id = db.Column(db.Integer, db.ForeignKey('item_location.id'), primary_key=True)
    status = db.Column(db.Boolean, nullable=False, default=False)
    quantity = db.Column(db.Integer, nullable=False)
    quantity_ret = db.Column(db.Integer, nullable=True)
    reserved_on = db.Column(db.DateTime(timezone=True), nullable=False,
                            server_default=db.func.now().op('AT TIME ZONE')(text("'Europe/Paris'")))
    reserved_by = db.Column(db.UUID, db.ForeignKey('users.id'))

    r_users = db.relationship(Users, backref='reserved_users', cascade="save-update")
    r_event = db.relationship(Event, backref="reserved_event", cascade="save-update")
    r_item_location = db.relationship(Item_location, backref="reserved_item_location", cascade="save-update")

    def json(self):
        return {
            "event_id": self.r_event.json(),
            "item_location_id": self.r_item_location.json(),
            "status": self.status,
            "quantity": self.quantity,
            "quantity_ret": self.quantity_ret,
            "reserved_on": self.reserved_on,
            "reserved_by": self.r_users.json(),
        }


class Permissions(db.Model):
    __tablename__ = "permission"

    id = db.Column(db.Integer, primary_key=True, unique=True, nullable=False, autoincrement=True)
    label = db.Column(db.String(20), nullable=False, unique=True)

    def json(self):
        return {
            "id": self.id,
            "label": self.label
        }


class Role_permissions(db.Model):
    __tablename__ = "role_permission"

    role_id = db.Column(db.Integer, db.ForeignKey('role.id', onupdate='CASCADE', ondelete='CASCADE'), primary_key=True)
    permission_id = db.Column(db.Integer, db.ForeignKey('permission.id', onupdate='CASCADE', ondelete='CASCADE'),
                              primary_key=True)

    r_role = db.relationship(Roles, backref="role_permissions")
    r_permission = db.relationship(Permissions, backref="permission")

    def json(self):
        return {
            "role": self.r_role.json(),
            "permission": self.r_permission.json()
        }


def empty(str):
    return str == "" or str.isspace()
