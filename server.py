from flask import Flask
from flask import request
from graph import MovieGraph
from data import load_data

app = Flask(__name__)

movies, actors, directors = load_data()
graph = MovieGraph(movies, actors, directors)

@app.route('/movies')
def movies_api():
  return graph.export_movies()


@app.route('/actors')
def actors_api():
  return graph.export_actors()


@app.route('/directors')
def directors_api():
  return graph.export_directors()


@app.route('/set_range', methods=['POST'])
def set_range():
  year_min = int(request.form['year_min'])
  year_max = int(request.form['year_max'])
  graph.set_range(year_min, year_max)
  return 'OK', 200


@app.route('/update', methods=['GET', 'POST'])
def update_api():
  # if step is None, will use the default step with exponential decay
  step = None
  if request.method == 'POST':
    step = request.form['step']
  graph.update(step)
  return graph.export_positions()
