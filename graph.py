import numpy as np
import cv2
import matplotlib as plt
import json
from tqdm import tqdm
from layout import update_layout
from config import *


class MovieGraph:
  def __init__(self, movies, actors, directors):
    self.movies = movies
    self.actors = actors
    self.directors = directors
    self.N = len(self.movies) + len(self.actors) + len(self.directors)
    np.random.seed(960822)
    self.positions_all = np.random.uniform(size=[self.N, 2])

    self.max_step = 1e-2
    self.min_step = 1e-4
    self.current_step = self.max_step
    self.decay = 0.99

    self.movie_half_life = 2592000 * 6 # months

    self.N_selected = None
    self.movies_selected = None
    self.actors_selected = None
    self.directors_selected = None
    self.positions_selected = None
    self.edges_selected = None
    self.edges_selected_uniform_id = None
    self.id_uniform_to_selected = None
    self.id_selected_to_uniform = None

    self.pin_id = None
    self.pin_pos

    self.set_range(0, 1576243793)

  def set_range(self, date_min, date_max):
    self.current_step = min(self.max_step, self.current_step * 1.1)

    self.id_selected_to_uniform = {}
    self.id_uniform_to_selected = {}
    self.N_selected = 0

    self.movies_selected = []
    for m in self.movies.values():
      if m.date < date_min:
        m.size = 0.5 ** ((date_min - m.date) / self.movie_half_life)
      elif m.date > date_max:
        m.size = 0.5 ** ((m.date - date_max) / self.movie_half_life)
      else:
        m.size = 1
        self.movies_selected.append(m.id)

    for m_id in self.movies_selected:
      self.id_selected_to_uniform[self.N_selected] = m_id
      self.id_uniform_to_selected[m_id] = self.N_selected
      self.N_selected += 1

    self.actors_selected = []
    for m_id in self.movies_selected:
      for a in self.movies[m_id].cast.values():
        if a.id not in self.id_uniform_to_selected.keys():
          self.id_selected_to_uniform[self.N_selected] = a.id
          self.id_uniform_to_selected[a.id] = self.N_selected
          self.actors_selected.append(a.id)
          self.N_selected += 1

    self.directors_selected = []
    for m_id in self.movies_selected:
      for d in self.movies[m_id].director.values():
        if d.id not in self.id_uniform_to_selected.keys():
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

  def pin(self, node_id):
    self.pin_id = node_id
    self.pin_pos = self.positions_all[node_id].copy()

  def unpin(self):
    self.pin_id = None

  def update(self, step=None):
    if self.positions_selected.shape[0] <= 0:
      return
    if step is None:
      step = self.current_step
      self.current_step = max(self.current_step * self.decay, self.min_step)
    self.positions_selected = \
      update_layout(self.positions_selected, self.edges_selected, step)
    self.positions_all[
      self.movies_selected + self.actors_selected + self.directors_selected
    ] = self.positions_selected
    if self.pin_id is not None:
      self.positions_all[self.pin_id] = self.pin_pos.copy()

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
    return self.edges_selected_uniform_id

  def export_movie_weights(self):
    return {k: v.size for k, v in self.movies.items()}

  def export_actor_scores(self):
    data = {
      a.id: {k: 0.0 for k in SCORE_ATTRIBUTES} for a in self.actors.values()
    }
    for m in self.movies.values():
      for x in m.cast.values():
        for k in SCORE_ATTRIBUTES:
          data[x.id][k] += m.size * m.attributes[k]

    return data

  def export_director_scores(self):
    data = {
      a.id: {k: 0.0 for k in SCORE_ATTRIBUTES} for a in self.directors.values()
    }
    for m in self.movies.values():
      for x in m.director.values():
        for k in SCORE_ATTRIBUTES:
          data[x.id][k] += m.size * m.attributes[k]

    return data
