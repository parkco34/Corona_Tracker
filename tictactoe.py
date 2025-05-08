#!/usr/bin/env python
from IPython.display import clear_output
import random as r
def grid():
    clear_output()
    print('+--------------------+--------------------+--------------------+')
    print('|' + 20*' ' + '|' + 20*' ' + '|' + 20*' ' + '|')
    print('|' + 20*' ' + '|' + 20*' ' + '|' + 20*' ' + '|')
    print('|' + 8*' ' + bx[6] + 9*' ' + '|' + 8*' ' + bx[7] + 9*' ' + '|' + 8*' ' + bx[8] + 9*' ' + '|')
    print('|' + 20*' ' + '|' + 20*' ' + '|' + 20*' ' + '|')
    print('|' + 20*' ' + '|' + 20*' ' + '|' + 20*' ' + '|')
    print('+--------------------+--------------------+--------------------+')
    print('|' + 20*' ' + '|' + 20*' ' + '|' + 20*' ' + '|')
    print('|' + 20*' ' + '|' + 20*' ' + '|' + 20*' ' + '|')
    print('|' + 8*' ' + bx[3] + 9*' ' + '|' + 8*' ' + bx[4] + 9*' ' + '|' + 8*' ' + bx[5] + 9*' ' + '|')
    print('|' + 20*' ' + '|' + 20*' ' + '|' + 20*' ' + '|')
    print('|' + 20*' ' + '|' + 20*' ' + '|' + 20*' ' + '|')
    print('+--------------------+--------------------+--------------------+')
    print('|' + 20*' ' + '|' + 20*' ' + '|' + 20*' ' + '|')
    print('|' + 20*' ' + '|' + 20*' ' + '|' + 20*' ' + '|')
    print('|' + 8*' ' + bx[0] + 9*' ' + '|' + 8*' ' + bx[1] + 9*' ' + '|' + 8*' ' + bx[2] + 9*' ' + '|')
    print('|' + 20*' ' + '|' + 20*' ' + '|' + 20*' ' + '|')
    print('|' + 20*' ' + '|' + 20*' ' + '|' + 20*' ' + '|')
    print('+--------------------+--------------------+--------------------+')

bx = ['   ','   ','   ','   ','   ','   ','   ','   ','   ']

def moves():
    while True:
        try:
            pos = int(input('Pick a box corresponding to the numerical keypad: ')) - 1
            if bx[pos] == '   ':
                bx[pos] = x
                grid()
                break
            elif bx[pos] != '   ':
                print("\nSeat's taken... (▀̿Ĺ̯▀̿ ̿) " )
        except ValueError:
            print('\nNON-NUMERIC DATA FOUND IN THE FILE!!!!!... ( ͡° ͜ʖ ͡°)\n')


def cpu():
    while True:
        try:
            pos = int(r.randint(1,9) - 1)
            if bx[pos] == '  ':
                bx[pos] = x
                grid()
                break
            elif bx[pos] != '  ':
                print("\n Seat's taken... ( ͡° ͜ʖ ͡°) ")
        except ValueError:
            print('\nNON-NUMERIC DATA FOUND IN THE FILE!!!!!... ( ͡° ͜ʖ ͡°)\n')
        except IndexError:
            print('\nType ONLY single digits, please... ( ͡° ͜ʖ ͡°)\n')


def winning():
    if ((bx[0] == bx[3] and bx[0] == bx[6] and bx[3] == bx[6] and bx[0] != '   ')
        or (bx[1] == bx[4] and bx[1] == bx[7] and bx[4] == bx[7] and bx[7] != '   ') or
        (bx[2] == bx[5] and bx[2] == bx[8] and bx[5] == bx[8] and bx[8] != '   ') or
        (bx[0] == bx[4] and bx[0] == bx[8] and bx[4] == bx[8] and bx[8] != '   ') or
        (bx[0] == bx[1] and bx[0] == bx[2] and bx[1] == bx[2] and bx[2] != '   ') or
        (bx[3] == bx[4] and bx[3] == bx[5] and bx[4] == bx[5] and bx[5] != '   ') or
        (bx[6] == bx[4] and bx[6] == bx[2] and bx[4] == bx[2] and bx[2] != '   ') or
        (bx[8] == bx[4] and bx[8] == bx[0] and bx[4] == bx[0] and bx[0] != '   ') or
        (bx[6] == bx[7] and bx[6] == bx[8] and bx[7] == bx[8] and bx[7] != '   ') and
        (bx != ['   ','   ','   ','   ','   ','   ','   ','   ','   '])):
        print(x + " WINS!!!!!!")
        return True
    else:
        return False


for turn in range(9):
    grid()
    if (turn % 2 == 0) or turn == 0:
        x = '💩'
        moves()
    else:

        x = '🕷'
        moves()
    if winning():
        break



