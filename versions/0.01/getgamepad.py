from readPad import *
def gamepad_check():
    con = rPad(1)
    #print(f'State:{con.read}')
    dictionary=con.read
    lista=list(dictionary.values())
    return lista
