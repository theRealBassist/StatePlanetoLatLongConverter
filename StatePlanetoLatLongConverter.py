from pyproj import Transformer
import tkinter
from tkinter import filedialog
from tablib import Dataset
from difflib import SequenceMatcher
import os

def mainMenu():
    print("State Plane to Latitude/Longitude Converter")
    print("===============")

    print("[L] - State Plane to Latitude/Longitude Conversion")
    print("[S] - Latitude/Longitude to State Plane Conversion")
    print("[B] - State Plane to State Plane Conversion")
    print("[X] - Exit")

    userInput = input()

    file = getFile()
    data = importData(file)
    if userInput == "L" or userInput == "l":
        EPSGZone = getEPSG(True)
        convertedCoordinates = convertCoordinates(data, EPSGZone, 4326, False)
        newData = writeData(data, convertedCoordinates, False)
    elif userInput == "S" or userInput == "s":
        EPSGZone = getEPSG(False)
        convertedCoordinates = convertCoordinates(data, 4326, EPSGZone, True)
        newData = writeData(data, convertedCoordinates, True)
    elif userInput == "B" or userInput == "b":
        EPSGFrom = getEPSG(True)
        EPSGTo = getEPSG(False)
        convertedCoordinates = convertedCoordinates(data, EPSGFrom, EPSGTo, False)
        newData = writeData(data, convertedCoordinates, True)
    elif userInput == "X" or userInput == "x":
        quit()
    else:
        print("This is not a valid input. Please try again")
        mainMenu()
    
    exportData(file, newData)


def getEPSG(gettingFrom):
    if gettingFrom:
        print("Please input the EPSG Zone that the coordinates are in.")
        print("West Georgia is zone `2240`")
    else:
        print("Please input the EPSG Zone that you are converting to.")

    try:
        EPSGZone = int(input())
    except:
        print ("Please enter only digits for the EPSG Zone.")
        getEPSG(gettingFrom)
    return EPSGZone

def getFile(): #responsible for displaying the UI and collecting desired selections
    while True:
        try:
            tkinter.Tk().withdraw()
            workingFile = filedialog.askopenfilename(filetypes = [("CSV Files", "*.csv")], initialdir = "/", title = "Select the directory which contains your coordinates. \n Please ensure your EASTING and WESTING columns are named as such.") #Tkinter allows for the creation of pop-up file directories
        except:
            workingFile = input("Select the directory which contains your coordinates. \n Please ensure your EASTING and WESTING columns are named as such.")
        if os.path.exists(workingFile): #pathlib is incompatible with pyinstaller, so I'm using os.path
            return workingFile
        elif workingFile == "":
            break
        else:
            print("This is not a valid directory! Please try again.")
            getFile()

def importData(workingFile):
    with open(workingFile, 'r') as file:
        importedData = Dataset().load(file)
        return importedData

def getHeader(data, toFind):
    headers = data.headers

    for header in headers:
        if SequenceMatcher(None, toFind, header.lower()).ratio() > 0.75:
            return str(header)

def convertCoordinates(importedData, EPSGFrom, EPSGTo, LatLong):
    transformer = Transformer.from_crs(f'EPSG:{EPSGFrom}', f'EPSG:{EPSGTo}', always_xy=True)
    


    if not LatLong:
        x = importedData[getHeader(importedData, "easting")]
        y = importedData[getHeader(importedData, "northing")]
    else:
        x = importedData[getHeader(importedData, "latitude")]
        y = importedData[getHeader(importedData, "longitude")]

    convertedX = []
    convertedY = []
    for currentX, currentY in zip(x, y):
        coordinate = transformer.transform(currentX, currentY)
        convertedX.append(coordinate[0])
        convertedY.append(coordinate[1])

    convertedCoordinates = [convertedX, convertedY]
    return convertedCoordinates

def writeData(data, convertedCoordinates, statePlane):
    if statePlane:
        data.append_col(convertedCoordinates[1], header="NORTHING")
        data.append_col(convertedCoordinates[0], header="EASTING")
    else:
        data.append_col(convertedCoordinates[0], header="LATITUDE")
        data.append_col(convertedCoordinates[1], header = "LONGITUDE")
    return data

def exportData(file, data):
    outputPath = os.path.join(os.path.dirname(os.path.realpath(file)), "output.csv")
    with open(outputPath, 'w', newline='') as outputFile:
        outputFile.write(data.csv)

mainMenu()
