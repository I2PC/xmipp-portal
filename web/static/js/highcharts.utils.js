function loadBarChart(container, title, data){

    let options = {
        chart: {
            plotBackgroundColor: null,
            plotBorderWidth: null,
            plotShadow: false,
            type: 'column'
        },
        title: {
            text: title
        },
        xAxis: {
            type: "category"
        },
        // tooltip: {
        //     pointFormat: '{series.name}: <b>{point.y}</b> ({point.percentage:.1f}%)'
        // },
        plotOptions: {
            series: {
                dataLabels: {
                    enabled: true,
                    rotation: -45,
                    color: '#000000',
                    align: 'left',
                    format: '{point.y}', // one decimal
                    y: -10, // 10 pixels down from the top
                    x: 0, // 0 pixels
                    style: {
                        fontSize: '10px',
                        fontFamily: 'Verdana, sans-serif'
                    }
                }
            }
        },
        series: data
    };

    // Build the bar
    $(container).highcharts(options);
}



