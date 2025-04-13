import forallpeople as si

def main():
    si.environment("structural")

    a = 200 * si.kg
    b = 9.81 * si.m / si.s**2
    c = 200 * si.kN

    print (c+a*b)
    return (0)



main()