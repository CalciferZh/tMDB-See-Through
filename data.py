import pandas
from node import *
from config import *
from vctoolkit import pkl_save


def build_connections(movies, participants, role, threshold):
  """
  Build connections between movies and participants (cast and director).
  The `role` filed in the `attributes` will be constructed with corresponding
  pointers, and the nodes that are not connected to any movie will be removed.

  Parameters
  ----------
  movies : dict
    A dict of movies, with movie id as keys.
  participants : dict
    A dict of participants, with subject id as keys.
  role : str
    New key in the attributes to save the links.
  threshold : int
    Only the participants linked with more than `threshold` number of movies
    will be kept.

  Returns
  -------
  dict
    Updated `movies`.
  dict
    Updated `participants`.
  """
  linked = set()
  for m in movies.values():
    m.attributes[role] = {}
  for p in participants.values():
    movie_ids = [int(m.strip()) for m in p.attributes['movie_id'].split(',')]
    p.attributes.pop('movie_id')
    if len(movie_ids) <= threshold:
      continue
    for mid in movie_ids:
      if mid in movies.keys():
        movies[mid].attributes[role][p.id] = p
        p.movies[mid] = movies[mid]
        linked.add(p.id)
  to_pop = []
  for p in participants.keys():
    if p not in linked:
      to_pop.append(p)
  for p in to_pop:
    participants.pop(p)
  return movies, participants


def change_to_uniform_id(subjects, new_id):
  new_subjects = {}
  for old_id, v in subjects.items():
    new_subjects[new_id] = v
    v.id = new_id
    new_id += 1
  return new_subjects, new_id


def load_participant(node_file, attributs):
  """
  Load data from node file.

  Parameters
  ----------
  node_file : str
    Path to the file.
  attributs : list of str
    List of attribute names.

  Returns
  -------
  dict
    Loaded data with id as keys.
  """
  data = pandas.read_csv(node_file, encoding='ISO-8859-1')[attributs]
  participants = {}
  for d in data.iterrows():
    row = d[1].to_dict()
    participants[row['id']] = Participant(row)
  return participants


def load_movie():
  data = pandas.read_csv(MOVIE_NODE_FILE)[MOVIE_ATTRIBUTES]
  movies = {}
  for d in data.iterrows():
    row = d[1].to_dict()
    if row['popularity'] < MOVIE_POP_THRES:
      continue
    if int(row['release_date'].split('-')[0]) < MOVIE_YEAR_THRES:
      continue
    movies[row['id']] = Movie(row)
  return movies


def load_data():
  """
  Load & clean data and build the connections.

  Returns
  -------
  dict
    A dict of movies with id as keys.
  dict
    A dict of actors with id as keys.
  dict
    A dict of directors with id as keys.
  """
  movies = load_movie()
  actors = load_participant(ACTOR_NODE_FILE, ACTOR_ATTRIBUTES)
  directors = load_participant(DIRECTOR_NODE_FILE, DIRECTOR_ATTRIBUTES)
  movies, actors = \
    build_connections(movies, actors, 'cast_link', ACTOR_MOVIE_THRES)
  movies, directors = \
    build_connections(movies, directors, 'director_link', DIRECTOR_MOVIE_THRES)
  for m in movies.values():
    m.cast = m.attributes['cast_link']
    m.attributes.pop('cast_link')
    m.director = m.attributes['director_link']
    m.attributes.pop('director_link')
  new_id = 0
  movies, new_id = change_to_uniform_id(movies, new_id)
  actors, new_id = change_to_uniform_id(actors, new_id)
  directors, new_id = change_to_uniform_id(directors, new_id)
  print('movies:', len(movies))
  print('actors:', len(actors))
  print('directors:', len(directors))
  return movies, actors, directors


if __name__ == '__main__':
  load_data()
