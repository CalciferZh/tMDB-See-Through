from data import load_data
from graph import MovieGraph
from tqdm import tqdm
import numpy as np
import cv2
from vctoolkit import VideoWriter
from vctoolkit import imshow
from vctoolkit import imresize


def draw_graph(nodes, edges, size, padding=0.1):
  r = size // 128
  padding = np.round(padding * size).astype(np.int32)
  canvas = np.ones([size + padding * 2, size + padding * 2, 3], dtype=np.uint8)
  canvas *= 255
  nodes = np.round(nodes * size).astype(np.int32)
  for e in edges:
    cv2.line(
      canvas,
      (nodes[e[0]][0] + padding, nodes[e[0]][1] + padding),
      (nodes[e[1]][0] + padding, nodes[e[1]][1] + padding),
      (0, 0, 255), r // 4
    )
  for v in nodes:
    cv2.circle(canvas, (v[0] + padding, v[1] + padding), r, (255, 0, 0), -1)
  canvas = imresize(canvas, (size, size))
  return canvas


def graph_usage_example():
  movies, actors, directors = load_data()
  graph = MovieGraph(movies, actors, directors)
  graph.set_range(0, 9999)
  step = 1e-2
  decay = 0.99
  render_size = 2048
  writer = VideoWriter('./layout.mp4', render_size, render_size, 60)

  for _ in tqdm(list(range(1000)), ascii=True):
    graph.update(step)
    step *= decay
    frame = \
      draw_graph(graph.positions_selected, graph.edges_selected, render_size)
    writer.write_frame(frame)
  writer.close()


if __name__ == '__main__':
  graph_usage_example()
