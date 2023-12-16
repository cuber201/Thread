import keyboard
import csv
import time
from threading import Thread, Event
import psutil
from pynput import mouse


HOTKEYS = ["space", "ctrl+c", "ctrl+v", "alt+tab"]

hotkeys_using = 0
mouse_using= 0
mouse_idle= 0
stop = Event()

def update_csv():
    with open("result.csv", encoding='utf-8', mode="+a") as file:
        csv_writer = csv.writer(file, delimiter=",", lineterminator="\r")
        now = time.strftime('%Y-%m-%d %H:%M:%S')
        csv_writer.writerow([now, "Hotkeys press", hotkeys_using])
        csv_writer.writerow([now, "Mouse using", mouse_using])
        csv_writer.writerow([now, "RAM", psutil.virtual_memory().percent,"%"])
        csv_writer.writerow([now, "CPU(%)", psutil.cpu_percent(),"%"])


def handle():
    global hotkeys_using
    hotkeys_using += 1
    print("hotkeys =", hotkeys_using)


def run_keyboard_handler():
    for hotkey in HOTKEYS:
        keyboard.add_hotkey(hotkey, handle)
    keyboard.wait('esc')
    stop.set()


def on_mouse_action(*args, **kwargs):
    global mouse_idle
    mouse_idle = 0
    if stop.is_set():
        return False


def run_mouse_handler():
    listener = mouse.Listener(
        on_move=on_mouse_action,
        on_click=on_mouse_action,
        on_scroll=on_mouse_action)
    listener.start()
    return listener

def main():
    global hotkeys_using
    global mouse_using
    global mouse_idle

    keyboard_thread = Thread(name="KeyboardHandler", target=run_keyboard_handler, daemon=True)
    print("Start KeyboardHandler")
    keyboard_thread.start()


    mouse_thread = Thread(name="Mouse_using", target=run_mouse_handler, daemon=True)
    print("Start MouseHandler")
    mouse_thread .start()

    timer = 0
    while not stop.is_set():
        try:
            if timer >= 30:
                timer = 0
                print("Update CSV")
                update_csv()
                hotkeys_using = 0
                mouse_using= 0

            timer += 0.05
            mouse_idle += 0.05

            if mouse_idle < 0.5:
                mouse_using += 0.05
            time.sleep(0.05)
        except KeyboardInterrupt:
            stop.set()
            keyboard.send('esc')
            break
    print("Wait other threads")
    mouse_thread.join()
    print("MouseHandler Finished")
    keyboard_thread.join()
    print("KeyboardHandler Finished")
    print("Exit Program")

if __name__ == "__main__":
    print("For exit click the 'esc'")
    main()
