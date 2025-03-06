
# imports
from helper.time_change_helper import timeToMilliseconds, millisecondsToTime


def align_srt(srtFile: str, save:bool) -> tuple:
    startTimeList = []
    endTimeList = []
    sentenceList = []

    ###  total line of file  ###
    with open(srtFile, 'r', encoding='UTF8') as f:
        # number of line
        numberOfLines = len(f.readlines())

    #############################################################
    ###     read lines
    #############################################################
    with open(srtFile, 'r', encoding='UTF8') as f:
        for i in range(numberOfLines):
            readLine = f.readline()
            try:
                '-->' in readLine                 # if time line then True
                numberOfLines += 1
                readLine = readLine.strip('\n')
                temp = readLine.split(' --> ')
                startTimeList.append(timeToMilliseconds(temp[0].replace(',', '.')))
                endTimeList.append(timeToMilliseconds(temp[1].replace(',', '.')))

                readLine = f.readline()
                
                if '. ' in readLine and '.\n' in readLine:              # __. __.\n
                    readLine = readLine.replace('.\n', '.(^&)')
                    sentenceList.append(readLine)
                elif not '. ' in readLine and '.\n' in readLine:        # ______.\n
                    readLine = readLine.replace('.\n', '.(^&)')
                    sentenceList.append(readLine)
                elif '. ' in readLine and '\n' in readLine:             # __. ___\n
                    readLine = readLine.replace('. ', '.(^*)', 1)
                    readLine = readLine.replace('\n', ' ')
                    sentenceList.append(readLine)
                elif not '. ' in readLine and not '.\n' in readLine:    # _______\n
                    readLine = readLine.replace('\n', ' ')
                    sentenceList.append(readLine)
            except:
                pass

    #################################################################
    ###  edit sentence
    #################################################################
    
    ###  concatenate sentence : 문장 전체를 연결해서 하난의 str로 만듬
    l = str()
    for i in sentenceList:
        l = l + i

    # check unable parsing : 마침표가 없으면 파싱할 수 없다
    if not '.(^&)' in l:
        print('#################### not period, exit')
        print('filename: ', srtFile)
        exit(1)

    # split by period : 마침표를 기준으로 문장을 분리해서 editedSentenceList를 만듬
    temp = l.split('.(^&)')
    temp2 = []
    editedSentenceList = []
    for i in temp:
        temp2.append(i.split('.(^*)'))
    flat_list = [item for sublist in temp2 for item in sublist] # remove nested list
    for i in flat_list:
        i = i + '.\n'
        editedSentenceList.append(i)

    # create list
    editedStartTimeList = [0 for i in range(len(sentenceList))]
    editedEndTimeList   = [0 for i in range(len(sentenceList))]

    ##########################################################################
    ###  edit time : 재정렬된 문장에 맞게 시작,끝 시간을 조정
    ##########################################################################
    
    editedStartTimeList[0] = startTimeList[0]       # first start time

    for i in range(len(sentenceList)):
        # period at middle of sentence // _______. ________\n //
        if '.(^*)' in sentenceList[i] and not '.(^&)' in sentenceList[i]:
            # devide time
            totalNumberOfWords = sentenceList[i].split(' ')
            firstNumberOfWords = sentenceList[i].split('.(^*)')

            ratio = len(firstNumberOfWords[0].split(' ')) / len(totalNumberOfWords)
            editedEndTimeList[i] = startTimeList[i] + int((endTimeList[i] - startTimeList[i]) * ratio)
            try:
                editedStartTimeList[i + 1] = editedEndTimeList[i]
            except:
                pass

        # period at end of sentence // ________.\n //
        elif not '.(^*)' in sentenceList[i] and '.(^&)' in sentenceList[i]:
            try:
                editedEndTimeList[i] = endTimeList[i]
                editedStartTimeList[i + 1] = startTimeList[i + 1]
            except:
                pass
        
        # period at middle of sentence // _______. ________.\n //
        elif '.(^*)' in sentenceList[i] and '.(^&)' in sentenceList[i]:
            try:
                editedEndTimeList[i] = endTimeList[i]
                editedStartTimeList[i + 1] = startTimeList[i + 1]
            except:
                pass
    
    editedEndTimeList[-1] = endTimeList[-1]         # last end time

    ###################################################################
    ### remove zero in time list
    ###################################################################
    
    if editedStartTimeList[0] == 0: # making not 0 start time
        editedStartTimeList[0] = 1
    editedStartTimeList = [i for i in editedStartTimeList if (i != 0)]
    editedEndTimeList = [i for i in editedEndTimeList if (i != 0)]

    newVttFile = srtFile[:-4] + '_align.vtt'

    ###################################################################
    ###  write new vtt file
    ###################################################################
    if save:
        with open(newVttFile, 'w', encoding='UTF8') as f:
            f.write('WEBVTT\n\n')
            for i, j, k, l in zip(range(len(sentenceList)), editedStartTimeList, editedEndTimeList, editedSentenceList):
                f.write(str(i) + '\n')                                                      # number
                f.write(millisecondsToTime(j) + ' --> ' + millisecondsToTime(k) + '\n')     # time
                f.write(l + '\n')                                                           # sentence
    
    return newVttFile, len(sentenceList), editedStartTimeList, editedEndTimeList, editedSentenceList

if __name__ == '__main__':

    srtFile = u''
    print(align_srt(srtFile, save=False))
    