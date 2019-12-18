from flask import Flask, request, render_template
from graph import MovieGraph
from data import load_data
import json
import time
import datetime
from vctoolkit import Timer

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


@app.route('/all_edges')
def all_edges_api():
  # returns a dict, whose keys are participant (actor/director) ids, and values
  # are a list of ids, including all the participants it ever collaborated with,
  # plus all the movie ids it participated in
  return graph.export_neighbors()


@app.route('/set_range', methods=['POST'])
def set_range():
  date_min = time.mktime(
    datetime.datetime.strptime(request.json['date_min'], '%Y-%m-%d').timetuple()
  )
  date_max = time.mktime(
    datetime.datetime.strptime(request.json['date_max'], '%Y-%m-%d').timetuple()
  )
  graph.set_range(date_min, date_max)
  data = {
    'node_weights': graph.export_node_weights(),
    'actor_scores': graph.export_actor_scores(),
    'director_scores': graph.export_director_scores(),
    'edges': graph.export_selected_edges()
  }
  s = json.dumps(data)
  return s


@app.route('/update', methods=['POST', 'GET'])
def update_api():
  graph.update()
  return graph.export_positions()

# check Notion notebook for more details of the pin/unpin design

@app.route('/pin', methods=['POST'])
def pin_api():
  pin_id = int(request.json['pin'])
  graph.pin(pin_id)
  return 'OK', 200


@app.route('/unpin', methods=['GET'])
def unpin_api():
  graph.unpin()
  return 'OK', 200
