#!/bin/bash

# Context before
# I want to see this line in this file.
# Context after

# You will see me, too.
args='-A1 -B1 "in this file"'
# And me.
grep ${args} "${0}"
