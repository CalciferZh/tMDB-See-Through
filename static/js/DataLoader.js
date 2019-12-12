DataLoaderClass = function () {
    let that = this;

    that.color = d3.scaleOrdinal(d3.schemeCategory10);
    that.parseDate = d3.timeParse("%Y-%m-%d");

    // URL information
    that.get_movies_url = "/movies";
    that.get_actors_url = "/actors";
    that.get_directors_url = "/directors";
    that.set_range_url = "/set_range";
    that.update_url = "/update";

    // data
    that.data = [];
    that.movies = [];
    that.actors = [];
    that.directors = [];

    that.get_data = function (dataset) {
        let get_movies_node = new request_node(that.get_movies_url, (data) => {
            console.log("get_movies");
            for (let key in data) {
                that.data[key] = {
                    'id': key,
                    'type': 'movie',
                    'color': that.color('movie'),
                    'valid': true,
                    'x': 0,
                    'y': 0,
                    'other_info': {
                        'connected_id': [],
                    },
                };
                that.movies[key] = data[key];
                that.movies[key]['release_date'] = that.parseDate(data[key]['release_date']);
            }
            Layout.draw_time_window();
            that.set_range([new Date(1900,0,1), new Date(2100,0,1)]);
        }, "json", "GET");
        get_movies_node.set_header({
            "Content-Type": "application/json;charset=UTF-8"
        });
        let get_actors_node = new request_node(that.get_actors_url, (data) => {
            console.log("get_actors");
            for (let key in data) {
                that.data[key] = {
                    'id': key,
                    'type': 'actor',
                    'color': that.color('actor'),
                    'valid': true,
                    'other_info': {
                        'connected_id': [],
                    },
                };
                that.actors[key] = data[key];
            }
        }, "json", "GET");
        get_actors_node.set_header({
            "Content-Type": "application/json;charset=UTF-8"
        });
        let get_directors_node = new request_node(that.get_directors_url, (data) => {
            console.log("get_directors");
            for (let key in data) {
                that.data[key] = {
                    'id': key,
                    'type': 'director',
                    'color': that.color('director'),
                    'valid': true,
                    'other_info': {
                        'connected_id': [],
                    },
                };
                that.directors[key] = data[key];
            }
            that.get_coord(10, () => {
                Layout.init_graph();
                Layout.draw_single_graph();
            })
        }, "json", "GET");
        get_directors_node.set_header({
            "Content-Type": "application/json;charset=UTF-8"
        });
        get_directors_node.depend_on(get_actors_node);
        get_actors_node.depend_on(get_movies_node);
        get_movies_node.notify();
    };

    that.set_range = function (range) {
        that.set_valid(range[0], range[1]);
        let node = new request_node(that.set_range_url, (data) => {
            console.log("set_range");
        }, "json", "POST");
        node.set_header({
            "Content-Type": "application/json;charset=UTF-8"
        });
        node.set_data({
            'year_min': range[0].getFullYear(),
            'year_max': range[1].getFullYear(),
        });
        node.notify();
    };

    that.get_coord = function (step, callback) {
        let node = new request_node(that.update_url, (data) => {
            console.log("get_coord");
            for (let key in data) {
                that.data[key].x = data[key][0];
                that.data[key].y = data[key][1];
            }
            if (callback) callback();
        }, "json", "POST");
        node.set_header({
            "Content-Type": "application/json;charset=UTF-8"
        });
        node.set_data({
            'step': step,
        });
        node.notify();
    };

    that.set_valid = function(time_min, time_max) {
        for (let d in that.data) {
            if (d.type == 'movie') {
                let time = that.movies[d.id]['release_date'];
                d.valid = time_min < time && time < time_max;
            } else {
                d.valid = true;
            }
        }
    };

    that.get_valid_data = function () {
        return that.data.filter(d => d.valid);
    }
};