import numpy as np


class Movie:
  def __init__(self, attributes={}):
    self.attributes = attributes.copy()
    self.id = attributes.get('id', None)
    self.attributes.pop('id')
    self.date = int(self.attributes['release_date'].replace('-', ''))
    self.attributes['release_date'] = self.date

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
