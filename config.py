MOVIE_NODE_FILE = './data/movieNode_1206.csv'
ACTOR_NODE_FILE = './data/castNode_simplified.csv'
DIRECTOR_NODE_FILE = './data/directorNode.csv'

MOVIE_ATTRIBUTES = {
  'budget', 'genres', 'id', 'popularity',
  'release_date', 'revenue', 'runtime', 'title',
  'vote_average', 'vote_count', 'tagline'
}

MOVIE_POP_THRES = 90 # slightly less than 10% -> ~500 movies
MOVIE_YEAR_THRES = 2005
ACTOR_MOVIE_THRES = 10 # slightly less than 10% -> ~500 movies
DIRECTOR_MOVIE_THRES = 0

ACTOR_ATTRIBUTES = {'id', 'name', 'gender', 'movie_id'}
DIRECTOR_ATTRIBUTES = {'id', 'name', 'gender', 'movie_id'}

SCORE_ATTRIBUTES = [
  'budget', 'popularity', 'revenue', 'runtime', 'vote_average', 'vote_count'
]

PKL_SAVE_PATH = './data/nodes_all_in_one.pkl'
