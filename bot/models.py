from bot.config import config

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
from sqlalchemy import create_engine, distinct
from sqlalchemy import Column, Integer, String

import nltk
from nltk.corpus import stopwords

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
    weight = Column(Integer, nullable=False, default=1)


def process_text(in_text):
    stop_words = stopwords.words("english")
    ns = " ".join([w for w in in_text.split(" ") if w not in stop_words])
    if len(ns) == 0:
        ns = in_text
    return ns.lower()


def dist(s1, s2):
    # Find the similarity of the two given string between 0 and 1
    return 1 - (nltk.edit_distance(s1, s2) / max(len(s1), len(s2)))


class ChatBot:
    def __init__(self, min_similarity, max_similarity):
        self.engine = None
        self.Session = None
        self.session = None
        self.connected = False
        self.min_similarity = min_similarity
        self.max_similarity = max_similarity

    def is_valid_dist(self, d):
        # Checks if the distance is acceptable
        return self.min_similarity <= d <= self.max_similarity

    def connect(self):
        # Connect to the database
        self.engine = create_engine(
            f"{DATABASE_PROTOCOL}://{DATABASE_USERNAME}:{DATABASE_PASSWORD}@{DATABASE_IP}/{DATABASE_NAME}"
        )
        self.Session = sessionmaker(bind=self.engine)
        self.connected = True

    def create_session(self):
        self.session = self.Session()

    def close_session(self):
        if self.session:
            self.session.close()

    def rollback_session(self):
        if self.session:
            self.session.rollback()

    def get_response(self, personality, in_text):
        self.create_session()
        # Generate a response based on the personality and the input
        if not self.connected:
            return "The database is not currently connected"

        # Get all responses
        statements = self.session.query(Statement).filter_by(personality=personality).all()
        self.close_session()

        if len(statements) == 0:
            # No statements
            return ""

        value_list = []
        weight_list = []

        in_text = process_text(in_text)

        for s in statements:
            get_dist = dist(s.in_response_to, in_text)
            if self.is_valid_dist(get_dist):
                value_list.append(s.text)
                weight_list.append(get_dist * s.weight)

        if len(value_list) == 0:
            # No valid similar inputs
            return ""

        # Generate a weighted random
        choice = random.choices(value_list, weights=weight_list, k=1)[0]

        return choice

    def normalise_database(self):
        self.create_session()
        # Remove repeats while adjusting weights
        done = False
        target_index = self.session.query(Statement).first().id
        final_id = self.session.query(Statement).all()[-1].id

        while not done:
            base_state = self.session.query(Statement).filter_by(id=target_index).first()
            if base_state:
                base_state.in_response_to = base_state.in_response_to.lower()
                if not base_state.weight:
                    base_state.weight = 1
                dupes = self.session.query(Statement).filter_by(text=base_state.text,
                                                                in_response_to=base_state.in_response_to).all()
                if len(dupes) > 0:
                    for dupe in dupes:
                        if dupe.id != base_state.id and dupe != base_state:
                            base_state.weight += 1
                            self.session.delete(dupe)

            if target_index > final_id:
                break
            target_index += 1
            self.session.commit()
            self.session.close()

    def learn_response(self, personality, in_text, good_response):
        if not self.connected:
            return

        self.create_session()
        try:
            in_db = self.session.query(Statement).filter_by(text=good_response, in_response_to=process_text(in_text),
                                                            personality=personality).first()
            if in_db:
                in_db.weight += 1
                self.session.commit()
            else:
                new_statement = Statement(text=good_response, in_response_to=process_text(in_text),
                                          personality=personality)
                self.session.add(new_statement)
                self.session.commit()
        except Exception as e:
            self.rollback_session()
        finally:
            self.close_session()

    def discourage_response(self, personality, in_text, bad_response):
        self.create_session()
        try:
            in_db = self.session.query(Statement).filter_by(text=bad_response, in_response_to=process_text(in_text),
                                                            personality=personality).first()
            if in_db:
                if in_db.weight > 1:
                    in_db.weight -= 1
                else:
                    self.session.delete(in_db)
                self.session.commit()
        except Exception as e:
            self.rollback_session()
        finally:
            self.close_session()

    def get_personality_entries(self, personality):
        self.create_session()
        if not self.connected:
            return []
        personality_entries = self.session.query(Statement).filter_by(personality=personality).all()
        self.close_session()
        return personality_entries

    def get_total_entries(self):
        self.create_session()
        entries = self.session.query(Statement).all()
        self.close_session()
        return len(entries)

    def get_total_personalities(self):
        self.create_session()
        entries = self.session.query(distinct(Statement.personality)).all()
        self.close_session()
        return len(entries)
