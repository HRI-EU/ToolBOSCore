#
# High-performance implementation to remove duplicates from a list
#
# http://www.peterbe.com/plog/uniqifiers-benchmark
#
# Author: Peter Bengtsson
#
def f5(seq, idfun=None):
    # order preserving
    if idfun is None:
        def idfun(x): return x
    seen = {}
    result = []
    for item in seq:
        marker = idfun(item)
        # in old Python versions:
        # if seen.has_key(marker)
        # but in new ones:
        if marker in seen: continue
        seen[marker] = 1
        result.append(item)
    return result


# EOF
