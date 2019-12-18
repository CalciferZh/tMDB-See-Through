DataLoaderClass = function() {
  let that = this;

  that.color = d3.scaleOrdinal(d3.schemeCategory10);
  that.parseDate = d3.timeParse("%Y%m%d");

  // URL information
  that.get_movies_url = "/movies";
  that.get_actors_url = "/actors";
  that.get_directors_url = "/directors";
  that.set_range_url = "/set_range";
  that.update_url = "/update";

  // data
  that.edges = [];
  that.points = [];
  that.valid_points = [];
  that.movies = [];
  that.actors = [];
  that.directors = [];
  that.pins = [];

  // calculate attr
  const voteavg2size = x => (x.vote_average-5) * (x.vote_average-5);
  const budget2size = x => Math.log(x.budget + 1) / 10;
  const revenue2size = x => (Math.log(x.revenue + 1) - 10) *  (Math.log(x.revenue + 1) - 10) / 6;
  const popularity2size = x => Math.sqrt(x.popularity) / 1.5;
  const runtime2size = x => Math.sqrt(x.runtime);
  const attr2size = {
    'vote_average': voteavg2size,
    'budget': budget2size,
    'revenue': revenue2size,
    'popularity': popularity2size,
    'runtime': runtime2size,
  };
  that.man_size_method = popularity2size;
  that.movie_size_method = revenue2size;
  that.set_size_method = function (attr, is_man) {
    if (is_man) that.man_size_method = attr2size[attr];
    else that.movie_size_method = attr2size[attr];
  };

  that.set_size = function() {
    for(let point of that.points) {
      point.r = point.type == "movie" ? that.movie_size_method(point.info) : that.man_size_method(point.info);
    }
  };

  that.get_data = function(dataset) {
    let get_movies_node = new request_node(
      that.get_movies_url,
      data => {
        console.log("get_movies");
        for (let key in data) {
          that.movies[key] = data[key];
          that.movies[key].id = key;
          that.movies[key]["release_date"] = new Date(
            data[key]["release_date"] * 1000
          );
          that.movies[key]['popularity'] =  that.movies[key]['popularity'].toFixed(2);
          that.movies[key]['vote_average'] =  that.movies[key]['vote_average'].toFixed(1);
          that.movies[key]['name'] = that.movies[key]['title'];
          that.points[key] = {
            id: key,
            type: "movie",
            color: that.color("movie"),
            valid: true,
            x: 0,
            y: 0,
            r: 0,
            adj: [],
            info: that.movies[key],
          };
        }
        Layout.draw_time_window();
      },
      "json",
      "GET"
    );
    get_movies_node.set_header({
      "Content-Type": "application/json;charset=UTF-8"
    });
    let get_actors_node = new request_node(
      that.get_actors_url,
      data => {
        console.log("get_actors");
        for (let key in data) {
          that.actors[key] = data[key];
          that.actors[key].id = key;
          that.points[key] = {
            id: key,
            type: "actor",
            color: that.color("actor"),
            valid: true,
            x: 0,
            y: 0,
            r: 0,
            adj: [],
            info: that.actors[key],
          };
        }
      },
      "json",
      "GET"
    );
    get_actors_node.set_header({
      "Content-Type": "application/json;charset=UTF-8"
    });
    let get_directors_node = new request_node(
      that.get_directors_url,
      data => {
        console.log("get_directors");
        for (let key in data) {
          that.directors[key] = data[key];
          that.directors[key].id = key;
          that.points[key] = {
            id: key,
            type: "director",
            color: that.color("director"),
            valid: true,
            x: 0,
            y: 0,
            r: 0,
            adj: [],
            info: that.directors[key]
          };
        }
        that.set_range([new Date(1980, 0, 1), new Date(2020, 0, 1)]);
        Layout.init_graph();
        Layout.init_list();
      },
      "json",
      "GET"
    );
    get_directors_node.set_header({
      "Content-Type": "application/json;charset=UTF-8"
    });
    get_directors_node.depend_on(get_actors_node);
    get_actors_node.depend_on(get_movies_node);
    get_movies_node.notify();
  };

  that.set_range = function(range) {
    that.range = range;
    let node = new request_node(
      that.set_range_url,
      data => {
        console.log("set_range");
        that.edges = [];
        for (let point of that.points) {
          point.adj = [];
        }
        for (let key in data.movie_weights) {
          that.points[key].r = data.movie_weights[key] * 8;
        }
        for (let key in data.actor_scores) {
          for (let attr in data.actor_scores[key]) {
            that.actors[key][attr] = data.actor_scores[key][attr];
          }
          if ('popularity' in data.actor_scores[key]) that.actors[key]['popularity'] =  that.actors[key]['popularity'].toFixed(2);
          if ('vote_average' in data.actor_scores[key]) that.actors[key]['vote_average'] =  that.actors[key]['vote_average'].toFixed(1);
        }
        for (let key in data.director_scores) {
          for (let attr in data.director_scores[key]) {
            that.directors[key][attr] = data.director_scores[key][attr];
          }
          if ('popularity' in data.director_scores[key]) that.directors[key]['popularity'] =  that.directors[key]['popularity'].toFixed(2);
          if ('vote_average' in data.director_scores[key]) that.directors[key]['vote_average'] =  that.directors[key]['vote_average'].toFixed(1);
        }
        that.set_size(that.attr);
        for (let _edge of data.edges) {
          let edge = {
            source: that.points[_edge[0]],
            target: that.points[_edge[1]],
            weight: 1,
            id: 100000 * _edge[0] + _edge[1] // a naive hash
          };
          edge.source.adj.push(edge.target);
          edge.target.adj.push(edge.source);
          that.edges.push(edge);
        }
        that.set_valid();
        Layout.update_list();
      },
      "json",
      "POST"
    );
    node.set_header({
      "Content-Type": "application/json;charset=UTF-8"
    });
    node.set_data({
      date_min: that.range[0].toISOString().substring(0, 10),
      date_max: that.range[1].toISOString().substring(0, 10)
    });
    node.notify();
  };

  that.get_coord = function(callback) {
    let node = new request_node(
      that.update_url,
      data => {
        console.log("get_coord");
        for (let key in data) {
          that.points[key].x = data[key][0];
          that.points[key].y = data[key][1];
        }
        if (callback) callback();
      },
      "json",
      "POST"
    );
    node.set_header({
      "Content-Type": "application/json;charset=UTF-8"
    });
    node.set_data( {
      'pins': that.pins,
    });
    node.notify();
  };

  that.set_valid = function() {
    for (let point of that.points) point.valid = false;
    for (let edge of that.edges) {
      edge.source.valid = true;
      edge.target.valid = true;
    }
    that.valid_points = that.points.filter(d => d.valid);
  };

  that.get_graph_info_about_man = function(man) {
    let ret = {};
    ret.movies = man.adj.map(movie => movie.id);
    ret.collaborator = new Set();
    for (let movie of man.adj) {
      for (let _man of movie.adj) {
        ret.collaborator.add(_man.id);
      }
    }
    return ret;
  };
  that.get_graph_info_about_movie = function(movie) {
    let ret = {};
    ret.cast = movie.adj.map(man => man.id);
    return ret;
  };
};
