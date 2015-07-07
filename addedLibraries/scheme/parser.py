from __future__ import division
import re
import cStringIO

from symbol import Symbol
from token import Token


class Parser(object):
    tokenizer = r"""\s*(#`|#,@|#,|#'|,@|[('`,)]|"(?:[\\].|;|[^\\"])*"|;.*|[^\s('"`,;)]*)(.*)"""
    eof_object = Symbol('#<eof-object>')
    eol_object = Symbol('#<eol-object>')
    pause_object = Symbol('#<pause-object>')
    @classmethod
    def stringParser(cls, string):
        return cls(cStringIO.StringIO(string))
    def __init__(self, _file):
        self.file = _file;
        self.line = u''
        self.line_number = 0
        self.iga=self.igetast()
    def gettokens(self):
        """Return the next token, reading new text into line buffer if needed."""
        while True:
            if self.line == '\n' or self.line == '':
                self.line = self.file.readline().decode('utf-8')
                self.line_number += 1
                if (self.line_number == 1 or self.line_number == 2) and self.line.startswith('#!'):
                    self.line = self.file.readline().decode('utf-8')
                    self.line_number+=1
            if self.line == '':
                yield self.eof_object
                continue

            # noinspection PyUnresolvedReferences
            token, self.line = re.match(self.tokenizer, self.line).groups()
            if token != '' and not token.startswith(';'):
                yield Token(token).setLine(self.line_number)
            if self.line == '\n' or self.line == '':
                yield self.eol_object
        #yield self.eof_object
    tokens=property(gettokens)
    def igetast(self):
        tokens = self.gettokens()
        o = []

        for t in tokens:
            if t is self.eof_object:
                yield self.pause_object
                continue
            if t is self.eol_object:
                if o:
                    yield o
                    o=[]
                continue
            ra=self.read_ahead(t,tokens)
            n=ra.next()
            while n is self.pause_object:
                yield n
                n=ra.next()
            o.append(n)
    def getast(self):
        n = self.iga.next()
        if n is self.pause_object:
            return []
        return n
    def read_ahead(self, token, tokens):
        if '(' == token:
            L = []
            while True:
                token = tokens.next()
                if token is self.eof_object:
                    yield self.pause_object
                    continue
                if token is self.eol_object:
                    continue
                if token == ')':
                    yield L
                else:
                    ra = self.read_ahead(token, tokens)
                    n = ra.next()
                    while n is self.pause_object:
                        yield n
                        n = ra.next()
                    L.append(n)
        elif ')' == token:
            raise SyntaxError('unexpected )')
        elif token is self.eol_object:
            raise SyntaxError('unexpected eol')
        else:
            yield token.symbol
    ast=property(getast)



