from flask import Flask, request, render_template
from graph import MovieGraph
from data import load_data

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
  date_min = int(request.json['date_min'])
  date_max = int(request.json['date_max'])
  graph.set_range(date_min, date_max)
  return graph.export_selected_edges()


@app.route('/update', methods=['POST', 'GET'])
def update_api():
  graph.update()
  return graph.export_positions()
