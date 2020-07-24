from flask import Flask
from flask import Flask, render_template, jsonify, request,make_response
import os
dir_path = os.path.dirname(os.path.realpath(__file__))
import pandas as pd
import json
from datetime import datetime
from datetime import timedelta  
# For MongoDB
from flask_pymongo  import pymongo

# Import Python Modules
from modules.BusArrival_Modules import BusArrival_LTA,ArriveLah,BusStopList_df
# ------------------------

#-------------------------------------------
# A) IMPORT Required Files
#-------------------------------------------
# ------------------------
# ! Update Name of files Here !
# ------------------------
# Name: 1) BusService List with Frequency
name_BusSvcFreq_List = "BusServices_Excel (as of 2020-07-17).xlsx"
name_ridership_data = "LTAMall_Ridership_Data_Jun2020.geojson"
# ------------------------

# 1) Unique BCM Vlookup List
BusService_List = pd.read_excel('https://docs.google.com/spreadsheets/u/2/d/1Z7Q5JiT0tPpSEaIEP65I8JeJQRjWjoKI/export?format=xlsx&id=1Z7Q5JiT0tPpSEaIEP65I8JeJQRjWjoKI',sheet_name= 'Services')
BusService_List["Bus Service No."] = BusService_List["Bus Service No."].astype(str)

# 2) BusService List with Frequency (from LTA Mall)
# Used for Looping Svc Description & for Bus Frequency
BusSvcFreq_List = pd.read_excel(dir_path+"/static/data/"+name_BusSvcFreq_List)

# 3) Pre-load Ridership Data
with open(dir_path+"/static/data/" + name_ridership_data) as f:
    #ridership_data = geojson.load(f)
    ridership_data = json.load(f)

# 4) List of Bus Stops
df_BusStop = BusStopList_df()
#-------------------------------------------

# Start App
app = Flask(__name__)

# How to set config variables: https://www.youtube.com/watch?v=GW_2O9CrnSU
# CHANGE CONFIG based on 
if app.config["ENV"] == "production":
    # CONFIG IMPORTS
    app.config.from_object("config.ProductionConfig")
elif app.config["ENV"] == "testing":
    # CONFIG IMPORTS
    app.config.from_object("config.TestingConfig")
elif app.config["ENV"] == "development":
    # CONFIG IMPORTS
    app.config.from_object("config.DevelopmentConfig")

# MONGO DB
CONNECTION_STRING = app.config["DB_NAME"]
client = pymongo.MongoClient(CONNECTION_STRING)
db = client.get_database('GISData-Test1')
user_collection = pymongo.collection.Collection(db, app.config["DB_COLLECTION"]) # Goes down to specific collection
#-------------------------------------------
# B) HOME PAGE - Map
#-------------------------------------------
@app.route('/')
def index():
    print(app.config["ENV"])
    return render_template('index.html')

#-------------------------------------------
# C) Fetch User BSCODE Input
#-------------------------------------------
# Flask & the Fetch API 
# https://www.youtube.com/watch?v=QKcVjdLEX_s
@app.route('/BusArrival', methods=['POST'])
def BusArrival_Function():
    #-------------------------------------------
    # Bus Arrival Portion
    #-------------------------------------------
    req = request.get_json() # When /BusArrival receives POST.
    print(req)
    # # TESTING - Adding Data to Database
    # req['comments'] = "Testing Comments"
    # db.db.collection.insert_one(req)

    # Using Bus Arrival - LTA API
    # Note: To obtain Destination.
    LTA_Raw_BusArrival = BusArrival_LTA(req["BSCODE"])
    # Using ArriveLah.
    ArriveLah_Raw_BusArrival = ArriveLah(req["BSCODE"]) ## Using ArriveLah API.
    Service_List = []
    ArrivalTime_List = []
    Direction_List = []

    # From Frequency Bus Stop df
    LoopDes_List = []
    # Frequency Lists
    AMPeak_List = []
    AMOffpeak_List = []
    PMPeak_List = []
    PMOffpeak_List = []

    Number_Svcs = 0
    for i in range(len(ArriveLah_Raw_BusArrival["services"])):

        # LTA API
        Direction_Code = LTA_Raw_BusArrival["Services"][i]["NextBus"]["DestinationCode"]
        ArrivalTime = int(round(ArriveLah_Raw_BusArrival["services"][i]["next"]["duration_ms"]/(60*1000),0))
        BusType = ArriveLah_Raw_BusArrival["services"][i]["next"]["type"]
        if ArrivalTime <= 1:
            ArrivalTime = "ARR" + " ("+ BusType +")"
        else:
            ArrivalTime = str(ArrivalTime) + " min" + " ("+ BusType +")"
        ArrivalTime_List.append(ArrivalTime)

        Svc_Raw = ArriveLah_Raw_BusArrival["services"][i]["no"]

        try:
            LoopDes_Raw = BusSvcFreq_List[BusSvcFreq_List["SvcNo_Dest"]==str(Svc_Raw)+"_"+str(Direction_Code)]["LoopDes"].values[0]
        except IndexError:
            LoopDes_Raw = ""

        if (isinstance(LoopDes_Raw, str)):
            LoopDes_List.append(LoopDes_Raw)
        else:
            LoopDes_List.append("")

        # Frequency Timings
        AM_Peak_Freq_Raw = BusSvcFreq_List[BusSvcFreq_List["SvcNo_Dest"]==str(Svc_Raw)+"_"+str(Direction_Code)]["AM_Peak_Freq"].values[0]
        AM_Offpeak_Freq_Raw = BusSvcFreq_List[BusSvcFreq_List["SvcNo_Dest"]==str(Svc_Raw)+"_"+str(Direction_Code)]["AM_Offpeak_Freq"].values[0]
        PM_Peak_Freq_Freq_Raw = BusSvcFreq_List[BusSvcFreq_List["SvcNo_Dest"]==str(Svc_Raw)+"_"+str(Direction_Code)]["PM_Peak_Freq"].values[0]
        PM_Offpeak_Freq_Freq_Raw = BusSvcFreq_List[BusSvcFreq_List["SvcNo_Dest"]==str(Svc_Raw)+"_"+str(Direction_Code)]["PM_Offpeak_Freq"].values[0]
        AMPeak_List.append(AM_Peak_Freq_Raw + " min")
        AMOffpeak_List.append(AM_Offpeak_Freq_Raw + " min")
        PMPeak_List.append(PM_Peak_Freq_Freq_Raw + " min")
        PMOffpeak_List.append(PM_Offpeak_Freq_Freq_Raw + " min")

        # Services List
        Service_List.append(Svc_Raw)
        Direction_List.append(str(Direction_Code))
        Number_Svcs += 1

    # Create DataFrame
    df_BusArrival = pd.DataFrame(list(zip(Service_List,Direction_List,ArrivalTime_List,LoopDes_List,AMPeak_List,AMOffpeak_List,PMPeak_List,PMOffpeak_List)), 
               columns =['Services', 'Direction','ArrivalTime','LoopDes','AM_Peak_Freq','AM_Offpeak_Freq','PM_Peak_Freq','PM_Offpeak_Freq']) 
    
    
    # merge with BS Description
    df_BusArrival = df_BusArrival.merge(df_BusStop, left_on="Direction",right_on="BusStopCode", how = "left", indicator = False)
    # Merge with BCM package
    df_BusArrival = df_BusArrival.merge(BusService_List, left_on="Services",right_on="Bus Service No.", how = "left", indicator = False)

    # Concatenate Direction with LoopingDes
    df_BusArrival['Final_Direction'] = df_BusArrival["Description"] + "<br>" + df_BusArrival["LoopDes"]

    # Sort Dataframe by Service, then Package
    df_BusArrival = df_BusArrival.loc[pd.to_numeric(df_BusArrival["Services"], errors='coerce').sort_values(ascending=True).index] #https://stackoverflow.com/questions/47913881/
    df_BusArrival.sort_values(["Contract"],inplace = True,ascending=True)

    print(df_BusArrival)

    # Convert to lists
    Service_List = df_BusArrival["Services"].to_list()
    ArrivalTime_List = df_BusArrival["ArrivalTime"].to_list()
    Package_List = df_BusArrival["Package Name"].to_list()
    Direction_List = df_BusArrival["Final_Direction"].to_list()
    AMPeak_List = df_BusArrival["AM_Peak_Freq"].to_list()
    AMOffpeak_List = df_BusArrival["AM_Offpeak_Freq"].to_list()
    PMPeak_List = df_BusArrival["PM_Peak_Freq"].to_list()
    PMOffpeak_List = df_BusArrival["PM_Offpeak_Freq"].to_list()

    #-------------------------------------------

    #-------------------------------------------
    # Plotly z list -  based on BSCODE selected
    #-------------------------------------------
    zList_raw = {}
    for i in range(len(ridership_data["features"])):
        # WEEKDAY
        if ((ridership_data['features'][i]['properties']['PT_CODE']==req["BSCODE"]) and (ridership_data['features'][i]['properties']['DAY_TYPE']=="WEEKDAY")):
            tapIn_Identifier = "tapIn"+"WEEKDAY" + "_"+str(ridership_data['features'][i]['properties']["TIME_PER_HOUR"])
            zList_raw[tapIn_Identifier] = ridership_data['features'][i]['properties']["TOTAL_TAP_IN_VOLUME"]
        # WEEKENDS/PH
        elif ((ridership_data['features'][i]['properties']['PT_CODE']==req["BSCODE"]) and (ridership_data['features'][i]['properties']['DAY_TYPE']=="WEEKENDS/HOLIDAY")):
            tapIn_Identifier = "tapIn"+"WEEKENDS/HOLIDAY" + "_"+str(ridership_data['features'][i]['properties']["TIME_PER_HOUR"])
            zList_raw[tapIn_Identifier] = ridership_data['features'][i]['properties']["TOTAL_TAP_IN_VOLUME"]
    #-------------------------------------------

    #-------------------------------------------
    # Construct json Response
    #-------------------------------------------
    res = make_response(jsonify(
        {
            "Number_Svcs":Number_Svcs,
            "Services":Service_List,
            "ArrivalTime":ArrivalTime_List,
            "Packages":Package_List,
            "Direction":Direction_List,
            "zList_raw":zList_raw,
            "AM_Peak_Freq":AMPeak_List,
            "AM_Offpeak_Freq": AMOffpeak_List,
            "PM_Peak_Freq": PMPeak_List,
            "PM_Offpeak_Freq": PMOffpeak_List
        }),200)
    #-------------------------------------------

    return res # Return back to JavaScript for Bus Arrival Data for selected BSCode.

#-------------------------------------------
# D) MONGODB Link Route
#-------------------------------------------
@app.route('/AddData', methods=['POST'])
def flask_mongodb_atlas():
    req = request.get_json() # When /AddData receives POST.
    # dd/mm/YY H:M:S
    now = datetime.now() + timedelta(hours=8)
    dt_string = '{:%d/%m/%Y (%H:%M:%S)}'.format(now)
    req['dt_string'] = dt_string
    req['comments'] = "Getting via /AddData"
    print(req)
    user_collection.insert_one(req) # Drills down to specific collection
    return ""


if __name__ == '__main__':
    app.run()