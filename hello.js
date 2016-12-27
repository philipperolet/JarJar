var page = require('webpage').create();

// Connects to monoprix
timer = Date.now();
page.open('http://www.monoprix.fr', function(status) {
    
    timeLap = Date.now();
    console.log("Loading monop : " + (timeLap - t)/1000 + "sec");
    console.log('Status: ' + status);
    page.includeJs("http://ajax.googleapis.com/ajax/libs/jquery/1.6.1/jquery.min.js", function() {
	console.log("jQuery injection : " + (Date.now()-timeLap()));
	if (status != 'success') {
	    console.log('Failed to open the page');
	} else {
	    var testValue = page.evaluate(function() {
		$('.dropdown.compte').click();
		return "Bouh";
	    });
	    console.log("Title : " + testValue);
	}
    })
    phantom.exit();
});


