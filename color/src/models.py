from . import db

class LightState(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    entity_id = db.Column(db.Integer, db.ForeignKey('entity.id'), nullable=True)
    is_on = db.Column(db.Boolean, default=False)
    red = db.Column(db.Integer, default=0)
    green = db.Column(db.Integer, default=0)
    blue = db.Column(db.Integer, default=0)
    brightness = db.Column(db.Integer, default=0)
    timestamp = db.Column(db.DateTime, default=db.func.current_timestamp())

class Entity(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(120), nullable=False)
    start_addr = db.Column(db.Integer, nullable=False)
    end_addr = db.Column(db.Integer, nullable=False)
    parent_id = db.Column(db.Integer, db.ForeignKey('entity.id'), nullable=True)

    # Define the relationship (self-referential)
    parent = db.relationship('Entity', remote_side=[id], backref=db.backref('children', lazy='dynamic'))