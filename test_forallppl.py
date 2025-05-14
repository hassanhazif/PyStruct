import forallpeople as si

def main():
    si.environment("structural")

    def unit (unit):
        a = getattr (si,unit)
        return (a)

    a = 200 *1000 * si.kg
    b = 9.81 * si.m / si.s**2
    c = 200 * si.kN
    d = 2 * si.m**2
    e = "MPa"
    print (((c+a*b)/d)+2*unit(e))
    return (0)

main()