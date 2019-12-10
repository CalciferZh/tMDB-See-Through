import pandas
import numpy as np
from config import *
import matplotlib.pyplot as plt


def movie_inspect():
  data = np.array(pandas.read_csv(MOVIE_NODE_FILE)['popularity'])
  threshold = np.percentile(data, 90)
  print(threshold)
  plt.hist(data, bins=500)
  plt.savefig('movie_popularity.png')
  plt.title('Movie Popularity Distribution')
  plt.xlabel('popularity')
  plt.ylabel('count')
  plt.show()


if __name__ == '__main__':
  movie_inspect()
