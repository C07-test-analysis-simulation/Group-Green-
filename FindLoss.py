import OpenReadNomandRedV2
import numpy as np
from datetime import datetime

'''
General notes & remarks:
- I assume time_end as time of first non-zero reading after (unexpected) loss
- as data is appended during the checking, OverviewTable is kinda ordered with increasing time & sat_id since we check it in that order
'''

def FindLosses(ListOfDataArrays, ListOfTimeStamps, L2orL1):
    print("we started")
    if str(L2orL1) == "L2": #pick which loss we're looking at
        L = 1
    if str(L2orL1) == "L1":
        L = 0

    OverviewTable = []
    for i in range(1, 33): #i is satellite id 
        BeginLossHad = False
        LossNoted = False
        print("Looking at sat_id", i)

        for Time in range(len(ListOfTimeStamps)): #choosing variables -> ListOfDataArrays[time][sat_id][parameter]
            DummyArray2 = ListOfDataArrays[Time] #one time slice of the read file, DummyArray2[sat_id][parameter]
            if Time > 0:
                PreviousDummy = ListOfDataArrays[Time - 1] #same, for previous time stamp
            if Time < (len(ListOfDataArrays)-1):
                NextDummy = ListOfDataArrays[Time + 1] #same, for next time stamp

            if int(DummyArray2[i][8]) == 1: #if it's supposed to be tracked
                #if DummyArray2[i][L] == 0.0 and Time%10 == 0.0:
                  #  print("Zero!", ListOfTimeStamps[Time])
                    
                if DummyArray2[i][L] != 0.0 and PreviousDummy[i][L] == 0.0 and BeginLossHad == False: #check if begin loss occured
                    BeginLossHad = True
                    #print("Begin loss ends!", ListOfTimeStamps[Time])
                
                if DummyArray2[i][L] == 0.0 and BeginLossHad == True: #this is not the first loss -> unexpected!
                    if LossNoted == False: #only first 0 detected, we don't want to record every 0
                        RunningLossList = [] #create mini-list for singe loss data
                        time_begin = ListOfTimeStamps[Time]
                        RunningLossList.append(time_begin)
                        LossNoted = True #set to true to not note further 0s in the loss

                    if NextDummy[i][8] == 0.0: #oh it was end loss! after 0s it's not supposed to be tracked 
                       # print("End loss!", ListOfTimeStamps[Time])
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

table = FindLosses(OpenReadNomandRedV2.ListOfDataArrays, OpenReadNomandRedV2.ListOfTimeStamps, 'L2')

print("Loss Table:","\n", table,
      "\n Nr of losses:", len(table),
      "\n Total duration:", np.sum(table[:, 2], axis=0), "s",
      "\n Average duation time:", np.average(table[:, 2], axis=0), "s"
      "\n Median duation time:", np.median(table[:, 2], axis=0), "s",
      "\n Percentage of losses:", 100*len(table)/len(OpenReadNomandRedV2.ListOfDataArrays), "%") #ask and change later


#structure: columns -> [time_begin (date format), time_end (date format), duration (seconds), sat_id (int)]
#           rows -> all losses "listed" (so length is total nr of losses)
#to use: - copy names ListOfDataArrays, ListOfTimeStamps (imported from OpenReadNomandRedV2)
#        - ENTER "L2" or "L1" (AS STRING!!!) to pick whether you want to track L2 or L1 losses
#        - dd= table[0][0].strftime("%m/%d/%Y, %H:%M:%S.%f") -> date format to string