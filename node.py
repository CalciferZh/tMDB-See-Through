import numpy as np
import time
import datetime
import ast
from config import *


class Movie:
  def __init__(self, attributes={}):
    self.attributes = attributes.copy()
    self.id = attributes.get('id', None)
    self.attributes.pop('id')
    self.date = time.mktime(
      datetime.datetime.strptime(
        self.attributes['release_date'], '%Y-%m-%d'
      ).timetuple()
    )
    self.attributes['release_date'] = self.date
    self.attributes['movie_count'] = 1 # a trick for average calculation
    self.attributes['genres'] = ast.literal_eval(self.attributes['genres'])
    self.main_genres = [0]
    # self.main_genres = \
    #   [GENRES.index(g) for g in self.attributes['genres'] if g in GENRES]

    self.directors = {}
    self.cast = {}

  def crew(self):
    return self.directors + self.cast


class Participant:
  def __init__(self, attributes={}):
    self.attributes = attributes.copy()
    self.id = attributes.get('id', None)
    self.attributes.pop('id')

    self.movies = {}
