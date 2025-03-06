import os

def scan_path(path:str, ext:str, excepts:str) -> list:

    ### make .vtt filename list ##################################
    filelist = []
    len_ext = -len(ext)
    len_excepts = -len(excepts)
    for root, dirs, files in os.walk(path):
        for file in files:
            # append the file name to the list
            try:
                if file[len_excepts:].lower() == excepts.lower():
                    pass
                elif file[len_ext:].lower() == ext.lower():
                    temp = file[:len_ext]
                    temp = temp + excepts
                    #print(temp)
                    if not temp in files:
                        filelist.append(os.path.join(root, file))
                        #print(os.path.join(root, file))
            except:
                print('except')

    return filelist


if __name__ == '__main__':
    path = ""
    result = scan_path(path, '.mp4', '_ko.srt')
    for i in result:
        print(i)
        exit(1)

