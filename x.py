from itertools import cycle

c = 1
for x in cycle(['b', 'c', 'd', 'a']):
    # print(c, x)
    c += 1
    if c > 1000000:
        print (x)
        break
       
