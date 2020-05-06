from collections import ChainMap

from event_model import DocumentRouter
import matplotlib.pyplot as plt


class DerivedPlot(DocumentRouter):
    def __init__(
        self,
        func,
        ax=None,
        xlabel=None,
        ylabel=None,
        title=None,
        legend_keys=None,
        stream_name="primary",
        **kwargs
    ):
        """
        func expects an Event document which looks like this:
        {'time': <UNIX epoch>,
         'seq_num': integer starting from 1 (!),
         'data': {...},
         'timestamps': {...},  # has same keys as data, always
         'filled': {}  # only important if you have big array data
        }
        and should return (x, y)
        """
        super().__init__()
        self.func = func
        if ax is None:
            fig, ax = plt.subplots()
        self.ax = ax
        if xlabel is None:
            xlabel = ""
        if ylabel is None:
            ylabel = ""
        self.ax.set_xlabel(xlabel)
        self.ax.set_ylabel(ylabel)
        if title is not None:
            plt.title(title)

        if legend_keys is None:
            legend_keys = []
        self.legend_keys = ["scan_id"] + legend_keys
        self.ax.margins(0.1)
        self.kwargs = kwargs
        self.lines = []
        self.legend = None
        self.legend_title = " :: ".join([name for name in self.legend_keys])
        self.stream_name = stream_name
        self.descriptors = {}

    def start(self, doc):
        # The doc is not used; we just use the signal that a new run began.
        self.x_data, self.y_data = [], []
        self.descriptors.clear()
        label = " :: ".join([str(doc.get(name, name)) for name in self.legend_keys])
        kwargs = ChainMap(self.kwargs, {"label": label})
        (self.current_line,) = self.ax.plot([], [], **kwargs)
        self.lines.append(self.current_line)
        self.legend = self.ax.legend(loc=0, title=self.legend_title).set_draggable(True)
        super().start(doc)

    def descriptor(self, doc):
        if doc["name"] == self.stream_name:
            self.descriptors[doc["uid"]] = doc

    def event(self, doc):
        if not doc["descriptor"] in self.descriptors:
            # This is from some other event stream and we should ignore it.
            return
        x, y = self.func(doc)
        self.y_data.append(y)
        self.x_data.append(x)
        self.current_line.set_data(self.x_data, self.y_data)
        # Rescale and redraw.
        self.ax.relim(visible_only=True)
        self.ax.autoscale_view(tight=True)
        self.ax.figure.canvas.draw_idle()

    def stop(self, doc):
        super().stop(doc)
