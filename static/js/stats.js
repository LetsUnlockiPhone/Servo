/**
 * stats.js
 */

function showTooltip(x, y, contents) {
    $("<div id='tooltip'>" + contents + "</div>").css({
        position: "absolute",
        display: "none",
        top: y - 35,
        left: x,
        border: "1px solid #fdd",
        padding: "2px",
        "background-color": "#F3F6FA",
        opacity: 0.80
    }).appendTo("body").fadeIn(200);
}

function pieLabelFormatter(label, series) {
    var pct = Math.round(series.percent);
    return $('<div>' + label + '<br/>' + pct + '%</div>').css({
        "font-size": '8pt',
        "text-align": 'center',
        padding: '2px',
        color: 'white'
    }).html();
    //return "<div style='font-size:8pt; text-align:center; padding:2px; color:white;'>" + label + "<br/>" + Math.round(series.percent) + "%</div>";
}

var prevX = null,
    prevY = null;

$('.plot').on('plothover', function(e, pos, item) {
    if (!item) {
        return false; // hovering outside data
    }

    var x = item.datapoint[0],
        y = item.datapoint[1];

    if (x == prevX && y == prevY) {
        return false; // hovering over the same point
    }

    $('#tooltip').remove();

    prevX = x;
    prevY = y;

    var label = item.series.label + ": " + y;

    if ($(this).is('.plot-bar')) {
        label = y;
    }

    showTooltip(item.pageX, item.pageY, label);

});

$('.plot').each(function(){
    var el = $(this);
    var source = $(this).data('source');

    var options = {
        xaxis: {
            mode: 'time',
            timeformat: "%d.%m",
            minTickSize: [1, "day"]
        },
        lines: {
            show: true,
            fill: false
        },
        points: {
            show: true,
            fill: true
        },
        legend: {
            show: true,
            noColumns: 9,
            container: $(el).next('.legend-container')
        },
        grid: {
            hoverable: true,
            tickColor: "#f9f9f9",
            borderWidth: 0
        },
    };

    $.getJSON(source, function(data) {
        if(el.is(".plot-bar")) {
            options.legend = { show: false };
            options.tooltip = false;
            options.bars = { show: true };
            options.lines = { show: false };
            options.points = { show: false };
            options.xaxis = {
                ticks: data[0].label
            };
        }

        if(el.is(".plot-pie")) {
            options.tooltip = false;
            options.legend = { show: false };
            options.series = {
                pie: {
                    show: true,
                    radius: 1,
                    label: {
                        show: true,
                        radius: 1,
                        formatter: pieLabelFormatter,
                        background: { opacity: 0.8 }
                    }
                }
            };
        }

        $.plot(el, data, options);

    });
});
