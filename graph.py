import numpy as np
import cv2
import matplotlib as plt
from tqdm import tqdm
from math_utils import *


class MovieGraph:
  def __init__(self, movies, actors, directors):
    self.movies = movies
    self.actors = actors
    self.directors = directors
    self.N = len(self.movies) + len(self.actors) + len(self.directors)
    self.year_min = 9999
    self.year_max = -1
    self.year_index = {}
    for m in movies.values():
      year = int(m.attributes['release_date'].split('-')[0])
      if year in self.year_index.keys():
        self.year_index[year].append(m)
      else:
        self.year_index[year] = [m]
      self.year_max = max(year, self.year_max)
      self.year_min = min(year, self.year_min)
    np.random.seed(960822)
    self.positions_all = np.random.uniform(size=[self.N, 2])

    self.N_selected = None
    self.movies_selected = None
    self.actors_selected = None
    self.directors_selected = None
    self.positions_selected = None
    self.edges_selected = None
    self.id_uniform_to_selected = None
    self.id_selected_to_uniform = None

  def set_range(self, year_min, year_max):
    self.id_selected_to_uniform = {}
    self.id_uniform_to_selected = {}
    self.N_selected = 0

    self.movies_selected = [
      m.id for m in sum(
        [v for k, v in self.year_index.items() if k >= year_min and k <= year_max],
        []
      )
    ]
    for m_id in self.movies_selected:
      self.id_selected_to_uniform[self.N_selected] = m_id
      self.id_uniform_to_selected[m_id] = self.N_selected
      self.N_selected += 1

    self.actors_selected = []
    for m_id in self.movies_selected:
      for a in self.movies[m_id].cast.values():
        if a.id in self.id_uniform_to_selected.keys():
          continue
        self.id_selected_to_uniform[self.N_selected] = a.id
        self.id_uniform_to_selected[a.id] = self.N_selected
        self.actors_selected.append(a.id)
        self.N_selected += 1

    self.directors_selected = []
    for m_id in self.movies_selected:
      for d in self.movies[m_id].director.values():
        if d.id in self.id_uniform_to_selected.keys():
          continue
        self.id_selected_to_uniform[self.N_selected] = d.id
        self.id_uniform_to_selected[d.id] = self.N_selected
        self.directors_selected.append(d.id)
        self.N_selected += 1

    self.positions_selected = self.positions_all[
      self.movies_selected + self.actors_selected + self.directors_selected
    ]

    self.edges_selected = []
    for m_id in self.movies_selected:
      for a in self.movies[m_id].cast.values():
        self.edges_selected.append([
          self.id_uniform_to_selected[m_id], self.id_uniform_to_selected[a.id]
        ])
      for d in self.movies[m_id].director.values():
        self.edges_selected.append([
          self.id_uniform_to_selected[m_id], self.id_uniform_to_selected[d.id]
        ])
    self.edges_selected = np.array(self.edges_selected, dtype=np.int32)

  def update(self, step):
    update_layout(self.positions_selected, self.edges_selected, step)
    self.positions_all[
      self.movies_selected + self.actors_selected + self.directors_selected
    ] = self.positions_selected
    return self.positions_all
