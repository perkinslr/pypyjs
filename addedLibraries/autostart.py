from twisted.internet import reactor
from twisted.internet.protocol import Protocol, ClientFactory
import js
import time
import sys


def tick():
    timeTaken=10
    itercount=0
    while timeTaken>0.01:
        itercount+=1
        startTime=time.time()
        reactor.iterate()
        endTime=time.time()
        timeTaken=endTime-startTime
    js.globals['setTimeout'](ticker, 100)
    return itercount

ticker=js.Function(tick)

def helloClient(msg):
    print msg

eventHandlers={}


def eventListener(e):
    if str(e.data.cmd) in eventHandlers:
        eh = eventHandlers[str(e.data.cmd)]
        args = [e.data.args[i] for i in range(eh.__code__.co_argcount)]
        apply(eh, args)

el=js.Function(eventListener)

js.eval('self').addEventListener('message',el)


def registerHandler(methodName, callback):
    eventHandlers[methodName]=callback
    js.globals['mainThreadEval'](('TestPage.method(function %s(self){'
                                 'var args=[];'
                                 'for (var i=1; i<arguments.length; i++){'
                                    'args.push(arguments[i]);'
                                    '}'
                                 'var msg = {cmd:%r, args:args};'
                                 'self.vm.postMessage(msg);'
                                 '});')%(methodName, methodName))

def callRemote(function, *values):
    js.globals['mainThreadEval']('TestPage.fromAthenaID(1).callRemote("%s",%r)'%(function, values[0]));


registerHandler('helloClient', helloClient)




callRemote("helloServer", "I'm a client");


def test(msg):
    class WelcomeMessage(Protocol):
        def connectionMade(self):
            self.transport.write(msg)
        def dataReceived(self, data):
            print (data)
    cf=ClientFactory()
    cf.protocol=WelcomeMessage
    reactor.connectTCP('127.0.0.1', '9000/ws', cf)


def main():
    reactor.startRunning(False)
    tick()
    test('xyzzy')

if __name__=='__console__':
    main()
