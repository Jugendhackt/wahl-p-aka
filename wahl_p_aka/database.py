from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import Integer, String, Column, DateTime, Text, ForeignKey, Table, Float
from sqlalchemy.orm import relationship

from wahl_p_aka import app

app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)


class Party(db.Model):
    id = Column(Integer, primary_key=True)
    full_name = Column(String(255))
    short_name = Column(String(255))
    aw_id = Column(Integer, unique=True)
    politicians = relationship("Politician", back_populates="party")
    votes = relationship("PartyVote", back_populates="party")


class Politician(db.Model):
    id = Column(Integer, primary_key=True)
    first_name = Column(String(255))
    last_name = Column(String(255))
    aw_id = Column(Integer)
    constituency_id = Column(Integer, ForeignKey('constituency.id'))
    constituency = relationship("Constituency", back_populates="politicians")
    party_id = Column(Integer, ForeignKey('party.id'))
    party = relationship("Party", back_populates="politicians")
    votes = relationship("PoliticianVote", back_populates="politician")


class Constituency(db.Model):
    id = Column(Integer, primary_key=True)
    state = Column(String(255))
    politicians = relationship('Politician', back_populates="constituency")


poll_poll_topic_association_table = Table(
    'poll_poll_topic_association_table',
    db.Model.metadata,
    Column('poll_id', Integer, ForeignKey('poll.id')),
    Column('poll_topic_id', Integer, ForeignKey('poll_topic.id'))
)


class PollTopic(db.Model):
    id = Column(Integer, primary_key=True)
    name = Column(String(255))
    aw_id = Column(Integer)
    parent_id = Column(Integer, ForeignKey('poll_topic.id'))
    parent = relationship("PollTopic", back_populates="children", remote_side=[id])
    children = relationship("PollTopic", back_populates="parent")


class Poll(db.Model):
    id = Column(Integer, primary_key=True)
    topics = relationship("PollTopic", secondary=poll_poll_topic_association_table)
    aw_id = Column(Integer, unique=True)
    date = Column(DateTime)
    title = Column(String(255))
    abstract = Column(Text)
    politician_votes = relationship('PoliticianVote')
    party_votes = relationship('PartyVote')


class PoliticianVote(db.Model):
    id = Column(Integer, primary_key=True)
    politician_id = Column(Integer, ForeignKey('politician.id'))
    politician = relationship('Politician', back_populates="votes")
    poll_id = Column(Integer, ForeignKey('poll.id'))
    poll = relationship('Poll', back_populates="politician_votes")
    vote = Column(String(255))


class PartyVote(db.Model):
    id = Column(Integer, primary_key=True)
    party_id = Column(Integer, ForeignKey('party.id'))
    party = relationship('Party', back_populates="votes")
    poll_id = Column(Integer, ForeignKey('poll.id'))
    poll = relationship('Poll', back_populates="party_votes")
    percent_yes = Column(Float)
    percent_no = Column(Float)
    percent_abstain = Column(Float)
    percent_absent = Column(Float)


db.create_all()
