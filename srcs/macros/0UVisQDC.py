import sys

sys.path.insert(0, "../../")
from lib import *

default_dict = {
    "input_file": ["TUTORIAL"],
    "runs": ["CALIB_RUNS", "LIGHT_RUNS", "ALPHA_RUNS", "MUONS_RUNS", "NOISE_RUNS"],
    "channels": ["CHAN_TOTAL"],
}
user_input, info = initialize_macro(
    "0UVisQDC",
    ["input_file", "runs", "channels", "variables", "save", "debug"],
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
    ypbot, yptop = np.percentile(data, percentile)
    ypad = 0.2 * (yptop - ypbot)
    data = data[(data > ypbot - ypad) * (data < yptop + ypad)]
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

    # 3) QDC flags summary
    fig_flag, ax = plt.subplots(1, 1, figsize=(8, 6))
    add_grid(ax)
    labels, values = [], []
    for bit, label in flag_labels.items():
        n = np.count_nonzero(flags & bit)
        if n > 0:
            labels.append(label)
            values.append(100 * n / len(flags))
    ax.bar(labels, values, color=colors[3], alpha=0.95)
    ax.tick_params(axis="x", rotation=45)
    ax.semilogy()
    fig_flag.supylabel("Flagged events (%)")
    fig_flag.suptitle(title + " - QDC flags")
    fig_flag.tight_layout()

    figures = {
        "QDC_Spectrum": fig_qdc,
        "QDC_Rate": fig_rate,
        "QDC_Flags": fig_flag,
    }

    # 4) If SCINT charges have already been computed (03Integration), compare them with the QDC output
    charge_keys = []
    for charge_key in user_input["variables"]:
        if (
            check_key(my_runs[run][ch], charge_key)
            and np.asarray(my_runs[run][ch][charge_key]).shape == energy.shape
        ):
            charge_keys.append(charge_key)
    for charge_key in charge_keys:
        charge = np.asarray(my_runs[run][ch][charge_key], dtype=float)
        fig_cmp, ax = plt.subplots(1, 1, figsize=(8, 6))
        add_grid(ax)
        xpbot, xptop = np.percentile(energy, percentile)
        ypbot, yptop = np.percentile(charge, percentile)
        width = max(1, int(np.ceil((xptop - xpbot) / 300)))
        xbins = np.arange(xpbot - 0.5, xptop + width + 0.5, width)
        hist = ax.hist2d(
            energy,
            charge,
            bins=[xbins, np.linspace(ypbot, yptop, 301)],
            norm=matplotlib.colors.LogNorm(),
        )
        fig_cmp.colorbar(hist[3], ax=ax, label="Counts")
        corr = np.corrcoef(energy, charge)[0, 1]
        fig_cmp.supxlabel("QDC Energy (ADC ch)")
        fig_cmp.supylabel(charge_key)
        fig_cmp.suptitle(
            title + " - QDC vs {} (corr {:.3f})".format(charge_key, corr), fontsize=14
        )
        figures[f"QDC_vs_{charge_key}"] = fig_cmp

        # 5) Overlay of both spectra on the same scale: QDC Energy rescaled with an event-by-event linear fit.
        # Iterative sigma-clipping so that off-diagonal populations (e.g. delayed light inside the QDC gate
        # but outside the SCINT window) do not bias the slope.
        clip = np.ones(len(energy), dtype=bool)
        for _ in range(5):
            a, b = np.polyfit(energy[clip], charge[clip], 1)
            res = charge - (a * energy + b)
            clip = np.abs(res - np.median(res[clip])) < 2.5 * np.std(res[clip])
        fig_ovl, ax = plt.subplots(1, 1, figsize=(8, 6))
        add_grid(ax)
        ypbot, yptop = np.percentile(charge, percentile)
        ypad = 0.2 * (yptop - ypbot)
        bins = np.linspace(ypbot - ypad, yptop + ypad, 401)
        for data, label, color in [
            (charge, charge_key + " (SCINT)", colors[0]),
            (a * energy + b, "QDC Energy x {:.1f} + {:.0f}".format(a, b), colors[5]),
        ]:
            counts, _ = np.histogram(data, bins=bins)
            ax.plot(
                bins[:-1],
                counts,
                drawstyle="steps",
                label=label,
                alpha=0.95,
                linewidth=1.2,
                c=color,
            )
        ax.semilogy()
        ax.legend()
        fig_ovl.supxlabel(charge_key + " (ADC x ticks)")
        fig_ovl.supylabel("Counts")
        fig_ovl.suptitle(title + " - QDC rescaled vs " + charge_key, fontsize=14)
        figures[f"QDC_Overlay_{charge_key}"] = fig_ovl
    if not charge_keys:
        rprint(
            f"[yellow]Run {run} ch {ch}: no {user_input['variables']} branches found. Run 03Integration to compare SCINT charges with the QDC output.[/yellow]"
        )

    if user_input["save"]:
        for label, fig in figures.items():
            save_figure(fig, out_path, run, ch, label, debug=user_input["debug"])

    plt.ion()
    plt.show()
    rprint("[cyan]Press any key on the last figure to continue...[/cyan]")
    while not plt.waitforbuttonpress(-1):
        pass
    plt.close("all")
