import numpy as np
from vctoolkit import Timer


def force_repulsive(dist):
  """
  Repulsive force between nodes.

  Parameters
  ----------
  dist : np.ndarray, [N, N, 1]
    Distance between nodes.
  area : int, optional
    Area of the layout space, by default 1

  Returns
  -------
  force_repulsive : np.ndarray, [N, N, 1]
    Repulsive force between nodes.
  """
  k_squared = 1 / dist.shape[0]
  fr = -k_squared / dist
  return fr


def force_attractive(dist):
  """
  Attractive force between edges.

  Parameters
  ----------
  dist : np.ndarray, [E, 1]
    Distance between nodes of each edge
  area : int, optional
    Area of layout space, by default 1

  Returns
  -------
  force_attractive : np.ndarray, [E, 1]
    Attractive forces between nodes.
  """
  k = np.sqrt(1 / dist.shape[0])
  fa = np.square(dist) / k
  return fa


def update_layout(positions, edges, step, gravity=0.2, verbose=False):
  n_points = positions.shape[0]
  n_edges = edges.shape[0]

  delta = np.expand_dims(positions, 0) - np.expand_dims(positions, 1)
  dist = np.linalg.norm(delta, axis=-1, keepdims=True)
  dist += np.finfo(np.float32).eps # avoid divide-by-zero
  pos_disp = np.sum(delta / dist * force_repulsive(dist), axis=1)

  # add a fake point
  positions = np.concatenate([positions, np.array([[.5, .5]])], 0)

  # attractive
  e_start = positions[list(edges[:, 0]) + [n_points] * n_points]
  e_end = positions[list(edges[:, 1]) + list(range(n_points))]
  delta = e_start - e_end
  dist = np.linalg.norm(delta, axis=-1, keepdims=True)
  dist += np.finfo(np.float32).eps
  disp = delta / dist * force_attractive(dist)
  for e, d in zip(edges, disp[:n_edges]):
    pos_disp[e[0]] -= d
    pos_disp[e[1]] += d
  pos_disp += disp[n_edges:] * gravity

  # update
  norm = np.linalg.norm(pos_disp, axis=-1, keepdims=True)
  norm += np.finfo(np.float32).eps
  positions = positions[:-1] + pos_disp / norm * np.minimum(norm, step)
  return positions
