from typing import Dict

def export_as_txt(results: Dict) -> str:
    """
    Export convergence study results as a plain text report with grouped intra/inter-triplet tables.

    Parameters
    ----------
    results : Dict
        Output of ConvergenceStudy.perform_analysis()

    Returns
    -------
    str
        Plain text string summarizing the convergence behavior.
    """
    lines = ["CONVERGENCE STUDY REPORT\n"]
    lines.append(f"Standard: {results['standard']}")
    lines.append(f"Meshes: {', '.join(results['meshes'])}\n")

    for param, triplets in results["parameters"].items():
        lines.append(f"Parameter: {param}\n")

        lines.append("  --- Intra-Triplet Metrics ---")
        lines.append("  Trip | Mesh Triplet           | Order | GCI_21 | GCI_32 | Ratio | Richardson | Monotonic | Asymptotic | Sign Flip | Rel Eps21 | Rel Eps32")
        lines.append("  -----+------------------------+-------+--------+--------+--------+-------------+-----------+-------------+------------+-----------+-----------")
        for i, triplet in enumerate(triplets, 1):
            if "error" in triplet:
                continue
            mt = " -> ".join(triplet["mesh_triplet"])
            intra = triplet["intra_triplet"]
            lines.append(
                f"  {i:<4} | {mt:<22} | {triplet['order']:<5} | {triplet['gci_21']:<6}% | {triplet['gci_32']:<6}% | {triplet['gci_ratio']:<6} | "
                f"{triplet['richardson_extrapolated']:<11} | {'Yes' if intra['monotonic'] else 'No':<9} | "
                f"{'Yes' if intra['asymptotic'] else 'No':<11} | {'Yes' if intra['sign_flip'] else 'No':<10} | "
                f"{intra['rel_eps21']:<9} | {intra['rel_eps32']:<9}"
            )

        lines.append("\n  --- Inter-Triplet Trends ---")
        lines.append("  Trip | ΔOrder | ΔGCI")
        lines.append("  -----+--------+------")
        for i, triplet in enumerate(triplets, 1):
            if "error" in triplet:
                continue
            inter = triplet["inter_triplet"]
            delta_order = inter["delta_order"] if inter["delta_order"] is not None else "--"
            delta_gci = inter["delta_gci"] if inter["delta_gci"] is not None else "--"
            lines.append(f"  {i:<4} | {delta_order:<6} | {delta_gci:<5}")

        lines.append("\n")

    return "\n".join(lines)


def save_txt_report(results: Dict, filepath: str) -> None:
    """
    Save the convergence study report to a .txt file.

    Parameters
    ----------
    results : Dict
        Output of ConvergenceStudy.perform_analysis()
    filepath : str
        Path to save the .txt report.
    """
    with open(filepath, 'w') as file:
        file.write(export_as_txt(results))
