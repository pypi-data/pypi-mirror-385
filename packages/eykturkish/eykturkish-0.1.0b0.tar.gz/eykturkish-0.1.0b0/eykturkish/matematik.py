import math
temp = ""
temp1 = ""
temp2 = ""
temp3 = ""
temp4 = ""
temp5 = ""
def mutlak(sayi = int):
    global temp
    temp = sayi
    temp = str(temp)
    temp = temp.replace("-","")
    return temp
def topla(sayi,sayie): return sayi + sayie
def cikart(sayi,sayie): return sayi - sayie
def carp(sayi,sayie): return sayi * sayie
def bol(sayi,sayie):
    global temp1
    try:
        temp1 = sayi / sayie
    except ZeroDivisionError:
        return None
    return temp1 # 1 kere bölüyoruz optimizasyon
def negatif(sayi): return 0 - sayi
def kendiylecarp(sayi): return sayi * sayi
def kendiyletopla(sayi): return sayi + sayi
def pi(): return "3.1415926535897932384626433832795028841971693993751058209749445923078164062862089986280348253421170679"
def sin(sayi):
    global temp2
    try:
        temp2 = math.sin(sayi)
    except:
        return None
    return temp2
def sonsuzluksimge(): return "∞"
