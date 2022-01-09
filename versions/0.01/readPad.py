"""Read the current state of Xbox Controllers"""
from ctypes import *
import pandas as pd
from time import time_ns

# Xinput DLL
try:
    _xinput = windll.xinput1_4
except OSError as err:
    _xinput = windll.xinput1_3


class _xinput_gamepad(Structure):
    """CType XInput Gamepad Object"""
    _fields_ = [
        ("wButtons",
         c_ushort),  #Contains all button information in one integer
        ("LT", c_ubyte),  #Left Trigger
        ("RT", c_ubyte),  #Right Trigger
        ("Lx", c_short),  #Right stick horizontal movement
        ("Ly", c_short),  #Right stick vertical movement
        ("Rx", c_short),  #Left stick horizontal movement
        ("Ry", c_short)
    ]  #Left stick vertical movement

    fields = [f[0] for f in _fields_]

    def __dict__(self):
        return {field: self.__getattribute__(field) for field in self.fields}

    def __str__(self):
        return str(self.__dict__())

    def __getitem__(self, string):
        return self.__dict__()[string]


class _xinput_state(Structure):
    """CType XInput State Object"""
    _fields_ = [("dwPacketNumber", c_uint),
                ("XINPUT_GAMEPAD", _xinput_gamepad)]

    fields = fields = [f[0] for f in _fields_]

    def __dict__(self):
        return {field: self.__getattribute__(field) for field in self.fields}

    def __str__(self):
        return str(self.__dict__())

    def __getitem__(self, string):
        return self.__dict__()[string]


class rPad(object):
    """XInput Controller State reading object"""

    _buttons = {  # All possible button values
        'UP': 0x0001,
        'DOWN': 0x0002,
        'LEFT': 0x0004,
        'RIGHT': 0x0008,
        'START': 0x0010,
        'SELECT': 0x0020,
        'L3': 0x0040,
        'R3': 0x0080,
        'LB': 0x0100,
        'RB': 0x0200,
        'A': 0x1000,
        'B': 0x2000,
        'X': 0x4000,
        'Y': 0x8000
    }

    def __init__(self, ControllerID: int = 1, absolute: bool = False):
        """
        Initialise Controller object.
        ControllerID    Int     Position of gamepad.
        """
        self.ControllerID = ControllerID
        self.dwPacketNumber = c_uint()
        self.absolute = absolute


        #print(f"Now reading gamepad#{ControllerID} as ABSOLUTE values"
        #      ) if self.absolute else print(
        #          f"Now reading gamepad#{ControllerID}")


        self.dwPacketNumber = c_uint()

    @property
    def read(self):
        """
        Returns the current gamepad state.
        """
        """If you wanna optimize reading, this is THE method to look at first"""
        state = _xinput_state()
        _xinput.XInputGetState(self.ControllerID - 1, pointer(state))
        self.dwPacketNumber = state.dwPacketNumber
        check = lambda x: (state.XINPUT_GAMEPAD.wButtons & x) == x
        buttons = {name: check(value) for name, value in rPad._buttons.items()}
        analogs = state.XINPUT_GAMEPAD.__dict__()
        del analogs['wButtons']
        return {**analogs, **buttons}

    def __loop(self, line, start, wait_ns, i):  #Provides an easy loop
        #foo=str(xbox.read)
        #jot.write(foo+"\n")
        if (time_ns() >= start[0] + wait_ns):
            moment = self.read  # will return a dictionary for instantaneous state of the controller
            moment['time(ns)'] = time_ns()  #store current time in nanoseconds
            moment['timeDelta(ms)'] = (
                time_ns() -
                start[0]) / 10**6  #Store the time diffference in milliseconds
            moment['error(ms)'] = moment['timeDelta(ms)'] - wait_ns / 10**6
            line.append(moment)
            i[0] += 1
            #print(f"time elapsed={((time_ns()-start)/10**6)/1000}")
            start[0] = time_ns()

    def __write(
            self, line, type: str,
            dest: str):  #Provides writing facility given a type and location

        supportedTypes = ["df"]
        if type not in supportedTypes:
            print(
                f"sorry, currently supported types are: {str(supportedTypes)[1:-1]}"
            )

        if (type == "df"):
            output = pd.DataFrame(line)
            if not self.absolute:
                #The following line is technically inaccurate as Bryan says "Axis are -32768 to 32767"
                output[['Lx', 'Ly', 'Rx',
                        'Ry']] = output[['Lx', 'Ly', 'Rx', 'Ry']] / 32768
                output[['LT', 'RT']] = output[['LT', 'RT']] / 255

        #Save to disk if required
        if (len(dest) > 0 and type == "df"):
            (pd.DataFrame(line)).to_feather(dest)
        #elif(len(file) > 0 and type == "list"):

        return output
        #elif(type == "list"):

    def __write_array(
            self, line, type: str,
            dest: str):  #Provides writing facility given a type and location

        supportedTypes = ["df"]
        if type not in supportedTypes:
            print(
                f"sorry, currently supported types are: {str(supportedTypes)[1:-1]}"
            )

        if (type == "df"):
            output = pd.DataFrame(line)
            if not self.absolute:
                #The following line is technically inaccurate as Bryan says "Axis are -32768 to 32767"
                output[['Lx', 'Ly', 'Rx',
                        'Ry']] = output[['Lx', 'Ly', 'Rx', 'Ry']] / 32768
                output[['LT', 'RT']] = output[['LT', 'RT']] / 255

        #Save to disk if required
        if (len(dest) > 0 and type == "df"):
            (pd.DataFrame(line)).to_feather(dest)
        #elif(len(file) > 0 and type == "list"):

        return output
        #elif(type == "list"):



    def record(self,
               duration: float = 5,
               rate: float = float(1 / 120),
               file: str = "",
               type="df"):
        """
        Records for a given duration at a fixed rate, possibly to a file
        """

        #Setup loop parameters
        line = []
        start = [time_ns()]
        count = duration // rate
        wait_ns = rate * 10**9
        i = [0]

        #Time for the loop
        #pbar = tq(total=count, position=0, leave=True)
        while (i[0] < count):
            self.__loop(line, start, wait_ns, i)

        return self.__write(line, type, file)
        #write to disk if wanted

    def capture(self,
                stopper,
                rate: float = float(1 / 120),
                file: str = "",
                type="df"):
        """
        Records till mentioned button is pressed at a fixed rate, possibly to a file
        """
        if stopper not in self._buttons:
            print("Choose a button label to end recording please")
            print(f"Your choices are ${self._buttons}")
            return 1

        #Setup loop parameters
        line = [self.read]
        start = [time_ns()]
        wait_ns = rate * 10**9
        i = [0]

        while not bool((line[-1])[stopper]):
            self.__loop(line, start, wait_ns, i)
        #write to disk if wanted
        return self.__write(line, type, file)



    def capture_array(self,
                stopper,
                rate: float = float(1 / 120),
                file: str = "",
                type="df"):
        """
        Records till mentioned button is pressed at a fixed rate, possibly to a file
        """
        if stopper not in self._buttons:
            print("Choose a button label to end recording please")
            print(f"Your choices are ${self._buttons}")
            return 1

        #Setup loop parameters
        line = [self.read]
        start = [time_ns()]
        wait_ns = rate * 10**9
        i = [0]

        while not bool((line[-1])[stopper]):

            self.__loop(line, start, wait_ns, i)
        #write to disk if wanted
        print(line)
        return self.__write_array(line, type, file)









def main():
    """Test the functionality of the rPad object"""
    from time import sleep

    print('Testing controller in position 1:')
    print(
        "This will just take a second. We'll look at the controller values in 200 milli-second intervals:"
    )
    # Initialise Controller
    con = rPad(1)
    # Loop printing controller state and buttons held
    for i in range(5):
        print(f"{i}---------------------------------------------")
        print(f'State:{con.read}')
        print("---------------------------------------------")
        sleep(0.2)

    print(
        "Better yet, you can use prettyRead() to sample as many times as desired for any required duration."
    )
    print(
        f"And then return it as a dataframe, can even write it to a file by supplying the filename.\n {con.prettyRead(1).head()}"
    )
    print("Do note that the final three columns are metadata.")


if __name__ == '__main__':
    main()
