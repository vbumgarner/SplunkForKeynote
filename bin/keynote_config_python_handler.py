import splunk.admin as admin
import splunk.entity as en
import base64
# import your required python modules

'''
Copyright (C) 2005 - 2010 Splunk Inc. All Rights Reserved.
Description:    This skeleton python script handles the parameters in the configuration page.
                handleList method: lists configurable parameters in the configuration page
                                   corresponds to handleractions = list in restmap.conf
                handleEdit method: controls the parameters and saves the values 
                                   corresponds to handleractions = edit in restmap.conf

'''


class KeynoteConfigApp(admin.MConfigHandler):
    '''
    Set up supported arguments
    '''
    def setup(self):
        if self.requestedAction == admin.ACTION_EDIT:
            for arg in ['user', 'password']:
                self.supportedArgs.addOptArg(arg)

    '''
    Read the initial values of the parameters from the custom file myappsetup.conf
    and write them to the setup screen. 
    If the app has never been set up, uses <appname>/default/myappsetup.conf. 
    If app has been set up, looks at local/myappsetup.conf first, then looks at 
    default/myappsetup.conf only if there is no value for a field in local/myappsetup.conf

    For boolean fields, may need to switch the true/false setting
    For text fields, if the conf file says None, set to the empty string.
    '''
    def handleList(self, confInfo):
        confDict = self.readConf('keynote')
        if None != confDict:
            for stanza, settings in confDict.items():
                for key, val in settings.items():
#                    if key in ['field_2_boolean']:
#                        if int(val) == 1:
#                            val = '0'
#                        else:
#                            val = '1'
                    if key in ['user','password'] and val in [None, '']:
                        val = ''
                    if key == 'password':
                        val = ''
                        if len(val.strip())>0:
                            try:
                                val = base64.decodestring( val.strip() )
                            except:
                                val = 'failed decoding password'

                    confInfo[stanza].append(key, val)

    '''
    After user clicks Save on setup screen, take updated parameters, normalize them, and 
    save them somewhere
    '''
    def handleEdit(self, confInfo):
        name = self.callerArgs.id
        args = self.callerArgs

#        if int(self.callerArgs.data['field_3'][0]) < 60:
#            self.callerArgs.data['field_3'][0] = '60'
                
#        if int(self.callerArgs.data['field_2_boolean'][0]) == 1:
#            self.callerArgs.data['field_2_boolean'][0] = '0'
#        else:
#            self.callerArgs.data['field_2_boolean'][0] = '1'

        self.normalizeStringFields(['user','password'], self.callerArgs.data)
        self.callerArgs.data['password'][0] = base64.encodestring( self.callerArgs.data['password'][0] )

        '''
        Since we are using a conf file to store parameters, write them to the [setupentity] stanza
        in <appname>/local/myappsetup.conf  
        '''

        self.writeConf('keynote', 'keynote', self.callerArgs.data)

        

    def normalizeStringFields(self, fieldNames, data):
        for f in fieldNames:
            v = data[f][0]
            if v is None:
                v = ''
            data[f][0] = v.strip()

# initialize the handler
admin.init(KeynoteConfigApp, admin.CONTEXT_APP_ONLY) #admin.CONTEXT_NONE)


