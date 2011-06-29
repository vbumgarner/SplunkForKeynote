App:                Splunk for Keynote
Current Version:    1.0
Last Modified:      2011-05-27
Splunk Version:     4.1.x, and 4.2.x
Authors:            Vincent Baumgartner and Todd Gow


The Splunk for Keynote app provides the ability to pull in Keynote XML Datafeed data into Splunk and utilize performance reports and dashboards. 

	* Scripts pull the latest 15-minute xml files from the Keynote Datafeed server  

	* XML files are parsed into individual events and organized into the following sourcetypes: keynote_output, keynote_summary, keynote_page and keynote_detail

        * Lookup files are created for agent, slot and error information

 	* Data is inserted into Splunk as individual events of raw text

	* Basic dashboard views are available and can be customized

##### What's New #####

4.2.0 (2011-06-02)
- First Release 

##### Technology Add-on Details ######

Sourcetype(s):
	* keynote_summary
	* keynote_page
	* keynote_detail
	* keynote_output
    
Supported Technologies:     Keynote XML Datafeed service

###### Installation Instructions ######

The Splunk for Keynote app can be downloaded and installed by using the Splunk app setup screen. Apps-->Manage Apps-->Find more apps online 

###### Automated setup using the app setup #####

The automated setup is designed to walk you through the configuration of the Splunk for Keynote app once it is installed on your Splunk deployment.  The setup screen can be accessed in one of the following ways:

1. Select the Keynote app from the App drop down.

2. Select the "Continue to app setup page" link.

3. Enter the User ID (Agreement ID) and Password that you can get from your friendly Keynote Sales Rep.

4. Data will start downloading within minutes. This can take a while depending on how much Keynote data you have. You will probably need to log out and restart Splunk from the command line to get this going properly. $SPLUNK_HOME/bin/splunk restart

5. You can check the default Keynote dashboard (Import Status) for status statistics on the Datafeed XML file download and parsing. 

6. Once all of the Datafeed XML files have been downloaded and parsed then you need to run the following command to populate the summary indexes:

$SPLUNK_HOME/etc/apps/Keynote/bin/backfill.sh


###### Getting Help ######

  * Contact Todd Gow at Splunk ( tgow@splunk.com ) for any issues, complaints, enhancement requests, etc.
  * Questions and answers (Unix app specific): http://answers.splunk.com/questions/tagged/unix
  * Questions and answers (General Splunk): http://answers.splunk.com
  * General support: http://www.splunk.com/support

##### Possible Future Enhancements #####

  * Test the app on Windows
  * Add other data sources such as web log data into the default dashboards
  * Enhance dashboards with additional drop downs (ability to select more than one measurement to compare performance)
  * Put more of the Keynote data into summary indexes to increase performance of dashboard views. 

*** Send me (Todd Gow) any more enhancement requests ***
