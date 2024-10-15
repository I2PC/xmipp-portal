function getDataAndDrawCharts(){
    // From: https://xmipp.i2pc.es/api/users/country-bar-chart/
    var xmippUsageDataURL = "https://xmipp.i2pc.es/api/users/country-bar-chart/"; //TODO: change URL to production URL

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
};

// $(window).ready(function(){
//     getDataAndDrawCharts();
// });