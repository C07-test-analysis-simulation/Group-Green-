from OpenReadNomandRed import *
import numpy as np
from datetime import datetime

'''
General notes & remarks / issues to resolve:
- some durations are 0 s, possible causes -> bug in code that reads same date twice
or loss lasts precisely 1s so appears only in one time reading (see eg. timestamp 13  9  2  0  0 42.6200000 for satellite 21), so time_begin and time_end belong to the same timestamp
I'm not sure how we want to treat it, because it is a loss noted in data but apparently has duration <=1s
- I assume time_end as time of first non-zero reading after (unexpected) loss
- the import 'from OpenReadNomandRed import *' takes quite a bit -> possile improvement
- as data is appended during the checking, OverviewTable is kinda ordered with increasing time & sat_id since we check it in that order
- please double (triple!) check everything, it doesn't give an error but I may have messed something up with indexing (it happens quite often ^^)
- tbh I don't know how to validate the data in the table other than manually compare (which is a pain), so ideas & feedback are very welcome
'''

def FindLosses(TotNumbSat, ListOfDataArrays, ListOfTimeStamps, L2orL1):
    print("we started")
    if str(L2orL1) == "L2": #pick which loss we're looking at
        L = 1
    if str(L2orL1) == "L1":
        L = 0

    OverviewTable = []
    for i in range(1, 3): #i is satellite id 
        BeginLossHad = False
        LossNoted = False

        for Time in range(len(ListOfDataArrays)): #choosing variables -> ListOfDataArrays[time][sat_id][parameter]
            DummyArray2 = ListOfDataArrays[Time] #one time slice of the read file, DummyArray2[sat_id][parameter]
            if Time > 0:
                PreviousDummy = ListOfDataArrays[Time - 1] #same, for previous time stamp
            if Time < (len(ListOfDataArrays)-1):
                NextDummy = ListOfDataArrays[Time + 1] #same, for next time stamp

            if int(DummyArray2[i][8]) == 1: #if it's supposed to be tracked
                    
                if DummyArray2[i][L] != 0.0 and PreviousDummy[i][L] == 0.0 and BeginLossHad == False: #check if begin loss occured
                    BeginLossHad = True
                
                if DummyArray2[i][L] == 0.0 and BeginLossHad == True: #this is not the first loss -> unexpected!
                    if LossNoted == False: #only first 0 detected, we don't want to record every 0
                        RunningLossList = [] #create mini-list for singe loss data
                        time_begin = ListOfTimeStamps[Time]
                        RunningLossList.append(time_begin)
                        LossNoted = True #set to true to not note further 0s in the loss

                    if NextDummy[i][8] == 0.0: #oh it was end loss! after 0s it's not supposed to be tracked 
                        BeginLossHad = False
                        LossNoted = False

                if DummyArray2[i][L] != 0.0 and LossNoted == True: #loss ends! we see something right after after 0
                    time_end = ListOfTimeStamps[Time - 1] #I assume time_end to be the time of first non-zero reading 
                    sat_id = i
                    td = time_end-time_begin
                    duration = td.total_seconds() + 1
                    RunningLossList.append(time_end)
                    RunningLossList.append(duration)
                    RunningLossList.append(sat_id)
                    OverviewTable.append(RunningLossList)

                    LossNoted = False #finished gathering data from one loss

            elif int(DummyArray2[i][8]) == 0.0:
                BeginLossHad = False
                LossNoted = False


    OverviewTable = np.array(OverviewTable)            

    return OverviewTable

table = FindLosses(TotNumbSat, ListOfDataArrays, ListOfTimeStamps, 'L2')
print("Loss Table:","\n", table,
      "\n Nr of losses:", len(table),
      "\n Total duration:", np.sum(table[:, 2], axis=0), "s")

#structure: columns -> [time_begin (date format), time_end (date format), duration (seconds), sat_id (int)]
#           rows -> all losses "listed" (so length is total nr of losses)
#to use: - copy names TotNumbSat, ListOfDataArrays, ListOfTimeStamps (imported from OpenReadNomandRed)
#        - ENTER "L2" or "L1" (AS STRING!!!) to pick whether you want to track L2 or L1 losses