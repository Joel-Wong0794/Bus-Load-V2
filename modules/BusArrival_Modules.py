# For Bus Arrival App
import urllib.request, json
import httplib2 as http #External library
from urllib.parse import urlparse
import pandas as pd

def BusStopList_df():
    headers = { 'AccountKey' : 'iu9Da+lnTES9dh66RZYupA==',
               'accept' : 'application/json'} #this is by default

    # 1 to 500th: BS Info.
    #API parameters
    uri = 'http://datamall2.mytransport.sg' #Resource URL
    skip_operator1=""
    path = '/ltaodataservice/BusStops'+ skip_operator1
    #Build query string & specify type of API call
    target = urlparse(uri + path)
    # print(target.geturl())
    method = 'GET'
    body = ''
    
    #Get handle to http
    h = http.Http(".cache")
    #Obtain results
    response, content = h.request(
        target.geturl(),
        method,
        body,
        headers)

    # #Parse JSON to print
    json_output = json.loads(content)
    # Extract only the value
    json_output = json_output["value"]
    
    BS_List = {}
    for i in range(len(json_output)):
        BS_List[json_output[i]["BusStopCode"]] = json_output[i]
        
    # 501 to last (until no more to extract): BS Info.
    increment = 500
    while json_output != []:
        #API parameters
        uri = 'http://datamall2.mytransport.sg' #Resource URL
        skip_operator2="?$skip="+ str(increment)
        path = '/ltaodataservice/BusStops'+ skip_operator2
        #Build query string & specify type of API call
        target = urlparse(uri + path)
        # print(target.geturl())
        method = 'GET'
        body = ''
        
        #Get handle to http
        h = http.Http()
        #Obtain results
        response, content = h.request(
            target.geturl(),
            method,
            body,
            headers)
        
        # #Parse JSON to print
        json_output = json.loads(content)
        # Extract only the value
        json_output = json_output["value"]
        
        for i in range(len(json_output)):
            BS_List[json_output[i]["BusStopCode"]] = json_output[i]
        increment +=500 # Step up to the next 500 x BusStops
    # -----------------------------------------------------------------------------------------------------------------------------------------
    ## OUTPUT ##
    # -----------------------------------------------------------------------------------------------------------------------------------------

    return pd.DataFrame.from_dict(BS_List,orient="index") # Converts Dictionary to Pandas Dataframe.


def BusArrival_LTA(BSCODE):
    #------------------------------------------------------------------------------------------------
    # LTA Datamall - live bus arrival
    #----------------------------------------------------------------------------------------------------
    # Authentication parameters - joel_wong@lta.gov.sg
    headers = { 'AccountKey' : 'v6w89/j9RmK3xATjl9S5GQ==',
    'accept' : 'application/json'} #this is by default

    #API parameters
    uri = 'http://datamall2.mytransport.sg' #Resource URL
    path = '/ltaodataservice/BusArrivalv2?BusStopCode='+ str(BSCODE)
    #Build query string & specify type of API call
    target = urlparse(uri + path)
    method = 'GET'
    body = ''

    #Get handle to http
    h = http.Http()
    #Obtain results
    response, content = h.request(
        target.geturl(),
        method,
        body,
        headers)

    # #Parse JSON to print
    # global BS_Arrival_LTA
    return json.loads(content)

def ArriveLah(BSCode_Input):
    #----------------------------------------------------------------------------------------------------
    # ArriveLah API
    #----------------------------------------------------------------------------------------------------
    uri = 'https://arrivelah2.busrouter.sg' #Resource URL
    path = '/?id='+ BSCode_Input
    #Build query string & specify type of API call
    target = urlparse(uri + path)
    method = 'GET'
    body = ''

    #Get handle to http
    h = http.Http()
    #Obtain results
    response, content = h.request(
        target.geturl(),
        method,
        body)

    # Parse JSON to print
    return json.loads(content)