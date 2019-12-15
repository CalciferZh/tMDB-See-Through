LayoutClass = function() {
  let that = this;

  that.time_window_div = d3.select("#time-windows");
  that.graph_div = d3.select("#graph");
  that.detail_table = d3.select("#detail-table");

  that.table = null;
  that.current_tab = null; // 'movie or actor or director'

  that.default_line_opacity = 0.3;
  that.default_point_opacity = 0.5;
  that.highlight_line_opacity = 1;
  that.highlight_point_opacity = 1;

  let graph_vars = {};

  that.draw_time_window = function() {
    let margin = { top: 10, right: 30, bottom: 30, left: 40 };
    let width =
      that.time_window_div.node().getBoundingClientRect().width -
      margin.left -
      margin.right;
    let height =
      that.time_window_div.node().getBoundingClientRect().height -
      margin.top -
      margin.bottom;

    let maxDate = new Date(
      Math.max(...DataLoader.movies.map(x => x.release_date))
    );
    let minDate = new Date(
      Math.min(...DataLoader.movies.map(x => x.release_date))
    );
    let xScale = d3
      .scaleTime()
      .domain([minDate, maxDate])
      .rangeRound([0, width]);
    let yScale = d3.scaleLinear().range([height, 0]);
    let histogram = d3
      .histogram()
      .value(function(d) {
        return d.release_date;
      })
      .domain(xScale.domain())
      .thresholds(xScale.ticks(30));
    let bins = histogram(DataLoader.movies);
    yScale.domain([0, d3.max(bins, d => d.length)]);

    let svg = that.time_window_div
      .append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
      .append("g")
      .attr("transform", `translate(${margin.left}, ${margin.top})`);
    // bins
    svg
      .selectAll("rect")
      .data(bins)
      .enter()
      .append("rect")
      .attr("class", "bar")
      .attr("x", 1)
      .attr("transform", d => `translate(${xScale(d.x0)}, ${yScale(d.length)})`)
      .attr("width", d => xScale(d.x1) - xScale(d.x0) - 1)
      .attr("height", d => height - yScale(d.length))
      .attr("fill", "lightblue");

    // Axises
    svg
      .append("g")
      .attr("transform", `translate(0, ${height})`)
      .call(d3.axisBottom(xScale));

    svg.append("g").call(d3.axisLeft(yScale));

    // brush
    let line_brush = d3
      .brushX()
      .extent([
        [0, 0],
        [width, height]
      ])
      .on("start brush end", () => {
        if (
          d3.event.selection &&
          d3.event.selection[1] - d3.event.selection[0] > 10
        ) {
          DataLoader.set_range([
            xScale.invert(d3.event.selection[0]),
            xScale.invert(d3.event.selection[1])
          ]);
        }
      });
    let brush_g = svg.append("g").attr("class", "brush");
    brush_g.call(line_brush);
  };

  that.init_graph = function() {
    let margin = { top: 10, right: 30, bottom: 30, left: 60 };
    let width =
      that.graph_div.node().getBoundingClientRect().width -
      margin.left -
      margin.right;
    let height =
      that.graph_div.node().getBoundingClientRect().height -
      margin.top -
      margin.bottom;

    graph_vars["svg"] = that.graph_div
      .append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
      .append("g")
      .attr("transform", `translate(${margin.left}, ${margin.top})`);

    graph_vars["xScale"] = d3.scaleLinear().range([0, width]);
    graph_vars["yScale"] = d3.scaleLinear().range([height, 0]);

    that.update_graph();
  };

  that.update_graph = function() {
    DataLoader.get_coord(() => {
      that.draw_single_graph();
      that.update_graph();
    });
  };

  that.draw_single_graph = function() {
    let svg = graph_vars["svg"];
    let xScale = graph_vars["xScale"];
    let yScale = graph_vars["yScale"];
    let xs = DataLoader.points.map(d => d.x);
    let ys = DataLoader.points.map(d => d.x);
    let x_min = Math.min(...xs);
    let x_max = Math.max(...xs);
    let y_min = Math.min(...ys);
    let y_max = Math.max(...ys);
    xScale.domain([x_min, x_max]);
    yScale.domain([y_min, y_max]);

    let links = svg.selectAll(".link").data(DataLoader.edges, d => d.id);
    let points = svg
      .selectAll(".point")
      .data(DataLoader.valid_points, x => x.id);
    points.each(d => {
      d.cx = xScale(d.x);
      d.cy = yScale(d.y);
    });

    // draw link first

    links.exit().remove();

    links
      .attr("x1", d => d.source.cx)
      .attr("y1", d => d.source.cy)
      .attr("x2", d => d.target.cx)
      .attr("y2", d => d.target.cy);
    links
      .enter()
      .append("line")
      .attr("class", "link")
      .attr("x1", d => d.source.cx)
      .attr("y1", d => d.source.cy)
      .attr("x2", d => d.target.cx)
      .attr("y2", d => d.target.cy)
      .style("stroke", "lightgray")
      .style("stroke-width", 1)
      .style("stroke-opacity", that.default_line_opacity);

    points.exit().remove();

    points.attr("cx", d => d.cx).attr("cy", d => d.cy);

    let drag_handler = d3
      .drag()
      .on("start drag", d => {
        DataLoader.pins = [
          {
            id: d.id,
            x: xScale.invert(d3.event.x),
            y: xScale.invert(d3.event.y)
          }
        ];
      })
      .on("end", () => {
        DataLoader.pins = [];
      });

    points
      .enter()
      .append("circle")
      .attr("class", "point")
      .attr("cx", d => d.cx)
      .attr("cy", d => d.cy)
      .attr("r", d => d.r)
      .style("fill", d => d.color)
      .style("fill-opacity", that.default_point_opacity)
      .on("mouseover", that.on_mouseover)
      .on("mouseout", that.on_mouseout)
      .call(drag_handler);
  };

  that.on_mouseover = function(d) {
    that.draw_detail_table(d);
    let ids = [];
    if (d.type == "movie") {
      let info = DataLoader.get_graph_info_about_movie(d);
      ids = new Set([...info.cast, d.id]);
    } else {
      let info = DataLoader.get_graph_info_about_man(d);
      ids = new Set([...info.movies, ...info.collaborator]);
    }
    d3.selectAll(".point").style("fill-opacity", d =>
      ids.has(d.id) ? that.highlight_point_opacity : that.default_point_opacity
    );
    d3.selectAll(".link").style("stroke-opacity", d =>
      ids.has(d.source.id) && ids.has(d.target.id)
        ? that.highlight_line_opacity
        : that.default_line_opacity
    );
  };

  that.on_mouseout = function(d) {
    d3.selectAll(".point").style("fill-opacity", that.default_point_opacity);
    d3.selectAll(".link").style("stroke-opacity", that.default_line_opacity);
  };

  that.draw_detail_table = function(d) {
    let tbody = that.detail_table.select("tbody");
    let display_attr = [
      "name",
      "popularity",
      "budget",
      "revenue",
      "vote_average"
    ];
    let strings = display_attr.map(
      attr => `<tr><th>${capitalize(attr)}</th><td>${d.info[attr]}</td></tr>`
    );
    strings.splice(
      1,
      0,
      `<tr><th>Type</th><td>${capitalize(d.type)}</td></tr>`
    );
    tbody.html(strings.join(""));
  };

  that.init_list = function() {
    let columns = [
      {
        field: "name",
        title: "Name"
      },
      {
        field: "vote_average",
        title: "Vote",
        sortable: true
      },
      {
        field: "revenue",
        title: "Revenue",
        sortable: true
      },
      {
        field: "budget",
        title: "Budget",
        sortable: true
      }
    ];

    that.table = $("#table-list").bootstrapTable({
      height: 500,
      sortName: "vote_average",
      sortOrder: "desc",
      columns: columns,
      data: DataLoader.movies,
      onClickRow: function(row, element, field) {
        that.on_mouseover(DataLoader.points[row.id]);
      }
    });
    that.current_tab = 'movie';

    d3.select("#movie-tab").on('click', () => that.switch_tab('movie'));
    d3.select("#actor-tab").on('click', () => that.switch_tab('actor'));
    d3.select("#director-tab").on('click', () => that.switch_tab('director'));
  };

  that.update_list = function() {
    let data = null;
    if (that.current_tab == 'movie') {
      data = DataLoader.movies.filter(
        movie =>
          DataLoader.range[0] < movie.release_date &&
          movie.release_date < DataLoader.range[1]
      );
    }
    else if (that.current_tab == 'actor') {
      data = DataLoader.actors.filter(x => x);
    } else {
      data = DataLoader.directors.filter(x => x);
    }
    that.table.bootstrapTable("refreshOptions", { data: data });
  };

  that.switch_tab = function(name) {
    if (that.current_tab == name) return;
    that.current_tab = name;
    that.update_list();
  }
};

const capitalize = s => s.charAt(0).toUpperCase() + s.slice(1);
