###  Finding an ANY_REQUIRE

In a large graph with many identical components or libraries (e.g. BPL) it's hard to find out which one caused 
the ANY_REQUIRE and why.

* use ANY_REQUIRE_MSG and ANY_REQUIRE_VMSG within libraries
* convince people to use descriptive error messages (i.e. not "ROI failed" but containing the actual values of the ROI)
  in order to get a hint on where to start investigating

