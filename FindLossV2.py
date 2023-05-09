import OpenReadNomandRedV2
import numpy as np
from datetime import datetime

'''
General notes & remarks:
- I assume time_end as time of first non-zero reading after (unexpected) loss
- as data is appended during the checking, OverviewTable is kinda ordered with increasing time & sat_id since we check it in that order
- THIS IS FINAL VERSION (04.05)
- THIS HAS BEEN CLEANED 
'''


def FindLosses(ListOfDataArrays, ListOfTimeStamps): #Function to find the unexpected losses.
    OverviewTable = [] #Empty lists to be filled in later.
    TrackDurations = []

    for i in range(1, 33):  #Loop past all satellites.
        BeginLossHad = False #In order to know the sort of loss we look at, we shall know the "state" of the algorithm.
        LossNoted = False
        TrackDurationCount = 0 #Variable to count the duration of all tracks.

        for Time in range(len(ListOfTimeStamps)):  #Loop through the time (per satellite).
            DummyArray2 = ListOfDataArrays[Time]  #Load the data of one point in time.
            if Time > 0:
                PreviousDummy = ListOfDataArrays[Time - 1]  #Load the previous and next datapoint.
            if Time < (len(ListOfDataArrays) - 1):
                NextDummy = ListOfDataArrays[Time + 1]

            if int(DummyArray2[i][8]) == 1:  #Checks whether the satellite was supposed to be tracked.

                if (DummyArray2[i][0] * DummyArray2[i][1]) != 0.0 and (PreviousDummy[i][0] * PreviousDummy[i][1]) == 0.0 and BeginLossHad == False:
                    #This means the track is past the stage of the first "loss"(expected).
                    BeginLossHad = True
                    TrackBegin = ListOfTimeStamps[Time] #Save at what time the track began.

                if (DummyArray2[i][0] * DummyArray2[i][1]) == 0.0 and BeginLossHad == True:
                    #This means we are potentially experiencing an unexpected loss.
                    if LossNoted == False:  #This means this is the start of this loss.
                        RunningLossList = []  
                        SaveTimeDummy = Time
                        time_begin = ListOfTimeStamps[Time]
                        RunningLossList.append(time_begin)
                        LossNoted = True  #We save the begin time of this possibly unexpected loss 
                        # and set LossNoted to True to let the algorithm know the next zero it will encounter is not the
                        # start of this loss.

                    if NextDummy[i][8] == 0.0:  #This check whether at the end of this loss the satellite was still 
                        # supposed to be tracked. If it was not, the loss was actually expected since it is an endloss.
                        TrackEnd = ListOfTimeStamps[SaveTimeDummy - 1]
                        BeginLossHad = False
                        LossNoted = False

                if (DummyArray2[i][0] * DummyArray2[i][1]) != 0.0 and LossNoted == True:  #The loss ended and we see 
                    #that after this the satellite is still being tracked, meaning the loss was unexpected.
                    time_end = ListOfTimeStamps[Time - 1]  #Therefor we save the time of the end of the loss.
                    sat_id = i
                    td = time_end - time_begin
                    duration = td.total_seconds() + 1 #Compute the length and save the times.
                    RunningLossList.append(time_end)
                    RunningLossList.append(duration)
                    RunningLossList.append(sat_id)
                    OverviewTable.append(RunningLossList)

                    LossNoted = False  #This loss is finished, but another possibly unexpected loss can still occur. 
                    #We reset the state.

                if (DummyArray2[i][0] * DummyArray2[i][1]) != 0.0 and NextDummy[i][8] == 0.0: 
                    #This denotes the end of the entire track. 
                    #We save the time to compute the duration of the entire track
                    TrackEnd = ListOfTimeStamps[Time]
                    TD = TrackEnd - TrackBegin
                    TrackDuration = TD.total_seconds() + 1
                    TrackDurationCount += TrackDuration

            elif int(DummyArray2[i][8]) == 0.0: #The track ended, we reset all states for next tracks.
                BeginLossHad = False
                LossNoted = False

        TrackDurations.append(TrackDurationCount)

    OverviewTable = np.array(OverviewTable)
    TrackDurations = np.sum(TrackDurations) #We compile the lists and compute the relevant durations.

    return OverviewTable, TrackDurations


table, tracks_total_duration = FindLosses(OpenReadNomandRedV2.ListOfDataArrays, OpenReadNomandRedV2.ListOfTimeStamps)
#This runs the algorithm and saves the outcomes for later plotting.
