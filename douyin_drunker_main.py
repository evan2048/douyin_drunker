# by evan2048

import os
import time
import random
import hashlib
import urllib.request
import urllib.parse
import base64
import json
from PIL import Image

###################################################################################################
API_URL = 'https://api.ai.qq.com/fcgi-bin/face/face_detectface'
APP_ID = 0  # config your own APP_ID here (int)
APP_KEY = ''  # config your own APP_KEY here (string)
###################################################################################################

###################################################################################################
# Redmi 7
SCREEN_WIDTH = 720
SCREEN_HEIGHT = 1520
TAP_LIKE_POINT_X = 650
TAP_LIKE_POINT_Y = 750
###################################################################################################

SWIPE_START_POINT_X = SCREEN_WIDTH / 2
SWIPE_START_POINT_Y = SCREEN_HEIGHT / 10 * 7
SWIPE_END_POINT_X = SCREEN_WIDTH / 2
SWIPE_END_POINT_Y = SCREEN_HEIGHT / 10 * 5
SWIPE_DURATION_MS = 100

TAP_POINT_THRESHOLD = 10
SWIPE_POINT_THRESHOLD = 20
SWIPE_DURATION_MS_THRESHOLD = 10

GENDER_THRESHOLD = 30
AGE_THRESHOLD = 30
BEAUTY_THRESHOLD = 80

ADB_SCREENCAP_DIRCTORY_NAME = 'screencap'
ADB_SCREENCAP_PNG_FILE_NAME = 'screencap.png'
ADB_SCREENCAP_JPG_FILE_NAME = 'screencap.jpg'


def set_array_key_value(array, key, value):
    array[key] = value


def generate_sign_string(array, app_key):
    sorted_array = sorted(array.items(), key=lambda item: item[0], reverse=False)
    sorted_array.append(('app_key', app_key))
    encoded_url = urllib.parse.urlencode(sorted_array).encode()
    md5 = hashlib.md5(encoded_url)
    upper_md5 = md5.hexdigest().upper()
    return upper_md5


def get_response_json(image_file_path):
    request_data = {}
    current_timestamp = int(time.time())
    set_array_key_value(request_data, 'app_id', APP_ID)
    set_array_key_value(request_data, 'time_stamp', current_timestamp)
    set_array_key_value(request_data, 'nonce_str', str(current_timestamp * random.randint(1, current_timestamp)))
    with open(image_file_path, 'rb') as bin_data:
        image_data = bin_data.read()
    base64encoded_image_data = base64.b64encode(image_data)
    set_array_key_value(request_data, 'image', base64encoded_image_data)
    set_array_key_value(request_data, 'mode', 0)
    set_array_key_value(request_data, 'sign', generate_sign_string(request_data, APP_KEY))
    print('send request...')
    url_data = urllib.parse.urlencode(request_data).encode()
    # print('url_data:%s' % url_data)
    response = urllib.request.urlopen(API_URL, url_data)
    response_string = response.read()
    response_string_json = json.loads(response_string)
    print('response_string_json:%s' % response_string_json)
    return response_string_json


def init_adb_screencap_directory():
    adb_screencap_dirctory = os.getcwd() + '/' + ADB_SCREENCAP_DIRCTORY_NAME
    if not os.path.exists(adb_screencap_dirctory):
        print('create dirctory:%s' % adb_screencap_dirctory)
        os.mkdir(adb_screencap_dirctory)


def get_adb_screencap_png_file_path():
    return os.getcwd() + '/' + ADB_SCREENCAP_DIRCTORY_NAME + '/' + ADB_SCREENCAP_PNG_FILE_NAME


def get_adb_screencap_jpg_file_path():
    return os.getcwd() + '/' + ADB_SCREENCAP_DIRCTORY_NAME + '/' + ADB_SCREENCAP_JPG_FILE_NAME


def png2jpg(png_file_path, jpg_file_path):
    png_image = Image.open(png_file_path)
    jpg_image = png_image.convert('RGB')
    jpg_image.save(jpg_file_path)


def add_random_offset(value, offset):
    random_offset = random.randint(-offset, offset)
    return value + random_offset


def check_adb_devices():
    print('adb wait-for-device...')
    os.system('adb wait-for-device')
    os.system('adb devices')


def adb_tap(x, y):
    os.system('adb shell input tap %d %d' % (x, y))


def adb_swipe(x1, y1, x2, y2, duration_ms):
    os.system('adb shell input swipe %d %d %d %d %d' % (x1, y1, x2, y2, duration_ms))


def adb_screencap(file_path):
    os.system('adb shell screencap -p > %s' % file_path)


init_adb_screencap_directory()
check_adb_devices()

for i in range(0, 3):
    print('\nloop=%d start...' % i)
    swipe_start_point_x = add_random_offset(SWIPE_START_POINT_X, SWIPE_POINT_THRESHOLD)
    swipe_start_point_y = add_random_offset(SWIPE_START_POINT_Y, SWIPE_POINT_THRESHOLD)
    swipe_end_point_x = add_random_offset(SWIPE_END_POINT_X, SWIPE_POINT_THRESHOLD)
    swipe_end_point_y = add_random_offset(SWIPE_END_POINT_Y, SWIPE_POINT_THRESHOLD)
    swipe_duration_ms = add_random_offset(SWIPE_DURATION_MS, SWIPE_DURATION_MS_THRESHOLD)
    adb_swipe(swipe_start_point_x, swipe_start_point_y, swipe_end_point_x, swipe_end_point_y, swipe_duration_ms)
    time.sleep(1)
    print('screencap...')
    adb_screencap(get_adb_screencap_png_file_path())
    print('convert png to jpg...')
    png2jpg(get_adb_screencap_png_file_path(), get_adb_screencap_jpg_file_path())
    response_json = get_response_json(get_adb_screencap_jpg_file_path())
    if response_json['ret'] == 0:
        face_list = response_json['data']['face_list']
        for face in face_list:
            gender = face['gender']
            age = face['age']
            beauty = face['beauty']
            if (gender < GENDER_THRESHOLD) and (age < AGE_THRESHOLD) and (beauty > BEAUTY_THRESHOLD):
                print('verify pass, gender=%d, age=%d, beauty=%d' % (gender, age, beauty))
                tap_like_point_x = add_random_offset(TAP_LIKE_POINT_X, TAP_POINT_THRESHOLD)
                tap_like_point_y = add_random_offset(TAP_LIKE_POINT_Y, TAP_POINT_THRESHOLD)
                adb_tap(tap_like_point_x, tap_like_point_y)
                time.sleep(0.5)
                print('save screencap...face_id=%s' % face['face_id'])
                os.system('cp %s %s' % (get_adb_screencap_jpg_file_path(), (os.getcwd() + '/' + ADB_SCREENCAP_DIRCTORY_NAME + '/' + face['face_id'] + '.jpg')))
                break  # one is enough, avoid duplicate
    simulate_human_delay_time = random.randint(1, 3)
    print('loop done, delay %d seconds...' % simulate_human_delay_time)
    time.sleep(simulate_human_delay_time)
