from ..db import db

class Link(db.Model):
  __tablename__ ='Link'
  id = db.Column(db.Integer, primary_key=True)
  name = db.Column(db.String(255), unique=True, nullable=False)
  url = db.Column(db.Text, nullable=False)

  def __init__(self, name, url):
    self.name = name
    self.url = url

  def __repr__(self):
    return '<Link %r>' % self.name

  @property
  def serialize(self):
    """Return object data in easily serializable format"""
    return {
      'id': self.id,
      'name': self.name,
      'url': self.url
    }