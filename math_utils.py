import numpy as np
from vctoolkit import Timer


def force_repulsive(dist, area=1):
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
  k_squared = area / dist.shape[0]
  fr = -k_squared / dist
  return fr


def force_attractive(dist, area=1):
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
  k = np.sqrt(area / dist.shape[0])
  fa = np.square(dist) / k
  return fa


def update_layout(positions, edges, step, centralize=0.5, verbose=False):
  timer = Timer()

  timer.tic()
  delta = np.expand_dims(positions, 0) - np.expand_dims(positions, 1)
  dist = np.linalg.norm(delta, axis=-1, keepdims=True)
  dist += np.finfo(np.float32).eps # avoid divide-by-zero
  pos_disp = \
    np.sum(delta / dist * force_repulsive(dist, area=centralize**2), axis=1)

  # attractive
  e_start = positions[edges[:, 0]] # E x 2
  e_end = positions[edges[:, 1]]
  delta = e_start - e_end
  dist = np.linalg.norm(delta, axis=-1, keepdims=True)
  dist += np.finfo(np.float32).eps
  disp = \
    delta / dist * force_attractive(dist, area=centralize**2)
  for e, d in zip(edges, disp):
    pos_disp[e[0]] -= d
    pos_disp[e[1]] += d

  # update
  norm = np.linalg.norm(pos_disp, axis=-1, keepdims=True)
  norm += np.finfo(np.float32).eps
  positions += pos_disp / norm * np.minimum(norm, step)
  positions = np.clip(positions, 0, 1)
  return positions
