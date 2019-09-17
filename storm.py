import numpy as np
from scipy import stats
from shapely.geometry import Point, Polygon

class Storm:
  def __init__(self, key, values):
    self.key = key
    self.path = np.zeros([0,4])
    self.timeSteps = np.array([])
    typeEvents = np.array([])
    for row in values:
      self.path = np.append(self.path,np.array(row[1:5]).reshape(1,4),axis=0)
      self.timeSteps = np.append(self.timeSteps,row[0])
      typeEvents = np.append(typeEvents,row[5])
    self.typeEvent = stats.mode(typeEvents).mode[0].astype(int)

  def getNumberOfTimeStep(self):
    return self.path.shape[0]

  def checkIfInTimeFrame(self,start,end):
    window = 0
    minimuOverlap = 0.5
    startTime = self.timeSteps[0]
    endTime = startTime + self.getNumberOfTimeStep()
    startOverlap = np.max([start, startTime])
    endOverlap = np.min([end, endTime])
    if startOverlap >= endOverlap:
      return False
    return True

  def getAreaStats(self):
    areas = np.array([])
    for a in self.path:
      areas = np.append(areas,((a[2]-a[0])*(a[3]-a[1])))
    return [np.mean(areas), np.std(areas)]

  def getType(self):
    return self.typeEvent

  def getStartingEndingPosition(self):
    y_start = (self.path[0,0] + self.path[0,2]) / 2
    x_start = (self.path[0,1] + self.path[0,3]) / 2
    y_end = (self.path[-1,0] + self.path[-1,2]) / 2
    x_end = (self.path[-1,1] + self.path[-1,3]) / 2
    return [y_start, x_start,y_end,x_end]

  def getLatitudeLongitudePoint(self,point):
    lat = 90 - point[1] *180/768
    lon = (1152 - point[0])*360/1152
    if lon > 180:
      lon -= 360
    return [lon,lat]

  def getCentroid(self,position):
    x = (position[1] + position[3]) / 2
    y = (position[0] + position[2]) / 2
    return [x,y]

  def getMinimalDistanceCountry(self,countryISOList,world):
    minimalDistance = 1000
    for position in self.path:
      [x,y] = self.getCentroid(position)
      [lon,lat] = self.getLatitudeLongitudePoint([x,y])
      stormCentroid = Point(lat,lon)
      for iso in countryISOList:
        borders = world[world['iso_a3']==iso]['geometry']
        distanceFrame = borders.distance(stormCentroid).values
        #print(distanceFrame, type(distanceFrame))
        if distanceFrame < minimalDistance:
          minimalDistance = distanceFrame
    return minimalDistance

  def getStartingTime(self):
    return self.timeSteps[0]

  def getKey(self):
    return self.key

  def addEMDatabaseInput(self,row):
    self.deaths = row['Total deaths']
    self.affected = row['Total affected']
    self.damage = row['Total damage (000 US$)']

  def getDeaths(self):
    return self.deaths

  def getDamage(self):
    return self.damage

  def getAffected(self):
    return self.affected