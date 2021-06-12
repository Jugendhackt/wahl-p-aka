from flask_sqlalchemy import SQLAlchemy
from sqlalchemy.orm import relationship

from wahl_p_aka import app

db = SQLAlchemy(app)


class Party(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    full_name = db.Column(db.String(255))
    short_name = db.Column(db.String(255))
    aw_id = db.Column(db.Integer)
    politicians = relationship("Politician", back_populates="party")
    votes = relationship("PartyVote", back_populates="party")


class Politician(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    first_name = db.Column(db.String(255))
    last_name = db.Column(db.String(255))
    aw_id = db.Column(db.Integer)
    constituency_id = db.Column(db.Integer, db.ForeignKey('constituency.id'))
    constituency = relationship("Constituency", back_populates="politicians")
    party_id = db.Column(db.Integer, db.ForeignKey('party.id'))
    party = relationship("Party", back_populates="politicians")
    votes = relationship("PoliticianVote", back_populates="politician")


class Constituency(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    state = db.Column(db.String(255))
    politicians = relationship('Politician', back_populates="constituency")


class Poll(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    topic = db.Column(db.String)
    date = db.Column(db.DateTime)
    title = db.Column(db.String(255))
    abstract = db.Column(db.Text)
    politician_votes = relationship('PoliticianVote')
    party_votes = relationship('PartyVote')


class PoliticianVote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    politician_id = db.Column(db.Integer, db.ForeignKey('politician.id'))
    politician = relationship('Politician', back_populates="votes")
    poll_id = db.Column(db.Integer, db.ForeignKey('poll.id'))
    poll = relationship('Poll', back_populates="politician_votes")
    vote = db.Column(db.String(255))


class PartyVote(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    party_id = db.Column(db.Integer, db.ForeignKey('party.id'))
    party = relationship('Party', back_populates="votes")
    poll_id = db.Column(db.Integer, db.ForeignKey('poll.id'))
    poll = relationship('Poll', back_populates="party_votes")
    vote = db.Column(db.String(255))
