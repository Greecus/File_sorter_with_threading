from threading import Thread, Event, RLock
import os
from collections import deque
import shutil

while True:
    try:
        FOLDER_PATH = input("Enter the path to the folder: ")
        if not os.path.exists(FOLDER_PATH): raise ValueError
    except ValueError:
        print("Provide correct path")
    else:
        break

SORTED_DIR=os.path.join(FOLDER_PATH,'Sorted')
try: os.mkdir(SORTED_DIR)
except FileExistsError:
    pass

files,dirs=deque(),deque()

def seperate_files_from_directories(folder_path,thread_ended_event,dirs_lock,files_lock):
    global files
    global dirs
    '''files = deque()
    dirs = deque()'''

    # Iterate over files in the folder
    for file_name in os.listdir(folder_path):
        file_path = os.path.join(folder_path, file_name)
        
        if os.path.isdir(file_path):
            with dirs_lock: dirs.append(os.path.join(folder_path,file_name))
        else:
            with files_lock: files.append(os.path.join(folder_path,file_name))
    thread_ended_event.set()

def sort_files(dir_for_sorted_files,thread_ended_event:Event,all_threads_ended_event:Event,files_lock:RLock):
    global files
    while True:
        while files:
            with files_lock:file_name = files.popleft()
            file_extension = os.path.splitext(file_name)[1].lower()
            try:
                shutil.move(file_name,os.path.join(dir_for_sorted_files,file_extension,file_name.split('\\')[-1]))
            except FileNotFoundError:
                os.mkdir(os.path.join(dir_for_sorted_files,file_extension))
                shutil.move(file_name,os.path.join(dir_for_sorted_files,file_extension,file_name.split('\\')[-1]))
            '''except Exception:
                pass'''

        if all_threads_ended_event.is_set(): break
        thread_ended_event.wait()
        thread_ended_event.clear()
        

# Iterate over files in the folder
for file_name in os.listdir(FOLDER_PATH):
    file_path = os.path.join(FOLDER_PATH, file_name)
    
    if os.path.isdir(file_path):
        dirs.append(file_path)
    else:
        files.append(file_path)

thread_ended_event=Event()
all_threads_ended_event=Event()
dirs_lock=RLock()
files_lock=RLock()
sorting_thread=Thread(target=sort_files,args=(SORTED_DIR,thread_ended_event,all_threads_ended_event,files_lock))
sorting_thread.start()
threads=[]
while dirs:
    while dirs:
        directory=dirs.popleft()
        thread= Thread(target=seperate_files_from_directories,args=(directory,thread_ended_event,dirs_lock,files_lock))
        thread.start()
        threads.append(thread)
    [el.join() for el in threads]
    threads.clear()
all_threads_ended_event.set()