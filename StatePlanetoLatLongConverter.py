from pyproj import Transformer
import tkinter
from tkinter import filedialog
from tablib import Dataset
from difflib import SequenceMatcher
import os

def mainMenu():
    print("State Plane to Latitude/Longitude Converter")
    print("===============\n")

    print("[L] - State Plane to Latitude/Longitude Conversion")
    print("[S] - Latitude/Longitude to State Plane Conversion")
    print("[B] - State Plane to State Plane Conversion")
    print("[X] - Exit")

    userInput = input("\nSelection: ")

    if userInput == "X" or userInput == "x":
            exitProgram()
    elif userInput == "":
        print("This is not a valid input. Please try again")
        mainMenu()

    file = getFile()
    data = importData(file)
    if userInput == "L" or userInput == "l":
        print("This conversion format will accept any EPSG code as a target.")
        print("Some useful codes: \n1. [26916] - NAD83 / UTM zone 16N\n2. [4326] - WGS 84 Latitude/Longitude\n3. [2240] - NAD83 State Plane West Georgia (Code 1713)")
        continueInput = input("Press `Enter` to continue...")
        EPSGZone = getEPSG(True)
        convertedCoordinates = convertCoordinates(data, EPSGZone, 4326, False)
        newData = writeData(data, convertedCoordinates, False)
    elif userInput == "S" or userInput == "s":
        print("This conversion format will accept any EPSG code as a target.")
        print("Some useful codes: \n1. [26916] - NAD83 / UTM zone 16N\n2. [4326] - WGS 84 Latitude/Longitude\n3. [2240] - NAD83 State Plane West Georgia (Code 1713)")
        continueInput = input("Press `Enter` to continue...")
        EPSGZone = getEPSG(False)
        convertedCoordinates = convertCoordinates(data, 4326, EPSGZone, True)
        newData = writeData(data, convertedCoordinates, True)
    elif userInput == "B" or userInput == "b":
        print("This conversion format will accept any EPSG code as a source and target.")
        print("Some useful codes: \n1. [26916] - NAD83 / UTM zone 16N\n2. [4326] - WGS 84 Latitude/Longitude\n3. [2240] - NAD83 State Plane West Georgia (Code 1713)")
        continueInput = input("Press `Enter` to continue...")
        EPSGFrom = getEPSG(True)
        EPSGTo = getEPSG(False)
        convertedCoordinates = convertedCoordinates(data, EPSGFrom, EPSGTo, False)
        newData = writeData(data, convertedCoordinates, True)
    exportData(file, newData)


def getEPSG(gettingFrom):
    if gettingFrom:
        print("Please input the EPSG Zone that the coordinates are in.")
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
            window = tkinter.Tk()
            window.wm_attributes("-topmost", 1)
            window.withdraw()
            workingFile = filedialog.askopenfilename(parent = window, filetypes = [("CSV Files", "*.csv")], initialdir = "/", title = "Select the directory which contains your coordinates.") #Tkinter allows for the creation of pop-up file directories
        except:
            workingFile = input("Enter the directory which contains your coordinates.")
        if os.path.exists(workingFile): #pathlib is incompatible with pyinstaller, so I'm using os.path
            return workingFile
        elif workingFile == "":
            exitProgram()
        else:
            print("This is not a valid .csv file! Please try again.")
            getFile()

def importData(workingFile):
    try:
        with open(workingFile, 'r') as file:
            importedData = Dataset().load(file)
            return importedData
    except:
        print("There was an error importing the data.\n Please ensure the file exists where specified and is in the correct format.")
        exitProgram()

def getHeader(data, toFind):
    headers = data.headers

    for header in headers:
        if SequenceMatcher(None, toFind, header.lower()).ratio() > 0.75:
            return str(header)
    
    print ("Please make sure that you have columns in your .csv file which contain Easting/Northing or Latitude/Longitude!")
    exitProgram()

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

def exitProgram():
    while True:
        userInput = input("Press `Enter` to exit...")
        quit()

mainMenu()