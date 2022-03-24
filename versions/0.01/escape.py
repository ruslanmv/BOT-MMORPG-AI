import msvcrt
import time

aborted = False

for time_remaining in range(10,0,-1):
    # First of all, check if ESCape was pressed
    if msvcrt.kbhit() and ord(msvcrt.getch()) == 27:
        aborted = True
        break

    print(str(time_remaining))       # so I can see loop is working
    time.sleep(1)                    # delay for 1 second
#endfor timing loop

if aborted:
    print("Program was aborted")
else:
    print("Program was not aborted")

time.sleep(5)  # to see result in command window before it disappears!