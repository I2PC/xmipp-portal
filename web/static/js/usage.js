function getDataAndDrawCharts(){
    // From: https://xmipp.i2pc.es/api/users/country-bar-chart/
    var xmippUsageDataURL = "https://xmipp.i2pc.es/api/users/country-bar-chart/";

    console.log("HOLA!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!!")

    $.getJSON( xmippUsageDataURL).done(function( data ) {

        loadBarChart('#usersByCountry', 'Number of users per country', data);

    }).fail(function( jqxhr, textStatus, error ) {
        var err = textStatus + ", " + error;
        console.log( "Request Failed: " + err );
    }).always(function() {
        console.log( "complete" );
    });
};

$(window).ready(function(){
    getDataAndDrawCharts();
});