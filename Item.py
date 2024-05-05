from app import db, app, make_response, jsonify


class Item(db.Model):
    __tablename__ = "item"

    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50), nullable=False)

    def __repr__(self):
        return f'<Item {self.name}>'

    def json(self):
        return {
            'id': self.id,
            'name': self.name,
        }


@app.route('/items')
def get_item_data():
    try:
        item_list = Item.query.all()
        return make_response(jsonify([item.json() for item in item_list]), 200)
    except Exception as e:
        return make_response(jsonify({'message': f'Error getting items, {e}'}), 500)


@app.route('/items/<int:id>/')
def item(id):
    item = Item.query.get_or_404(id)
    return item.json()
