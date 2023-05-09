#order of columns is: L1    L2    C1    P1    P2    S1    S2    CH     should it be tracked(Binary)      SatID

# imports
import numpy as np
from datetime import datetime

'''
General notes & remarks:
- THIS IS FINAL VERSION (04.05)
- IT HAS BEEN CLEANED
'''

def GetTimeStamp(header): #With this function a timestamp can be made by reading the header of a datapoint.
    # Documentation can be found here: https://docs.python.org/3/library/datetime.html
    dummylist = 6*[0] #An empty list is made to later store year, month etc. in.
    for i in range(len(dummylist)):
        dummylist[i] = header[i] #The list is filled with the floats from the datafile.
    dummy = dummylist[-1]
    dummy = dummy[:-1] #For some reason python doesnt like 7 decimals for the milliseconds so the last one is deleted.
    # It is however not important since milliseconds are not relevant for this 1Hz data.
    dummylist[-1] = dummy
    timestring = '20'+dummylist[0]+'-'+dummylist[1]+'-'+dummylist[2]+' '+dummylist[3]+':'+dummylist[4]+':'+dummylist[5]
    #The string that Python will read into a timestamp is made here.
    dt = datetime.strptime(timestring, '%Y-%m-%d %H:%M:%S.%f') #Timestamp is made.
    return dt #The timestamp is returned.


def ReadLinesAftHeader(TotNumbSat, NumbSat, HeaderLineNumber, header, lines):
    #Handles the data after a certain header and puts it in a 2D array.
    LineAftHeader = 0
    TwoDArray = np.zeros((TotNumbSat, 10))  #Make an empty array for the data to be stored in.
    # 8+2 because we want to store the TimeStamp and 'whether the sat was supposed to be seen'
    # on top of the 8 datapoints like L1, L2, etc.
    for row in range(NumbSat): #go past a row to fill it into the array.
        SatIDNumb = int(header[8 + row]) #First SatID is index 8 in the headerline,
        # from there on we read all of them one by one.
        CurrentLine = lines[HeaderLineNumber+LineAftHeader+1]+lines[HeaderLineNumber+LineAftHeader+2] #Append lines
        CurrentLine = CurrentLine.split() #Split lines.


        if len(CurrentLine) == 8: #This is for the normal situation without losses,
            # If there are losses it adds an extra entry hence len would be 9.
            CurrentLine = CurrentLine+[str(int(1)), str(int(SatIDNumb))] #Add TStamp, iftracked(binary) and SatID here.
            # We have the lines as nice lists of strings now, lets put it into an array.
            for column in range(10):
                #Now we make a 2D array from al these lists for the current point in time.
                TwoDArray[SatIDNumb][column] = CurrentLine[column]#Means that satID number 0 is always ampty as it
                # doesnt exist but this way it is a little nicer in Python.


        elif len(CurrentLine) == 9: #Now if there is a trackingloss, it gives extra entries.
            # Due to weird formatting it could either be 9 or 10 entries. This is fixed by simply skipping the extra
            # entries.
            CurrentLine = CurrentLine + [str(int(1)), str(int(SatIDNumb))]
            if CurrentLine[0] == 0:
                TwoDArray[SatIDNumb][0] = CurrentLine[0]
                for column in range(1, 10):
                    TwoDArray[SatIDNumb][column] = CurrentLine[column+1]

            else:
                TwoDArray[SatIDNumb][0] = CurrentLine[0]
                TwoDArray[SatIDNumb][1] = CurrentLine[1]
                for column in range(2, 10):
                    TwoDArray[SatIDNumb][column] = CurrentLine[column+1]

        elif len(CurrentLine) == 10:
            CurrentLine = CurrentLine + [str(int(1)), str(int(SatIDNumb))]
            TwoDArray[SatIDNumb][0] = CurrentLine[0]
            TwoDArray[SatIDNumb][1] = CurrentLine[2]
            for column in range(2, 10):
                TwoDArray[SatIDNumb][column] = CurrentLine[column+2]

        LineAftHeader += 2 #We read 2 lines per SatID, so we skip 2 to go to the next SatID.
    return TwoDArray #Returns the Array made for a single point in Time.

def ReadFile(filename):
    #Open the file and read all lines into a list of lines.
    NOM = False  #Set this to true for nominal data.
    # The data is slightly less nicely formatted there so some extra splits were needed.
    with open(filename) as myfile:
        lines = myfile.readlines() #Reads the lines and puts it into a list of the lines.
    return lines

def ReadRest(lines, NOM):
    HeaderLineNumberStart = 15  #Because first lines are not data but just the header of the file.
    HeaderLineNumber = HeaderLineNumberStart  #This is the start condition as well as the definition of the variable.
    TotNumbSat = 32 + 1  #Total amount of sats determines the length of one dimension of the 3D array.
    # +1 because 0 index will be empty.


    ListOfDataArrays = []
    ListOfTimeStamps = [] #Python doesnt like timestamps apparently even though its their own thing but whatever.
    # Anyway having a separate list for it is nice for searching based on time later on anyway.

    while HeaderLineNumber < len(lines): #Make it stop at the end of the file.
        header = lines[HeaderLineNumber] #Make headerline.
        header = header.split() #Split on any whitespace.
        NumbSat = int(header[7]) #Determine the number of sats being tracked.
        x = "-" in header[-1]
        if NumbSat == 12 and NOM == True and x == True: #Again a format mistake being filtered out.
            dummy = header[-1].split('-')
            header[-1] = dummy[0]
            header.append(dummy[1])
        TimeStamp = GetTimeStamp(header)
        ListOfTimeStamps.append(TimeStamp) #Append timestamp to list of timestamps.
        ArrayDummy = ReadLinesAftHeader(TotNumbSat, NumbSat, HeaderLineNumber, header, lines)
        #Now we add the 2d array with the data per timestamp to a list of 2D arrays, to essentiay get a 3D array.
        ListOfDataArrays.append(ArrayDummy)
        HeaderLineNumber += (2*NumbSat+1) #Skip to the next timestamp by going to the next header.
    return ListOfDataArrays, ListOfTimeStamps #Return the lists.


ListOfDataArrays = [] #Make two empty lists.
ListOfTimeStamps = []
for i in range(29): #This way all files can be opened at once, making one big list for the entire month.
    print(i)
    index = 2450+10*i #This stems from the way the files are named.
    #Remember to update path and set NOM to True/False according to what you want!
    filename = r"C:\Users\Acer NITRO\Desktop\AE STUDIES\Year 2\Q3\Project\GOCE data\Observation data red\To read\repro.goce{}.13o".format(index)
    lines = ReadFile(filename)
    CurrentListOfDataArrays, CurrentListOfTimeStamps = ReadRest(lines, NOM=False)
    ListOfTimeStamps += CurrentListOfTimeStamps #"Append the days to create the month.
    ListOfDataArrays += CurrentListOfDataArrays