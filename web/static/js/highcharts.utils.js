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
            type: "category",
            labels: {
                style: {
                    fontSize: '12px', 
                },
                rotation: -45
            }
        },
        yAxis: {
            title: {
                text: 'Number of users',  // Cambia el texto del título del eje Y
                style: {
                    fontSize: '12px',  // Cambia el tamaño del título del eje Y aquí
                    fontFamily: 'Verdana, sans-serif'
                }
            }
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
    // Build the bar
    Highcharts.chart(container, options);
    // $(container).highcharts(options);
}


function prepareSeriesForTimeChart(data, name){

    series = {
        name: name,
        dataSorting: { enabled: true},
        data: []
        }
    
    // Get unique list of xmipp branches
    // Fill with data processing
    return series;
}

function loadTimeChart(container, title, data){

    let options = {
        chart: {
            plotBackgroundColor: null,
            plotBorderWidth: null,
            plotShadow: false,
            type: 'line',
            zoomType: 'x',
        },
        title: {
            text: title
        },
        xAxis: {
            type: "datetime",
            labels: {
                style: {
                    fontSize: '12px', 
                },
            }
        },
        yAxis: {
            title: {
                text: 'Installations',  // Cambia el texto del título del eje Y
                style: {
                    fontSize: '12px',  // Cambia el tamaño del título del eje Y aquí
                    fontFamily: 'Verdana, sans-serif'
                }
            }
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


function drawPieChartPerRelease(chartId, preparedList, release_pie_chart_URL){
    // Get container
    const chartsContainer = document.getElementById(chartId);

    // Create pie chart per release
    preparedList.forEach(async (branch, index) => {

        // Call release endpoint
        const response = await fetch(`${release_pie_chart_URL}${branch.id}`);
        const releaseData = await response.json();

        // Prepare data for the chart
        const chartData = releaseData.map(item => ({
            name: item.previous_failures !== null ? `Failures: ${item.previous_failures}` : 'No Failures',
            y: item.count
        }));

        // Create div to contain the graph
        const chartDiv = document.createElement('div');
        chartDiv.style.width = '300px'; 
        chartDiv.style.display = 'inline-flex'; // All graphs in one row
        chartDiv.className = 'px-2'; // Space
        chartDiv.id = `chart-${index}`;
        chartsContainer.appendChild(chartDiv);
    
        // Create graph
        Highcharts.chart(chartDiv.id, {
            chart: {
                type: 'pie'
            },
            title: {
                text: `Branch: ${branch.branch}`
            },
            series: [{
                name: 'Count',
                colorByPoint: true,
                data: chartData
            }]
        });
    });

}

function prepareXmippReleasesList(data){
    const releaseBranches = data.filter(item => item.branch.startsWith("release"));
    return releaseBranches;
}