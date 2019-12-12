MOVIE_NODE_FILE = './data/movieNode_1206.csv'
ACTOR_NODE_FILE = './data/castNode_simplified.csv'
DIRECTOR_NODE_FILE = './data/directorNode.csv'

MOVIE_ATTRIBUTES = {
  'budget', 'genres', 'id', 'popularity',
  'release_date', 'revenue', 'runtime', 'title',
  'tagline', 'vote_average', 'vote_count'
}

MOVIE_POP_THRES = 100 # slightly less than 10% -> ~500 movies
ACTOR_MOVIE_THRES = 10 # slightly less than 10% -> ~500 movies
DIRECTOR_MOVIE_THRES = 0

ACTOR_ATTRIBUTES = {'id', 'name', 'gender', 'movie_id'}
DIRECTOR_ATTRIBUTES = {'id', 'name', 'gender', 'movie_id'}
