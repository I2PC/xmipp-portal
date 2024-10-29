function getDataAndDrawCharts(){
    const XMIPP_URL = "http://127.0.0.1:8000/"

    // Country Bar Chart
    getCountryBarChart(XMIPP_URL);
    getInstallationOverTimeChart(XMIPP_URL);
}
;

function getCountryBarChart(XMIPP_URL){

    // Country Bar Chart
    var xmippUsageDataURL = XMIPP_URL + "/api/users/country-bar-chart/";

    $.getJSON( xmippUsageDataURL).done(function( data ) {

        const preparedData = prepareSeriesForBarChart(data, "users by country"); 
        console.log(preparedData)   
        loadBarChart('usersByCountry', 'Number of users per country', preparedData);

    }).fail(function( jqxhr, textStatus, error ) {
        var err = textStatus + ", " + error;
        console.log( "Request Failed: " + err );
    }).always(function() {
        console.log( "complete" );
    });
}

function getInstallationOverTimeChart(XMIPP_URL){

    // Installation over time Chart
    var xmippUsageDataURL = XMIPP_URL + "/api/xmipp/installed-branches-time-chart/"; 

    $.getJSON( xmippUsageDataURL).done(function( data ) {

        const preparedData = prepareSeriesForTimeChart(data, "Installations over time"); 
        console.log(preparedData)   
        loadTimeChart('installationsOverTime', 'Installations over time', preparedData);

    }).fail(function( jqxhr, textStatus, error ) {
        var err = textStatus + ", " + error;
        console.log( "Request Failed: " + err );
    }).always(function() {
        console.log( "complete" );
    });
}