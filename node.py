import numpy as np


class Movie:
  def __init__(self, attributes={}):
    self.attributes = attributes.copy()
    self.id = attributes.get('id', None)
    self.attributes.pop('id')

    self.director = {}
    self.cast = {}

    self.pos = np.random.uniform(size=[2])

  def crew(self):
    return self.director + self.cast


class Participant:
  def __init__(self, attributes={}):
    self.attributes = attributes.copy()
    self.id = attributes.get('id', None)
    self.attributes.pop('id')

    self.movies = {}

    self.pos = np.random.uniform(size=[2])
