import OpenReadNomandRedV2
import numpy as np
from datetime import datetime

'''
General notes & remarks:
- I assume time_end as time of first non-zero reading after (unexpected) loss
- as data is appended during the checking, OverviewTable is kinda ordered with increasing time & sat_id since we check it in that order
- THIS IS FINAL VERSION (04.05)
'''

def FindLosses(ListOfDataArrays, ListOfTimeStamps):
    print("we started")

    OverviewTable = []
    TrackDurations = []
    for i in range(1, 33): #i is satellite id 
        BeginLossHad = False
        LossNoted = False
        TrackDurationCount = 0
        print("Looking at sat_id", i)

        for Time in range(len(ListOfTimeStamps)): #choosing variables -> ListOfDataArrays[time][sat_id][parameter]
            DummyArray2 = ListOfDataArrays[Time] #one time slice of the read file, DummyArray2[sat_id][parameter]
            if Time > 0:
                PreviousDummy = ListOfDataArrays[Time - 1] #same, for previous time stamp
            if Time < (len(ListOfDataArrays)-1):
                NextDummy = ListOfDataArrays[Time + 1] #same, for next time stamp

            if int(DummyArray2[i][8]) == 1: #if it's supposed to be tracked
                    
                if (DummyArray2[i][0] * DummyArray2[i][1]) != 0.0 and (PreviousDummy[i][0] * PreviousDummy[i][1]) == 0.0 and BeginLossHad == False: #check if begin loss occured
                    BeginLossHad = True
                    TrackBegin = ListOfTimeStamps[Time]
                
                if (DummyArray2[i][0] * DummyArray2[i][1]) == 0.0 and BeginLossHad == True: #this is not the first loss -> unexpected!
                    if LossNoted == False: #only first 0 detected, we don't want to record every 0
                        RunningLossList = [] #create mini-list for singe loss data
                        SaveTimeDummy = Time
                        time_begin = ListOfTimeStamps[Time]
                        RunningLossList.append(time_begin)
                        LossNoted = True #set to true to not note further 0s in the loss

                    if NextDummy[i][8] == 0.0: #oh it was end loss! after 0s it's not supposed to be tracked 
                        TrackEnd = ListOfTimeStamps[SaveTimeDummy-1]
                        BeginLossHad = False
                        LossNoted = False

                if (DummyArray2[i][0] * DummyArray2[i][1]) != 0.0 and LossNoted == True: #loss ends! we see something right after after 0
                    time_end = ListOfTimeStamps[Time - 1] #I assume time_end to be the time of first non-zero reading 
                    sat_id = i
                    td = time_end-time_begin
                    duration = td.total_seconds() + 1
                    RunningLossList.append(time_end)
                    RunningLossList.append(duration)
                    RunningLossList.append(sat_id)
                    OverviewTable.append(RunningLossList)

                    LossNoted = False #finished gathering data from one loss
                
                if (DummyArray2[i][0] * DummyArray2[i][1]) != 0.0 and NextDummy[i][8] == 0.0:
                    TrackEnd = ListOfTimeStamps[Time]
                    TD = TrackEnd - TrackBegin
                    TrackDuration = TD.total_seconds() + 1
                    TrackDurationCount += TrackDuration

            elif int(DummyArray2[i][8]) == 0.0:
                BeginLossHad = False
                LossNoted = False

        TrackDurations.append(TrackDurationCount)

    OverviewTable = np.array(OverviewTable)
    TrackDurations = np.sum(TrackDurations)          

    return OverviewTable, TrackDurations


table, tracks_total_duration = FindLosses(OpenReadNomandRedV2.ListOfDataArrays, OpenReadNomandRedV2.ListOfTimeStamps)

print(#"Loss Table:", "\n", table,
      "\n Nr of losses:", len(table),
      "\n Total duration:", np.sum(table[:, 2], axis=0), "s",
      "\n Average duation time:", np.average(table[:, 2], axis=0), "s"
      "\n Median duation time:", np.median(table[:, 2], axis=0), "s",
      "\n Percentage of losses:", np.sum(table[:, 2], axis=0)/tracks_total_duration)


#structure: columns -> [time_begin (date format), time_end (date format), duration (seconds), sat_id (int)]
#           rows -> all losses "listed" (so length is total nr of losses)
#to use: - copy names ListOfDataArrays, ListOfTimeStamps (imported from OpenReadNomandRedV2)
#        - dd= table[0][0].strftime("%m/%d/%Y, %H:%M:%S.%f") -> date format to string
