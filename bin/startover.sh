../../../../bin/splunk stop
../../../../bin/splunk clean eventdata -f -index keynote
../../../../bin/splunk clean eventdata -f -index keynote_summary
rm ../local/*.last
rm ../local/firstRun
../../../../bin/splunk start

