from __future__ import division, unicode_literals
from nevow.appserver import NevowSite
from nevow.athena import LivePage, LiveElement, expose
from nevow.dirlist import DirectoryLister, formatFileSize
from nevow.loaders import xmlfile
from twisted.internet import reactor
from nevow.static import File
from twisted.python.filepath import FilePath
import json
import os
import urllib
import stat
website=FilePath(__file__).sibling('website')
js = website.child('js')


class DL(DirectoryLister):
    def data_listing(self, context, data):
        from nevow.static import getTypeAndEncoding

        if self.dirs is None:
            directory = os.listdir(self.path)
            directory.sort()
        else:
            directory = self.dirs
        files = []; dirs = []
        for path in directory:
            url = '/js/'+urllib.quote(path, '/')
            if os.path.isdir(os.path.join(self.path, path)):
                url = url + '/'
                dirs.append({
                    'link': url,
                    'linktext': path + "/",
                    'type': '[Directory]',
                    'filesize': '',
                    'encoding': '',
                    })
            else:
                mimetype, encoding = getTypeAndEncoding(
                    path,
                    self.contentTypes, self.contentEncodings, self.defaultType)
                try:
                    filesize = os.stat(os.path.join(self.path, path))[stat.ST_SIZE]
                except OSError, x:
                    if x.errno != 2 and x.errno != 13:
                        raise x
                else:
                    files.append({
                        'link': url,
                        'linktext': path,
                        'type': '[%s]' % mimetype,
                        'filesize': formatFileSize(filesize),
                        'encoding': (encoding and '[%s]' % encoding or '')})

        return dirs + files


class TestPage(LivePage):
    docFactory = xmlfile(website.child('testpage.html').path)
    docFactory.useDocType = '<!DOCTYPE html>'
    def __init__(self, *args):
        LivePage.__init__(self, *args)
        self.jsModules.mapping[u'TestPage'] = js.child('testPage.js').path
        self.jsModules.mapping[u'PyPyWorker'] = js.child('PyPyWorker.js').path
        self.jsModules.mapping[u'jqconsole'] = js.child('jqconsole.min.js').path
        self.jsModules.mapping[u'pypyDrawThread'] = js.child('pypyDrawThread.js').path
    def render_TestElement(self, *_):
        """
        Replace the tag with a new L{MenuCreatorElement}.
        """
        c = TestElement()
        c.setFragmentParent(self)
        return c
    def locateChild(self, ctx, segments):
        if segments[0]=='js':
            s=list(segments)
            p=website.child(s.pop(0))
            while p.exists() and s:
                p=p.child(s.pop(0))
            if p.exists:
                if p.isdir():
                    return DirectoryLister(p.path), ()
                return File(p.path), s
            else:
                return LivePage.locateChild(self, ctx, segments)
        if segments[0] == '':
            return self, ()
        return LivePage.locateChild(self, ctx, segments)





class TestElement(LiveElement):
    """
    A "live" Menu Creator controller.

    """
    docFactory = xmlfile(website.child('testpage.html').path, 'TestPattern')
    docFactory.useDocType = '<!DOCTYPE html>'
    jsClass = u"TestPage"

    def __init__(self, *a, **k):
        super(TestElement, self).__init__(*a, **k)
    @expose
    def echo(self, msg):
        print msg
        self.callRemote('echo',msg)
    @expose
    def helloServer(self, msg):
        print msg
        self.callRemote('helloClient','Pleased to meet you')


class PageServer(TestPage):
    def renderHTTP(self, ctx):
        return TestPage().renderHTTP(ctx)



if __name__=='__main__':
    # noinspection PyUnresolvedReferences
    reactor.listenTCP(8888, NevowSite(PageServer()))
    # noinspection PyUnresolvedReferences
    reactor.run()

