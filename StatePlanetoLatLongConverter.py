from pyproj import Transformer
import tkinter
from tkinter import filedialog
from tablib import Dataset
import os

def getFile(): #responsible for displaying the UI and collecting desired selections
    selections = [] #to simplify calls later, the selections are stored in a single array
    
    print("State Plane to Latitude/Longitude Converter")
    print("===============")

    while True:
        try:
            tkinter.Tk().withdraw()
            workingFile = filedialog.askopenfilename(filetypes = [("CSV Files", "*.csv")], initialdir = "/", title = "Select the directory which contains your coordinates. \n Please ensure your EASTING and WESTING columns are named as such.") #Tkinter allows for the creation of pop-up file directories
        except:
            workingFile = input("Select the directory which contains your coordinates. \n Please ensure your EASTING and WESTING columns are named as such.")
        if os.path.exists(workingFile): #pathlib is incompatible with pyinstaller, so I'm using os.path
            EPSGZone = input("Please enter the EPSG zone of the coordinates to be converted, or press `Enter` to default to `2240` West Georgia.\n")
            return workingFile
        else:
            print("This is not a valid directory! Please try again.")
            break

def importData(workingFile):
    with open(workingFile, 'r') as file:
        importedData = Dataset().load(file)
        return importedData

def selectData(importedData):
    transformer = Transformer.from_crs(f'EPSG:{EPSGZone}', "EPSG:4326", always_xy=True)

    eastings = importedData['EASTING']
    northings = importedData['NORTHING']

    latitudes = []
    longitudes = []
    for easting, northing in zip(eastings, northings):
        coordinate = transformer.transform(easting, northing)
        longitudes.append(coordinate[0])
        latitudes.append(coordinate[1])

    coordinates = [latitudes, longitudes]
    return coordinates

def writeData(file, data, selectedData):
    data.append_col(selectedData[0], header="LATITUDE")
    data.append_col(selectedData[1], header = "LONGITUDE")

    outputPath = os.path.join(os.path.dirname(os.path.realpath(file)), "output.csv")
    with open(outputPath, 'w', newline='') as outputFile:
        outputFile.write(data.csv)

EPSGZone = 2240

file = getFile()
data = importData(file)
selectedData = selectData(data)
writeData(file, data, selectedData)
