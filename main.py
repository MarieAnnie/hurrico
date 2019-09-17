import math
import numpy as np
import pandas as pd
import matplotlib as plt
from shapely.geometry import Point, Polygon
from sklearn.metrics import confusion_matrix
from scipy import stats
import geopandas as gpd
import h5py

from storm import Storm
from readData import ReadEMData

print(Storm(1,[[4,0,6,7,8,9]]))

print("hello world")

#get EM data
def extractDataEM():
    databaseEM = ReadEMData("data/disastersStats.xlsx", "Feuil2")
    databaseEM.reformatDates()
    databaseEM.changeDatesToTimeStep()
    databaseEM.addYearColumn()
    return databaseEM, databaseEM.aggregateByDisasterNo()

def addYear(year, df, world,databaseEM, dataEM):
    realDisasters = dataEM[dataEM["year"] == year]
    path = "./climo_" + str(year) + ".h5"
    simulatedDisasters = creatStormObjectList(path)
    selectedDisasters = databaseEM.matchEMDatabaseWithSimulatedData(realDisasters, simulatedDisasters, world)
    df = createDF(year, simulatedDisasters,  selectedDisasters, df)
    return df

def createDF(year,storms,selectedStorms, dfObj):
    for i in selectedStorms:
        # y_start, x_start,y_end,x_end
        storm = storms[i]
        lst = storm.getStartingEndingPosition()
        dfObj = dfObj.append({
            'StormID': storm.getKey(),
            'xStart': lst[1] ,
            'xEnd': lst[3],
            'yStart': lst[0],
            'yEnd': lst[2],
            'Area': storm.getAreaStats()[0],
            'Duration': storm.getNumberOfTimeStep(),
            'Year': year,
            'Class': storm.getType(),
            'Casualty': storm.getDeaths(),
            'Damage': storm.getDamage()
        }, ignore_index=True)
        return dfObj

databaseEM, dataEM = extractDataEM()
world = gpd.read_file(gpd.datasets.get_path('naturalearth_lowres'))
ColName = ['StormID','yStart','xStart','yEnd','xEnd','Area','Duration','Year','Class','Casualty','Damage']
dfObj = pd.DataFrame(columns = ColName)

year=1990
dfObj = addYear(year,dfObj, world,databaseEM, dataEM)
dfObj.to_pickle("/content/data.pkl")
