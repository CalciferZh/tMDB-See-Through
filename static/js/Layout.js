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

  that.line_brush = null;
  that.brush_g = null;

  // for play
  that.play_timer = 0;
  that.left_border = 0;
  that.right_border = 0;
  that.is_playing = false;

  d3.select("#man-size").on("change", function() {
    let val = document.getElementById("man-size").value;
    DataLoader.set_size_method(val, true);
    DataLoader.set_size();
    d3.selectAll(".rect")
      .attr("width", d => d.r)
      .attr("height", d => d.r);
    d3.selectAll(".circle").attr("r", d => d.r);
  });

  d3.select("#movie-size").on("change", function() {
    let val = document.getElementById("movie-size").value;
    DataLoader.set_size_method(val, false);
    DataLoader.set_size();
    d3.selectAll(".rect")
      .attr("width", d => d.r)
      .attr("height", d => d.r);
    d3.selectAll(".circle").attr("r", d => d.r);
  });

  let graph_vars = {};

  that.draw_time_window = function() {
    let margin = { top: 20, right: 30, bottom: 20, left: 100 };
    let width =
      that.time_window_div.node().getBoundingClientRect().width -
      margin.left -
      margin.right;
    let height =
      that.time_window_div.node().getBoundingClientRect().height -
      margin.top -
      margin.bottom;
    that.max_right_border = width;
    let xScale = d3
      .scaleTime()
      .domain(d3.extent(DataLoader.movies.map(x => x.release_date)))
      .rangeRound([0, width]);
    let yScale = d3.scaleLinear().range([height, 0]);
    let histogram = d3
      .histogram()
      .value(function(d) {
        return d.release_date;
      })
      .domain(xScale.domain())
      .thresholds(xScale.ticks(40));
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
      .call(d3.axisBottom(xScale).ticks(20));

    svg.append("g").call(d3.axisLeft(yScale).ticks(5));

    //that.time_window_div.select("svg").append("rect").attr("id", "play-button").attr("x", 25).attr("y", height / 2).attr("height", height / 2).attr("width", height / 2).style("fill", "red");
    that.time_window_div.select("svg").append("image").attr("id", "play-button").attr("x", 25).attr("y", height / 2).attr("height", height / 2).attr("width", height / 2)
    .attr("xlink:href","/static/svg/play-button.svg").attr("cursor", "pointer").on('click', that.toggle_play);
    // brush
    that.line_brush = d3
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
          that.left_border = d3.event.selection[0];
          that.right_border = d3.event.selection[1];
          DataLoader.set_range([xScale.invert(that.left_border), xScale.invert(that.right_border)]);
        }
      });
    that.brush_g = svg.append("g").attr("class", "brush");
    that.brush_g.call(that.line_brush);
  };

  that.init_graph = function() {
    let margin = { top: 10, right: 10, bottom: 10, left: 10 };
    let width =
      that.graph_div.node().getBoundingClientRect().width -
      margin.left -
      margin.right;
    let height =
      that.graph_div.node().getBoundingClientRect().height -
      margin.top -
      margin.bottom;

    that.zoom = d3
      .zoom()
      .scaleExtent([0.5, 2])
      .extent([
        [0, 0],
        [width, height]
      ])
      .on("start", function() {
        graph_vars["xScale-back"] = graph_vars["xScale"];
        graph_vars["yScale-back"] = graph_vars["yScale"];
      })
      .on("zoom", function() {
        // graph_vars["svg"].attr("transform", d3.event.transform);
        graph_vars["xScale"] = d3.event.transform.rescaleX(
          graph_vars["xScale-back"]
        );
        graph_vars["yScale"] = d3.event.transform.rescaleY(
          graph_vars["yScale-back"]
        );
      })
      .on("end", function() {
        graph_vars["xScale-back"] = null;
        graph_vars["yScale-back"] = null;
        if (d3.event.transform != d3.zoomIdentity.scale(1))
          that.zoom_svg.call(that.zoom.transform, d3.zoomIdentity.scale(1));
      });

    that.zoom_svg = that.graph_div
      .append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom - 40)
      .append("rect")
      .attr("class", "zoom")
      .attr("width", width)
      .attr("height", height)
      .style("fill", "none")
      .style("pointer-events", "all")
      .attr("transform", `translate(${margin.left}, ${margin.top})`);

    that.zoom_svg.call(that.zoom);

    graph_vars["svg"] = that.graph_div
      .select("svg")
      .append("g")
      .attr("transform", `translate(${margin.left}, ${margin.top})`);

    graph_vars["xScale"] = d3
      .scaleLinear()
      .range([0, width])
      .domain([-1, 2]);
    graph_vars["yScale"] = d3
      .scaleLinear()
      .range([height, 0])
      .domain([-1, 2]);

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
    // graph_vars["xScale"].domain(d3.extent(DataLoader.points.map(d => d.x)));
    // graph_vars["yScale"].domain(d3.extent(DataLoader.points.map(d => d.x)));

    DataLoader.valid_points.forEach(function(d) {
      d.cx = xScale(d.x);
      d.cy = yScale(d.y);
    });

    let links = svg.selectAll(".link").data(DataLoader.edges, d => d.id);
    let points = svg.selectAll(".circle").data(
      DataLoader.valid_points.filter(x => x.type != "movie"),
      x => x.id
    );
    let rects = svg.selectAll(".rect").data(
      DataLoader.valid_points.filter(x => x.type == "movie"),
      x => x.id
    );

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
      .style("stroke-opacity", d =>
        d.highlighted ? that.highlight_point_opacity : d.opacity
      );

    points.exit().remove();
    rects.exit().remove();

    rects
      .attr("x", d => d.cx - d.r / 2)
      .attr("y", d => d.cy - d.r / 2)
      .attr("width", d => d.r)
      .attr("height", d => d.r)
      .style("fill-opacity", d =>
        d.highlighted ? that.highlight_point_opacity : d.opacity
      );
    points
      .attr("cx", d => d.cx)
      .attr("cy", d => d.cy)
      .attr("r", d => d.r)
      .style("fill-opacity", d =>
        d.highlighted ? that.highlight_point_opacity : d.opacity
      );
    d3.selectAll(".visiable-name")
      .attr("x", d => d.cx + d.r)
      .attr("y", d => d.cy + d.r / 2)
      .text(d => (d.r > 8 ? d.info.abbr : ""))
      .attr("opacity", d =>
      1.5 * (d.highlighted ? that.highlight_point_opacity : d.opacity));

    rects
      .enter()
      .append("rect")
      .attr("class", "point rect")
      .attr("x", d => d.cx - d.r / 2)
      .attr("y", d => d.cy - d.r / 2)
      .attr("width", d => d.r)
      .attr("height", d => d.r)
      .style("fill", d => d.color)
      .style("fill-opacity", d => d.opacity)
      .on("mouseover", that.on_mouseover)
      .on("mouseout", that.on_mouseout)
      .on("dblclick", that.pin);

    points
      .enter()
      .append("circle")
      .attr("class", "point circle")
      .attr("cx", d => d.cx)
      .attr("cy", d => d.cy)
      .attr("r", d => d.r)
      .style("fill", d => d.color)
      .style("fill-opacity", d =>
        d.highlighted ? that.highlight_point_opacity : d.opacity
      )
      .on("mouseover", that.on_mouseover)
      .on("mouseout", that.on_mouseout)
      .on("dblclick", that.pin);
    points
      .enter()
      .append("text")
      .attr("class", "visiable-name")
      .attr("x", d => d.cx + d.r)
      .attr("y", d => d.cy + d.r / 2)
      .text(d => (d.r > 8 ? d.info.abbr : ""))
      .attr("opacity", d =>
      1.5 * (d.highlighted ? that.highlight_point_opacity : d.opacity))
      .attr("font-family", "sans-serif")
      .attr("font-size", "12px");
  };

  that.on_mouseover = function(d) {
    if (d.weight < 0.05) return;
    that.draw_detail_table(d);
    let ids = [];
    if (d.type == "movie") {
      let info = DataLoader.get_graph_info_about_movie(d);
      ids = new Set([...info.cast, d.id]);
    } else {
      let info = DataLoader.get_graph_info_about_man(d);
      ids = new Set([...info.movies, ...info.collaborator]);
    }
    d3.selectAll(".point").each(d => (d.highlighted = ids.has(d.id)));
    d3.selectAll(".link").each(
      d => (d.highlighted = ids.has(d.source.id) && ids.has(d.target.id))
    );
    d3.selectAll(".point").style("fill-opacity", d =>
      d.highlighted ? that.highlight_point_opacity : d.opacity
    );
    d3.selectAll(".link").style("stroke-opacity", d =>
      d.highlighted ? that.highlight_point_opacity : d.opacity
    );
  };

  that.pin = function(d) {
    console.log("dblclick");
    DataLoader.pin(d.id);
  };

  that.on_mouseout = function(d) {
    d3.selectAll(".point").each(d => (d.highlighted = false));
    d3.selectAll(".link").each(d => (d.highlighted = false));
    d3.selectAll(".point").style("fill-opacity", d => d.opacity);
    d3.selectAll(".link").style("stroke-opacity", d => d.opacity);
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
    that.draw_detail_table(DataLoader.points[0]);
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
      height:
        d3
          .select("#list-row")
          .node()
          .getBoundingClientRect().height - 40,
      sortName: "vote_average",
      sortOrder: "desc",
      columns: columns,
      data: DataLoader.movies,
      onClickRow: function(row, element, field) {
        that.on_mouseover(DataLoader.points[row.id]);
      }
    });
    that.current_tab = "movie";

    d3.select("#movie-tab").on("click", () => that.switch_tab("movie"));
    d3.select("#actor-tab").on("click", () => that.switch_tab("actor"));
    d3.select("#director-tab").on("click", () => that.switch_tab("director"));
  };

  that.update_list = function() {
    let data = null;
    if (that.current_tab == "movie") {
      data = DataLoader.movies.filter(
        movie =>
          DataLoader.range[0] < movie.release_date &&
          movie.release_date < DataLoader.range[1]
      );
    } else if (that.current_tab == "actor") {
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
  };
  that.toggle_play = function() {
    if (that.is_playing) {
      d3.select("#play-button").attr("xlink:href","/static/svg/play-button.svg");
      that.pause();
    } else {
      d3.select("#play-button").attr("xlink:href","/static/svg/pause-button.svg");
      that.play();
    }
    that.is_playing = !that.is_playing;
  }
  that.play = function() {
    that.left_border += 10;
    that.right_border += 10;
    if (that.right_border > that.max_right_border) return;
    that.line_brush.move(that.brush_g, [that.left_border, that.right_border]);
    that.play_timer = setTimeout(that.play, 1000);
  };
  that.pause = function() {
    clearTimeout(that.play_timer);
  };
};

const capitalize = s => s.charAt(0).toUpperCase() + s.slice(1);
