from flask import Flask, request, render_template
from graph import MovieGraph
from data import load_data
import json
import time
import datetime

movies, actors, directors = load_data()
graph = MovieGraph(movies, actors, directors)

app = Flask(__name__)


@app.route('/')
def index():
  return render_template("index.html")


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
  date_min = time.mktime(
    datetime.datetime.strptime(request.json['date_min'], '%Y%m%d').timetuple()
  )
  date_max = time.mktime(
    datetime.datetime.strptime(request.json['date_max'], '%Y%m%d').timetuple()
  )
  graph.set_range(date_min, date_max)
  data = {
    'movie_sizes': graph.export_movie_sizes(),
    'actor_scores': graph.export_actor_scores(),
    'director_scores': graph.export_director_scores(),
    'edges': graph.export_selected_edges()
  }
  return json.dumps(data)


@app.route('/update', methods=['POST', 'GET'])
def update_api():
  graph.update()
  return graph.export_positions()
