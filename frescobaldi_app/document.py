# This file is part of the Frescobaldi project, http://www.frescobaldi.org/
#
# Copyright (c) 2008 - 2014 by Wilbert Berendsen
#
# This program is free software; you can redistribute it and/or
# modify it under the terms of the GNU General Public License
# as published by the Free Software Foundation; either version 2
# of the License, or (at your option) any later version.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA
# See http://www.gnu.org/licenses/ for more information.

"""
A Frescobaldi (LilyPond) document.
"""

from __future__ import unicode_literals

import os

from PyQt4.QtCore import QUrl
from PyQt4.QtGui import QPlainTextDocumentLayout, QTextCursor, QTextDocument

import app
import util
import variables
import signals


class Document(QTextDocument):
    
    urlChanged = signals.Signal() # new url, old url
    closed = signals.Signal()
    loaded = signals.Signal()
    saved = signals.Signal()
    
    def __init__(self, url=None, encoding=None):
        super(Document, self).__init__()
        self.setDocumentLayout(QPlainTextDocumentLayout(self))
        self._encoding = encoding
        if url is None:
            url = QUrl()
        self._url = url # avoid urlChanged on init
        self.setUrl(url)
        self.modificationChanged.connect(self.slotModificationChanged)
        self.load()
        app.documents.append(self)
        app.documentCreated(self)
        
    def slotModificationChanged(self):
        app.documentModificationChanged(self)

    def close(self):
        self.closed()
        app.documentClosed(self)
        app.documents.remove(self)

    def load(self, url=None, keepUndo=False):
        """Load the specified or current url (if None was specified).
        
        Currently only local files are supported. An IOError is raised
        when trying to load a nonlocal URL.
        
        If loading succeeds and an url was specified, the url is make the
        current url (by calling setUrl() internally).
        
        If keepUndo is True, the loading can be undone (with Ctrl-Z).
        
        """
        u = url if url is not None else self.url()
        if not u.isEmpty():
            filename = u.toLocalFile()
            if not filename:
                raise IOError("not a local file")
            with open(filename) as f:
                data = f.read()
            text = util.decode(data)
            if keepUndo:
                c = QTextCursor(self)
                c.select(QTextCursor.Document)
                c.insertText(text)
            else:
                self.setPlainText(text)
            if url is not None:
                self.setUrl(url)
            self.setModified(False)
            self.loaded()
            app.documentLoaded(self)
            
    def save(self, url=None):
        """Saves the document to the specified or current url.
        
        Currently only local files are supported. An IOError is raised
        when trying to save a nonlocal URL.
        
        If saving succeeds and an url was specified, the url is made the
        current url (by calling setUrl() internally).
        
        """
        u = url if url is not None else self.url()
        if not u.isEmpty():
            with app.documentSaving(self):
                filename = u.toLocalFile()
                if not filename:
                    raise IOError("not a local file")
                with open(filename, "w") as f:
                    f.write(self.encodedText())
                    f.flush()
                    os.fsync(f.fileno())
                if url is not None:
                    self.setUrl(url)
                self.setModified(False)
                self.saved()
                app.documentSaved(self)

    def url(self):
        return self._url
        
    def setUrl(self, url):
        """ Change the url for this document. """
        if url is None:
            url = QUrl()
        old, self._url = self._url, url
        changed = old != url
        # number for nameless documents
        if self._url.isEmpty():
            nums = [0]
            nums.extend(doc._num for doc in app.documents if doc is not self)
            self._num = max(nums) + 1
        else:
            self._num = 0
        if changed:
            self.urlChanged(url, old)
            app.documentUrlChanged(self, url, old)
    
    def encoding(self):
        return variables.get(self, "coding") or self._encoding
        
    def setEncoding(self, encoding):
        self._encoding = encoding
    
    def encodedText(self):
        """Returns the text of the document encoded in the correct encoding.
        
        Useful to save to a file.
        
        """
        try:
            return self.toPlainText().encode(self.encoding() or 'utf-8')
        except (UnicodeError, LookupError):
            return self.toPlainText().encode('utf-8')
        
    def documentName(self):
        """ Returns a suitable name for this document. """
        if self._url.isEmpty():
            if self._num == 1:
                return _("Untitled")
            else:
                return _("Untitled ({num})").format(num=self._num)
        else:
            return os.path.basename(self._url.path())


