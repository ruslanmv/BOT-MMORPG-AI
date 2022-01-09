from pandas import DataFrame, read_feather
"""Virtual Controller Object for Python

Python Implepentation of vXbox from:
http://vjoystick.sourceforge.net/site/index.php/vxbox"""
from ctypes import *
import os, platform
from time import time_ns, sleep
from pandas import DataFrame

if '32' in platform.architecture()[0]:
    arc = '86'
else:
    arc = '64'

_path = os.path.abspath(
    os.path.join(os.path.dirname(__file__), 'vXboxInterface-x{}'.format(arc),
                 'vXboxInterface.dll'))
_xinput = WinDLL(_path)


class MaxInputsReachedError(Exception):
    """Exception when no inputs are available.

    Attributes:
        message -- explanation of the error
    """
    def __init__(self, message):
        self.message = message


class wPad(object):
    """Virtual Controller Object
    percent, Bool, Determines if absolute or percentage values are passed"""
    DPAD_OFF = 0
    DPAD_UP = 1
    DPAD_DOWN = 2
    DPAD_LEFT = 4
    DPAD_RIGHT = 8

    def __init__(self, percent=True):
        self.percent = percent
        self.id = 0
        self.PlugIn()

    def __del__(self):
        """Unplug self if object is cleaned up"""
        self.UnPlug()

    @classmethod
    def available_ids(self):
        ids = [
            x for x in range(1, 5) if _xinput.isControllerExists(c_int(x)) == 0
        ]

        return ids

    def PlugIn(self):
        """Take next available controller id and plug in to Virtual USB Bus"""
        ids = self.available_ids()
        if len(ids) == 0:
            raise MaxInputsReachedError('Max Inputs Reached')

        self.id = ids[0]

        _xinput.PlugIn(self.id)
        while self.id in self.available_ids():
            pass

    def UnPlug(self, force=False):
        """Unplug controller from Virtual USB Bus and free up ID"""
        if force:
            _xinput.UnPlugForce(c_uint(self.id))
        else:
            _xinput.UnPlug(c_uint(self.id))
        while self.id not in self.available_ids():
            if self.id == 0:
                break

    def set_value(self, label, value=None):
        """Set a value on the controller
    If percent is True all controls will accept a value between -1.0 and 1.0

    If not then:
        Triggers are 0 to 255
        Axis are -32768 to 32767

    Control List:
        AxisLx          , Left Stick X-Axis
        AxisLy          , Left Stick Y-Axis
        AxisRx          , Right Stick X-Axis
        AxisRy          , Right Stick Y-Axis
        BtnBack         , Menu/Back Button
        BtnStart        , Start Button
        BtnA            , A Button
        BtnB            , B Button
        BtnX            , X Button
        BtnY            , Y Button
        BtnThumbL       , Left Thumbstick Click
        BtnThumbR       , Right Thumbstick Click
        BtnShoulderL    , Left Shoulder Button
        BtnShoulderR    , Right Shoulder Button
        Dpad            , Set Dpad Value (0 = Off, Use DPAD_### Constants)
        TriggerL        , Left Trigger
        TriggerR        , Right Trigger
    """
        control = label
        if label in ("Lx", "Ly", "Rx", "Ry"):
            target_type = c_short
            control = "Axis" + label
            print(f"inside:{control}")

            if self.percent:
                target_value = int(32767 * value)
            else:
                target_value = value
        elif label in ('A', 'B', 'X', 'Y'):
            target_type = c_bool
            target_value = bool(value)
            control = "Btn" + label
        elif control in ('LT', 'RT'):
            target_type = c_byte

            if self.percent:
                target_value = int(255 * value)
            else:
                target_value = value
        elif control in ('UP', 'DOWN', 'LEFT', 'RIGHT'):
            target_type = c_int
            target_value = int(value)

        print(f"outside:{control} and type: {type(control)}")
        func = getattr(_xinput, 'Set' + control)
        func(c_uint(self.id), target_type(target_value))

    _buttons = {
        # key button name is mapped to list of label,type,value(for on)
        'UP': ["Dpad", c_int, 1],
        'DOWN': ["Dpad", c_int, 2],
        'LEFT': ["Dpad", c_int, 4],
        'RIGHT': ["Dpad", c_int, 8],
        'START': ["BtnStart", c_bool, 1],
        'SELECT': ["BtnStart", c_bool, 1],
        'L3': ["BtnThumbL", c_bool, 1],
        'R3': ["BtnThumbR", c_bool, 1],
        'LB': ["BtnX", c_bool, 1],
        'RB': ["BtnX", c_bool, 1],
        'A': ["BtnX", c_bool, 1],
        'B': ["BtnX", c_bool, 1],
        'X': ["BtnX", c_bool, 1],
        'Y': ["BtnY", c_bool, 1],
        'Lx': ["AxisLx", c_short, 32767],
        'Ly': ["AxisLy", c_short, 32767],
        'Rx': ["AxisRx", c_short, 32767],
        'Ry': ["AxisRy", c_short, 32767],
        'LT': ["TriggerL", c_byte, 255],
        'RT': ["TriggerR", c_byte, 255]
    }

    def __read(self, file: str = "", type: str = "df"):
        if len(file) == 0:
            print("file not found ?!")
        elif type == "df":
            return read_feather(file)

    def playMoment(self, snapshot: dict, check=True):
        """
        Pass in a snapshot, say a row of the dataframe, or a part of it, and this function will 
        (by default vet it first), and then send it to the emulated gamepad.

        Remember, it takes inputs only in the percentage form rn
        """
        if check:  #We'll vet the keys of the dictionary a bit
            for key in snapshot:
                if key not in self._buttons.keys():
                    raise IndexError(
                        f"please pass in a valid snapshot, got issues with {key}"
                    )
            else:
                print(f"doSnap got a valid dictionary: {snapshot}")

        for key in snapshot:
            """
            See there are three things: label, target_type and target value
            """
            info = self._buttons[key]
            #Extract relevant info
            label = info[0]
            type = info[1]
            value = round(info[2] * snapshot[key])
            #Send it
            func = getattr(_xinput, 'Set' + label)
            func(c_uint(self.id), type(value))

    def playback(self, data, rate: float = 1 / 120, check: bool = False):
        # Oi this is a naive attempt at writing from a dataframe,
        # a sophisticated attempt that reads the error column and self-corrects will be the focus of v1.1

        wait_ns = rate * 10**9

        #Time for the loop
        #pbar = tq(total=count, position=0, leave=True)
        if isinstance(data, DataFrame):
            dataframe = data
        elif isinstance(data, str):
            dataframe = self.__read(data)

        for moment in dataframe.to_dict('records'):
            #Get the metadata out
            error = moment.pop('error(ms)')
            timeDelta = moment.pop('timeDelta(ms)')
            time = moment.pop('time(ns)')
            #set gamepad state
            self.playMoment(moment, False)
            #reset timer
            start = time_ns()
            while (time_ns() <= start + wait_ns):
                pass  #gotta do this cos sleep isnt very accurate
            #print(f"timeDeltaDELTA={timeDelta-time_ns()+(start+wait_ns)}(plus or minus)")


def main():
    import time
    cons = []

    print('Testings multiple connections')
    while True:
        print('Connecting Controller:')
        try:
            cons.append(wPad())
        except MaxInputsReachedError:
            break
        else:
            print('Available:', wPad.available_ids())
            print('This ID:', cons[-1].id)

        # time.sleep(1)

    print('Done, disconnecting controllers.')
    del cons
    print('Available:', wPad.available_ids())
    time.sleep(2)

    print('Testing Value setting')
    print('Connecting Controller:')
    try:
        con = wPad()
    except MaxInputsReachedError:
        print('Unable to connect controller for testing.')
    else:
        print('This ID:', con.id)
        print('Available:', wPad.available_ids())
        print('Setting TriggerR and AxisLx:')
        for x in range(11):
            val = x / 10
            print(val)
            con.set_value('TriggerR', val)
            con.set_value('AxisLx', val)
            #add test for Dpad and button as well
            time.sleep(0.5)

        print('Done, disconnecting controller.')
        del con
        print('Available:', wPad.available_ids())
        time.sleep(2)


if __name__ == '__main__':
    main()
