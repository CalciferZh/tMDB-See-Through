from data import load_data
from graph import MovieGraph
from tqdm import tqdm
import numpy as np
import cv2
import json
import time
import datetime
from vctoolkit import VideoWriter
from vctoolkit import imshow
from vctoolkit import imresize


def draw_graph(nodes, edges, size, padding=0.1):
  r = size // 128
  padding = np.round(padding * size).astype(np.int32)
  canvas = np.ones([size + padding * 2, size + padding * 2, 3], dtype=np.uint8)
  canvas *= 255
  for e in edges:
    n1 = (
      np.round(nodes[str(e[0])][0] * size + padding).astype(np.int32),
      np.round(nodes[str(e[0])][1] * size + padding).astype(np.int32)
    )
    n2 = (
      np.round(nodes[str(e[1])][0] * size + padding).astype(np.int32),
      np.round(nodes[str(e[1])][1] * size + padding).astype(np.int32)
    )
    cv2.line(canvas, n1, n2, (0, 0, 255), r // 4)
    cv2.circle(canvas, n1, r, (255, 0, 0), -1)
    cv2.circle(canvas, n2, r, (255, 0, 0), -1)
  canvas = imresize(canvas, (size, size))
  return canvas


def set_range_speed_test():
  movies, actors, directors = load_data()
  graph = MovieGraph(movies, actors, directors)
  for _ in tqdm(list(range(1000)), ascii=True):
    date_min = np.random.randint(20050101)
    date_max = np.random.randint(date_min, 20151231)
    graph.set_range(date_min, date_max)
    data = {
      'movie_weights': graph.export_movie_weights(),
      'actor_scores': graph.export_actor_scores(),
      'director_scores': graph.export_director_scores(),
      'edges': graph.export_selected_edges()
    }
    json.dumps(data)


def graph_dump_data_test():
  movies, actors, directors = load_data()
  graph = MovieGraph(movies, actors, directors)
  graph.set_range(
    time.mktime(
      datetime.datetime.strptime('20100101', '%Y%m%d').timetuple()
    ),
    time.mktime(
      datetime.datetime.strptime('20140101', '%Y%m%d').timetuple()
    )
  )
  data = {
    'movie_weights': graph.export_movie_weights(),
    'actor_scores': graph.export_actor_scores(),
    'director_scores': graph.export_director_scores(),
    'edges': graph.export_selected_edges()
  }
  s = json.dumps(data)
  with open('./test.json', 'w') as f:
    f.write(s)
  exit(0)


def graph_usage_example():
  movies, actors, directors = load_data()
  graph = MovieGraph(movies, actors, directors)
  graph.set_range(
    time.mktime(
      datetime.datetime.strptime('20050101', '%Y%m%d').timetuple()
    ),
    time.mktime(
      datetime.datetime.strptime('20200101', '%Y%m%d').timetuple()
    )
  )
  render_size = 512

  writer = VideoWriter('./layout.mp4', render_size, render_size, 60)

  for _ in tqdm(list(range(1000)), ascii=True):
    graph.update()
    edges = graph.export_selected_edges()
    positions = json.loads(graph.export_positions())
    frame = draw_graph(positions, edges, render_size)
    writer.write_frame(frame)
  writer.close()


if __name__ == '__main__':
  graph_usage_example()
