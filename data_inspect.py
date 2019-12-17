import pandas
import numpy as np
import ast
from config import *
import matplotlib.pyplot as plt


def movie_popularity_inspect():
  data = np.array(pandas.read_csv(MOVIE_NODE_FILE)['popularity'])
  threshold = np.percentile(data, 90)
  print(threshold)
  plt.hist(data, bins=500)
  plt.savefig('movie_popularity.png')
  plt.title('Movie Popularity Distribution')
  plt.xlabel('popularity')
  plt.ylabel('count')
  plt.show()


def movie_vote_count_inspect():
  data = np.array(pandas.read_csv(MOVIE_NODE_FILE)['vote_count'])
  threshold = np.percentile(data, 90)
  print(threshold)
  plt.hist(data, bins=500)
  plt.savefig('movie_vote_count.png')
  plt.title('Movie Vote Count Distribution')
  plt.xlabel('vote_count')
  plt.ylabel('count')
  plt.show()


def actor_inspect():
  data = \
    [len(r.split(',')) for r in pandas.read_csv(ACTOR_NODE_FILE)['movie_id']]
  threshold = np.percentile(data, 90)
  print(threshold)
  plt.hist(data, bins=100)
  plt.savefig('actor_movies.png')
  plt.title('Number of Movies for Actors')
  plt.xlabel('movie number')
  plt.ylabel('actor number')
  plt.show()


def genre_inspect():
  data = pandas.read_csv(MOVIE_NODE_FILE)['genres']
  genre_cnt = {}
  for r in data:
    for g in ast.literal_eval(r):
      if g in genre_cnt.keys():
        genre_cnt[g] += 1
      else:
        genre_cnt[g] = 1

  for x in list(sorted(genre_cnt.items(), key=lambda x: x[1])):
    print(x)

  plt.pie(list(genre_cnt.values()), labels=list(genre_cnt.keys()))
  plt.show()


if __name__ == '__main__':
  movie_vote_count_inspect()
