import pandas
from node import *
from config import *
from tqdm import tqdm


def load_actor():
  data = pandas.read_csv(ACTOR_NODE_FILE)[ACTOR_ATTRIBUTES]
  actors = {}
  for d in data.iterrows():
    row = d[1].to_dict()
    actors[row['id']] = Participant(row)
  return actors


def load_director():
  data = pandas.read_csv(DIRECTOR_NODE_FILE)[DIRECTOR_ATTRIBUTES]
  directors = {}
  for d in data.iterrows():
    row = d[1].to_dict()
    directors[row['id']] = Participant(row)
  return directors


def load_movie():
  data = pandas.read_csv(MOVIE_NODE_FILE)[MOVIE_ATTRIBUTES]
  movies = {}
  for d in data.iterrows():
    row = d[1].to_dict()
    if row['popularity'] < MOVIE_POP_THRES:
      continue
    movies[row['id']] = Movie(row)
  print(len(movies))
  return movies


def load_data():
  movies = load_movie()
  actors = load_actor()
  directors = load_director()



if __name__ == '__main__':
  load_data()
