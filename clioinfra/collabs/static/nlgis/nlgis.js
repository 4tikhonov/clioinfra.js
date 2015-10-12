function showmap(datayear, mapyear, handle, varname, colors, catnum, ctrlist) {
    var rightdiv = document.getElementById("#showmap");
    var margin = {top: -120, right: 20, bottom: 70, left: 40},
    width = 920 - margin.left - margin.right,
    height = 420 - margin.top - margin.bottom;

    var zoom = d3.behavior.zoom()
            .scaleExtent([1, 60])
            .size([width, height])
            .on('zoom', onZoom);

    var projection2 = d3.geo.winkel3()
            .scale(Math.min(150 / 772 * width, 150 / 472 * height))

    var projectionM = d3.geo.mercator()
    .center([5, 52])
    .scale(180)
    .translate([width / 2, height / 2]);

    var projection = d3.geo.equirectangular()
    .scale(150)
    .translate([width / 2, height / 2])
    .precision(.1);

    var path = d3.geo.path().projection(projection);

    d3.select("svg")
       .transition().duration(250).style("opacity", 0).remove();
    var svg = d3.select("#showmap").append("svg")
            .attr("width", width)
            .attr("height", height)
            .call(zoom);

    var g = svg.append('g');

    var locations = {};
    var locations = {};
    var allcountries = [];

    var tip = d3.tip()
  	.attr('class', 'd3-tip')
  	.offset([-10, 0])
  	.html(function(d) {
	
	if (typeof locations[d.properties.AREA] === 'undefined')
	{
	    return d.properties.AREA + ': no data'
	}
	else
	{
    	    return "<strong>" + d.properties.AREA + ":</strong> <span style='color:red'>" + locations[d.properties.AREA].value + "</span>";
	}
  	})

    mapapi = "http://clearance.sandbox.socialhistoryservices.org/api/maps?world=on&year=" + mapyear;
    d3.json(mapapi, function (error, world) {
        if (error) {
            console.log(error);
            return;
        } 	
	else
	{
	    locations = topojson.feature(world, world.objects.countries).features;
	}

	datapi = "/api/dataapi?handle=" + handle + "&year=" + datayear + "&catmax=" + catnum + "&datarange=calculate";
	datapi = datapi + '&colors=' + colors + '&ctrlist=' + ctrlist;
	d3.json(datapi, function (error, data) {

            if (error) {
                console.log(error);
            } else {
                locations = data;
            }

            var countries = topojson.feature(world, world.objects.countries).features;

            g.selectAll('.country').data(countries).enter()
                    .append('path')
                    .attr('class', 'country')
                    .attr('d', path)
		    .attr("data-legend",function(d) { return d.properties.AREA})
      		    .on('mouseover', tip.show)
      		    .on('mouseout', tip.hide)
		    .on("click", clicked)
		    .attr("stroke", "#848482")
                    .attr("stroke-width", 0.5)
                    .style('fill', function (d) {
                        var color = locations[d.properties.AREA] && locations[d.properties.AREA].color;
                        return color || '#ffffff';
                    })

            for (var i in locations) {
                if (locations.hasOwnProperty(i) && locations[i].name) {
                    allcountries.push.apply(allcountries, locations[i].name);
                }
            }

        });
    });
    svg.call(tip);

  function legendDemo() {
  sampleNumerical = [1,2.5,5,10,20];
  var legendValues=[{color: "green", stop: [0,1]},{color: "green", stop: [1,2]},{color: "purple", stop: [2,3]},{color: "yellow", stop: [3,4]},{color: "black", stop: [4,5]}];

  datapi = "/api/dataapi?handle=" + handle + "&year=" + datayear + "&catmax=" + catnum + "&datarange=calculate";
  datapi = datapi + '&colors=' + colors + '&ctrlist=' + ctrlist;
  datapi = datapi + '&getrange=yes';
  d3.json(datapi, function (error, rangedata) {

            if (error) {
                console.log(error);
            } else {
                scales = rangedata;
            }

  var sampleCategoricalData = scales['scale'];
  var COLORS = scales['colors']; 
  sampleOrdinal = d3.scale.category20().domain(sampleCategoricalData);

  verticalLegend = d3.svg.legend(legendValues, COLORS).labelFormat("none").cellPadding(5).orientation("vertical").units("Legend").cellWidth(25).cellHeight(18).inputScale(sampleOrdinal).cellStepping(10);

  d3.select("svg").append("g").attr("transform", "translate(20,250)").attr("class", "legend").style("font-size","12px").call(verticalLegend);
   })

  }

legend = svg.append("g")
  .attr("class","legend")
  .style("font-size","5px")
  .call(legendDemo)

function clicked(d) {
  var centroid = path.centroid(d),
      translate = projection.translate();

  projection.translate([
    translate[0] - centroid[0] + width / 2,
    translate[1] - centroid[1] + height / 2
  ]);

  projection.translate(d3.event.translate).scale(d3.event.scale);
  zoom.translate(projection.translate());
  onZoom();

  g.selectAll("path").transition()
      .duration(700)
      .attr("d", path);
}

function zoomed() {
  projection.translate(d3.event.translate).scale(d3.event.scale);
  g.selectAll("path").attr("d", path);
}
    function onZoom () {
        var t = d3.event.translate;
        var s = d3.event.scale;

        t[0] = Math.max(Math.min(t[0], 0), width * (1 - s));
        t[1] = Math.max(Math.min(t[1], 0), height * (1 - s));

        zoom.translate(t);

        g.style("stroke-width", 1 / s)
                .attr('transform', 'translate(' + t + ')scale(' + s + ')');
    }
}

