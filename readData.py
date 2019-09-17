import pandas as pd
import numpy as np

class ReadEMData:
    def __init__(self, path, sheetName):
        # Read data from file
        #path = "/content/drive/My Drive/disastersStats.xlsx"
        # sheetName = 'Feuil2'
        columnNames = ['Start date', 'End date', 'Country name', 'ISO', 'Location', 'Latitude', 'Longitude', 'Magnitude value',
                 'Magnitude scale', 'Disaster Type', 'Disaster subtype', 'Associated dis.', 'Associated dis2.',
                 'Total deaths', 'Total affected', 'Total damage (000 US$)', 'Insured losses (000 US$)', 'Disaster name',
                'Disaster No.']
        self.data = pd.read_excel(path,sheet_name=sheetName,header=None, names=columnNames)

    def reformatDates(self):
        #add date time type to dates
        self.data['Start date'] = pd.to_datetime(self.data['Start date'], format='%d/%m/%Y', errors='coerce')
        self.data['End date'] = pd.to_datetime(self.data['End date'], format='%d/%m/%Y', errors='coerce')

        #remove incomplete dates
        self.data = self.data[~(pd.isnull(self.data['Start date']) | pd.isnull(self.data['End date']))]

    def changeDatesToTimeStep(self):
        regularYear = np.array([0, 31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30])
        for x in range(11, 0, -1):
            regularYear[x] = np.sum(regularYear[0:x + 1])
        self.data['StartTimeStep'] = 4 * (regularYear[self.data['Start date'].dt.month - 1] + self.data['Start date'].dt.day - 1)
        self.data['EndTimeStep'] = 4 * (regularYear[self.data['End date'].dt.month - 1] + self.data['End date'].dt.day + 2)
        self.data['AverageTimeStep'] = np.round((self.data['StartTimeStep'] + self.data['EndTimeStep']) / 2)
        self.data['AverageTimeStep'] = self.data['AverageTimeStep'].astype(int)

    def addYearColumn(self):
        self.data['year'] = self.data['Start date'].dt.year

    def aggregateByDisasterNo (self):
        data_cleaned = self.data.groupby('Disaster No.').agg(
            {'year': lambda x: x.value_counts().index[0], 'StartTimeStep': 'min', 'EndTimeStep': 'min', 'Total deaths': 'sum',
            'Total affected': 'sum', 'Total damage (000 US$)': 'sum', 'Insured losses (000 US$)': 'sum',
            'Disaster subtype': lambda x: x.value_counts().index[0]})
        data_cleaned['AverageTimeStep'] = np.round(
            (data_cleaned['StartTimeStep'] + data_cleaned['EndTimeStep']) / 2).astype(int)
        data_iso = self.data.groupby('Disaster No.')['ISO'].apply(list)
        data = pd.merge(data_cleaned, data_iso, left_index=True, right_index=True)
        return data

    def matchEMDatabaseWithSimulatedData(dataEM, simulatedData, world):
        selectedObjects = []
        for index, row in dataEM.iterrows():
            startTime = row['StartTimeStep']
            endTime = row['EndTimeStep']
            isoList = row['ISO']
            stormsList = []
            minimalDistance = np.array([])
            for obj in simulatedData:
                if obj.checkIfInTimeFrame(startTime, endTime):
                    stormsList.append(obj)
                    minimalDistance = np.append(minimalDistance, obj.getMinimalDistanceCountry(isoList, world))
                if len(stormsList) > 0:
                    idxMin = np.argmin(minimalDistance)
                    stormId = stormsList[idxMin].getKey()
                    selectedObjects.append(stormId)
                    simulatedData[stormId].addEMDatabaseInput(row)
        return selectedObjects