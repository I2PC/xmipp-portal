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


function prepareSeriesForTimeChart(data, name) {
    const colorPalette = ['#c12e2a', '#8e1919', '#540000', '#d9534f', '#DBD9D9', '#808080'];
    let seriesData = {};

    function getStartOfWeek(date) {
        const d = new Date(date);
        const day = d.getDay(),
              diff = d.getDate() - day + (day == 0 ? -6 : 1); // El lunes es el primer día de la semana
        d.setDate(diff);
        d.setHours(0, 0, 0, 0);
        return d.getTime(); // Devolvemos el timestamp del lunes
    }
    for (let item of data) {
        const branch = item.xmipp__branch;
        if (!seriesData[branch]) {
            seriesData[branch] = {
                name: branch,
                dataSorting: { enabled: true },
                data: [],
            };
        }
        const weekStart = getStartOfWeek(item.date);
        let found = false;
        for (let entry of seriesData[branch].data) {
            if (entry[0] === weekStart) {
                entry[1]++;
                found = true;
                break;
            }
        }
        if (!found) {
            seriesData[branch].data.push([weekStart, 1]);
        }
    }
    let colorIndex = 0;
    let series = [];
    for (let branch in seriesData) {
        let branchData = seriesData[branch];
        branchData.color = colorPalette[colorIndex];
        let dataArray = [];
        for (let entry of branchData.data) {
            dataArray.push([entry[0], entry[1]]);
        }
        branchData.data = dataArray;
        colorIndex = (colorIndex + 1) % colorPalette.length;
        series.push(branchData);
    }
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
            minRange: 7 * 24 * 3600 * 1000, // Intervalo mínimo de una semana
            tickInterval: 7 * 24 * 3600 * 1000,
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
            minTickInterval: 1,  // Esto asegura que el intervalo mínimo entre marcas de ticks es 1
            allowDecimals: false,  // Esto evitará que los valores del eje Y tengan decimales

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
        colors: ['#c12e2a', '#8e1919', '#540000', '#d9534f', '#DBD9D9', '#808080'],
        series: [data]
    };
    // Build the bar
    Highcharts.chart(container, options);
}
async function loadTimeChartPerRelease(chartId, preparedList, release_pie_chart_URL, title) {
    // Agrupar los lanzamientos por nombre de la rama y consolidar los IDs
    const branchesMap = preparedList.reduce((acc, branch) => {
        if (!acc[branch.branch]) {
            acc[branch.branch] = { ...branch, ids: [branch.id] }; // Inicializar con lista de IDs
        } else {
            acc[branch.branch].ids.push(branch.id); // Agregar ID a la lista si la rama ya existe
        }
        return acc;
    }, {});

    // Obtener el contenedor de los gráficos
    const chartsContainer = document.getElementById(chartId);

    // Crear gráficos para cada rama única
    for (const braemana o fecha
            releaseData.forEach(item => {
                const weekStart = getStartOfWeek(item.date); // Usamos la misma función para obtener la semana

                // Inicializamos el objeto para esa semana si no existe
                if (!combinedData[weekStart]) {
                    combinedData[weekStart] = {};
                }

                const failureKey = item.previous_failures !== null ? `Failures: ${item.previous_failures}` : 'No Failures';

                // Sumar el conteo al failureKey correspondiente
                if (combinedData[weekStart][failureKey]) {
                    combinedData[weekStart][failureKey] += item.count;
                } else {
                    combinedData[weekStart][failureKey] = item.count;
                }
            });
        }

        // Crear el conjunto de datos para el gráfico
        let series = [];
        for (const weekStart in combinedData) {
            const weekData = combinedData[weekStart];

            // Para cada clave de fallo, agregamos una serie
            for (const failureKey in weekData) {
                let existingSeries = series.find(s => s.name === failureKey);
                if (!existingSeries) {
                    existingSeries = { name: failureKey, data: [] };
                    series.push(existingSeries);
                }

                // Agregar el punto de datos (fecha de la semana y el conteo)
                existingSeries.data.push([weekStart, weekData[failureKey]]);
            }
        }

        // Crear un div para contener el gráfico
        const chartDiv = document.createElement('div');
        chartDiv.style.width = '100%';
        chartDiv.style.height = '400px';
        chartDiv.className = 'px-2'; // Espacio
        chartDiv.id = `chart-${branchName.replace(/\s+/g, '-')}`;
        chartsContainer.appendChild(chartDiv);

        // Crear gráfico de líneas con eje datetime
        Highcharts.chart(chartDiv.id, {
            chart: {
                type: 'line'
            },
            title: {
                text: `${title} - ${branchName}`
            },
            xAxis: {
                type: 'datetime',  // Usamos un eje datetime
                title: {
                    text: 'Fecha'
                }
            },
            yAxis: {
                title: {
                    text: 'Conteo'
                },
                min: 0
            },
            series: series,
            colors: ['#c12e2a', '#8e1919', '#540000', '#d9534f', '#DBD9D9', '#808080']
        });
    }
}
function prepareXmippReleasesList(data){
    const releaseBranches = data.filter(item => item.branch.startsWith("release"));
    return releaseBranches;
}