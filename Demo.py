#!/share/data1/anaconda3/bin/python
# This is where I install my python,
# please edit it to be suitable with your PC.
import os
import numpy as np
import pandas as pd
from plotly.offline import download_plotlyjs, init_notebook_mode, plot, iplot
from plotly.graph_objs import Scatter, Figure, Layout

init_notebook_mode(connected=True)


# Add Lat and Long into list
def add_lat_long(nlat, nlong, lat, lng):
    # Check if input value is longtitude and latitude
    if isinstance(lat,float) and isinstance(lng,float):
        llat = float(lat)
        llng = float(lng)
        # Correct problem that longtitude and latitude are mistaken
        if lat > lng:
            nlong.append(llat)
            nlat.append(llng)
        else:
            nlat.append(llat)
            nlong.append(llng)


# Extract longtitude and latitute from Excel file
def parse_lat_long_data(df,data_type):
    len = df[data_type].size
    nlat = list()
    nlong = list()

    for i in range(0, len):
            add_lat_long(nlat, nlong, df['Lat'][i], df['Lng'][i])
    return pd.DataFrame({'Lat': nlat, 'Lng': nlong})

# Push all routes into list for comparision
def get_all_routes(directory):
    files = os.listdir(directory)
    data_frames = list()
    for file in files:
        df = parse_lat_long_data(pd.read_excel(directory + "/" + file),"Route_Id")
        data_frames.append(df)
    return data_frames


def calculate_correlation(journey, route):
    # Get specific values like mean, std, min, max of data set
    journey_arr = [journey['Lat']['mean'],
                   journey['Lat']['std'],
                   journey['Lat']['min'],
                   journey['Lat']['max'],
                   journey['Lng']['mean'],
                   journey['Lng']['std'],
                   journey['Lng']['min'],
                   journey['Lng']['max']]


    route_arr = [route['Lat']['mean'],
                 route['Lat']['std'],
                 route['Lat']['min'],
                 route['Lat']['max'],
                 route['Lng']['mean'],
                 route['Lng']['std'],
                 route['Lng']['min'],
                 route['Lng']['max']]

    # From array of data set specific value,
    # calculate Correlation
    return np.corrcoef(journey_arr, route_arr)[1,0]

# Main task, map journey with suitable route
def search_route_for_journey(data_frames, df, files, journey):
    df = parse_lat_long_data(df,'Lat')
    journey_data = df.describe()

    correl_val = calculate_correlation(journey_data, data_frames[0].describe())
    #print (data_frames[0]['Lat'].values)
    found_index = 0

    for i in range(1, len(data_frames)):
        correl_val_tmp = calculate_correlation(journey_data, data_frames[i].describe())
        if correl_val_tmp > correl_val:
            correl_val = correl_val_tmp
            found_index = i

    trace1 = Scatter(
        x = df['Lat'].values,
        y = df['Lng'].values,
        mode = 'lines',
        name = 'Journey'
    )
    
    trace2 = Scatter(
        x = data_frames[found_index]['Lat'].values,
        y = data_frames[found_index]['Lng'].values,
        mode = 'markers',
        name = 'Route'
    )
    data = [trace1, trace2]
    iplot(data, filename='basic-line')

    print("========================= Journey: " + journey + " =========================")
    print("Recommendation for Bus Number: " + files[found_index].replace(".xlsx", ""))
    print("Correlation: ", correl_val)
    print("\n")

def main():
    print("Reading data from excel files...")
    data_frames = get_all_routes("Route")
    f = os.listdir("Route")
    df_51B02635 = pd.read_excel("Journey/51B02635.xlsx")
    df_51B02517 = pd.read_excel("Journey/51B02517.xlsx")

    search_route_for_journey(data_frames, df_51B02635, f, "51B02635")
    search_route_for_journey(data_frames, df_51B02517, f, "51B02517")

if __name__ == "__main__":
    main()
