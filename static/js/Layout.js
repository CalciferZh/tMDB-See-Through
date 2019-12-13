LayoutClass = function() {
  let that = this;

  that.time_window_div = d3.select("#time-windows");
  that.graph_div = d3.select("#graph");
  that.detail_div = d3.select("#detail");
  that.list_div = d3.select("#list");

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
      .thresholds(xScale.ticks(d3.timeYear));
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
      .on("start brush", () => {})
      .on("end", () => {
        DataLoader.set_range([
          xScale.invert(d3.event.selection[0]),
          xScale.invert(d3.event.selection[1])
        ]);
      });
    let brush_g = svg.append("g").attr("class", "brush");
    brush_g.call(line_brush);
  };

  that.init_graph = function() {
    let margin = { top: 10, right: 30, bottom: 30, left: 60 };
    let width = that.graph_div.node().getBoundingClientRect().width - margin.left - margin.right;
    let height = that.graph_div.node().getBoundingClientRect().height - margin.top - margin.bottom;

    graph_vars['svg'] = that.graph_div
      .append("svg")
      .attr("width", width + margin.left + margin.right)
      .attr("height", height + margin.top + margin.bottom)
      .append("g")
      .attr("transform", `translate(${margin.left}, ${margin.top})`);

    graph_vars['xScale'] = d3.scaleLinear().range([0, width]);
    graph_vars['yScale'] = d3.scaleLinear().range([height, 0]);

    d3.select("#draw").on("click", () => {
      that.update_graph(100);
    });
  };

  that.update_single_graph = function() {
    console.log("update_single_graph");
    DataLoader.get_coord(1, that.draw_single_graph);
  };

  that.draw_single_graph = function() {
    let svg=graph_vars['svg'];
    let xScale = graph_vars['xScale'];
    let yScale = graph_vars['yScale'];
    let xs = DataLoader.data.map(d => d.x);
    let ys = DataLoader.data.map(d => d.x);
    let x_min = Math.min(-5, ...xs);
    let x_max = Math.max(5, ...xs);
    let y_min = Math.min(-5, ...ys);
    let y_max = Math.max(5, ...ys);

    console.log(xs[0],xs[10],ys[0],ys[10])
    
    xScale.domain([x_min, x_max])
    yScale.domain([y_min, y_max])

    let points = svg.selectAll("circle").data(DataLoader.data, x => x.id);

    points.exit().remove();

    points.attr("cx", d => xScale(d.x)).attr("cy", d => yScale(d.y));

    points
      .enter()
      .append("circle")
      .attr("cx", d => xScale(d.x))
      .attr("cy", d => yScale(d.y))
      .attr("r", 3)
      .style("fill", d => d.color);
  };

  that.update_graph = function(counter) {
    if (counter == 0) return;
    that.update_single_graph();
    setTimeout(() => {
      that.update_graph(counter - 1);
    }, 50);
  };
};
