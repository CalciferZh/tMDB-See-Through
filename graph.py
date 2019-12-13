import numpy as np
import cv2
import matplotlib as plt
import json
from tqdm import tqdm
from math_utils import *


class MovieGraph:
  def __init__(self, movies, actors, directors):
    self.movies = movies
    self.actors = actors
    self.directors = directors
    self.N = len(self.movies) + len(self.actors) + len(self.directors)
    np.random.seed(960822)
    self.positions_all = np.random.uniform(size=[self.N, 2])

    self.default_step = 2e-3
    self.current_step = self.default_step
    self.default_decay = 1

    self.N_selected = None
    self.movies_selected = None
    self.actors_selected = None
    self.directors_selected = None
    self.positions_selected = None
    self.edges_selected = None
    self.edges_selected_uniform_id = None
    self.id_uniform_to_selected = None
    self.id_selected_to_uniform = None

    self.set_range(0, 99999999)

  def set_range(self, date_min, date_max):
    self.current_step = self.default_step

    self.id_selected_to_uniform = {}
    self.id_uniform_to_selected = {}
    self.N_selected = 0

    self.movies_selected = \
      [m.id for m in self.movies.values() \
        if m.date >= date_min and m.date <= date_max]

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
    self.edges_selected_uniform_id = []
    for m_id in self.movies_selected:
      for a in self.movies[m_id].cast.values():
        self.edges_selected_uniform_id.append([m_id, a.id])
        self.edges_selected.append([
          self.id_uniform_to_selected[m_id], self.id_uniform_to_selected[a.id]
        ])
      for d in self.movies[m_id].director.values():
        self.edges_selected_uniform_id.append([m_id, d.id])
        self.edges_selected.append([
          self.id_uniform_to_selected[m_id], self.id_uniform_to_selected[d.id]
        ])
    self.edges_selected = np.array(self.edges_selected, dtype=np.int32)

  def update(self, step=None):
    if self.positions_selected.shape[0] <= 0:
      return
    if step is None:
      step = self.current_step
      self.current_step *= self.default_decay
    update_layout(self.positions_selected, self.edges_selected, step)
    self.positions_all[
      self.movies_selected + self.actors_selected + self.directors_selected
    ] = self.positions_selected
    self.positions_all = np.clip(self.positions_all, 0, 1)

  def export_movies(self):
    s = json.dumps({k: v.attributes for k, v in self.movies.items()})
    return s

  def export_actors(self):
    s = json.dumps({k: v.attributes for k, v in self.actors.items()})
    return s

  def export_directors(self):
    s = json.dumps({k: v.attributes for k, v in self.directors.items()})
    return s

  def export_positions(self):
    s = json.dumps(
      {k: [self.positions_all[k][0], self.positions_all[k][1]] \
        for k in range(self.N)}
    )
    return s

  def export_selected_edges(self):
    s = json.dumps(self.edges_selected_uniform_id)
    return s
