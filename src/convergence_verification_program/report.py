# src\convergence_verification_program\report.py

from typing import Dict
from .config import REPORT_FORMAT, REPORT_FLOAT_PRECISION


def export_report(results: Dict) -> str:
    if REPORT_FORMAT == "txt":
        return _export_txt(results)
    elif REPORT_FORMAT == "md":
        return _export_markdown(results)
    elif REPORT_FORMAT == "tex":
        return _export_latex(results)
    else:
        raise ValueError(f"Unsupported report format: {REPORT_FORMAT}")


def save_report(results: Dict, filepath: str) -> None:
    with open(filepath, "w", encoding="utf-8") as f:
        f.write(export_report(results))

# ==============================
# Plain Text Report
# ==============================

def _export_txt(results: Dict) -> str:
    p = REPORT_FLOAT_PRECISION
    lines = ["CONVERGENCE STUDY REPORT", f"Standard: {results['standard']}", f"Tuple Size: {results.get('tuple_size')}", f"Meshes: {', '.join(results['meshes'])}"]
    for param, data in results['parameters'].items():
        lines.append(f"\nParameter: {param}")
        for tup in data['tuples']:
            idx = data['tuples'].index(tup) + 1
            mt = ' -> '.join(tup['mesh_tuple'])
            if 'error' in tup:
                lines.append(f"Tuple {idx}: ERROR {tup['error']}")
                continue
            # Raw errors & ratios
            lines.append(f"  Tuple {idx} Mesh-Pair Metrics:")
            for i, r in enumerate(tup['refinement_ratios']):
                err = tup['errors'][i]
                rel = tup['rel_eps_table'][1][i]
                gci = tup['GCI_table'][1][i]
                lines.append(f"    Pair {i+1}: R={r:.{p}f}, err={err:.{p}f}, rel={rel:.{p}f}, GCI={gci:.{p}f}" )
            # Romberg / order / GCI tables
            lines.append("  Richardson Extrapolation Table:")
            for lvl, row in tup['R_table'].items():
                vals = ', '.join(f"{v:.{p}f}" for v in row.values())
                lines.append(f"    Level {lvl}: {vals}")
            lines.append("  Observed Orders:")
            for lvl, row in tup['p_table'].items():
                vals = ', '.join(f"{v:.{p}f}" for v in row.values())
                lines.append(f"    Level {lvl}: {vals}")
            # Global summaries
            ofp = tup['order_finest_pair']
            oavg = tup['order_tuple_avg']
            gfp = tup['gci_finest_pair']
            glob = tup['global_gci_ratio']
            lines.append(f"  Global: order_fp={ofp:.{p}f}, order_avg={oavg:.{p}f}, gci_fp={gfp:.{p}f}, ratio={glob:.{p}f}")
            # Flags
            for lvl in tup['monotonic_table']:
                mono = tup['monotonic_table'][lvl]
                sf = tup['signflip_table'][lvl]
                asym = tup['asymptotic_table'][lvl]
                lines.append(f"    Level {lvl} flags: monotonic={mono}, signflip={sf}, asymptotic={asym}")
        # Inter-tuple
        lines.append("\nInter-Tuple Trends:")
        for i, tup in enumerate(data['tuples'],1):
            if 'error' in tup: continue
            d = tup['inter_tuple']
            lines.append(f"  Tuple {i}: Δorder={d['delta_order']:.{p}f}, Δgci={d['delta_gci']:.{p}f}")
    return '\n'.join(lines)

# ==============================
# Markdown Report
# ==============================

def _export_markdown(results: Dict) -> str:
    p = REPORT_FLOAT_PRECISION
    md = ["# Convergence Study Report", f"**Standard:** {results['standard']}  ", f"**Tuple Size:** {results.get('tuple_size')}  ", f"**Meshes:** {', '.join(results['meshes'])}"]
    for param, data in results['parameters'].items():
        md.append(f"## Parameter: `{param}`")
        for tup in data['tuples']:
            idx = data['tuples'].index(tup) + 1
            if 'error' in tup:
                md.append(f"- **Tuple {idx}: ERROR** {tup['error']}")
                continue
            md.append(f"### Tuple {idx}: Mesh Tuple `{ ' → '.join(tup['mesh_tuple']) }`")
            # Mesh-Pair Metrics
            md.append("**Mesh-Pair Metrics**")
            md.append("| Pair | R | Error | RelErr | GCI |")
            md.append("|------|---|-------|--------|-----|")
            for i, r in enumerate(tup['refinement_ratios']):
                err = tup['errors'][i]
                rel = tup['rel_eps_table'][1][i]
                gci = tup['GCI_table'][1][i]
                md.append(f"| {i+1} | {r:.{p}f} | {err:.{p}f} | {rel:.{p}f} | {gci:.{p}f} |")
            # Romberg table
            md.append("**Richardson Extrapolation Table**")
            headers = "| Level | " + " | ".join(str(l) for l in tup['R_table'].keys()) + " |"
            md.append(headers)
            md.append("|-----|" + "----|"*len(tup['R_table']) )
            vals = "| R | " + " | ".join(f"{v:.{p}f}" for v in tup['R_table'].values()) + " |"
            md.append(vals)
            # Global summary
            md.append("**Global Summaries**")
            ofp = tup['order_finest_pair']
            oavg = tup['order_tuple_avg']
            gfp = tup['gci_finest_pair']
            glob = tup['global_gci_ratio']
            md.append(f"- Order (finest): {ofp:.{p}f}  ")
            md.append(f"- Order (avg): {oavg:.{p}f}  ")
            md.append(f"- GCI (finest): {gfp:.{p}f}  ")
            md.append(f"- GCI Ratio: {glob:.{p}f}  ")
            # Flags
            md.append("**Flags by Level**")
            for lvl in tup['monotonic_table']:
                md.append(f"- Level {lvl}: monotonic={tup['monotonic_table'][lvl]}, signflip={tup['signflip_table'][lvl]}, asymptotic={tup['asymptotic_table'][lvl]}  ")
        # Inter-tuple
        md.append("## Inter-Tuple Trends")
        md.append("| Tuple | ΔOrder | ΔGCI |")
        md.append("|-------|--------|------|")
        for i, tup in enumerate(data['tuples'],1):
            if 'error' in tup: continue
            d = tup['inter_tuple']
            md.append(f"| {i} | {d['delta_order']:.{p}f} | {d['delta_gci']:.{p}f} |")
    return '\n'.join(md)

# ==============================
# LaTeX Report
# ==============================

def _export_latex(results: Dict) -> str:
    p = REPORT_FLOAT_PRECISION
    latex = [r"\documentclass{article}", r"\usepackage{booktabs}", r"\begin{document}"]
    latex.append(r"\section*{Convergence Study Report}")
    latex.append(f"\\textbf{{Standard:}} {results['standard']}\\\\")
    latex.append(f"\\textbf{{Tuple Size:}} {results.get('tuple_size')}\\\\")
    latex.append(f"\\textbf{{Meshes:}} {', '.join(results['meshes'])}\\\\\n")
    for param, data in results['parameters'].items():
        latex.append(f"\\subsection*{{Parameter: \texttt{{{param}}}}}")
        for tup in data['tuples']:
            idx = data['tuples'].index(tup) + 1
            if 'error' in tup:
                latex.append(rf"{idx} & ERROR & \multicolumn{{3}}{{l}}{{{tup['error']}}}\\")
                continue
            # Mesh-Pair
            latex.append(r"\subsubsection*{Mesh-Pair Metrics}")
            latex.append(r"\begin{tabular}{lcccc}")
            latex.append(r"\toprule")
            latex.append(r"Pair & R & Error & RelErr & GCI \\")
            latex.append(r"\midrule")
            for i, r in enumerate(tup['refinement_ratios']):
                err = tup['errors'][i]
                rel = tup['rel_eps_table'][1][i]
                gci = tup['GCI_table'][1][i]
                latex.append(f"{i+1} & {r:.{p}f} & {err:.{p}f} & {rel:.{p}f} & {gci:.{p}f}\\")
            latex.append(r"\bottomrule\end{tabular}\n")
            # Romberg
            latex.append(r"\subsubsection*{Richardson Table}")
            levels = sorted(tup['R_table'].keys())
            cols = 'l' + 'c'*len(levels)
            latex.append(rf"\begin{{tabular}}{{{cols}}}")
            latex.append(r"\toprule")
            head = ' & '.join(f"L{lvl}" for lvl in levels)
            latex.append(rf"Tuple & {head}\\")
            latex.append(r"\midrule")
            row = ' & '.join(f"{tup['R_table'][lvl][idx-1]:.{p}f}" for lvl in levels)
            latex.append(rf"{idx} & {row}\\")
            latex.append(r"\bottomrule\end{tabular}\n")
            # Global
            latex.append(r"\subsubsection*{Global Summaries}")
            ofp = tup['order_finest_pair']; oavg = tup['order_tuple_avg']; gfp = tup['gci_finest_pair']; glob = tup['global_gci_ratio']
            latex.append(r"\begin{tabular}{lcccc}")
            latex.append(r"\toprule")
            latex.append(r"Metric & Order_{fp} & Order_{avg} & GCI_{fp} & Ratio\\")
            latex.append(r"\midrule")
            latex.append(f"{idx} & {ofp:.{p}f} & {oavg:.{p}f} & {gfp:.{p}f}\% & {glob:.{p}f}\\")
            latex.append(r"\bottomrule\end{tabular}\n")
            # Flags
            latex.append(r"\subsubsection*{Flags}")
            latex.append(r"\begin{tabular}{lccc}")
            latex.append(r"\toprule")
            latex.append(r"Level & Mono & SignFlip & Asym\\")
            latex.append(r"\midrule")
            for lvl in tup['monotonic_table']:
                mono = tup['monotonic_table'][lvl]; sf = tup['signflip_table'][lvl]; asym = tup['asymptotic_table'][lvl]
                latex.append(f"{lvl} & {'Y' if mono else 'N'} & {'Y' if sf else 'N'} & {'Y' if asym else 'N'}\\")
            latex.append(r"\bottomrule\end{tabular}\n")
        # Inter-tuple
        latex.append(r"\subsection*{Inter-Tuple Trends}")
        latex.append(r"\begin{tabular}{lcc}")
        latex.append(r"\toprule")
        latex.append(r"Tuple & DeltaOrder & DeltaGCI\\")
        latex.append(r"\midrule")
        for i, tup in enumerate(data['tuples'],1):
            d = tup['inter_tuple']
            latex.append(f"{i} & {d['delta_order']:.{p}f} & {d['delta_gci']:.{p}f}\\")
        latex.append(r"\bottomrule\end{tabular}\n")
    latex.append(r"\end{document}")
    return '\n'.join(latex)