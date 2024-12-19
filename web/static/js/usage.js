function getDataAndDrawCharts(){
    const XMIPP_URL = "https://xmipp.i2pc.es/"

    // Country Bar Chart
    getCountryBarChart(XMIPP_URL);
    getInstallationOverTimeChart(XMIPP_URL);
    installationsReleasesDevel(XMIPP_URL);
    installationsMetricsPerReleaseDevel(XMIPP_URL);
}
;

function getCountryBarChart(XMIPP_URL){

    // Country Bar Chart
    var xmippUsageDataURL = XMIPP_URL + "/api/users/country-bar-chart/";

    $.getJSON( xmippUsageDataURL).done(function( data ) {

        const preparedData = prepareSeriesForBarChart(data, "users by country"); 
        loadBarChart('usersByCountry', 'Number of users per country', preparedData);

    }).fail(function( jqxhr, textStatus, error ) {
        var err = textStatus + ", " + error;
        console.log( "Request Failed: " + err );
    }).always(function() {
        console.log( "complete getCountryBarChart" );
    });
}

function getInstallationOverTimeChart(XMIPP_URL){

    // Installation over time Chart
    var xmippUsageDataURL = XMIPP_URL + "/api/xmipp/installed-branches-time-chart/"; 

    $.getJSON( xmippUsageDataURL).done(function( data ) {

        const preparedData = prepareSeriesForTimeChart(data, "Installations over time");
        console.log("preparedData: ")
        console.log(preparedData)   
        loadTimeChart('installationsOverTime', 'Weekly Installation Attempts by user: Success vs. Failure', preparedData);

    }).fail(function( jqxhr, textStatus, error ) {
        var err = textStatus + ", " + error;
        console.log( "Request Failed: " + err );
    }).always(function() {
        console.log( "complete getInstallationOverTimeChart" );
    });
}

function installationsReleasesDevel(XMIPP_URL){
    // Installations Release and Devel Pie Chart
    var xmippInstallationsDataURL = XMIPP_URL + "/api/xmipp/installed-branches-pie-chart/";

    $.getJSON(xmippInstallationsDataURL).done(function( data ) {

        const preparedData = prepareSeriesForReleaseDevelPieChart(data, "Successfully Installed branches"); 
        loadReleaseDevelPieChart('installationsReleasesDevel', 'Number of branches successfully installed', preparedData);

    }).fail(function( jqxhr, textStatus, error ) {
        var err = textStatus + ", " + error;
        console.log( "Request Failed: " + err );
    }).always(function() {
        console.log( "complete installationsReleasesDevel" );
    });
}

function installationsMetricsPerReleaseDevel(XMIPP_URL){

    // Installation over time Chart
    var installed_branches_list_URL = XMIPP_URL + "/api/xmipp/"; 
    var release_pie_chart_URL = XMIPP_URL + "api/installations/releases-stats-pie-chart/"; 

    $.getJSON(installed_branches_list_URL).done(function( data ) {

        const preparedList = prepareXmippReleasesList(data); // Filter and keep only branches which names start with "release"
        // TODO: sum two version of release counts
        loadPieChartPerRelease("installationsMetricsPerReleaseDevel", preparedList, release_pie_chart_URL, "Installations for ");

    }).fail(function( jqxhr, textStatus, error ) {
        var err = textStatus + ", " + error;
        console.log( "Request Failed: " + err );
    }).always(function() {
        console.log( "complete installationsMetricsPerReleaseDevel" );
    });
}