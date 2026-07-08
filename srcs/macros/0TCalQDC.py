import sys, select

sys.path.insert(0, "../../")
from lib import *

default_dict = {
    "input_file": ["TUTORIAL"],
    "runs": ["CALIB_RUNS", "LIGHT_RUNS", "ALPHA_RUNS", "MUONS_RUNS", "NOISE_RUNS"],
    "channels": ["CHAN_TOTAL"],
}
user_input, info = initialize_macro(
    "0TCalQDC",
    ["input_file", "runs", "channels", "variables", "save", "debug"],
    default_dict=default_dict,
    debug=True,
)

### 0TCalQDC
QDC_DIVISOR = 128       # DPP-QDC rescaling of the gate integral for coarse gain X1
INPUT_IMPEDANCE = 50    # Ohm
E_CHARGE = 1.602e-19    # C

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
ana_cal_path = os.path.expandvars(f'{root}/{info["OUT_PATH"][0]}/analysis/calibration')
percentile = [0.1, 99.9]
amplification = dict(zip(info["CHAN_TOTAL"], info["CHAN_AMPLI"]))

for run, ch in product(my_runs["NRun"], my_runs["NChannel"]):
    if check_key(my_runs[run][ch], "Energy") == False:
        rprint(
            f"[yellow]Run {run} ch {ch} has no QDC branches (Energy). Run 00Raw2Np with RAW_DATA: COMPASS_BIN. Skipping.[/yellow]"
        )
        continue

    energy = np.asarray(my_runs[run][ch]["Energy"], dtype=float)
    title = f'Run_{run} - {my_runs[run][ch]["Label"]}'.replace("#", " ") + f" (Ch {ch})"
    # ADC counts x ticks -> Coulombs delivered by the SiPM (undo digitization,
    # sampling, input impedance and amplification)
    adc2C = (
        info["DYNAMIC_RANGE"][0] / info["BITS"][0]
    ) * info["SAMPLING"][0] / INPUT_IMPEDANCE / amplification[ch]
    figures = {}

    # 1) QDC calibration: fit the same gaussian train used by 04Calibration to the
    # QDC Energy spectrum. The gain is taken as the median separation between
    # consecutive peak centers, which is robust against the pedestal peak being
    # clipped at E=0 (channels where the baseline pushes the pedestal below zero)
    data = energy[energy != 0xFFFF]  # 0xFFFF marks under/overflow of the QDC gate
    if data.size == 0 or np.count_nonzero(data) < 0.01 * len(data):
        rprint(
            f"[yellow]Run {run} ch {ch}: QDC Energy is ~all zeros or overflow. Skipping QDC calibration.[/yellow]"
        )
        continue
    ypbot, yptop = np.percentile(data, percentile)
    ypad = 0.2 * (yptop - ypbot)
    data = data[(data >= ypbot - ypad) * (data <= yptop + ypad)]
    # Integer-valued spectrum: align the binning with the channel grid
    width = max(1, int(np.ceil((data.max() - data.min()) / 400)))
    bins = np.arange(data.min() - 0.5, data.max() + width + 0.5, width)
    counts, bins = np.histogram(data, bins=bins)

    gain_qdc, gain_qdc_err, snr_qdc, ge_qdc = None, None, None, None
    fig_gain, ax = plt.subplots(1, 1, figsize=(8, 6))
    add_grid(ax)
    center_bins = (bins[:-1] + bins[1:]) / 2
    ax.hist(
        center_bins,
        bins,
        weights=counts,
        histtype="step",
        lw=2,
        color=colors[0],
        align="mid",
        zorder=1,
    )
    try:
        popt, pcov = calibration_fit_plot(
            ax, counts, bins, OPT={}, debug=user_input["debug"]
        )
    except (RuntimeError, ValueError, IndexError, TypeError) as e:
        popt = []
        rprint(f"[yellow]Run {run} ch {ch}: QDC gain fit failed ({e}).[/yellow]")
    centers = np.sort(np.asarray(popt[0::3], dtype=float))
    if len(centers) >= 2:
        seps = np.diff(centers)
        gain_qdc = np.median(seps)
        gain_qdc_err = np.std(seps) / np.sqrt(len(seps))
        snr_qdc = spe_snr(popt)
        ge_qdc = gain_qdc * QDC_DIVISOR * adc2C / E_CHARGE
        fig_gain.suptitle(
            title + " - QDC calibration (gain {:.1f} ch/PE)".format(gain_qdc)
        )
        # Persist the QDC calibration next to the 04Calibration output
        update_yaml_file(
            f"{ana_cal_path}/run{get_run_name(run)}/ch{ch}/qdc_calibration_run{get_run_name(run)}_ch{ch}.yml",
            {
                "popt": np.asarray(popt, dtype=float).tolist(),
                "pcov": np.asarray(pcov, dtype=float).tolist(),
                "gain": float(gain_qdc),
                "gain_err": float(gain_qdc_err),
                "snr": None if snr_qdc is None else float(snr_qdc),
                "gain_electrons": float(ge_qdc),
            },
            debug=user_input["debug"],
        )
    else:
        rprint(
            f"[yellow]Run {run} ch {ch}: not enough QDC peaks fitted to compute a gain.[/yellow]"
        )
        fig_gain.suptitle(title + " - QDC calibration")
    fig_gain.supxlabel("QDC Energy (ADC ch)")
    fig_gain.supylabel("Counts")
    figures["QDC_Calibration"] = fig_gain

    # 2) Comparison with the ADC waveform analysis (charges computed by 03Integration)
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

        # 3) Overlay of both spectra on the same scale: QDC Energy rescaled with an
        # event-by-event linear fit. Iterative sigma-clipping so that off-diagonal
        # populations (e.g. delayed light inside the QDC gate but outside the ADC
        # integration window) do not bias the slope.
        clip = np.ones(len(energy), dtype=bool)
        a, b = 0.0, 0.0
        for _ in range(5):
            if np.count_nonzero(clip) < 2:
                break
            a, b = np.polyfit(energy[clip], charge[clip], 1)
            if not np.isfinite(a):
                break
            res = charge - (a * energy + b)
            clip = np.abs(res - np.median(res[clip])) < 2.5 * np.std(res[clip])
        if not np.isfinite(a) or a <= 0:
            rprint(
                f"[yellow]Run {run} ch {ch}: degenerate QDC vs {charge_key} fit (a={a:.2f}). Skipping overlay figure.[/yellow]"
            )
            continue
        fig_ovl, ax = plt.subplots(1, 1, figsize=(8, 6))
        add_grid(ax)
        ypbot, yptop = np.percentile(charge, percentile)
        ypad = 0.2 * (yptop - ypbot)
        # Bin both spectra on the rescaled QDC lattice (bin width = a, edges halfway
        # between the allowed values a*n + b) so the discrete QDC values produce no
        # moire pattern against the binning
        n_lo = np.floor((ypbot - ypad - b) / a)
        n_hi = np.ceil((yptop + ypad - b) / a)
        bins = a * (np.arange(n_lo, n_hi + 2) - 0.5) + b
        for data, label, color in [
            (charge, charge_key + " (ADC)", colors[0]),
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

        # 4) Gain comparison: ADC waveform calibration (04Calibration yml) vs the QDC
        # gain fitted above, both as the median separation between consecutive peak
        # centers. Consistency requires gain_ADC ~ a * gain_QDC, with a the
        # event-by-event conversion factor from the overlay fit. Gains are also
        # converted to SiPM electrons through the DAQ constants and amplification.
        if gain_qdc is not None:
            yml_path = f"{ana_cal_path}/run{get_run_name(run)}/ch{ch}/calibration_run{get_run_name(run)}_ch{ch}_{charge_key}.yml"
            if os.path.exists(yml_path):
                with open(yml_path, encoding="latin1") as f:
                    cal = yaml.safe_load(f)
                adc_centers = np.sort(np.asarray(cal["popt"][0::3], dtype=float))
                if len(adc_centers) < 2:
                    rprint(
                        f"[yellow]Run {run} ch {ch}: 04Calibration fit for {charge_key} has <2 gaussians. Re-run 04Calibration.[/yellow]"
                    )
                    continue
                adc_seps = np.diff(adc_centers)
                gain_adc = np.median(adc_seps)
                gain_adc_err = np.std(adc_seps) / np.sqrt(len(adc_seps))
                snr_adc = spe_snr(cal["popt"])
                ge_adc = gain_adc * adc2C / E_CHARGE
                fmt_snr = lambda s: "-" if s is None else "{:.2f}".format(s)
                ratio = gain_adc / gain_qdc
                gain_table = Table(title=f"Gain comparison - run {run} ch {ch} ({charge_key})")
                gain_table.add_column("gain QDC (ch/PE)", justify="center")
                gain_table.add_column("gain ADC (ADC x ticks/PE)", justify="center")
                gain_table.add_column("ratio", justify="center")
                gain_table.add_column("a overlay", justify="center")
                gain_table.add_column("agreement", justify="center")
                gain_table.add_column("Ge QDC (e-)", justify="center")
                gain_table.add_column("Ge ADC (e-)", justify="center")
                gain_table.add_row(
                    "{:.2f} +/- {:.2f}".format(gain_qdc, gain_qdc_err),
                    "{:.1f} +/- {:.1f}".format(gain_adc, gain_adc_err),
                    "{:.2f}".format(ratio),
                    "{:.2f}".format(a),
                    "{:+.1f}%".format(100 * (ratio / a - 1)),
                    "{:.2e}".format(ge_qdc),
                    "{:.2e}".format(ge_adc),
                )
                rprint(gain_table)
                snr_table = Table(title=f"SPE SNR - run {run} ch {ch} ({charge_key})")
                snr_table.add_column("SNR QDC", justify="center")
                snr_table.add_column("SNR ADC", justify="center")
                snr_table.add_row(fmt_snr(snr_qdc), fmt_snr(snr_adc))
                rprint(snr_table)
                # Persist the comparison next to the QDC calibration results
                update_yaml_file(
                    f"{ana_cal_path}/run{get_run_name(run)}/ch{ch}/qdc_calibration_run{get_run_name(run)}_ch{ch}.yml",
                    {
                        charge_key: {
                            "gain_adc": float(gain_adc),
                            "gain_adc_err": float(gain_adc_err),
                            "snr_adc": None if snr_adc is None else float(snr_adc),
                            "gain_adc_electrons": float(ge_adc),
                            "a_overlay": float(a),
                            "ratio": float(ratio),
                            "agreement_percent": float(100 * (ratio / a - 1)),
                        }
                    },
                    debug=user_input["debug"],
                )
            else:
                rprint(
                    f"[yellow]Run {run} ch {ch}: no calibration yml for {charge_key} (run 04Calibration). QDC gain = {gain_qdc:.2f} ch/PE.[/yellow]"
                )
    if not charge_keys:
        rprint(
            f"[yellow]Run {run} ch {ch}: no {user_input['variables']} branches found. Run 03Integration to compare the ADC charges with the QDC output.[/yellow]"
        )

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
