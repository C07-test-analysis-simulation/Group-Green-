#order of columns is: L1    L2    C1    P1    P2    S1    S2    CH     should it be tracked(Binary)      SatID
#:)
# imports
import numpy as np
from datetime import datetime

#open file and read all lines into list of lines
filename = r"C:\Users\Acer NITRO\Desktop\AE STUDIES\Year 2\Q3\Project\Code\test data\repro.goce2450red.13o"
NOM = False #set this to true for nom data. The data is slightly less nicely formatted there so needed some extra splits
with open(filename) as myfile:
    lines = myfile.readlines()

#start going through lines, keeping track of line number
HeaderLineNumberStart = 15 #because first lines arent data but just some text
HeaderLineNumber = HeaderLineNumberStart # this is start condition as well as def var
TotNumbSat = 32+1 #Total amount of sats determines the length of one dimension of the 3D array. +1 because 0 index will be empty. I think the max is 32 but idk

def GetTimeStamp(header): #basically i just make a timestamp here so yeah, if you want to see how it works read https://docs.python.org/3/library/datetime.html or google
    dummylist = 6*[0]
    for i in range(len(dummylist)):
        dummylist[i] = header[i]
    dummy = dummylist[-1]
    dummy = dummy[:-1] #for some reason python doesnt like 7 decimals so I delete the last character of the milliseconds, IDK if its an issue, I guess I might ask Jose?
    dummylist[-1] = dummy
    timestring = '20'+dummylist[0]+'-'+dummylist[1]+'-'+dummylist[2]+' '+dummylist[3]+':'+dummylist[4]+':'+dummylist[5]
    dt = datetime.strptime(timestring, '%Y-%m-%d %H:%M:%S.%f')
    return dt


def ReadLinesAftHeader(TotNumbSat, NumbSat, HeaderLineNumber, header): #handles data after a header, puts it in a 2D array
    LineAftHeader = 0
    TwoDArray = np.zeros((TotNumbSat, 10))  # 8+2 because I want to store the TimeStamp and whether the sat was supposed to be seen on top of the 8 datathings.
    for row in range(NumbSat): #go past a row to fill it into the Array
        SatIDNumb = int(header[8 + row])
        CurrentLine = lines[HeaderLineNumber+LineAftHeader+1]+lines[HeaderLineNumber+LineAftHeader+2]
        CurrentLine = CurrentLine.split()


        if len(CurrentLine) == 8: #This is for the normal situation without losses, if there are losses it adds an extra entry hence len would be 9
            CurrentLine = CurrentLine+[str(int(1)), str(int(SatIDNumb))] #add TStamp, iftracked and SatID here
            # I have the lines as nice lists of strings now, lets put it into an array
            for column in range(10):
                TwoDArray[SatIDNumb][column] = CurrentLine[column]#means that satID number 0 is always ampty as it doesnt exist irl but does here because of python index things


        if len(CurrentLine) == 9: #now if there is a trackingloss, it gives an extra entry. I do some inefficient things here but it works. I essentially skip the 3rd entry(index 2) as to drop the extra number
            CurrentLine = CurrentLine + [str(int(1)), str(int(SatIDNumb))]  # add TStamp, iftracked and SatID here

            TwoDArray[SatIDNumb][0] = CurrentLine[0]
            TwoDArray[SatIDNumb][1] = CurrentLine[1]  # means that satID number 0 is always ampty as it doesnt exist irl but does here because of python index things
            for column in range(2, 10):
                TwoDArray[SatIDNumb][column] = CurrentLine[column+1]  # means that satID number 0 is always empty as it doesnt exist irl but does here because of python index things


        LineAftHeader += 2
    return TwoDArray

#loop to count datapoints
def CountDataPoints(): # counts datapoints from a file in terms of time (1 second is one count pretty much, should be 60*60*24 but nice to check)
    HeaderCount = 0
    while lines[HeaderLineNumber] != '':
        header = lines[HeaderLineNumber] #make headerline
        header = header.split() #split on any whitespace, incl mult white spaces
        NumbSat = int(header[7])
        HeaderCount += 1
        HeaderLineNumber += (2*NumbSat+1)
    return HeaderCount

#INITIATE PROGRAM!!!!!!!!!!
#make empty list to store 2D arrays in
ListOfDataArrays = []
ListOfTimeStamps = [] #Python doesnt like timestamps apparently even though its their own thing but whatever.
# Anyway having a separate list for it is nice for searching based on time later on anyway.

while HeaderLineNumber < len(lines):
    header = lines[HeaderLineNumber] #make headerline
    header = header.split() #split on any whitespace, incl mult white spaces
    #print(header)
    NumbSat = int(header[7])
    if NumbSat == 12 and NOM == True:
        dummy = header[-1].split('-')
        header[-1] = dummy[0]
        header.append(dummy[1])
    TimeStamp = GetTimeStamp(header)
    ListOfTimeStamps.append(TimeStamp)
    ArrayDummy = ReadLinesAftHeader(TotNumbSat, NumbSat, HeaderLineNumber, header)#adding the 2d array with the data per Tstamp to a list of 2D arrays, to essentiay get a 3D array
    ListOfDataArrays.append(ArrayDummy)
    HeaderLineNumber += (2*NumbSat+1) #skip to next TStamp by going to next header

if __name__ == '__main__' :

    print("done loading, now printing...")
    print(len(ListOfDataArrays), 60*60*24) #If its the same its awesome.
    print(len(ListOfDataArrays[0]), TotNumbSat)#I wouldnt print the entire thing because python printing is kinda slow, just pick an index between 0 and (60*60*24-1) to test
    print(ListOfTimeStamps[0])











