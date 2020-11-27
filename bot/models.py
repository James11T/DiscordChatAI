from bot.config import config

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine
from sqlalchemy import Column, Integer, String

import nltk
import random

DATABASE_PROTOCOL = config["DB_PROTOCOL"]
DATABASE_USERNAME = config["DB_USERNAME"]
DATABASE_PASSWORD = config["DB_PASSWORD"]
DATABASE_IP = config["DB_IP"]
DATABASE_NAME = config["DB_NAME"]

Base = declarative_base()


class Statement(Base):
    """Represents AI knowledge"""
    __tablename__ = "statement"
    id = Column(Integer, primary_key=True, autoincrement=True)
    text = Column(String(255), nullable=False)
    in_response_to = Column(String(255), nullable=False)
    personality = Column(String(64), nullable=False, default="normal")


class ChatBot:
    def __init__(self, min_similarity, max_similarity):
        self.engine = None
        self.session = None
        self.connected = False
        self.min_similarity = min_similarity
        self.max_similarity = max_similarity

    @staticmethod
    def dist(s1, s2):
        return 1 - (nltk.edit_distance(s1, s2) / max(len(s1), len(s2)))

    def is_valid(self, s1, s2):
        return self.min_similarity <= self.dist(s1, s2) <= self.max_similarity

    def connect(self):
        self.engine = create_engine(
            f"{DATABASE_PROTOCOL}://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_IP}/{DATABASE_NAME}"
        )
        self.session = sessionmaker(bind=self.engine)()
        self.connected = True

    def get_response(self, personality, in_text):
        if not self.connected:
            return "The database is not currently connected"

        statements = self.session.query(Statement).filter_by(personality=personality)
        similar_queries = [s.text for s in statements if self.is_valid(s.in_response_to, in_text)]

        if len(similar_queries) > 0:
            return random.choice(similar_queries)
        else:
            return in_text

    def learn_response(self, personality, in_text, good_response):
        if not self.connected:
            return
        new_statement = Statement(text=good_response, in_response_to=in_text, personality=personality)
        self.session.add(new_statement)
        self.session.commit()

    def get_personality_entries(self, personality):
        if not self.connected:
            return []
        return self.session.query(Statement).filter_by(personality=personality).all()


