# 파워쉘 가상환경 설정 명령
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
# .\venv\Scripts\activate.ps1

# import library
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from helper.align_srt_helper import align_srt
from helper.time_change_helper import millisecondsToTime
from helper.scan_path_helper import scan_path

def translate_ko(fileList: list):

    # setting driver
    driver = webdriver.Edge()
    driver.get('https://papago.naver.com/?sk=en&tk=ko&hn=0')
    #driver.minimize_window()
    time.sleep(3)

    # 번역된 문장을 담을 리스트 생성
    translatedSentenceList = []
    
    # fileList 순회하며 각 파일 처리하기.
    for filename in fileList:
        try:
            # 파일 이름 출력
            print(f"Processing file: {filename}")

            # pre-process srt file
            aligned_srt_filename, sentenceNumber, editedStartTimeList, editedEndTimeList, editedSentenceList = \
                align_srt(filename, save=False)

            # 번역
            for sentence in editedSentenceList:

                # xpath define
                input_xpath =  '//*[@id="txtSource"]'
                output_xpath = '//*[@id="txtTarget"]/span'
                                
                # textarea clear
                driver.find_element(By.XPATH, input_xpath).clear()
                time.sleep(0.2)

                # input sentence
                driver.find_element(By.XPATH, input_xpath).send_keys(sentence)
                time.sleep(3)

                # read translated textarea
                readText = driver.find_element(By.XPATH, output_xpath).text
                print(readText)
                time.sleep(0.5)

                # append list
                translatedSentenceList.append(readText)
         
            #########################
            ### write new srt file
            #########################
            newSrtFile = aligned_srt_filename[:-10] + '_ko.srt'
            with open(newSrtFile, 'w', encoding='UTF8') as f:
                for i, j, k, l in zip(range(sentenceNumber), editedStartTimeList, editedEndTimeList, translatedSentenceList):
                    f.write(str(i) + '\n')                              # number
                    f.write(millisecondsToTime(int(j)) + ' --> ' + \
                            millisecondsToTime(int(k)) + '\n')          # time
                    f.write(l + '\n\n')                                 # sentence
            # 저장 완료 메시지 출력
            print(f'{newSrtFile}가 저장되었음.')

        except:
            print('에러 발생, 다음 파일로 이동')
            continue


if __name__ == '__main__':

    path = u"D:\\Tutorials\\test_sample"

    fileList = scan_path(path, '.srt', '_ko.srt')

    translate_ko(fileList)
