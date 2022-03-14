from readPad import *
# Create a function that normalize "Axis are -32768 to 32767"
#Lx', 'Ly', 'Rx', 'Ry'
def normalize(x): return round(x / 32768,1)  
#'LT', 'RT'
def normalizet(x): return round(x / 255,1)  
def gamepad_check():
    con = rPad(1)
    #print(f'State:{con.read}')
    dictionary=con.read
    lista=list(dictionary.values())
    # Convert bolean to 1
    lista = list(map(int, lista))
    # Create a list that applies updated() to all elements of lista
    listab=list(map(normalize, lista[2:6]))
    lista[2:6] = listab[:]
    listac=list(map(normalizet, lista[0:2]))
    lista[0:2] = listac[:]
    return lista
