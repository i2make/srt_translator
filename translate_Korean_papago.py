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

def translate_ko(d_filename):
    
    # List
    translatedSentenceList = []
    
    # pre-process srt file
    aligned_srt_filename, sentenceNumber, editedStartTimeList, editedEndTimeList, editedSentenceList = \
        align_srt(d_filename, save=False)
  
    # setting driver
    driver = webdriver.Edge()
    driver.get('https://papago.naver.com/?sk=en&tk=ko&hn=0')
    #driver.minimize_window()
    time.sleep(3)

    # translate
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
            f.write(str(i) + '\n')                                              # number
            f.write(millisecondsToTime(int(j)).replace('.', ',') + ' --> ' + \
                    millisecondsToTime(int(k)).replace('.', ',') + '\n')             # time
            f.write(l + '\n\n')                                                 # sentence


if __name__ == '__main__':

    ###  variable initialization  ################################################

    path = u"D:\\Tutorials\\JS\\Remake Retro Games with JavaScript"

    input_dir = ''
    output_dir = ''
    fileList = []

    ###  local directory scan  ###################################################

    fileList = scan_path(path, '.srt', '_ko.srt')

    ###  exec batch ##############################################################

    # print(fileList)
    for down_filename in fileList[:]:
        print(down_filename)
        translate_ko(down_filename)
