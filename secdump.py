import html5lib
from bs4 import BeautifulSoup
import time
import json
import os
import pyautogui
import pyperclip
import sys



# assumptions/questions
"""
Employee Name column is unique
each employee's docs in a separate folder
Do you want the meta data in a json or something? Who uploaded it, when it was uploaded, and doc type?
Do you need any data from the employee table? employee id, title, facility code, org, clearance, access/caveats, status, Type, Citizenship? I imagine you have this somewhere else, but thought I'd ask jsut in case.
"""

SEPARATE_FOLDER = True
PATH_TO_SAVE_PDFS = os.getcwd()#update if different


def new_tab():
    # open a new tab and switch to it
    logger.info('opening new tab')
    pyautogui.hotkey('ctrl', 't')
    time.sleep(1)


def close_tab():
    logger.info('closing tab')
    pyautogui.hotkey('ctrl', 'f4')
    time.sleep(1)


def do_captcha(text=''):
    # to notify the operator that a captcha needs to be clicked or that a program needs attention.
    # will raise error (so the site will be skipped) if a text file named skip.txt is in the cwd
    # will play a sound of the json is set to true
    files = os.listdir()
    if 'skip.txt' in files:
        raise OSError('Would have gotten stuck on do_captcha(), but we dont want to stop.')
        return None
    logger.info('start')
    if text == '':
        text = 'do captcha'
    with open(os.path.join('support_files', 'play_captcha_sound.json')) as f:
        play_sound = json.load(f)['sound']

    if play_sound:
        wav_file = os.path.join('support_files', 'Alarm05.wav')
        playsound(wav_file)
    x = pyautogui.alert(text=text, title='do captcha', button='captcha submitted')
    logger.info('done')
    return x


def get_soup():
    old_clipboard = pyperclip.paste()
    pyperclip.copy('')

    def get_to_html():
        pyautogui.hotkey('ctrl', 'shift', 'c')
        time.sleep(2)
    get_to_html()
    time.sleep(.5)
        #pyautogui.press('down')
        #time.sleep(.5)
    pyautogui.hotkey('ctrl', 'c')
    html_found = False
    counter = 0
    pyautogui.press('home')
    time.sleep(.5)
    while not html_found:
        if pyperclip.paste()[0:5] == '<html':
            html_found = True
            break
        else:
            counter += 1
            time.sleep(.5)
            pyautogui.hotkey('ctrl', 'c')
            time.sleep(.5)
            pyautogui.press('down')
            time.sleep(.5)
            if counter % 15 == 0:
                pyautogui.press('home')
                time.sleep(.5)
            if counter == 50:
                pyautogui.press('f12')
                time.sleep(1)
                get_to_html()
                pyautogui.hotkey('ctrl', 'c')
                time.sleep(.5)
            if counter > 100:
                raise OSError("couldn't get soup in less than 100 tries")
    time.sleep(.5)
    pyautogui.press('f12')

    soup = BeautifulSoup(pyperclip.paste(), 'html.parser')
    pyperclip.copy(old_clipboard)
    return soup


def run_js(script):
    # was javascript_in_browser
    pyautogui.hotkey('ctrl', 'shift', 'j')
    time.sleep(1)
    pyautogui.typewrite(script)
    time.sleep(1)
    pyautogui.press('enter')
    time.sleep(.75)
    pyautogui.press('f12')
    time.sleep(1)


def update_completed(person_name):
    path_to_tracker = 'tracker.json'
    with open(path_to_tracker) as f:
        data = json.load(f)
    data.append(person_name)
    with open(path_to_tracker, 'w') as f:
        json.dump(data, f)


def check_if_done(person_name):
    path_to_tracker = 'tracker.json'
    with open(path_to_tracker) as f:
        data = json.load(f)
    if person_name in data:
        return True
    return False


def set_document_path(soup, row_number):
    table = soup.find_all('table')[2]
    rows = table.find_all('tr')
    row = rows[row_number]
    description = row.find_all('td')[3]
    employee_name = soup.find_all(class_='hpanel')[1].find_all(class_='ng-binding')[0].text.replace(',\xa0', ' ')
    file_name = f'{employee_name}_{description}.pdf'
    path = os.path.join(PATH_TO_SAVE_PDFS, file_name)
    if SEPARATE_FOLDER:
        if os.path.exists(os.path.join(PATH_TO_SAVE_PDFS, employee_name)):
            pass
        else:
            os.mkdir(os.path.join(PATH_TO_SAVE_PDFS, employee_name))
        path = os.path.join(PATH_TO_SAVE_PDFS, employee_name, file_name)
    return path


def create_tracker():
    path_to_tracker = 'tracker.json'
    if os.path.exists(path_to_tracker):
        pass
    else:
        with open(path_to_tracker, 'w') as f:
            json.dump({}, f)
    return True


def download_one_persons_docs():
    #soup = get_soup()
    # set the visible rows to be the max
    script = 'document.getElementsByTagName("select")[0].focus();'
    run_js(script)
    pyautogui.press('end')
    #time.sleep(1)
    #pyautogui.press('enter')
    #time.sleep(1)
    #pyautogui.press('enter')
    #time.sleep(1)
    # not sure if I need this. See if it works.
    #script = 'document.getElementsByClassName("dataTables_info")[0].focus();'
    #run_js(script)
    time.sleep(2)
    soup = get_soup()
    downloaded_for_someone = False
    rows = soup.find('table').find_all('tr')[1:]# exclude the header
    row_counter = 0# zero because of header
    for row in rows:
        row_counter += 1
        employee_name = row.find_all('td')[2].text
        if check_if_done(employee_name):
            print(f'already completed {employee_name}')
            continue
        else:
            # click edit
            print(f'starting {employee_name}')
            script = f'document.getElementsByTagName("table")[0].getElementsByTagName("tr")[{row_counter}].getElementsByClassName("cust_icon_blue")[1].click();'# changed from 0 to 1 since you need to click on edit, not view. changed after chat on 12/22 at 15:22 ET. 
            run_js(script)
            time.sleep(2)
            soup = get_soup()
            # click on the 'others' tab
            #soup.find_all(class_='nav-link')[7].text == 'Others'
            script = 'document.getElementsByClassName("nav-link")[7].click();'
            run_js(script)
            time.sleep(2)
            soup = get_soup()
            # click the associated box element
            a_tags= soup.find_all('a')
            for i in range(len(a_tags)):
                a = a_tags[i]
                if 'Associated Doc(s)' in a.text:
                    break
            script = f'document.getElementsByTagName("a")[{i}].click();'
            run_js(script)
            time.sleep(2)
            soup = get_soup()
            # we are now showing the downloads - make sure we can see all the records.
            rows_shown = soup.find(class_='dataTables_info').text.replace('Showing 1 to ', '').replace('of ', '').replace(' rows ', '').split(' ')[0]
            total_rows = soup.find(class_='dataTables_info').text.replace('Showing 1 to ', '').replace('of ', '').replace(' rows ', '').split(' ')[1]
            while rows_shown != total_rows:
                # click the select box to change the rows shown.
                script = 'document.getElementsByTagName("select")[0].focus();'
                run_js(script)
                pyautogui.press('end')
                time.sleep(1)
                pyautogui.press('enter')
                time.sleep(1)
                pyautogui.press('enter')
                # udpate based on the same thing above.
                # not sure if I need this. See if it works.
                script = 'document.getElementsByClassName("dataTables_info")[0].focus();'
                run_js(script)
                time.sleep(2)
                soup = get_soup()
                rows_shown = soup.find(class_='dataTables_info').text.replace('Showing 1 to ', '').replace('of ', '').replace(' rows ', '').split(' ')[0]
                total_rows = soup.find(class_='dataTables_info').text.replace('Showing 1 to ', '').replace('of ', '').replace(' rows ', '').split(' ')[1]
                if rows_shown == total_rows:
                    break
            # download the items one by one.
            rows = soup.find_all('table')[2].find_all('tr')
            for i in range(len(rows)):
                if i == 0:# header row
                    pass
                else:
                    document_path = set_document_path(soup=soup, row_number=i)
                    if os.path.exists(document_path):
                        print('document already downloaded')
                        continue
                    # click download
                    # not sure if this will need some tweaking. TBD
                    script = f'document.getElementsByTagName("table")[2].getElementsByTagName("tr")[{i}].getElementsByClassName("cust_icon_blue")[1].click();'
                    run_js(script)
                    time.sleep(2)
                    # download dialog box
                    pyperclip.copy(document_path)
                    pyautogui.hotkey('ctrl', 'v')
                    time.sleep(2)
                    pyautogui.press('enter')
                    time.sleep(2)
            # done with this person
            update_completed(employee_name)
            print(f'done with {employee_name}')
            downloaded_for_someone = True
            break
    # get back to main page
    if downloaded_for_someone:
        a_tags = soup.find_all('a')
        for i in range(len(a_tags)):
            a = a_tags[i]
            if 'Personnel Management' in a.text:
                break
        script = f'document.getElementsByTagName("a")[{i}].click();'
        run_js(script)
        # do we need to do more to get here? click search?
        time.sleep(1)
        script = 'document.getElementsByTagName("button")[0].click();'
        run_js(script)
        time.sleep(2)
        soup = get_soup()
        return False
    # otherwise, click the next button on the personnel page
    else:
        a_tags = soup.find_all('a')
        for i in range(len(a_tags)):
            a = a_tags[i]
            if a.text == '>':
                break
        script = f'document.getElementsByTagName("a")[{i}].click();'
        run_js(script)
        print('clicking on the next page')
        time.sleep(2)
        new_soup = get_soup()
        if soup == new_soup():
            print('it looks like we are done!')
            return True


def go():
    # this assumes you will get us to Chrome and to the the personnel page
    time.sleep(4)
    create_tracker()
    #soup = get_soup()
    # go through each row of the table
    done = False
    while done == False:
        done = download_one_persons_docs()
        if done:
            break
