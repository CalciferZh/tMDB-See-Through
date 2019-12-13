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

  that.get_data = function(dataset) {
    let get_movies_node = new request_node(
      that.get_movies_url,
      data => {
        console.log("get_movies");
        for (let key in data) {
          that.points[key] = {
            id: key,
            type: "movie",
            color: that.color("movie"),
            valid: true,
            x: 0,
            y: 0,
            r: (Math.log(data[key].revenue) + data[key].vote_average) / 2,
          };
          that.movies[key] = data[key];
          that.movies[key]["release_date"] = that.parseDate(
            data[key]["release_date"]
          );
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
          that.points[key] = {
            id: key,
            type: "actor",
            color: that.color("actor"),
            valid: true,
            x: 0,
            y: 0,
            r: 3,
          };
          that.actors[key] = data[key];
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
          that.points[key] = {
            id: key,
            type: "director",
            color: that.color("director"),
            valid: true,
            x: 0,
            y: 0,
            r: 3,
          };
          that.directors[key] = data[key];
        }
        that.set_range([new Date(1900, 0, 1), new Date(2100, 0, 1)]);
        that.get_coord(() => {
          Layout.init_graph();
          Layout.draw_single_graph();
        });
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
    let node = new request_node(
      that.set_range_url,
      data => {
        console.log("set_range");
        that.edges = [];
        for (let edge of data) {
          that.edges.push({
            'source': that.points[edge[0]],
            'target': that.points[edge[1]],
            'weight': 1,
            'id': 100000 * edge[0] + edge[1], // a naive hash
          })
        }
        that.set_valid();
      },
      "json",
      "POST"
    );
    node.set_header({
      "Content-Type": "application/json;charset=UTF-8"
    });
    node.set_data({
      date_min: range[0].getFullYear() * 10000 + (range[0].getMonth() + 1) * 100 + range[0].getDate(),
      date_max: range[1].getFullYear() * 10000 + (range[1].getMonth() + 1) * 100 + range[1].getDate() 
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
      "GET"
    );
    node.set_header({
      "Content-Type": "application/json;charset=UTF-8"
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
};
