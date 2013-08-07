"""
Base class for pcef syntax hightlighters
"""
import os
from pcef.core.mode import Mode
from pcef.core.textblockuserdata import TextBlockUserData
from pcef.qt import QtGui, QtCore


class FoldDetector(object):
    """
    A fold detector take care of detecting the folding indent of a specific text
    block.

    A code folding marker will appear the line *before* the one where the
    indention level increases. The code folding region will end in the last
    line that has the same indention level (or higher), skipping blank lines.

    You must override the getFoldIndent method to create a custom fold detector.

    The base implementation does not perform any detection.
    """
    def getFoldIndent(self, highlighter, block, text):
        """
        Return the fold indent of a QTextBlock

        A code folding marker will appear the line *before* the one where the
        indention level increases.
        The code folding reagion will end in the last line that has the same
        indention level (or higher).

        :param highlighter: Reference to the highlighter

        :param block: Block to parse
        :param text: Text of the block (for convenience)

        :return: int
        """
        return -1

    def isFoldStart(self, currentBlock, nextBlock):
        currUsd = currentBlock.userData()
        nextUsd = nextBlock.userData()
        if currUsd.foldIndent < nextUsd.foldIndent:
            return True


class IndentBasedFoldDetector(FoldDetector):
    """
    Perform folding detection based on the line indentation level.

    Suitable for languages such as python, cython, batch, data interchange
    formats such as xml and json or even markup languages (html, rst).

    It does not work well with c based languages nor with vb or ruby.
    """
    def getFoldIndent(self, highlighter, block, text):
        pb = block.previous()
        if pb:
            ptxt = pb.text().rstrip()
            if(ptxt.endswith("(") or ptxt.endswith(",") or
               ptxt.endswith("\\") or ptxt.endswith("+") or
               ptxt.endswith("-") or ptxt.endswith("*") or
               ptxt.endswith("/") or ptxt.endswith("and") or
               ptxt.endswith("or")):
                return pb.userData().foldIndent
        stripped = len(text.strip())
        if stripped:
            return int((len(text) - len(text.strip())))
        else:
            return -1

    def isFoldStart(self, currentBlock, nextBlock):
        """
        Checks if the current block is a start fold block

        :param current: Current block
        :param next: Next block
        :return: True or False
        """
        currUsd = currentBlock.userData()
        nextUsd = nextBlock.userData()
        if currUsd.foldIndent < nextUsd.foldIndent:
            return True


class SyntaxHighlighter(QtGui.QSyntaxHighlighter, Mode):
    """
    Base class for syntax highlighter modes.

    It takes care of filling the document with our custom user data.

    It also provides signal that you can hook to apply apply custom
    highlighting
    """
    #: Mode identifier
    IDENTIFIER = "syntaxHighlighterMode"

    #: Signal emitted at the start of highlightBlock. Parameters are the
    #: highlighter instance and the current text block
    blockHighlightStarted = QtCore.Signal(object, object)

    #: Signal emitted at the end of highlightBlock. Parameters are the
    #: highlighter instance and the current text block
    blockHighlightFinished = QtCore.Signal(object, object)

    def __init__(self, parent, foldDetector=None):
        QtGui.QSyntaxHighlighter.__init__(self, parent)
        Mode.__init__(self)
        self._spacesExpression = QtCore.QRegExp('\s+')
        if os.environ["QT_API"] == "PyQt":
            # there is a bug with QTextBlockUserData in PyQt4, we need to
            # keep a reference on the otherwise they are removed from memory
            self.__blocks = set()
        self._foldDetector = foldDetector

    def __del__(self):
        self.__blocks.clear()

    def setFoldDetector(self, foldDetector):
        self._foldDetector = foldDetector

    def getFoldingIndent(self, text):
        """
        Return the folding indent of the block.

        This must be specialised for a specific language, it just use the
        regular indent here.

        :param text:
        :return:
        """
        pb = self.currentBlock().previous()
        if pb:
            ptxt = pb.text().rstrip()
            if(ptxt.endswith("(") or ptxt.endswith(",") or
               ptxt.endswith("\\") or ptxt.endswith("+") or
               ptxt.endswith("-") or ptxt.endswith("*") or
               ptxt.endswith("/") or ptxt.endswith("and") or
               ptxt.endswith("or")):
                return pb.userData().foldIndent
        stripped = len(text.strip())
        if stripped:
            return int((len(text) - len(text.strip())))
        else:
            return -1

    def isFoldStart(self, currentBlock, nextBlock):
        """
        Checks if the current block is a start fold block

        :param current: Current block
        :param next: Next block
        :return: True or False
        """
        currUsd = currentBlock.userData()
        nextUsd = nextBlock.userData()
        if currUsd.foldIndent < nextUsd.foldIndent:
            return True

    def highlightBlock(self, text):
        # parse line indent
        userData = self.currentBlockUserData()
        if userData is None:
            userData = TextBlockUserData()
            self.setCurrentBlockUserData(userData)
        # update user data with parenthesis infos, indent info,...
        userData.lineNumber = self.currentBlock().blockNumber() + 1
        # Collect folding informations
        if self._foldDetector:
            userData.foldIndent = self._foldDetector.getFoldIndent(
                self, self.currentBlock(), text)
            prevBlock = self.currentBlock().previous()
            if prevBlock and prevBlock.isValid():
                # skip blank lines
                while (prevBlock and prevBlock.isValid() and
                       len(prevBlock.text().strip()) == 0):
                    prevBlock = prevBlock.previous()
                prevUsd = prevBlock.userData()
                if prevUsd:
                    prevUsd.foldStart = self._foldDetector.isFoldStart(
                        prevBlock, self.currentBlock())
                prevBlock.setUserData(prevUsd)
        # set current block's user data
        if os.environ["QT_API"] == "PyQt":
            self.__blocks.add(userData)
        self.setCurrentBlockUserData(userData)
