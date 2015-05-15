import js
from multiprocessing import Queue
import os


jq = js.globals['$']



def tst():
    print "running test"
    try:
        v=IQ.get(False)
        print "got value",v
        OQ.put(apply(jq(v[0]).css, v[1]))
    except Exception as e:
        print e
    print js.globals['setTimeout'](tst, 5000)


def helloWorld(iq,oq):
    global IQ, OQ
    IQ=iq
    OQ=oq
    print js.globals['setTimeout'](tst, 5000)
