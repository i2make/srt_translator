# 파워쉘 가상환경 활성화
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
# .\venv\Scripts\activate.ps1

# 임포트
import re
from helper.time_change_helper import timeToMilliseconds, millisecondsToTime

# 변수
# 문장 종결 문자
# sentenceEndings = ['.', '!', '?']
# ending = '.'

# 중간 종결 문자까지의 시간 추정 함수
def estimateTime(startTime, endTime, sentence):
    wordTime = int((endTime - startTime) / len(sentence))
    return wordTime

# 시작, 끝 시간 및 문장 추출 함수
def extract_times_and_sentences(text):
    # 정규표현식 패턴: (|시간|)문장(|시간|)
    pattern = r'\(\|(\d+)\|\)(.*?)\(\|(\d+)\|\)'
    
    # 모든 일치하는 부분 찾기
    matches = re.findall(pattern, text)
    
    startTimeList = []
    endTimeList = []
    sentenceList = []
    
    for match in matches:
        startTime = match[0]
        sentence = match[1].strip()  # 문장의 앞뒤 공백 제거
        endTime = match[2]
        
        startTimeList.append(startTime)
        endTimeList.append(endTime)
        sentenceList.append(sentence)
    
    return startTimeList, endTimeList, sentenceList

# 문장 내의 스페이스 정리 함수
def clean_spaces(sentence):
    # re.sub() 함수는 정규표현식에 매치되는 부분을 다른 문자열로 대체합니다.
    # 여기서 '\s+'는 하나 이상의 공백 문자를 의미하고, ' '는 단일 공백으로 대체합니다.
    cleaned_sentence = re.sub(r'\s+', ' ', sentence)
    return cleaned_sentence.strip()  # 혹시 남아있는 앞뒤 공백 제거

# srt 파일 저장 함수
def write_srtFile(newSrtFile, startTimeList, endTimeList, finalSentenceList):
    with open(newSrtFile, 'w', encoding='UTF8') as f:
        for i, j, k, l in zip(range(len(finalSentenceList)), startTimeList, endTimeList, finalSentenceList):
            f.write(str(i) + '\n')                                                              # number
            f.write(millisecondsToTime(int(j)) + ' --> ' + millisecondsToTime(int(k)) + '\n')   # time
            f.write(l + '\n\n')                                                                 # sentence

# 라인을 읽어서 정리
def read_and_align_srt(rawSentenceList, ending):
    numberOfLines = len(rawSentenceList)    # 총 라인수
    sentenceList = []                       # 리턴용 리스트

    for i in range(numberOfLines):
        readLine = rawSentenceList[i] # 한 줄 읽기

        # 공백 줄인 경우:
        if readLine.strip('\n') == '':          # if empty line then True
            continue

        # identifier 표시줄인 경우:
        if readLine.strip('\n').isdigit():    # if identifier line then True
            # print(readLine)
            continue

        # 타임코드 표시줄인 경우:
        if '-->' in readLine:                 # if time line then True
            # print(readLine)                     # print time line
            readLine = readLine.strip('\n')     # remove '\n'
            temp = readLine.split(' --> ')      # divide
            startTime = timeToMilliseconds(temp[0].replace(',', '.'))   # start time
            endTime = timeToMilliseconds(temp[1].replace(',', '.'))   # end time
            continue

        # 문장의 중간에 종결 문자가 있는 경우: ____. _____\n 
        if f'{ending} ' in readLine and not f'{ending}\n' in readLine:

            # 글자당 시간을 구한다.
            estimateTimeUnit = estimateTime(startTime, endTime, readLine)
            # print(f'시간유닛: {estimateTimeUnit}')

            # 문장을 나눈다. readLine[0], readLine[1], ...
            readLine = readLine.split(f'{ending} ')

            # 문장 끝에 마침표 추가
            for i in range(len(readLine)-1):            
                readLine[i] = readLine[i] + f'{ending}'

            # 문장 중간의 마침표 위치의 시간 계산
            middleEnding = []
            previousTime = startTime
            middleEnding.append(startTime)
            for i in range(len(readLine)):
                middleEnding.append(previousTime + estimateTimeUnit * len(readLine[i]))
                previousTime = previousTime + estimateTimeUnit * len(readLine[i])

            # for i in range(len(readLine)):
            #     print(f'문장: {readLine[i]} : {middleEnding[i]}')

            # 문장을 sentenceList에 기록
            for i in range(len(readLine)-1):
                # 첫 번째 문장 저장
                temp = f'(|{middleEnding[i]}|)'                
                temp = temp + readLine[i].strip('\n')
                temp = temp + f'(|{middleEnding[i+1]}|)'
                sentenceList.append(temp)

            # 마지막 문장 저장
            temp = f'(|{str(middleEnding[-2])}|)'
            temp = temp + readLine[-1].strip('\n')
            temp = temp + f' (|{str(endTime)}|)-'
            sentenceList.append(temp)
            continue

        # 문장의 끝에 종결 문자가 있는 경우: ____________.\n
        if not f'{ending} ' in readLine and f'{ending}\n' in readLine:
            temp = f'(|{str(startTime)}|) '
            temp = temp + readLine.strip('\n')  # 개행 문자 제거
            temp = temp + f' (|{str(endTime)}|)'
            sentenceList.append(temp)
            continue

        # 문장의 중간과 끝에 종결 문자가 있는 경우: ______. ______.\n
        if f'{ending} ' in readLine and f'{ending}\n' in readLine:

            # 글자당 시간을 구한다.
            estimateTimeUnit = estimateTime(startTime, endTime, readLine)
            # print(f'시간유닛: {estimateTimeUnit}')

            # 문장을 나눈다. readLine[0], readLine[1], ...
            readLine = readLine.split(f'{ending} ')

            # 문장 끝에 마침표 추가
            for i in range(len(readLine)-1):            
                readLine[i] = readLine[i] + f'{ending}'

            # 문장 중간의 마침표 위치의 시간 계산
            middleEnding = []
            previousTime = startTime
            middleEnding.append(startTime)
            for i in range(len(readLine)):
                middleEnding.append(previousTime + estimateTimeUnit * len(readLine[i]))
                previousTime = previousTime + estimateTimeUnit * len(readLine[i])

            # for i in range(len(readLine)):
            #     print(f'문장: {readLine[i]} : {middleEnding[i]}')

            # 문장을 sentenceList에 기록
            for i in range(len(readLine)):
                # 첫 번째 문장 저장
                temp = f'(|{middleEnding[i]}|)'                
                temp = temp + readLine[i].strip('\n')
                temp = temp + f'(|{middleEnding[i+1]}|)'
                sentenceList.append(temp)

            # 마지막 문장 저장
            # temp = f'(|{str(middleEnding[-2])}|)'
            # temp = temp + readLine[-1].strip('\n')
            # temp = temp + f' (|{str(endTime)}|)'
            # sentenceList.append(temp)
            continue

        # 문장에 종결 문자가 없는 경우: ___________\n
        if not f'{ending} ' in readLine and not f'{ending}\n' in readLine:
            # print('/' + readLine)
            temp = f'(|{str(startTime)}|) '
            readLine = readLine.replace('\n', ' ')
            temp = temp + readLine
            temp = temp + f' (|{str(endTime)}|)-'
            sentenceList.append(temp)
            continue
    return sentenceList

# srt 파일에 마침표가 있는지 체크
def check_ending(sentenceList:list, ending='.') -> bool:
    # 마침표가 없으면 파싱할 수 없다
    l = ''
    for sentence in sentenceList:
        # 공백 줄인 경우:
        # print('empty line')
        if sentence.strip('\n') == '':      # if empty line then True
            continue

        # identifier 표시줄인 경우:
        # print('identifier line')
        if sentence.strip('\n').isdigit():  # if identifier line then True
            continue

        # 타임코드 표시줄인 경우:
        # print('time line')                   # if time line then True
        if '-->' in sentence:               # if time line then True
            continue

        # concat list
        # print('concat list')
        l = l + sentence                    # concat list

    if not f'{ending} ' in l or not f'{ending}\n' in l:
        print('#################### not period, exit')
        return False
    return True

# srt 파일을 문장 단위로 정리하는 함수
def align_srt(srtFile: str, save:bool, _ending='.') -> tuple:
    rawSentenceList = []    # 읽어 온 srt 파일
    sentenceList = []       # 정리 과정에 사용할 문장리스트
    ending = _ending        # 종결 문자

    #########################################################
    ###  파일 안의 문장을 읽어서 리스트에 담는다
    #########################################################
    with open(srtFile, 'r', encoding='UTF8') as f:
        # 총 라인수
        numberOfLines = len(f.readlines())
        # 파일 포인터를 처음으로
        f.seek(0)
        # 문장 리스트
        for i in range(numberOfLines):
            readLine = f.readline()
            rawSentenceList.append(readLine)

    # srt 파일에 마침표가 있는지 확인
    if not check_ending(rawSentenceList):
        return False, 0, [], [], []

    #############################################################
    ###  라인을 읽어서 마침표 단위로 정리
    #############################################################
    sentenceList = read_and_align_srt(rawSentenceList, ending)

    # print(f'총 개수: {len(sentenceList)}')
    # for i in range(len(sentenceList)):
    #     print(sentenceList[i], '\n')
    # exit(1)

    ##################################################################
    # 문장을 연결하고 정리
    ##################################################################

    # 문장 연결
    concatSentence = str()
    for i in sentenceList:
        concatSentence = concatSentence + i

    # 문장 중간의 (|숫자|)-(|숫자|) 제거
    concatSentence = re.sub(r'\(\|\d+\|\)-\(\|\d+\|\)', '', concatSentence)

    # 시작, 끝 시간과 문장을 리스트로 만든다
    startTimeList, endTimeList, finalSentenceList = extract_times_and_sentences(concatSentence)

    # 문장 중간의 여러 개의 스페이스 정리
    for i in range(len(finalSentenceList)):
        finalSentenceList[i] = clean_spaces(finalSentenceList[i])  # 스페이스 클리어

    # 테스트 인쇄
    # for i in range(len(finalSentenceList)):
    #     # print(f'{startTimeList[i]} - {endTimeList[i]}: {finalSentenceList[i]}\n')
    #     print(f'{millisecondsToTime(int(startTimeList[i]))} - {millisecondsToTime(int(endTimeList[i]))}: {finalSentenceList[i]}\n')
    # exit(1)

    ########################################################################
    # 파일 이름 설정 및 저장
    ########################################################################
    newSrtFile = srtFile[:-4] + '_align.srt'
    if save:
        write_srtFile(newSrtFile, startTimeList, endTimeList, finalSentenceList)

    return newSrtFile, len(finalSentenceList), startTimeList, endTimeList, finalSentenceList


if __name__ == '__main__':
    srtFile = u"D:\\Tutorials\\test_sample"
    align_srt(srtFile, save=True)
