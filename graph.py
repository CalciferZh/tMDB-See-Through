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
    self.positions_all = np.random.uniform(size=[self.N, 2]) * 2 - 0.5

    self.genre_nodes = np.array([[0.5, 0.5]])

    self.max_step = 1e-2
    self.min_step = 1e-4
    self.current_step = self.max_step
    self.decay = 0.992
    self.reset_step = True

    self.movie_half_life = 2592000 * 6 # months

    self.N_selected = None
    self.movies_selected = None
    self.actors_selected = None
    self.directors_selected = None
    self.positions_selected = None
    self.edges_selected = None
    self.edges_selected_uniform_id = None
    self.genre_edges_selected = None
    self.id_uniform_to_selected = None
    self.id_selected_to_uniform = None
    self.date_min = None
    self.data_max = None
    self.node_weights = {}

    self.pin_id = None
    self.pin_pos = None

    self.set_range(0, 1576243793)

    self.related = {}
    for m in self.movies.values():
      for x in m.participants.values():
        self.related[x.id] = set([m.id, x.id])
      for a in m.participants.values():
        for b in m.participants.values():
          self.related[a.id].add(b.id)
          self.related[b.id].add(a.id)

  def set_range(self, date_min, date_max):
    self.reset_step = True
    self.date_min = date_min
    self.date_max = date_max
    self.date_mid = (self.date_max + self.date_min) / 2
    self.window_size = (self.date_max - self.date_min) / 2

    self.id_selected_to_uniform = {}
    self.id_uniform_to_selected = {}
    self.N_selected = 0

    self.movies_selected = []
    self.node_weights = {}
    for m in self.movies.values():
      if m.date < date_min:
        self.node_weights[m.id] = 0
      elif m.date > date_max:
        self.node_weights[m.id] = 0
      else:
        x = 1 - abs(m.date - self.date_mid) / self.window_size
        s = 5
        self.node_weights[m.id] = np.log(x * (np.e ** s - 1) + 1) / s
        self.movies_selected.append(m.id)
      for a in m.cast.values():
        if a.id in self.node_weights.keys():
          self.node_weights[a.id] = \
            max(self.node_weights[m.id], self.node_weights[a.id])
        else:
          self.node_weights[a.id] = self.node_weights[m.id]
      for d in m.directors.values():
        if d.id in self.node_weights.keys():
          self.node_weights[d.id] = \
            max(self.node_weights[m.id], self.node_weights[d.id])
        else:
          self.node_weights[d.id] = self.node_weights[m.id]

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
      for d in self.movies[m_id].directors.values():
        if d.id not in self.id_uniform_to_selected.keys():
          self.id_selected_to_uniform[self.N_selected] = d.id
          self.id_uniform_to_selected[d.id] = self.N_selected
          self.directors_selected.append(d.id)
          self.N_selected += 1

    self.positions_selected = self.positions_all[
      self.movies_selected + self.actors_selected + self.directors_selected
    ]

    self.actor_scores = {
      a.id: {k: 1e-8 for k in SCORE_ATTRIBUTES} for a in self.actors.values()
    }
    self.director_scores = {
      a.id: {k: 1e-8 for k in SCORE_ATTRIBUTES} for a in self.directors.values()
    }
    for m in self.movies.values():
      for x in m.cast.values():
        for k in SCORE_ATTRIBUTES:
          self.actor_scores[x.id][k] += \
            self.node_weights[m.id] * m.attributes[k]
      for x in m.directors.values():
        for k in SCORE_ATTRIBUTES:
          self.director_scores[x.id][k] += \
            self.node_weights[m.id] * m.attributes[k]

    for v in self.actor_scores.values():
      for k in SCORE_ATTRIBUTES:
        if k != 'movie_count':
          if k == 'vote_average':
            v[k] /= v['movie_count']
          else:
            v[k] /= (self.window_size / (7 * 24 * 60 * 60))
    for v in self.director_scores.values():
      for k in SCORE_ATTRIBUTES:
        if k != 'movie_count':
          if k == 'vote_average':
            v[k] /= v['movie_count']
          else:
            v[k] /= (self.window_size / (7 * 24 * 60 * 60))

    self.edges_selected = []
    self.edges_selected_uniform_id = []
    for m_id in self.movies_selected:
      for a in self.movies[m_id].cast.values():
        self.edges_selected_uniform_id.append([m_id, a.id])
        self.edges_selected.append([
          self.id_uniform_to_selected[m_id], self.id_uniform_to_selected[a.id]
        ])
      for d in self.movies[m_id].directors.values():
        self.edges_selected_uniform_id.append([m_id, d.id])
        self.edges_selected.append([
          self.id_uniform_to_selected[m_id], self.id_uniform_to_selected[d.id]
        ])
    self.edges_selected = np.array(self.edges_selected, dtype=np.int32)

    self.genre_edges_selected = []
    for m_id in self.movies_selected:
      for g_id in self.movies[m_id].main_genres:
        self.genre_edges_selected.append([self.id_uniform_to_selected[m_id], g_id])
    self.genre_edges_selected = \
      np.array(self.genre_edges_selected, dtype=np.int32)

  def pin(self, node_id):
    self.pin_pos = self.positions_all[node_id].copy()
    self.pin_id = node_id
    for m in self.movies.values():
      if m.id not in self.related[self.pin_id]:
        self.node_weights[m.id] = 0
    for a in self.actors.values():
      if a.id not in self.related[self.pin_id]:
        self.node_weights[a.id] = 0
    for a in self.directors.values():
      if a.id not in self.related[self.pin_id]:
        self.node_weights[a.id] = 0

  def unpin(self):
    self.pin_id = None

  def update(self):
    if self.positions_selected.shape[0] <= 0:
      return
    if self.reset_step:
      self.reset_step = False
      self.current_step = self.max_step
    step = self.current_step
    self.current_step = max(self.current_step * self.decay, self.min_step)
    self.positions_selected = update_layout(
      self.positions_selected, self.edges_selected,
      self.genre_nodes, self.genre_edges_selected,
      step
    )
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

  def export_node_weights(self):
    return self.node_weights

  def export_actor_scores(self):
    return self.actor_scores

  def export_director_scores(self):
    return self.director_scores
