import sys, select

sys.path.insert(0, "../../")
from lib import *

default_dict = {
    "input_file": ["TUTORIAL"],
    "runs": ["CALIB_RUNS", "LIGHT_RUNS", "ALPHA_RUNS", "MUONS_RUNS", "NOISE_RUNS"],
    "channels": ["CHAN_TOTAL"],
}
user_input, info = initialize_macro(
    "0UVisQDC",
    ["input_file", "runs", "channels", "save", "debug"],
    default_dict=default_dict,
    debug=True,
)

### 0UVisQDC
# CAEN CoMPASS event flags (GD6300 CoMPASS Quick Start Guide rev. 27)
flag_labels = {
    0x1: "Dead-time",
    0x2: "TS roll-over",
    0x4: "TS ext. reset",
    0x8: "Fake event",
    0x10: "Memory full",
    0x20: "Trigger lost",
    0x40: "N triggers lost",
    0x80: "Saturation in gate",
    0x100: "1024 trg counted",
    0x200: "After board busy",
    0x400: "Input saturating",
    0x800: "N triggers counted",
    0x1000: "No time correlation",
    0x4000: "Fine timestamp",
    0x8000: "Pile-up",
    0x80000: "PLL lock loss",
    0x100000: "Over-temperature",
    0x200000: "ADC shutdown",
}

my_runs = load_npy(
    np.asarray(user_input["runs"]).astype(str),
    np.asarray(user_input["channels"]).astype(str),
    preset="EVA",
    info=info,
    compressed=True,
    debug=user_input["debug"],
)

style_selector()
colors = get_prism_colors()
out_path = os.path.expandvars(f'{root}/{info["OUT_PATH"][0]}/images')
percentile = [0.1, 99.9]

for run, ch in product(my_runs["NRun"], my_runs["NChannel"]):
    if check_key(my_runs[run][ch], "Energy") == False:
        rprint(
            f"[yellow]Run {run} ch {ch} has no QDC branches (Energy). Run 00Raw2Np with RAW_DATA: COMPASS_BIN. Skipping.[/yellow]"
        )
        continue

    energy = np.asarray(my_runs[run][ch]["Energy"], dtype=float)
    tstamp = np.asarray(my_runs[run][ch]["TimeStamp"], dtype=float)
    flags = np.asarray(my_runs[run][ch]["Flags"], dtype=int)
    title = f'Run_{run} - {my_runs[run][ch]["Label"]}'.replace("#", " ") + f" (Ch {ch})"

    # 1) QDC spectrum: Energy (long gate)
    fig_qdc, ax = plt.subplots(1, 1, figsize=(8, 6))
    add_grid(ax)
    data = energy
    # 0xFFFF marks under/overflow of the QDC gate counter
    overflow = 100 * np.count_nonzero(data == 0xFFFF) / len(data)
    if overflow > 0:
        data = data[data != 0xFFFF]
    if data.size == 0 or np.count_nonzero(data) < 0.01 * len(data):
        rprint(
            f"[yellow]Run {run} ch {ch}: QDC Energy is ~all zeros or overflow. Check the QDC gate/threshold settings of this channel.[/yellow]"
        )
        if data.size == 0:
            data = np.zeros(1)
    ypbot, yptop = np.percentile(data, percentile)
    ypad = 0.2 * (yptop - ypbot)
    data = data[(data >= ypbot - ypad) * (data <= yptop + ypad)]
    # Energy is integer-valued: align the binning with the channel grid (integer bin
    # width, edges at half-integers) so no bin falls between two allowed values
    width = max(1, int(np.ceil((data.max() - data.min()) / 400)))
    bins = np.arange(data.min() - 0.5, data.max() + width + 0.5, width)
    counts, bins = np.histogram(data, bins=bins)
    ax.plot(
        bins[:-1],
        counts,
        drawstyle="steps",
        alpha=0.95,
        linewidth=1.2,
        c=colors[0],
    )
    if overflow > 0:
        ax.plot([], [], " ", label="{:.1f}% ovf removed".format(overflow))
        ax.legend()
    ax.semilogy()
    fig_qdc.supxlabel("QDC Energy (ADC ch)")
    fig_qdc.supylabel("Counts")
    fig_qdc.suptitle(title + " - QDC spectrum")

    # 2) Trigger rate stability from the digitizer timestamps
    duration = tstamp[-1] - tstamp[0]
    fig_rate, ax = plt.subplots(1, 1, figsize=(8, 6))
    add_grid(ax)
    counts, bins = np.histogram(tstamp - tstamp[0], bins=100)
    ax.plot(
        bins[:-1],
        counts / (bins[1] - bins[0]),
        drawstyle="steps",
        alpha=0.95,
        linewidth=1.2,
        c=colors[2],
    )
    fig_rate.supxlabel("Time (s)")
    fig_rate.supylabel("Rate (Hz)")
    fig_rate.suptitle(
        title + " - Rate (mean {:.2f} Hz)".format(len(tstamp) / duration)
    )

    # 3) QDC flags summary: sorted horizontal bars on a linear scale with the exact
    # percentage printed on each bar
    fig_flag, ax = plt.subplots(1, 1, figsize=(8, 6))
    add_grid(ax)
    labels, values = [], []
    for bit, label in flag_labels.items():
        n = np.count_nonzero(flags & bit)
        if n > 0:
            labels.append(label)
            values.append(100 * n / len(flags))
    if values:
        order = np.argsort(values)
        labels = [labels[i] for i in order]
        values = [values[i] for i in order]
        ax.barh(labels, values, color=colors[3], alpha=0.95)
        for i, v in enumerate(values):
            ax.text(v + 0.012 * max(values), i, "{:.3g}%".format(v), va="center")
        ax.set_xlim(0, 1.18 * max(values))
    fig_flag.supxlabel("Flagged events (%)")
    fig_flag.suptitle(title + " - QDC flags")
    fig_flag.tight_layout()

    figures = {
        "QDC_Spectrum": fig_qdc,
        "QDC_Rate": fig_rate,
        "QDC_Flags": fig_flag,
    }

    if user_input["save"]:
        for label, fig in figures.items():
            save_figure(fig, out_path, run, ch, label, debug=user_input["debug"])

    if plt.get_backend().lower() != "agg":
        plt.ion()
        plt.show()
        rprint("[cyan]Figures open. Press ENTER in the terminal to continue...[/cyan]")
        # Keep the GUI event loop alive while waiting for the terminal so the
        # figure windows stay responsive (zoom, pan, etc.). Unlike plt.pause,
        # start_event_loop does not re-show/raise the windows on every cycle.
        while not select.select([sys.stdin], [], [], 0)[0]:
            plt.gcf().canvas.start_event_loop(0.2)
        sys.stdin.readline()
    plt.close("all")
