#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
A simple example that shows how to setup CodeEdit, in this example we install
a syntax highlighter mode (base on pygments), a mode that highlights the
current line and a _search and replace_ panel.

There are many other modes and panels, feel free to use this example as a
starting point and experiment!
"""
import sys

from PyQt4 import QtGui

from pyqode.core import frontend
from pyqode.core.frontend import modes
from pyqode.core.frontend import panels


def main():
    app = QtGui.QApplication(sys.argv)
    window = QtGui.QMainWindow()
    editor = frontend.CodeEdit()
    frontend.start_server(editor, 'server.py')
    frontend.open_file(editor, __file__)
    frontend.install_mode(editor, modes.CodeCompletionMode())
    frontend.install_mode(editor,
                          modes.PygmentsSyntaxHighlighter(editor.document()))
    frontend.install_mode(editor, modes.CaretLineHighlighterMode())
    frontend.install_panel(editor, panels.SearchAndReplacePanel(),
                           position=panels.SearchAndReplacePanel.Position.TOP)
    window.setCentralWidget(editor)
    window.show()
    app.exec_()
    del editor
    del window
    del app


if __name__ == "__main__":
    main()



