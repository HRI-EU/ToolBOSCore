#
# High-performance implementation to flatten a nested list
#
# http://rightfootin.blogspot.com/2006/09/more-on-python-flatten.html
#
# Author: Mike C. Fletcher
#
def flatten(l, ltypes=(list, tuple)):
    ltype = type(l)
    l = list(l)
    i = 0
    while i < len(l):
        while isinstance(l[i], ltypes):
            if not l[i]:
                l.pop(i)
                i -= 1
                break
            else:
                l[i:i + 1] = l[i]
        i += 1
    return ltype(l)


# EOF
