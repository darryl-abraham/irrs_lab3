#!/usr/bin/python

from collections import namedtuple
import time
import sys

class Edge:
    def __init__ (self, origin=None):
        self.origin = origin
        self.weight = 1

    def __repr__(self):
        return "edge: {0} {1}".format(self.origin, self.weight)
        
    ## write rest of code that you need for this class

class Airport:
    def __init__ (self, iden=None, name=None):
        self.code = iden
        self.name = name
        self.routes = [] # vector of edges of incoming routes
        self.routeHash = dict()
        self.outweight =  0  # sum of all routes in which the airport is origin

    def __repr__(self):
        return f"{self.code}\t{self.pageIndex}\t{self.name}"

edgeList = [] # list of Edge
edgeHash = dict() # hash of edge to ease the match
airportList = [] # list of Airport
airportHash = dict() # hash key IATA code -> Airport

def readAirports(fd):
    print("Reading Airport file from {0}".format(fd))
    airportsTxt = open(fd, "r");
    cont = 0
    for line in airportsTxt.readlines():
        a = Airport()
        try:
            temp = line.split(',')
            if len(temp[4]) != 5 :
                raise Exception('not an IATA code')
            a.name=temp[1][1:-1] + ", " + temp[3][1:-1]
            a.code=temp[4][1:-1]
        except Exception as inst:
            pass
        else:
            cont += 1
            airportList.append(a)
            airportHash[a.code] = a
    airportsTxt.close()
    print(f"There were {cont} Airports with IATA code")


def readRoutes(fd):
    print("Reading Routes file from {fd}")
    with open(fd, 'r') as file:
        for line in file:
            parts = line.strip().split(',')
            if not parts[2] or not parts[4]:
                continue  # Skip invalid or incomplete lines
            origin = parts[2].strip()
            destination = parts[4].strip()
            if origin in airportHash and destination in airportHash:
                originAirport = airportHash[origin]
                edge = Edge(origin=originAirport)
                originAirport.routes.append(edge)
                originAirport.outweight += 1
                edgeList.append(edge)
                edgeHash[(origin, destination)] = edge

def computePageRanks():
    # write your code

def outputPageRanks():
    # write your code

def main(argv=None):
    readAirports("airports.txt")
    readRoutes("routes.txt")
    time1 = time.time()
    iterations = computePageRanks()
    time2 = time.time()
    outputPageRanks()
    print("#Iterations:", iterations)
    print("Time of computePageRanks():", time2-time1)


if __name__ == "__main__":
    sys.exit(main())
