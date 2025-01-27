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
        legend: {
            itemStyle: {
                fontSize: '0px', // Ajusta el tamaño del texto de la leyenda
                fontFamily: 'Verdana, sans-serif',
            },
            itemHoverStyle: {
                color: '#333333', // Cambia el color al pasar el mouse (opcional)
            }
        },
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


function prepareSeriesForTimeChart(data, name) {
    console.log(data);
    let colors= ['#878787','#c12e2a', '#F6AE2D','#4F1271', '#B8E2C8', '#8e1919', '#540000', '#d9534f', '#808080'];
    let colorIndex = 0;
    // Sort by date
    data.sort((a, b) => {
        const dateA = a.date ? new Date(a.date) : null;
        const dateB = b.date ? new Date(b.date) : null;
        return dateA - dateB;
    });

    // Get start of the week
    function getStartOfWeek(date) {
        const d = new Date(date);
        const day = d.getDay();
        const diff = d.getDate() - day + (day == 0 ? -6 : 1);
        d.setDate(diff);
        d.setHours(0, 0, 0, 0);
        return d;
    }

    function lightenColor(hex, factor) {
    let r = parseInt(hex.slice(1, 3), 16);
    let g = parseInt(hex.slice(3, 5), 16);
    let b = parseInt(hex.slice(5, 7), 16);

    r = Math.min(255, r + factor);
    g = Math.min(255, g + factor);
    b = Math.min(255, b + factor);

    return `#${(1 << 24 | r << 16 | g << 8 | b).toString(16).slice(1).toUpperCase()}`;
    }

    let series = {};

    for (let item of data) {
        const branch = item.xmipp__branch;
        const returnCode = item.returnCode;
        const weekStart = getStartOfWeek(item.date);
        const weekStamp = weekStart.getTime();

        const branchKey = branch;

        if (!series[branchKey]) {
            const successColor = colors[colorIndex % colors.length];
            series[branchKey] = {
                success: {
                    name: `${branch} success`,
                    dataSorting: { enabled: false },
                    data: [],
                    color: successColor,
                    dashStyle: 'Solid',
                    marker: { symbol: 'circle' }
                },
                fails: {
                    name: `${branch} fails`,
                    dataSorting: { enabled: false },
                    data: [],
                    color: lightenColor(successColor, 50),
                    marker: { symbol: 'triangle-down' }
                }
            };
            colorIndex++;
        }

        const targetSeries = returnCode === 0 ? series[branchKey].success : series[branchKey].fails;

        let found = false;
        for (let [index, entry] of targetSeries.data.entries()) {
            if (entry.x === weekStamp) {
                targetSeries.data[index].y += 1;
                found = true;
                break;
            }
        }

        if (!found) {
            targetSeries.data.push({ x: weekStamp, y: 1 });
        }
    }

    for (const branchKey in series) {
        series[branchKey].success.data.sort((a, b) => a.x - b.x);  // Ordenar por fecha
        series[branchKey].fails.data.sort((a, b) => a.x - b.x);  // Ordenar por fecha
    }

    let resultSeries = [];
    for (const branchKey in series) {
        resultSeries.push(series[branchKey].success);
        resultSeries.push(series[branchKey].fails);
    }

    console.log(resultSeries);
    return resultSeries;
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
//            minRange:  3600 * 1000, // Intervalo mínimo de una semana
//            tickInterval:  3600 * 1000,
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
            },
            //minTickInterval: 1,  // Esto asegura que el intervalo mínimo entre marcas de ticks es 1
            allowDecimals: false,  // Esto evitará que los valores del eje Y tengan decimales

        },
        // tooltip: {
        //     pointFormat: '{series.name}: <b>{point.y}</b> ({point.percentage:.1f}%)'
        // },
        legend: {
            itemStyle: {
                fontSize: '12px', // Ajusta el tamaño del texto de la leyenda
                fontFamily: 'Verdana, sans-serif',
            },
            itemHoverStyle: {
                color: '#333333', // Cambia el color al pasar el mouse (opcional)
            }
        },
        plotOptions: {
            series: {
                connectNulls: false,
                color: '#8e1919',
                dataLabels: {
                    enabled: true,
                    rotation: 0,
                    color: '#000000',
                    align: 'left',
                    //format: '{point.y}', // one decimal
                    y: -10, // 10 pixels down from the top
                    x: 0, // 0 pixels
                    style: {
                        fontSize: '12px',
                        fontFamily: 'Verdana, sans-serif'
                    }
                }
            }
        },
        series: data
    };
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
        plotOptions: {
            pie: {
                allowPointSelect: true,
                cursor: 'pointer',
                dataLabels: {
                    enabled: true,
                    format: '{point.name}',
                    style: {
                        fontSize: '11px',
                        fontFamily: 'Verdana, sans-serif',
                    }
                }
            }
        },
        colors: ['#c12e2a', '#878787', '#F6AE2D','#4F1271', '#B8E2C8', '#8e1919', '#540000', '#d9534f', '#808080'], //move 1 position the gray #878787 if new release appear

        series: [data]
    };
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
        
        let combinedData = { 
            'Successful': 0,
            'Failed': 0
        };

        // Combine date per each release
        for (const id of branch.ids) {
            // Llamada al endpoint
            const response = await fetch(`${release_pie_chart_URL}${id}`);
            const releaseData = await response.json();

            // Sume data
            releaseData.forEach(item => {
                if (item.successfull_installations !== undefined) {
                    combinedData['Successful'] += item.successfull_installations;
                }
                if (item.failed_installations !== undefined) {
                    combinedData['Failed'] += item.failed_installations;
                }
            });
        }

        // Formate data
        const chartData = Object.keys(combinedData).map(key => ({
            name: key,
            y: combinedData[key]
        }));

        // Create div to include graph
        const chartDiv = document.createElement('div');
        chartDiv.style.width = '300px';
        chartDiv.style.display = 'inline-flex'; // Todos los gráficos en una fila
        chartDiv.className = 'px-2'; // Espacio
        chartDiv.id = `chart-${branchName.replace(/\s+/g, '-')}`;
        chartsContainer.appendChild(chartDiv);
    
        // Create graph
        Highcharts.chart(chartDiv.id, {
            chart: {
                type: 'pie'
            },
            title: {
                text: `${title}${branchName}`
            },
            colors: ['#c12e2a', '#623CEA'], 
            series: [{
                name: 'Count',
                colorByPoint: true,
                data: chartData,
                dataLabels: {
                    enabled: true,
                    style: {
                        fontSize: '10px',
                    }
                }
            }]
        });
    }
}

async function loadPieChartPerReleaseDetail(chartId, preparedList, release_pie_chart_URL, title) {
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

        let combinedData = {
            'Successful': 0,
            'Failed': 0,
            'SuccessAfterFails': 0
        };

        // Combine date per each release
        for (const id of branch.ids) {
            // Llamada al endpoint
            const response = await fetch(`${release_pie_chart_URL}${id}`);
            const releaseData = await response.json();

            // Sume data
            releaseData.forEach(item => {
                if (item.successfull_installations !== undefined) {
                    combinedData['Successful'] += item.full_success;
                }
                if (item.failed_installations !== undefined) {
                    combinedData['SuccessAfterFails'] += item.success_after_fails;
                }
                if (item.failed_installations !== undefined) {
                    combinedData['Failed'] += item.fail;
                }
            });
        }

        // Formate data
        const chartData = Object.keys(combinedData).map(key => ({
            name: key,
            y: combinedData[key]
        }));

        // Create div to include graph
        const chartDiv = document.createElement('div');
        chartDiv.style.width = '300px';
        chartDiv.style.display = 'inline-flex'; // Todos los gráficos en una fila
        chartDiv.className = 'px-2'; // Espacio
        chartDiv.id = `chart-${branchName.replace(/\s+/g, '-')}`;
        chartsContainer.appendChild(chartDiv);

        // Create graph
        Highcharts.chart(chartDiv.id, {
            chart: {
                type: 'pie'
            },
            title: {
                text: `${title}${branchName}`
            },
            colors: ['#c12e2a','#ffffff', '#623CEA' ],
            series: [{
                name: 'Count',
                colorByPoint: true,
                data: chartData,
                dataLabels: {
                    enabled: true,
                    style: {
                        fontSize: '10px',
                    }
                }
            }]
        });
    }
}





function prepareXmippReleasesList(data){
    const releaseBranches = data.filter(item => item.branch.startsWith("v3."));
    return releaseBranches;
}