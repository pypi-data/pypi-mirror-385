#!/usr/bin/env python

# --------------------------------------------------------------------
def diceMain():
    from sys import path
    
    from argparse import ArgumentParser
    from pywargame.common.dicedraw import DiceDrawer

    ap = ArgumentParser(description='Make a series of dice images')
    ap.add_argument('-n','--sides', choices=[4,6,8,10,12,20],
                    default=6, type=int,
                    help='Number of sides')
    ap.add_argument('-f','--foreground', type=str, default='white',
                    help='Foreground color')
    ap.add_argument('-b','--background', type=str, default='#333333',
                    help='Background color')
    ap.add_argument('-W','--width',type=int,default=75,
                    help='Width of images')
    ap.add_argument('-H','--height',type=int,default=75,
                    help='Height of images')
    ap.add_argument('-B','--base',type=str,default='d{sides}-{value}.png',
                    help='Format of file names')

    args = ap.parse_args()

    dd = DiceDrawer(args.sides,
                    args.width,
                    args.height,
                    fg = args.foreground,
                    bg = args.background)

    base = args.base

    vals = list(range(0,args.sides) if args.sides == 10 else
                range(1,args.sides+1))
    for val in vals:
        dd.draw(val).save(filename=base.format(sides=args.sides,value=val))
    
# --------------------------------------------------------------------
if __name__ == '__main__':
    diceMain()

# --------------------------------------------------------------------
#
# EOF
#

    
