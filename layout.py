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


def update_layout(positions, edges, anchors, anchor_edges, step,
                  anchor_strength=1.0, density=1.0):
  """
  Update graph layout with node positions and virtual nodes (anchors).

  Parameters
  ----------
  positions : np.ndarray
    Node positions.
  edges : np.ndarray
    Node edges.
  anchors : np.ndarray
    Anchor positions.
  anchor_edges : np.ndarray
    Edges from nodes to anchors. The order should be (node_id, anchor_id).
  step : float
    Update step length.
  anchor_strength : float
    Anchor attractive force strength.
  density : float
    How "dense" the layout should be. `density` will be multiplied to attractive
    forces directly, and `1 / density` will be multiplied to the repulsive force.

  Returns
  -------
  np.ndarray
    Updated node positions.
  """
  delta = np.expand_dims(positions, 0) - np.expand_dims(positions, 1)
  dist = np.linalg.norm(delta, axis=-1, keepdims=True)
  dist += np.finfo(np.float32).eps # avoid divide-by-zero
  # repulsive
  pos_disp = np.sum(delta / dist * force_repulsive(dist), axis=1) / density

  # attractive from other nodes
  e_start = positions[edges[:, 0]]
  e_end = positions[edges[:, 1]]
  delta = e_start - e_end
  dist = np.linalg.norm(delta, axis=-1, keepdims=True)
  dist += np.finfo(np.float32).eps
  disp = delta / dist * force_attractive(dist) * density
  for e, d in zip(edges, disp):
    pos_disp[e[0]] -= d
    pos_disp[e[1]] += d

  # attractive from anchors
  e_start = positions[anchor_edges[:, 0]]
  e_end = anchors[anchor_edges[:, 1]]
  delta = e_start - e_end
  dist = np.linalg.norm(delta, axis=-1, keepdims=True)
  dist += np.finfo(np.float32).eps
  disp = delta / dist * force_attractive(dist) * anchor_strength
  for e, d in zip(anchor_edges, disp):
    pos_disp[e[0]] -= d

  # update
  norm = np.linalg.norm(pos_disp, axis=-1, keepdims=True)
  norm += np.finfo(np.float32).eps
  positions += pos_disp / norm * np.minimum(norm, step)
  return positions
