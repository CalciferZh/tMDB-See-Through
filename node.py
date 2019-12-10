import numpy as np


class Movie:
  def __init__(self, attributes={}):
    self.attributes = attributes
    self.id = attributes.get('id', None)
    self.director = {}
    self.cast = {}
    self.pos = np.random.uniform(size=[2])

  def crew(self):
    return self.director + self.cast


class Participant:
  def __init__(self, attributes={}):
    self.attributes = attributes
    self.id = attributes.get('id', None)
    self.pos = np.random.uniform(size=[2])
    self.movies = {}
