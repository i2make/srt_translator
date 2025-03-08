# 파워쉘 파이썬 가상환경 실행:
# Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope Process
# ./venv/Scripts/Activate.ps1

# 필요한 라이브러리 설치:
# pip install selenium

# 배포를 위한 pyinstaller 명령어:
# pyinstaller --onefile -w translate_Korean_GUI.py


# 필요한 라이브러리 임포트
import tkinter as tk
import tkinter.ttk as ttk
import os, sys, time
from helper.scan_path_helper import scan_path
import threading
from selenium import webdriver
from selenium.webdriver.common.by import By
from helper.align_srt_helper import align_srt
from helper.time_change_helper import millisecondsToTime

# 전역 변수 선언
numOfLines = 0
stop_flag = False


##########################################################
# 함수 정의
##########################################################

# 진행 상황 업데이트 함수
def update_progressbar1(maximum, processed):
    progress1['maximum'] = maximum
    progress1['value'] = processed

    if progress1['maximum'] == processed:
        status_text.set('1 File Translate Complete')
    root.update_idletasks()

def update_progressbar2(maximum, processed):
    progress2['maximum'] = maximum
    progress2['value'] = processed

    if progress2['maximum'] == processed:
        status_text.set('1 File Translate Complete')
    root.update_idletasks()

def stop_process():
    global stop_flag
    stop_flag = True

def run_process():
    global stop_flag

    # 버튼을 '번역 중지'로 변경
    button_check.config(text='번역 중지', command=stop_process)

    fileList = scan_path(entry_dir.get(), '.srt', '_ko.srt')

    # 웹드라이버 시작
    driver = webdriver.Edge()
    driver.get('https://papago.naver.com/?sk=en&tk=ko&hn=0')
    # driver.minimize_window()
    time.sleep(3)

    # 전체 파일 반복 ####################################################
    for filename in fileList:
        # 번역된 문장을 담을 리스트 생성
        translatedSentenceList = []

        # progress bar 업데이트
        update_progressbar2(len(fileList), fileList.index(filename) + 1)

        # 파일 이름 출력 (디렉토리이름과 파일이름을 분리해서 출력)
        directory_name = os.path.dirname(filename)
        folder_text.set(directory_name)
        file_name = os.path.splitext(os.path.basename(filename))[0]
        file_text.set(file_name)

        # pre-process srt file
        aligned_srt_filename, sentenceNumber, editedStartTimeList, editedEndTimeList, editedSentenceList = \
            align_srt(filename, save=False)

        # 파일당 문장 반복 #################################################
        for sentence in editedSentenceList:

            status_text.set("번역중...")

            # stop_flag 체크
            if stop_flag:
                # 버튼을 '번역 시작'으로 변경하고 종료
                button_check.config(text='번역 시작', command=check_button_click)
                driver.quit()
                stop_flag = False
                progress1['value'] = 0  # progress bar 업데이트
                progress2['value'] = 0  # progress bar 업데이트
                root.update_idletasks()
                status_text.set("번역이 중지되었습니다.")
                return

            # progress bar 업데이트
            update_progressbar1(sentenceNumber, editedSentenceList.index(sentence) + 1)

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

            # 번역된 문장 표시
            text_console.config(state=tk.NORMAL)
            text_console.insert(tk.END, f"{readText}\n")
            text_console.see(tk.END)
            text_console.config(state=tk.DISABLED)
            time.sleep(0.5)

            # append list
            translatedSentenceList.append(readText)

        #########################
        ### write new srt file
        #########################
        if not aligned_srt_filename == '':
            newSrtFile = aligned_srt_filename[:-10] + '_ko.srt'
            with open(newSrtFile, 'w', encoding='UTF8') as f:
                for i, j, k, l in zip(range(sentenceNumber), editedStartTimeList, editedEndTimeList, translatedSentenceList):
                    f.write(str(i) + '\n')                              # number
                    f.write(millisecondsToTime(int(j)) + ' --> ' + \
                            millisecondsToTime(int(k)) + '\n')          # time
                    f.write(l + '\n\n')                                 # sentence
            
            # 저장 완료 메시지 출력
            status_text.set('파일이 저장되었음.')

            text_console.config(state=tk.NORMAL)
            text_console.insert(tk.END, f"\n{newSrtFile}이 저장되었습니다.\n")
            text_console.see(tk.END)
            text_console.config(state=tk.DISABLED)
        else:
            text_console.config(state=tk.NORMAL)
            text_console.insert(tk.END, f"\n{filename}은 마침표가 없어서 스킵됩니다.\n")
            text_console.see(tk.END)
            text_console.config(state=tk.DISABLED)

    button_check.config(text='번역 시작', command=check_button_click)
    driver.quit()
    progress1['value'] = 0  # progress bar 업데이트
    progress2['value'] = 0  # progress bar 업데이트
    root.update_idletasks()
    status_text.set("번역이 완료되었습니다.")

def check_button_click():
    dir = entry_dir.get()
    if not dir:
        status_text.set("디렉토리를 입력해주세요.")
        return
    try:
        # 쓰레딩으로 백그라운드에서 함수를 실행합니다.
        background_thread = threading.Thread(target=run_process)
        background_thread.start()

    except Exception as e:
        status_text.set("폴더나 파일이 존재하지 않습니다.")

        text_console.config(state=tk.NORMAL)
        text_console.insert(tk.END, f"문제가 발생했습니다.\n{e}\n")
        text_console.see(tk.END)
        text_console.config(state=tk.DISABLED)



################################################################
# Window 설정에 필요한 함수들
################################################################

# 엔트리 위젯의 모든 텍스트 선택 함수
def select_all(event):
    event.widget.select_range(0, 'end')
    event.widget.icursor('end')

# 붙여넣기 함수
def paste_from_clipboard(event=None):
    try:
        # 클립보드에서 내용 가져오기
        clipboard_content = root.clipboard_get()
        # Entry 위젯에 내용 붙여넣기
        entry_dir.delete(0, tk.END)
        entry_dir.insert(tk.END, clipboard_content)
    except tk.TclError:
        status_text.set("클립보드가 비어 있습니다.")

# 팝업 메뉴 생성 함수
def create_popup_menu():
    popup_menu = tk.Menu(entry_dir, tearoff=0)
    popup_menu.add_command(label="붙여넣기", command=paste_from_clipboard)

    def show_context_menu(event):
        # 마우스 오른쪽 버튼 클릭 시 팝업 메뉴 표시
        entry_dir.focus_set()  # Entry에 포커스 설정
        popup_menu.post(event.x_root, event.y_root)
    
    entry_dir.bind("<Button-3>", show_context_menu)  # 우클릭 이벤트 바인딩

################################################################
# Window 설정
################################################################

root = tk.Tk()
root.title("srt 자막 번역 프로그램")
root.geometry("640x480")

##################################################################
# 위젯 추가
##################################################################

# 레이블 위젯(링크 입력 안내문)
label_link = tk.Label(root, text="디렉토리:", font=("Arial", 12))
label_link.grid(row=0, column=0, padx=0, pady=10)

# 엔트리 위젯(디렉토리 입력란)
entry_dir = tk.Entry(root, width=48, font=("Arial", 12))
entry_dir.insert(0, "D:\\Tutorials\\test_sample")  # 기본값 설정
entry_dir.bind("<FocusIn>", select_all)
entry_dir.grid(row=0, column=1, padx=0, pady=10)

# Check_button 위젯
button_check = tk.Button(root, text="번역 시작", command=check_button_click)
# button_check = tk.Button(root, text="번역 시작", command=toggle_button)
button_check.grid(row=0, column=2, padx=5, pady=10)


# 분리선 ###########################################################
separator = tk.Frame(root, height=2, bd=2, relief=tk.SUNKEN)
separator.grid(row=1, pady=15, columnspan=3, sticky="ew")


# 엔트리 위젯에 선택 폴더 표시
folder_text = tk.StringVar()
folder_text.set("작업 폴더")
entry_folder = tk.Entry(root, textvariable=folder_text, width=68,
                       font=("Arial", 12), state='readonly',
                       readonlybackground='lightgray',
                       justify='center')
entry_folder.grid(row=2, column=0, columnspan=3, padx=12, pady=0)

# 엔트리 위젯에 선택 파일 표시
file_text = tk.StringVar()
file_text.set("작업 파일")
entry_file = tk.Entry(root, textvariable=file_text, width=68,
                       font=("Arial", 12), state='readonly',
                       readonlybackground='lightgray',
                       justify='center')
entry_file.grid(row=3, column=0, columnspan=3, pady=10)


# 분리선 ###########################################################
separator = tk.Frame(root, height=2, bd=2, relief=tk.SUNKEN)
separator.grid(row=4, pady=10, columnspan=3, sticky="ew")


# 상태 위젯
status_text = tk.StringVar()
status_text.set("상태 표시")
entry_status = tk.Entry(root, textvariable=status_text, width=68,
                        font=("Arial", 12), state='readonly',
                        justify='center', readonlybackground='lightgray',
                        relief='sunken')
entry_status.grid(row=8, column=0, columnspan=3, pady=5)

######################################################################

# 진행률 표시 바 위젯
progress1 = ttk.Progressbar(root, orient=tk.HORIZONTAL, length=500, mode='determinate')
progress1.grid(row=9, column=0, columnspan=3, pady=5)

# 진행률 표시 바 위젯
progress2 = ttk.Progressbar(root, orient=tk.HORIZONTAL, length=500, mode='determinate')
progress2.grid(row=10, column=0, columnspan=3, pady=5)

#################################################################

# Text 위젯
text_console = tk.Text(root, height=15, width=80)
text_console.grid(row=11, column=0, columnspan=3, padx=5, pady=5)
text_console.config(state=tk.NORMAL)
text_console.insert(tk.END, '이 프로그램은 srt 파일에 마침표(.)가 없는 경우, 번역하지 못하고 스킵합니다.\n')
text_console.insert(tk.END, '이 프로그램은 셀레니움을 사용해서 papago 웹사이트에서 직접 번역하기 때문에\n')
text_console.insert(tk.END, 'API-KEY가 필요하지 않으나 웹사이트가 변경되면 xpath를 변경해야 할 수도 있습니다.\n')
text_console.insert(tk.END, '빠르게 번역하거나 대량의 번역이 필요한 경우 적절하지 않습니다.\n')
text_console.insert(tk.END, '번역이 시작되면 웹페이지 창을 최소화 해도 번역이 진행되지만,\n')
text_console.insert(tk.END, '시작과 동시에 최소화 할 경우 문제가 발생했음.\n')
text_console.see(tk.END)
text_console.config(state=tk.DISABLED)

# 붙여넣기 우클릭 메뉴 생성 및 바인딩
create_popup_menu()

# 루프 실행
root.mainloop()
