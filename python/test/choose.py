import numpy as np


def choose(n, k):

    rval = [np.random.normal() for _ in range(n)]
    num = [i for i in range(n)]

    for i in range(n):
        ival = num[i]
        fval = rval[i]
        j = i
        while j > 0 and rval[j-1] > fval:
            num[j] = num[j-1]
            rval[j] = rval[j-1]
            j -= 1
        num[j] = ival;
        rval[j] = fval;

    for i in range(k):
        ival = num[i]
        j = i
        while j > 0 and num[j-1] > ival:
            num[j] = num[j-1]
            j -= 1
        num[j] = ival

    return num, rval

def main():
    print(choose(10, 5))

if __name__ == '__main__':
    main()