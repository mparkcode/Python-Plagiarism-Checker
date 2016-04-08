'''
 The MIT License(MIT)
 
 Copyright(c) 2016 Copyleaks LTD (https://copyleaks.com)
 
 Permission is hereby granted, free of charge, to any person obtaining a copy
 of this software and associated documentation files (the "Software"), to deal
 in the Software without restriction, including without limitation the rights
 to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
 copies of the Software, and to permit persons to whom the Software is
 furnished to do so, subject to the following conditions:
 
 The above copyright notice and this permission notice shall be included in all
 copies or substantial portions of the Software.
 
 THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR
 IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY,
 FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE
 AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER
 LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING FROM,
 OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER DEALINGS IN THE
 SOFTWARE.
'''

import requests
from dateutil import parser

from models.resultrecord import ResultRecord

from consts import Consts
from errors.commandfailederror import CommandFailedError

class CopyleaksProcess(object):
    '''
    Process on Copyleaks servers
    '''

    def __init__(self, loginToken, infoDict):
        self.token = loginToken
        self.PID = infoDict['ProcessId']
        self.CreationTimeUtc = parser.parse(infoDict['CreationTimeUTC'])
        if 'CustomFields' in infoDict:
            self.__setCustomFields(infoDict['CustomFields'])
        
    def getPID(self):
        return self.PID
    def __setPID(self, value):
        self.PID = value
        
    def getCreationTimeUtc(self):
        return self.CreationTimeUtc
    def __setCreationTimeUtc(self, value):
        self.CreationTimeUtc = value
    
    def getCustomFields(self):
        return self.CustomFields
    def __setCustomFields(self, value):
        self.CustomFields = value
    
    def isCompleted(self):
        '''
            Checks if the operation has been completed
        '''
        serviceUrl = '%s%s/detector/%s/status' % (Consts.SERVICE_ENTRY_POINT, Consts.SERVICE_VERSION, self.getPID())
        headers = {
            Consts.AUTHORIZATION_HEADER: self.token.generateAuthrizationHeader()
        }
            
        response = requests.get(serviceUrl, headers=headers)
        if (response.status_code == Consts.HTTP_SUCCESS):
            iscompleted = response.json()['Status'] == 'Finished'
            return [iscompleted, response.json()['ProgressPercents']]
        else:
            raise CommandFailedError(response) 

    def getResutls(self):
        '''
            Get the scan resutls from server.
        '''
        serviceUrl = '%s%s/detector/%s/result' % (Consts.SERVICE_ENTRY_POINT, Consts.SERVICE_VERSION, self.getPID())
        headers = {
            Consts.AUTHORIZATION_HEADER: self.token.generateAuthrizationHeader()
        }
            
        response = requests.get(serviceUrl, headers=headers)
        if (response.status_code == Consts.HTTP_SUCCESS):
            return ResultRecord.parseResults(response.json());
        else:
            raise CommandFailedError(response) 
        
    def delete(self):
        '''
            Deletes the process once it has finished running
        '''
        serviceUrl = '%s%s/detector/%s/delete' % (Consts.SERVICE_ENTRY_POINT, Consts.SERVICE_VERSION, self.getPID())
        headers = {
            Consts.AUTHORIZATION_HEADER: self.token.generateAuthrizationHeader()
        }
            
        response = requests.delete(serviceUrl, headers=headers)
        if (response.status_code != Consts.HTTP_SUCCESS):
            raise CommandFailedError(response)
        
    @staticmethod
    def parseProcesses(token, processes):
        lst = []
        
        for process in processes:
            lst.append(CopyleaksProcess(token, process))
        
        return lst