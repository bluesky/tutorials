from collections import Counter

from bluesky_live.bluesky_run import BlueskyRun, DocumentCache
from bluesky_widgets.utils.streaming import stream_documents_into_runs
import numpy as np

from .simulated_hardware import SHAPE


def stream_to_figures(fig, axes_list, start_at=0):
    fig.patch.set_alpha(0.5)
    axes_list = axes_list.ravel()

    section = np.zeros((8, 8))
    section[:4, :4] = 1
    section[4:, 4:] = 1
    init_data = np.tile(section, (1 + SHAPE[0] // 8, 1 + SHAPE[1] // 8))[
        : SHAPE[0], : SHAPE[1]
    ]

    ims = [ax.imshow(init_data) for ax in axes_list]
    if len(axes_list) > 1:
        sample_text = "S"  # abbreviate for space
    else:
        sample_text = "Sample "
    for j, ax in enumerate(axes_list):
        ax.set_title(f"{sample_text}{j + start_at} N_shots: 0")
        ax.axis("off")
    counts = Counter()

    last_seen = None

    def update_plot(event):
        nonlocal last_seen
        run = event.run
        (sample,) = run.primary.read()["sample_selector"]
        sample = int(sample)
        img = run.primary.read()["detector_image"].mean(axis=0)
        img -= img.min()
        img /= img.max()

        if len(ims) == 1:
            (im,) = ims
            if sample != last_seen:
                counts.clear()
        else:
            im = ims[int(sample) - start_at]

        prev_count = counts[sample]
        old_data = im.get_array()

        new_data = (old_data * prev_count + img) / (prev_count + 1)

        counts[sample] += 1

        im.set_data(new_data)
        im.axes.set_title(f"{sample_text}{sample} N_shots: {counts[sample]}")

        last_seen = sample
        fig.canvas.draw_idle()

    def update_plot_on_stop(run):
        run.events.completed.connect(update_plot)

    return stream_documents_into_runs(update_plot_on_stop)
