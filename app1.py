from flask import Flask
from flask import Flask, render_template, jsonify, request,make_response
import os
dir_path = os.path.dirname(os.path.realpath(__file__))
import pandas as pd

# NEW MODULES
import geojson
# ------------------------


# Import Python Modules
from modules.BusArrival_Modules import BusArrival_LTA,ArriveLah,BusStopList_df

# Unique BCM Vlookup List
BusService_List = pd.read_excel('https://docs.google.com/spreadsheets/u/2/d/1Z7Q5JiT0tPpSEaIEP65I8JeJQRjWjoKI/export?format=xlsx&id=1Z7Q5JiT0tPpSEaIEP65I8JeJQRjWjoKI',sheet_name= 'Services')
BusService_List["Bus Service No."] = BusService_List["Bus Service No."].astype(str)

# List of Bus Stops
df_BusStop = BusStopList_df()

# Pre-load Ridership Data
with open(dir_path+"/static/data/LTAMall_Ridership_Data.geojson") as f:
    ridership_data = geojson.load(f)

app = Flask(__name__)

#-------------------------------------------
# HOME PAGE - Map
#-------------------------------------------
@app.route('/')
def index():
    return render_template('index.html')

#-------------------------------------------
# Fetch User BSCODE Input
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
    
    # Using Bus Arrival - LTA API
    # Note: To obtain Destination.
    LTA_Raw_BusArrival = BusArrival_LTA(req["BSCODE"])
    # Using ArriveLah.
    ArriveLah_Raw_BusArrival = ArriveLah(req["BSCODE"]) ## Using ArriveLah API.
    Service_List = []
    ArrivalTime_List = []
    Direction_List = []
    Number_Svcs = 0
    for i in range(len(ArriveLah_Raw_BusArrival["services"])):

        # LTA API
        Direction_Code = LTA_Raw_BusArrival["Services"][i]["NextBus"]["DestinationCode"]
        ArrivalTime = int(round(ArriveLah_Raw_BusArrival["services"][i]["next"]["duration_ms"]/(60*1000),0))
        BusType = ArriveLah_Raw_BusArrival["services"][i]["next"]["type"]
        if ArrivalTime <= 1:
            ArrivalTime = "<strong> -- Arr -- </strong>"
        else:
            ArrivalTime = str(ArrivalTime) + " min" + " ("+ BusType +")"
        ArrivalTime_List.append(ArrivalTime)

        Svc_Raw = ArriveLah_Raw_BusArrival["services"][i]["no"]
        Service_List.append(Svc_Raw)
        Direction_List.append(str(Direction_Code))
        Number_Svcs += 1

    # Create DataFrame
    df_BusArrival = pd.DataFrame(list(zip(Service_List,Direction_List,ArrivalTime_List)), 
               columns =['Services', 'Direction','ArrivalTime']) 
    
    
    # merge with BS Description
    df_BusArrival = df_BusArrival.merge(df_BusStop, left_on="Direction",right_on="BusStopCode", how = "left", indicator = False)
    # Merge with BCM package
    df_BusArrival = df_BusArrival.merge(BusService_List, left_on="Services",right_on="Bus Service No.", how = "left", indicator = False)
    # Sort Dataframe by Service, then Package
    df_BusArrival = df_BusArrival.loc[pd.to_numeric(df_BusArrival["Services"], errors='coerce').sort_values(ascending=True).index] #https://stackoverflow.com/questions/47913881/
    df_BusArrival.sort_values(["Contract"],inplace = True,ascending=True)

    print(df_BusArrival)
    # Convert to lists
    Service_List = df_BusArrival["Services"].to_list()
    ArrivalTime_List = df_BusArrival["ArrivalTime"].to_list()
    Package_List = df_BusArrival["Package Name"].to_list()
    Direction_List = df_BusArrival["Description"].to_list()

    #-------------------------------------------

    #-------------------------------------------
    # Plotly z list -  based on BSCODE selected
    #-------------------------------------------
    zList_raw = {}
    for i in range(len(ridership_data["features"])):
        # WEEKDAY
        if ((ridership_data['features'][i]['properties']['PT_CODE']==req["BSCODE"]) and (ridership_data['features'][i]['properties']['DAY_TYPE']=="WEEKDAY")):
            tapIn_Identifier = "tapIn"+"WEEKDAY" + "_"+str(ridership_data.features[i]['properties']["TIME_PER_HOUR"])
            zList_raw[tapIn_Identifier] = ridership_data.features[i]['properties']["TOTAL_TAP_IN_VOLUME"]
        # WEEKENDS/PH
        elif ((ridership_data['features'][i]['properties']['PT_CODE']==req["BSCODE"]) and (ridership_data['features'][i]['properties']['DAY_TYPE']=="WEEKENDS/HOLIDAY")):
            tapIn_Identifier = "tapIn"+"WEEKENDS/HOLIDAY" + "_"+str(ridership_data.features[i]['properties']["TIME_PER_HOUR"])
            zList_raw[tapIn_Identifier] = ridership_data.features[i]['properties']["TOTAL_TAP_IN_VOLUME"]
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
            "zList_raw":zList_raw

        }),200)
    #-------------------------------------------

    return res # Return back to JavaScript for Bus Arrival Data for selected BSCode.


if __name__ == '__main__':
    app.run()