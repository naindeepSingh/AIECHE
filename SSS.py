from flask import Flask, request, jsonify, send_file
import json
import requests
import os
import logging
import datetime
import sys
import time
import threading

app = Flask(__name__)
#chaage2
swb = {'4LLLF20207438279': {'state': '0000', 'ip': '192.168.0.104'},
       '4LLLFswitchboxid_1.1': {'state': '0000', 'ip': '192.168.0.104'},
       '1Lswitchboxid_1.2': {'state': '0', 'ip': '192.168.0.104'},
       '4LLLFswitchboxid_2.1': {'state': '0000', 'ip': '192.168.0.104'},
       '4LLLL010820230143': {'state': '0000', 'ip': '192.168.0.105'}}

#swb = {}

rooms = {'ids': ['Livingroom', 'Bedroom', 'Hall'],
         'Livingroom': ['4LLLFswitchboxid_1.1', '1Lswitchboxid_1.2'],
         'Bedroom': ['4LLLFswitchboxid_2.1'], 'Hall': ['4LLLL010820230143'], 'allocate': 0,
         }

# rooms = {'ids': []}

room_allocation = dict()

preset = dict()

master_preset_dict = {'presetIDs': []}

timed_preset = dict()

schedule = dict()

timed_schedule = dict()

master_group_dict = dict()

master_schedule_dict = {'scheduleIDs': []}

log_directory = "c:/smartswitch/Logs"
log_file = ""
log_format = "%(asctime)s - %(levelname)s - %(message)s\n\n"
date_format = "%Y-%m-%d"


def save():
    global swb
    global rooms
    global room_allocation
    global preset
    global master_preset_dict
    global timed_preset
    global schedule
    global timed_schedule
    global master_schedule_dict
    global master_group_dict
    with open('swb.json', 'w') as f:
        json.dump(swb, f)
    with open('rooms.json', 'w') as f:
        json.dump(rooms, f)
    with open('room_allocation.json', 'w') as f:
        json.dump(room_allocation, f)
    with open('preset.json', 'w') as f:
        json.dump(preset, f)
    with open('master_preset_dict.json', 'w') as f:
        json.dump(master_preset_dict, f)
    with open('timed_preset.json', 'w') as f:
        json.dump(timed_preset, f)
    with open('schedule.json', 'w') as f:
        json.dump(schedule, f)
    with open('timed_schedule.json', 'w') as f:
        json.dump(timed_schedule, f)
    with open('master_schedule_dict.json', 'w') as f:
        json.dump(master_schedule_dict, f)
    with open('master_group_dict.json', 'w') as f:
        json.dump(master_group_dict, f)


def create_logger():
    global log_file
    global log_directory
    global log_format
    global date_format

    if not os.path.exists(log_directory):
        os.makedirs(log_directory)

    today_date = datetime.date.today().strftime(date_format)
    log_file = os.path.join(log_directory, f"{today_date}.log")

    logger = logging.getLogger("MyLogger")
    logger.setLevel(logging.INFO)

    file_handler = logging.FileHandler(log_file)
    formatter = logging.Formatter(log_format, date_format)
    file_handler.setFormatter(formatter)

    logger.addHandler(file_handler)

    app.logger.addHandler(logging.StreamHandler(sys.stdout))

    return logger


def check_and_update_log_file():
    global log_file
    global log_directory
    global log_format
    global date_format
    today_date = datetime.date.today().strftime(date_format)
    if not log_file.endswith(f"{today_date}.log"):
        logging.shutdown()
        create_logger()
    return


def log(message):
    global log_file
    global log_directory
    global log_format
    global date_format

    check_and_update_log_file()

    logger = logging.getLogger("MyLogger")
    logger.info(message)


def setup():
    global swb
    global rooms
    global room_allocation
    global preset
    global master_preset_dict
    global timed_preset
    global schedule
    global timed_schedule
    global master_schedule_dict
    global master_group_dict
    if os.path.exists('swb.json'):
        with open('swb.json', 'r') as f:
            swb = json.load(f)
    if os.path.exists('rooms.json'):
        with open('rooms.json', 'r') as f:
            rooms = json.load(f)
    if os.path.exists('room_allocation.json'):
        with open('room_allocation.json', 'r') as f:
            room_allocation = json.load(f)
    if os.path.exists('preset.json'):
        with open('preset.json', 'r') as f:
            preset = json.load(f)
    if os.path.exists('master_preset_dict.json'):
        with open('master_preset_dict.json', 'r') as f:
            master_preset_dict = json.load(f)
    if os.path.exists('timed_preset.json'):
        with open('timed_preset.json', 'r') as f:
            timed_preset = json.load(f)
    if os.path.exists('schedule.json'):
        with open('schedule.json', 'r') as f:
            schedule = json.load(f)
    if os.path.exists('timed_schedule.json'):
        with open('timed_schedule.json', 'r') as f:
            timed_schedule = json.load(f)
    if os.path.exists('master_schedule_dict.json'):
        with open('master_schedule_dict.json', 'r') as f:
            master_schedule_dict = json.load(f)
    if os.path.exists('master_group_dict.json'):
        with open('master_group_dict.json', 'r') as f:
            master_group_dict = json.load(f)
    return


def http_ping(url):
    try:
        requests.get(url)
        log('    "--> http_ping function invoked (url : ' + url + ")")
    except requests.exceptions.RequestException:
        log('    "--> http_ping function invoked (url : ' + url + ") ***EXCEPTION***")
        return


def change_state(idn, state, ping):
    try:
        global swb
        state_list = list(swb[idn]['state'])
        for i in range(len(state_list)):
            if state[i] != 'N':
                state_list[i] = state[i]
        swb[idn]['state'] = ''.join(state_list)
        ip = swb[idn]['ip']
        # if ping == 1:
        #     http_ping("http://" + ip +":5000/GETSTATE")
        log('  "--> change_state function invoked (idn : ' + str(idn) + " || rooms : " + str(
            state) + ")")
    except Exception as e:
        log('\n\n**** change_state INITIATED AND FAILED ****\n' + str(
            e) + "\n\n" + master_string() + "\n*****************************")


def master_string():
    global swb
    global rooms
    global room_allocation
    global log_directory
    global log_file
    global log_format
    global date_format
    global preset
    global master_preset_dict
    global timed_preset
    global schedule
    global timed_schedule
    global master_schedule_dict
    global master_group_dict

    variables = {
        'swb': swb,
        'rooms': rooms,
        'room_allocation': room_allocation,
        'log_directory': log_directory,
        'log_file': log_file,
        'log_format': log_format,
        'date_format': date_format,
        'preset': preset,
        'master_preset_dict': master_preset_dict,
        'timed_preset': timed_preset,
        'schedule': schedule,
        'timed_schedule': timed_schedule,
        'master_schedule_dict': master_schedule_dict,
        'master_group_dict': master_group_dict
    }

    result = ""
    for var_name, var_value in variables.items():
        result += f"{var_name} = {var_value}\n"

    return result


@app.route('/favicon.ico', methods=['GET'])
def favicon():
    favicon_path = r"C:\Users\Andrew Nitin\PycharmProjects\Proto_Server_v1\IOT_Server\icon.ico"
    return send_file(favicon_path, mimetype='image/vnd.microsoft.ico')


@app.route('/check', methods=['GET'])
def check():
    print("PING!!")
    return "abcdefg"


@app.route('/check_app', methods=['POST'])
def check_app():
    try:
        d = request.get_data()
        d = d.decode('utf-8')
        print(d)
        if d == 'password':
            log("#### NEW APP SETUP DETECTED WITH RIGHT PASSCODE #### \n\n PASSCODE : " + str(d) + "\n")
            return "True"
        else:
            log("#!#!#!# INTRUSION DETECTED WITH WRONG PASSCODE #!#!#!# \n\n PASSCODE : " + str(d) + "\n")
            return "False"
    except Exception as e:
        log('\n\n**** "/ONOFF/getstate/app" INITIATED BY APP AND FAILED ****\n\n' + str(
            e) + "\n\n" + master_string() + "\n*****************************")


@app.route('/ONOFF/setup', methods=['POST'])
def set_info():
    global swb
    global rooms
    global room_allocation
    try:
        d = request.get_json()
        print(d)
        swb[d['id']] = {}
        swb[d['id']]['state'] = d['state']
        swb[d['id']]['ip'] = d['ip']
        rooms['allocate'] = 1
        room_allocation = d
        print(rooms)
        print(swb)
        print(room_allocation)
        log("@@@@ NEW SWITCH SETUP DETECTED AND WAITING FOR ALLOCATION @@@@ \n\n INFO : " + str(d) + "\n")
        return 'Done'
    except Exception as e:
        d = request.get_data()
        d = d.decode('utf-8')
        print(d)
        log("@*@*@*@ NEW SWITCH SETUP DETECTED AND FAILED! @*@*@*@ \n\n ERROR : " + str(e) + "\n")


@app.route('/ONOFF/getstate/app', methods=['POST'])
def get_state_app():
    try:
        global swb
        data = request.get_json()
        ids = data["ids"]
        states = list()
        for x in ids:
            li = list(swb[x]['state'])
            states.append(li)
        return jsonify({'states': states})
    except Exception as e:
        log('\n\n**** "/ONOFF/getstate/app" INITIATED BY APP AND FAILED ****\n\n' + str(
            e) + "\n\n" + master_string() + "\n*****************************")


@app.route('/ONOFF/getstate/switch', methods=['POST'])
def get_state_switch():
    try:
        global swb
        string = request.get_data()
        idn = str(string.decode('utf-8'))
        log('"/ONOFF/getstate/switch" initiated by switch (id : ' + str(idn) + "|| state : " + str(
            swb[idn]['state']) + ")")
        return swb[idn]['state']
    except Exception as e:
        log('\n\n**** "/ONOFF/getstate/switch" INITIATED BY SWITCH AND FAILED ****\n\n' + str(
            e) + "\n\n" + master_string() + "\n*****************************")


@app.route('/ONOFF/setstate/switch', methods=['POST'])
def set_state_switch():
    try:
        global swb
        data = request.get_json()
        swb[data['id']]['state'] = data['state']
        # print(s)
        log('"/ONOFF/setstate/switch" initiated by switch (data : ' + str(data) + ")")
        return 'done'
    except Exception as e:
        log('\n\n**** "/ONOFF/setstate/switch" INITIATED BY SWITCH AND FAILED ****\n\n' + str(
            e) + "\n\n" + master_string() + "\n*****************************")


@app.route('/ONOFF/setstate/app', methods=['POST'])
def set_state_app():
    try:
        global swb
        data = request.get_json()
        idn = data["id"]
        state = data["state"]
        log('"/ONOFF/setstate/app" initiated by app (data : ' + str(data) + ")")
        change_state(idn, state, 0)
        return 'done'
    except Exception as e:

        log('\n\n**** "/ONOFF/setstate/app" INITIATED BY APP AND FAILED ****\n\n' + str(
            e) + "\n\n" + master_string() + "\n*****************************")


@app.route('/ONOFF/switches', methods=['GET'])
def get_switch():
    try:
        global rooms
        return jsonify(rooms)
    except Exception as e:
        log('\n\n**** "/ONOFF/switches" INITIATED BY APP AND FAILED ****\n\n' + str(
            e) + "\n\n" + master_string() + "\n*****************************")


@app.route('/ONOFF/allocated', methods=['POST'])
def allocated():
    try:
        global room_allocation
        global rooms
        room_allocation = {}
        rooms = request.get_json()
        print(room_allocation)
        print(rooms)
        log('"/ONOFF/allocated" initiated by app (room_allocation : ' + str(room_allocation) + " || rooms : " + str(
            rooms) + ")")
        return 'done'
    except Exception as e:
        log('\n\n**** "/ONOFF/allocated" INITIATED BY APP AND FAILED ****\n\n' + str(
            e) + "\n\n" + master_string() + "\n*****************************")


@app.route('/ONOFF/allocate', methods=['GET'])
def allocate():
    try:
        global room_allocation
        print(room_allocation)
        log('"/ONOFF/allocate" initiated by app (room_allocation : ' + str(room_allocation) + ")")
        return jsonify(room_allocation)
    except Exception as e:
        log('\n\n**** "/ONOFF/allocate" INITIATED BY APP AND FAILED ****\n' + str(
            e) + "\n\n" + master_string() + "\n*****************************")


@app.route('/RESET', methods=['GET'])
def reset():
    try:
        setup()
        log('"/RESET" INITIATED SUCCESSFULLY')
        return 'DONE'
    except Exception as e:
        log('\n\n**** "/RESET" INITIATED AND FAILED ****\n' + str(
            e) + "\n\n" + master_string() + "\n*****************************")

        return 'RESET FAILED'


def preset_simplifier(l):
    try:
        length = len(l)
        remove_indexes = list()
        for i in range(0, length):
            if all(char == 'N' for char in l[i][2]):
                remove_indexes.append(i)
        filtered_list = [value for index, value in enumerate(l) if index not in remove_indexes]
        log('  "--> preset_simplifier() called... \n\n\t\t list : '+str(l))
        return filtered_list
    except Exception as e:
        log('  "--> *!*!*!* preset_simplifier() INITIATED BUT FAILED *!*!*!* \n\n Error : '
            +str(e)+'\n\n'+master_string()+"\n*****************************")


@app.route('/ONOFF/PRESET', methods=['POST'])
def preset_creator():
    try:
        global preset
        data = request.get_json()
        data['list'] = preset_simplifier(data['list'])
        preset[data['id']] = data['list']
        log('"/ONOFF/PRESET" ****PRESET CREATION INITIATED BY APP**** \n\n data : ' + str(data))

        return 'Done'
    except Exception as e:
        log('\n\n**** "/ONOFF/PRESET" INITIATED BY APP AND FAILED ****\n' + str(
            e) + "\n\n" + master_string() + "\n*****************************")


def calc_prev_state(state):
    pstate = ""
    for i in range(0, len(state)):
        if state[i] == '1':
            pstate += "0"
        elif state[i] == '0':
            pstate += "1"
        else:
            pstate += "N"
    return pstate


def add_time(hours, minutes, seconds):
    current_time = datetime.datetime.now()
    delta = datetime.timedelta(hours=hours, minutes=minutes, seconds=seconds)
    new_time = current_time + delta
    return new_time.strftime("%H%M%S")


def preset_manager(l):
    global timed_preset
    global swb
    for i in range(0, len(l)):
        sl = l[i]
        if sl[0] == 'ONF':
            change_state(sl[1], sl[2],1)
        elif sl[0] == 'TIM':
            pstate = calc_prev_state(sl[2])
            time = add_time(int(sl[3]), int(sl[4]), int(sl[5]))
            change_state(sl[1], sl[2],1)
            if time in timed_preset:
                timed_preset[time].append(['ONF', sl[1], pstate])
            else:
                timed_preset[time] = [['ONF', sl[1], pstate]]
        else:
            change_state(sl[1], sl[2],1)


@app.route('/ONOFF/PRESET/enable', methods=['POST'])
def preset_enabler():
    try:
        global preset
        id = request.get_data()
        id = id.decode('utf-8')
        log('"/ONOFF/PRESET/enable" initiated by app (preset id : '+str(id)+')')
        try:
            preset_manager(preset[id])
            log('"/ONOFF/PRESET/enable" initiated by app (preset id : ' + str(id) + ')')
            return 'Done'
        except KeyError as k:
            log('"/ONOFF/PRESET/enable" initiated by app ***KEY ERROR*** (preset id : ' + str(id) + ')\n ERROR : '+ str (k))
            return 'Invalid'
    except Exception as e:
        log('\n\n**** "/ONOFF/PRESET/store" INITIATED BY APP AND FAILED ****\n' + str(
            e) + "\n\n" + master_string() + "\n*****************************")


@app.route('/ONOFF/PRESET/store', methods=['POST'])
def preset_store():
    try:
        global master_preset_dict
        master_preset_dict = request.get_json()
        log('"/ONOFF/PRESET/store" initiated by app (dictionary : '+str(master_preset_dict)+')')
        return 'Done'
    except Exception as e:
        log('\n\n**** "/ONOFF/PRESET/store" INITIATED BY APP AND FAILED ****\n' + str(
            e) + "\n\n" + master_string() + "\n*****************************")

@app.route('/ONOFF/PRESET/fetch', methods=['GET'])
def preset_fetch():
    try:
        global master_preset_dict
        log('"/ONOFF/PRESET/fetch" initiated by app (dictionary : '+str(master_preset_dict)+')')
        return jsonify(master_preset_dict)
    except Exception as e:
        log('\n\n**** "/ONOFF/PRESET/fetch" INITIATED BY APP AND FAILED ****\n' + str(
            e) + "\n\n" + master_string() + "\n*****************************")

@app.route('/ONOFF/PRESET/delete', methods=['POST'])
def preset_delete():
    try:
        global preset
        id = request.get_data()
        id = id.decode('utf-8')
        try:
            preset.pop(id)
            log('"/ONOFF/PRESET/delete" initiated by app (preset ID : ' + id + ')')
            return 'Done'
        except KeyError as k:
            log('"/ONOFF/PRESET/delete" initiated by app ***KEY ERROR*** (preset ID : ' + id + ')\n'+ 'ERROR : '+str(k))
            return 'Invalid'
    except Exception as e:
        log('\n\n**** "/ONOFF/PRESET/delete" INITIATED BY APP AND FAILED ****\n' + str(
            e) + "\n\n" + master_string() + "\n*****************************")


def schedule_manager(l):
    global timed_preset
    global swb
    for i in range (0,len(l)):
        sl = l[i]
        if schedule[sl[-1]][0] == 0 :
            break
        if sl[0] == 'ONF':
            change_state(sl[1],sl[2],1)
        elif sl[0] == 'TIM':
            pstate = calc_prev_state(sl[2])
            time = add_time(int(sl[3]),int(sl[4]),int(sl[5]))
            change_state(sl[1],sl[2],1)
            if time in timed_preset:
                timed_preset[time].append(['ONF', sl[1], pstate])
            else:
                timed_preset[time] = [['ONF', sl[1], pstate]]
        else:
            change_state(sl[1],sl[2],1)


@app.route('/ONOFF/SCHEDULE', methods=['POST'])
def schedule_creator():
    global schedule
    global timed_schedule
    data = request.get_json()
    data['list'] = preset_simplifier(data['list'])
    schedule[data['id']] = ['1',data['time']]
    if data['time'] in timed_schedule:
        timed_schedule[data['time']].extend(data['list'])
    else:
        timed_schedule[data['time']] = data['list']
    return 'Done'


@app.route('/ONOFF/SCHEDULE/store', methods=['POST'])
def schedule_store():
    try:
        global master_schedule_dict
        master_schedule_dict = request.get_json()
        log('"/ONOFF/SCHEDULE/store" initiated by app (dictionary : '+str(master_schedule_dict)+')')
        return 'Done'
    except Exception as e:
        log('\n\n**** "/ONOFF/SCHEDULE/store" INITIATED BY APP AND FAILED ****\n' + str(
            e) + "\n\n" + master_string() + "\n*****************************")

@app.route('/ONOFF/SCHEDULE/fetch', methods=['GET'])
def schedule_fetch():
    try:
        global master_schedule_dict
        log('"/ONOFF/SCHEDULE/fetch" initiated by app (dictionary : '+str(master_schedule_dict)+')')
        return jsonify(master_schedule_dict)
    except Exception as e:
        log('\n\n**** "/ONOFF/SCHEDULE/fetch" INITIATED BY APP AND FAILED ****\n' + str(
            e) + "\n\n" + master_string() + "\n*****************************")


@app.route('/ONOFF/SCHEDULE/GROUP/store', methods=['POST'])
def schedule_group_store():
    try:
        global master_group_dict
        master_group_dict = request.get_json()
        log('"/ONOFF/SCHEDULE/GROUP/store" initiated by app (dictionary : '+str(master_group_dict)+')')
        return 'Done'
    except Exception as e:
        log('\n\n**** "/ONOFF/SCHEDULE/GROUP/store" INITIATED BY APP AND FAILED ****\n' + str(
            e) + "\n\n" + master_string() + "\n*****************************")


@app.route('/ONOFF/SCHEDULE/GROUP/fetch', methods=['GET'])
def schedule_group_fetch():
    try:
        global master_group_dict
        log('"/ONOFF/SCHEDULE/GROUP/fetch" initiated by app (dictionary : '+str(master_group_dict)+')')
        return jsonify(master_group_dict)
    except Exception as e:
        log('\n\n**** "/ONOFF/SCHEDULE/GROUP/fetch" INITIATED BY APP AND FAILED ****\n' + str(
            e) + "\n\n" + master_string() + "\n*****************************")


@app.route('/ONOFF/SCHEDULE/disable', methods=['POST'])
def schedule_disable():
    try:
        global schedule
        id = request.get_data()
        id = id.decode('utf-8')
        try:
            schedule[id][0] = 0
            log('"/ONOFF/SCHEDULE/disable" initiated by app (id : ' + str(id) + ')')
            return 'Done'
        except KeyError:
            log('"/ONOFF/SCHEDULE/disable" initiated by app (id : ' + str(id) + ') ***KEY ERROR***')
            return 'Invalid'
    except Exception as e:
        log('\n\n**** "/ONOFF/SCHEDULE/disable" INITIATED BY APP AND FAILED ****\n' + str(
            e) + "\n\n" + master_string() + "\n*****************************")


@app.route('/ONOFF/SCHEDULE/enable', methods=['POST'])
def schedule_enable():
    try:
        global schedule
        id = request.get_data()
        id = id.decode('utf-8')
        try:
            schedule[id][0] = 1
            log('"/ONOFF/SCHEDULE/enable" initiated by app (id : ' + str(id) + ')')
            return 'Done'
        except KeyError:
            log('"/ONOFF/SCHEDULE/enable" initiated by app (id : ' + str(id) + ') ***KEY ERROR***')
            return 'Invalid'
    except Exception as e:
        log('\n\n**** "/ONOFF/SCHEDULE/enable" INITIATED BY APP AND FAILED ****\n' + str(
            e) + "\n\n" + master_string() + "\n*****************************")


@app.route('/ONOFF/SCHEDULE/delete', methods=['POST'])
def schedule_delete():
    try:
        global schedule
        global timed_schedule
        id = request.get_data()
        id = id.decode('utf-8')
        try:
            time_list = schedule[id][1:]
            for time in time_list:
                l = timed_schedule[time]
                remove_indexes = list()
                for i in range(0,len(l)):
                    if l[i][-1] == id:
                        remove_indexes.append(i)
                l = [value for index, value in enumerate(l) if index not in remove_indexes]
                if not l:
                    timed_schedule.pop(time)
                else:
                    timed_schedule[time] = l
            schedule.pop(id)
            log('"/ONOFF/SCHEDULE/delete" initiated by app (id : ' + str(id) + ')\n\nSCHEDULE : '+str(schedule)+'\n\nTIMED_SCHEDULE'+str(timed_schedule))
            return 'Done'
        except KeyError:
            log('"/ONOFF/SCHEDULE/delete" initiated by app (id : ' + str(id) + ') ****KEY ERROR****\n\nSCHEDULE : ' + str(
                schedule) + '\n\nTIMED_SCHEDULE' + str(timed_schedule))
            return 'Invalid'
    except Exception as e:
        log('\n\n**** "/ONOFF/SCHEDULE/delete" INITIATED BY APP AND FAILED ****\n' + str(
            e) + "\n\n" + master_string() + "\n*****************************")

@app.route('/ONOFF/STREAM/start', methods=['POST'])
def start_stream():
    global swb
    list = request.get_json()
    list = list['list']
    for id in list:
        ip = swb[id]['ip']
        status = requests.get('http://'+ip+':5000/start')
        if status == 'Done':
            continue
        else:
            print(id+":"+status)


@app.route('/ONOFF/STREAM/stop', methods=['POST'])
def stop_stream():
    global swb
    list = request.get_json()
    list = list['list']
    for id in list:
        ip = swb[id]['ip']
        status = requests.get('http://'+ip+':5000/stop')
        if status == 'Done':
            continue
        else:
            print(id+":"+status)


def time_checker():
    global timed_preset
    global timed_schedule
    while True:
        current_time = datetime.datetime.now().strftime("%H%M%S")
        if current_time in timed_preset:
            preset_manager(timed_preset[current_time])
            timed_preset.pop(current_time)
        if current_time in timed_schedule:
            schedule_manager(timed_schedule[current_time])
        time.sleep(1)


try:
    if __name__ == '__main__':
        create_logger()
        thread = threading.Thread(target=time_checker)
        thread.daemon=True
        thread.start()
        # setup()
        app.run(host="0.0.0.0", port=5000)
finally:
    print("Done")
    # save()
