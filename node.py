import numpy as np
import time
import datetime


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
    self.weight = 1.0

    self.director = {}
    self.cast = {}

  def crew(self):
    return self.director + self.cast


class Participant:
  def __init__(self, attributes={}):
    self.attributes = attributes.copy()
    self.id = attributes.get('id', None)
    self.attributes.pop('id')

    self.movies = {}
