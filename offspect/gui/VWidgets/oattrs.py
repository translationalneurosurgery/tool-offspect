from PyQt5 import QtWidgets
from offspect.api import CacheFile, decode, encode
from functools import partial
from offspect.cache.attrs import valid_origin_keys
from .textedit import VTextEdit
from typing import Callable


def save_global(cf, idx: int, key: str, read: Callable):
    tattr = cf.get_trace_attrs(idx)
    text = read()
    if tattr[key] == text:
        return
    else:
        origin = tattr["origin"]
        for idx in range(len(cf)):
            tattr = cf.get_trace_attrs(idx)
            if tattr["origin"] == origin:
                tattr[key] = encode(text)
                cf.set_trace_attrs(idx, tattr)
        print(f"CF: Wrote globaly {origin}: {key} {text}")


class OattrWidget(QtWidgets.QWidget):
    """Widget listing all Origin Attributes
        

    Example::

        python -m offspect.gui.baseui stroke_map.hdf5  0
        python -m offspect.gui.baseui stroke_mep.hdf5  0
    """

    def __init__(self, cf: CacheFile, idx: int, *args, **kwargs):
        super(OattrWidget, self).__init__(*args, **kwargs)
        tattr = cf.get_trace_attrs(idx)
        layout = QtWidgets.QGridLayout()
        keys = sorted(valid_origin_keys).copy()
        keys.remove("global_comment")
        keys.remove("channel_labels")

        row = 0
        for key in keys:
            label = QtWidgets.QLabel(text=key)
            line = QtWidgets.QLabel(tattr[key])
            layout.addWidget(label, row, 0)
            layout.addWidget(line, row, 1)
            row += 1

        key = "channel_labels"
        label = QtWidgets.QLabel(text=key)
        line = QtWidgets.QListWidget()
        entries = decode(tattr[key])
        line.addItems(entries)
        line.setFlow(line.LeftToRight)
        line.setMaximumHeight(50)
        layout.addWidget(label, row, 0)
        layout.addWidget(line, row, 1)

        row += 1
        key = "global_comment"
        label = QtWidgets.QLabel(text=key)
        line = VTextEdit(tattr[key])
        trig = partial(save_global, cf=cf, idx=idx, key=key, read=line.toPlainText)
        line.editingFinished.connect(trig)
        layout.addWidget(label, row, 0)
        layout.addWidget(line, row, 1)

        self.setLayout(layout)