import urllib

import tempfile
import os
import sys
import re
import time
import base64

from zipfile import ZipFile

import splunk.bundle as bundle
import splunk.search
import logging

from parse import KeynoteParser

class KeynoteRetriever(object):

    def __init__(self, sessionKey, user, password, lastfile, logger):
        self.user = user
        self.password = password
        self.lastfile = lastfile
        self.url_base = 'https://' + self.user + ':' + self.password + '@datafeed.keynote.com/private/' + self.user + '/trans/xml/latest/'
        self.logger = logger
        self.sessionKey = sessionKey


    def getFileList(self):
        self.logger.debug( "getFileList" )

        f = urllib.urlopen(self.url_base + 'list')
        filelist = f.readlines()
        f.close()

        filelist.sort()

        self.logger.debug( "len(filelist) = %d" , len(filelist) )

        return filelist


    def determineNextFile(self, last_parsed=None):
        self.logger.debug( "determineNextFile parsed=" + str(last_parsed) )

        filelist = self.getFileList()

        #if it's not None, then we're being called in a loop, so no need to query the last
        if last_parsed is None:
            job = splunk.search.dispatch('search index="keynote" sourcetype="keynote_output" action="parsed" filename="*zip" NOT debug | head 1 | fields + filename', sessionKey=self.sessionKey)
            self.logger.debug('Started job ' + str(job) + ' to find last parsed.')
            splunk.search.waitForJob(job, maxtime=240)

            if job.count > 0:
                last_parsed = job.events[0]['filename']
                self.logger.info( "action=found last_parsed=" + str(last_parsed) )
            else:
                self.logger.warn( "Didn't find Successfully parsed in logs. Starting over, unless value found in last_file." )
                last_parsed = '0'

        try:
            lastfile_fh = open(self.lastfile, 'r')
            last_parsed = lastfile_fh.readline()
            lastfile_fh.close()
        except:
            sys.stderr.write( "Something went wrong reading the last file: " + self.lastfile + "\n" )

        for l in filelist:
            s = l.strip()
            self.logger.debug( "Is " + str(s) + " > " + str(last_parsed) + "?" )
            if str(s) > str(last_parsed):
                return s
        return None

    def getFileFromServer(self,filename):
        self.logger.info("action=downloading filename=" + filename)
        tmp_handle = tempfile.NamedTemporaryFile()
#        print filename
#        print 'temp:', tmp_handle
#        print 'temp.name:', tmp_handle.name

        zip_url_handle = urllib.urlopen( self.url_base + filename )
        tmp_handle.write( zip_url_handle.read() )
        zip_url_handle.close()

        return tmp_handle


    def getXmlHandleFromZip(self,file):
        zf = ZipFile(file, 'r')
        first_item = zf.namelist()[0]
        return zf.open( first_item )

    def updateLast(self, filename ):
        self.logger.info("Writing to " + self.lastfile + " action=completed filename=" + filename)
        try:
            last_parsed_file = open(self.lastfile, 'w')
            last_parsed_file.write(filename)
            last_parsed_file.close()
        except:
            sys.stderr.write( "Something went wrong writing the last file: " + self.lastfile + "\n" )

    def firstRun(self):
        firstRunPath = os.path.normcase('../local/firstRun')
        self.logger.debug("Checking firstRun")
        if not os.path.exists(firstRunPath):
            args = [ 'cmd', 'python', os.path.normcase('../../../../bin/fill_summary_index.py'), '-app', 'Keynote', '-name', 'Keynote - summary - KBsec by hour', '-et', '-14day@day', '-lt', '@h', '-dedup', 'true', '-sk', self.sessionKey, '-sleep', '2', '-j', '5' ]
            os.execv(os.path.normcase('../../../../bin/splunk'), args)
            first_run_file = open(firstRunPath, 'w')
            first_run_file.write(firstRunPath)
            first_run_file.close()



#--------------------------------------------------------------
def main():
    startTime = time.time()

    os.chdir( sys.path[0] ) #'/Applications/splunk.4.1.5/etc/apps/Keynote/bin'

    logger = setup_logging("KeynoteRetriever")

    logger.info( "action=starting" )

    try:
        #get the auth
        sessionKey = sys.stdin.readline()
    
        namespace = re.findall('.*[\\/](\w+)[\\/]bin',sys.path[0])[0]
    
        try:
            conf = bundle.getConf('keynote', sessionKey=sessionKey, namespace=namespace, owner='admin') #extract this from sys.path[0], unless there's a better way
            user = conf['keynote']['user']
            password =  base64.decodestring( conf['keynote']['password'].strip() ) 
        except:
            logger.error( "Failed to retrieve keynote config. Use the setup screen in the admin interface to configure. " + str(sys.exc_info()[0]) + "\n" )
            raise

        if user is None or len(user.strip()) == 0 or user == '000000' or password is None or len(password.strip()) == 0:
            logger.error( 'Keynote is not yet configured. Use the setup screen in the admin interface.' )
            return
    
        retriever = KeynoteRetriever(sessionKey, user, password, os.path.normcase('../local/') + user + '.last', logger)
        filename = retriever.determineNextFile()
    
        while filename is not None:
            logger.debug( "Next file is %s" , filename )
            if filename is not None:
                fileStartTime = time.time()

                fh = retriever.getXmlHandleFromZip( retriever.getFileFromServer(filename) )

                try:
                    parser = KeynoteParser()

                    parser.parse_fh( fh , filename )
        
                    retriever.updateLast(filename)
    
                    logger.info( "action=parsed filename=" + filename + " seconds=" + str( time.time() - fileStartTime ) )
                except:
                    raise
                finally:
                    fh.close()
            filename = retriever.determineNextFile(filename)
#            filename = None #uncomment this to limit to one file per run
    
        logger.info( "action=finished seconds=" + str( time.time() - startTime ) )
        retriever.firstRun()
    except:
        e = "Unexpected error (stack trace visible in splunkd.log):" + str(sys.exc_info()[0])
        logger.error( e )
        sys.stderr.write( e + "\n" )
        raise

def setup_logging(n):
    logger = logging.getLogger(n) # Root-level logger
    logger.setLevel(logging.DEBUG)

#    logpath = os.sep.join( ['..','..','..','..','var','log','splunk','Keynote.log'] )
#    logfile = logging.StreamHandler(open( logpath, "a"))
#    logfile.setLevel(logging.INFO)
#    logfile.setFormatter(logging.Formatter('%(asctime)s [%(process)06d] %(levelname)-8s %(name)s:  %(message)s'))
#    logger.addHandler(logfile)

    logstdout = logging.StreamHandler(sys.stdout)
    logstdout.setLevel(logging.INFO)
    logstdout.setFormatter(logging.Formatter('%(asctime)s [%(process)06d] %(levelname)-8s %(name)s:  %(message)s', '%Y-%m-%d %H:%M:%S %Z'))
    logger.addHandler(logstdout)

    return logger

if __name__ == '__main__':
    main()

