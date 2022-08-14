from subprocess import call, check_output, CalledProcessError, Popen, PIPE
from datetime import datetime
from rgb_cube import RgbCube
from time import sleep
from colorsys import hls_to_rgb
from collections import deque
from os import path, access, W_OK
from math import cos, pi
from sys import stdout
from signal import signal, SIGTERM, SIGHUP

terminate = False

def log(msg):
    stdout.write(msg + '\n')
    stdout.flush()


def is_system_running():
    return call(['/bin/systemctl', 'is-system-running']) == 0


def is_booted():
    try:
        out = check_output(['/sbin/runlevel'])
        numbers = [int(s) for s in out.split() if s.isdigit()]
        if len(numbers) > 0:
            return numbers[0] == 3
    except CalledProcessError:
        pass
    return False


def val_to_rgb(value, mod):
    h = (1. - value/255.) * 0.6666666667 # 240./360. = 0.6666666667
    (r, g, b) = hls_to_rgb(h, mod/2., 1.)
    return (int(r*255), int(g*255), int(b*255))


def debug_print(data):
    out = datetime.now().strftime("%H:%M:%S.%f") + ':'
    for v in data:
        out = out + str(v) + ','
    print(out)


def boot(cube):
    x = 0
    g = 3
    while g < 10:
        cube.fill(0, g, 0)
        cube.update()
        sleep(0.05)
        g = g + 3
    while not is_booted():
        y = (cos(x + pi) + 1.) / 2.
        g = 10 + int(y*50.)
        cube.fill(0, g, 0)
        cube.update()
        sleep(0.05)
        x = x + 0.1
    while g > 0:
        cube.fill(0, g, 0)
        cube.update()
        sleep(0.05)
        g = g - 3
    cube.fill(0, 0, 0)
    cube.update()


def finalize(cube):
    x = 0
    r = 3
    while r < 10:
        cube.fill(r, 0, 0)
        cube.update()
        sleep(0.05)
        r = r + 3
    global terminate
    while not terminate:
        y = (cos(x + pi) + 1.) / 2.
        r = 10 + int(y*50.)
        cube.fill(r, 0, 0)
        cube.update()
        sleep(0.05)
        x = x + 0.1
    while r > 0:
        cube.fill(r, 0, 0)
        cube.update()
        sleep(0.05)
        r = r - 3
    cube.fill(0, 0, 0)
    cube.update()
    sleep(0.05)


def run (cube):
    cava_process = Popen(['/usr/local/bin/cava', '-p', path.dirname(path.abspath(__file__)) + '/cava.conf'], stdout=PIPE)

    empty_data = [[0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0], [0,0,0,0,0,0,0,0]]
    data_fifo = deque(empty_data, len(empty_data))

    global terminate
    while not terminate:
        data = cava_process.stdout.read(8)
        #debug_print(data)

        if len(data) != 8:
            break

        if data == data_fifo[0] and data == data_fifo[1] and data == data_fifo[2] and data == data_fifo[3]:
            continue

        i_mod = sum(data) / float(len(data)) / 255.
        data_fifo.appendleft(data)

        for x in range(4):
            f_data = data_fifo[x]
            for y in range(4):
                l_val = f_data[y]
                r_val = f_data[7-y]
                for z in range(4):
                    val = l_val * ((3-z)/3.) + r_val * (z/3.)
                    (r, g, b) = val_to_rgb(val, i_mod)
                    cube.set(x, y, z, r, g, b)

        cube.update()


def sighup(sig, frame):
    log('SIGHUP detected') # this kills the cava thread


def sigterm(sig, frame):
    log('SIGTERM detected')
    global terminate
    terminate = True


def main():

    signal(SIGHUP, sighup)
    signal(SIGTERM, sigterm)

    tty_path = '/dev/ttyUSB0'

    log('Waiting for tty ' + tty_path)
    while not (path.exists(tty_path) and access('/dev/ttyUSB0', W_OK)):
        sleep(0.5)

    log('Initializing cube')
    cube = RgbCube(tty_path)

    log('Waiting for boot')
    boot(cube)

    log('Started')
    run(cube)

    log('Shutting down')
    finalize(cube)


if __name__ == "__main__":
    main()
