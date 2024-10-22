function prepareSeriesForBarChart(data, name){

    const series = {
        name: name,
        dataSorting: { enabled: true},
        data: []
    };


    for (let item of data){

        const pie = {
            name: item.country,
            y: item.users_count
        };

        series.data.push(pie);
        }

    return series;

}

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
                color: '#8e1919',
                dataLabels: {
                    enabled: true,
                    rotation: 0,
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
        series: [data]
    };
    console.log(options)   
    // Build the bar
    Highcharts.chart(container, options);
    // $(container).highcharts(options);
}



