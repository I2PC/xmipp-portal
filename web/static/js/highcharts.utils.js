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
                text: 'Number of users',
                style: {
                    fontSize: '12px',
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
                text: 'Installations',
                style: {
                    fontSize: '12px',
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


function prepareSeriesForReleaseDevelPieChart(data, name){
    const series = {
        name: name,
        dataSorting: { enabled: true},
        data: []
    };

    for (let item of data){

        const pie = {
            name: item.xmipp__branch,
            y: item.release_count
        };

        series.data.push(pie);
        }

    return series;
}

function loadReleaseDevelPieChart(container, title, data){

    let options = {
        chart: {
            plotBackgroundColor: null,
            plotBorderWidth: null,
            plotShadow: false,
            type: 'pie',
            zoomType: 'x',
        },
        title: {
            text: title
        },
        colors: ['#c12e2a', '#8e1919', '#540000', '#d9534f', '#DBD9D9', '#808080'],
        series: [data]
    };
    console.log(options)   
    // Build the bar
    Highcharts.chart(container, options);
}

async function loadPieChartPerRelease(chartId, preparedList, release_pie_chart_URL, title) {
    // Group releases per name and consolidate IDs
    const branchesMap = preparedList.reduce((acc, branch) => {
        if (!acc[branch.branch]) {
            acc[branch.branch] = { ...branch, ids: [branch.id] }; // Initialize with IDs list
        } else {
            acc[branch.branch].ids.push(branch.id); // Add ID to the list if release already exists
        }
        return acc;
    }, {});

    // Get container
    const chartsContainer = document.getElementById(chartId);

    // Create graphs for unique branches
    for (const branchName in branchesMap) {
        const branch = branchesMap[branchName];
        
        let combinedData = {};

        // Combine date per each release
        for (const id of branch.ids) {
            // Llamada al endpoint
            const response = await fetch(`${release_pie_chart_URL}${id}`);
            const releaseData = await response.json();

            // Sumar los datos al `combinedData`
            releaseData.forEach(item => {
                const key = item.previous_failures !== null ? `Failures: ${item.previous_failures}` : 'No Failures';
                
                // Sumar el conteo al key correspondiente en `combinedData`
                if (combinedData[key]) {
                    combinedData[key] += item.count;
                } else {
                    combinedData[key] = item.count;
                }
            });
        }

        // Formatear los datos para el gráfico
        const chartData = Object.keys(combinedData).map(key => ({
            name: key,
            y: combinedData[key]
        }));

        // Crear div para contener el gráfico
        const chartDiv = document.createElement('div');
        chartDiv.style.width = '300px';
        chartDiv.style.display = 'inline-flex'; // Todos los gráficos en una fila
        chartDiv.className = 'px-2'; // Espacio
        chartDiv.id = `chart-${branchName.replace(/\s+/g, '-')}`;
        chartsContainer.appendChild(chartDiv);
    
        // Crear gráfico
        Highcharts.chart(chartDiv.id, {
            chart: {
                type: 'pie'
            },
            title: {
                text: `${title}${branchName}`
            },
            colors: ['#c12e2a', '#8e1919', '#540000', '#d9534f', '#DBD9D9', '#808080'],
            series: [{
                name: 'Count',
                colorByPoint: true,
                data: chartData
            }]
        });
    }
}

function prepareXmippReleasesList(data){
    const releaseBranches = data.filter(item => item.branch.startsWith("release"));
    return releaseBranches;
}