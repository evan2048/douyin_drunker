import subprocess
import time

SCREEN_WIDTH = 1520
SCREEN_HEIGHT = 720


def execute_cmd(cmd_str):
    print('cmd_str=%s' % cmd_str)
    output = subprocess.check_output(cmd_str.split())
    print(output.decode())
    return output


def check_adb_devices():
    output = execute_cmd('adb devices')


def adb_tap(x, y):
    output = execute_cmd('adb shell input tap %d %d' % (x, y))


def adb_swipe(x1, y1, x2, y2, duration_ms):
    output = execute_cmd('adb shell input swipe %d %d %d %d %d' % (x1, y1, x2, y2, duration_ms))


check_adb_devices()
# adb_tap(280, 850)

for i in range(0, 100):
    print('loop----------------%d' % i)
    adb_swipe(300, 1000, 300, 600, 100)
    time.sleep(1)
