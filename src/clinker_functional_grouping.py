#!/usr/bin/env python3
"""
clinker_functional_grouping.py

Re-colour a clinker HTML output by broad functional category instead of by
clinker homology group.

clinker (Gilchrist & Chooi, 2021) embeds its figure data as a JSON object in the
generated HTML file. This script reads that object, keeps the clusters, genes,
links and alignment statistics exactly as clinker produced them, and replaces
only the "groups" entries, which control how genes are coloured in the figure.
Each coding sequence is assigned to a broad functional category using
keyword matching on its GenBank product annotation.

IMPORTANT
---------
Category assignment is a heuristic based on product names only. It is not an
automated functional annotation method, and every assignment should be reviewed
by the user before the figure is published. The underlying clinker alignments,
homology assignments and GenBank annotations are never modified.

Usage
-----
    python clinker_functional_grouping.py input.html output.html
    python clinker_functional_grouping.py input.html output.html --table categories.csv
"""

import argparse
import csv
import json
import sys

# ---------------------------------------------------------------------------
# Functional categories, in the order they appear in the figure legend.
# Colours follow the Okabe-Ito colour-blind-safe palette where possible.
# ---------------------------------------------------------------------------
CATEGORIES = [
    ("DNA replication / metabolism", "#0072B2"),
    ("Transcription / regulation",   "#CC79A7"),
    ("DNA packaging",                "#E69F00"),
    ("Head / capsid",                "#D55E00"),
    ("Tail / structural",            "#009E73"),
    ("Host recognition",             "#B79F00"),
    ("Lysis",                        "#C51B7D"),
    ("Other characterized",          "#56B4E9"),
    ("Hypothetical / unknown",       "#BBBBBB"),
]

# ---------------------------------------------------------------------------
# Keyword rules, evaluated in order. The first matching rule wins, so more
# specific rules must come before more general ones. For example,
# "head maturation protease" must match the protease rule before the
# "head" rule, and "head and packaging protein" must match "packaging"
# before "head".
# ---------------------------------------------------------------------------
RULES = [
    # --- lysis -------------------------------------------------------------
    ("Lysis", ["holin", "endolysin", "lysin", "spanin", "lysozyme"]),
    # --- host recognition --------------------------------------------------
    ("Host recognition", ["depolymerase", "tail fiber", "tail fibre",
                          "tail fibers", "tail fibres", "receptor binding",
                          "receptor-binding", "baseplate", "spike"]),
    # --- DNA packaging -----------------------------------------------------
    ("DNA packaging", ["terminase", "packaging"]),
    # --- proteases and recombinases handled before head/tail ---------------
    ("Other characterized", ["protease", "recombinase"]),
    # --- head / capsid -----------------------------------------------------
    ("Head / capsid", ["capsid", "portal", "head"]),
    # --- tail / structural -------------------------------------------------
    ("Tail / structural", ["tail", "tape measure", "tape-measure", "neck",
                           "virion structural", "structural protein"]),
    # --- DNA replication / metabolism --------------------------------------
    ("DNA replication / metabolism",
     ["helicase", "primase", "polymerase", "methyltransferase", "nuclease",
      "kinase", "recombination", "ssdna", "single strand dna",
      "single-strand dna", "phosphoesterase", "phosphatase", "ligase",
      "thymidylate", "ribonucleotide reductase", "dna binding"]),
    # --- transcription / regulation ----------------------------------------
    ("Transcription / regulation",
     ["transcriptional regulator", "rna polymerase", "sigma factor",
      "anti-sigma", "repressor", "transcription"]),
]

UNKNOWN_KEYWORDS = ["hypothetical", "unknown", "putative uncharacterised",
                    "putative uncharacterized", "uncharacterized",
                    "uncharacterised", "duf"]


def classify(product):
    """Return the functional category for a GenBank product annotation."""
    if not product:
        return "Hypothetical / unknown"
    text = product.lower()
    for keyword in UNKNOWN_KEYWORDS:
        if keyword in text:
            return "Hypothetical / unknown"
    for category, keywords in RULES:
        if any(keyword in text for keyword in keywords):
            return category
    return "Other characterized"


def read_clinker_html(path):
    """Return (html, data, start, end) for the JSON object embedded by clinker."""
    with open(path, encoding="utf-8") as handle:
        html = handle.read()
    marker = "<script>const data="
    start = html.find(marker)
    if start < 0:
        sys.exit("Error: no clinker data object found in %s" % path)
    start += len(marker)
    data, length = json.JSONDecoder().raw_decode(html[start:])
    return html, data, start, start + length


def collect_genes(data):
    """Return an ordered list of (uid, product) for every gene in the figure."""
    genes = []
    for cluster in data["clusters"]:
        for locus in cluster["loci"]:
            for gene in locus["genes"]:
                names = gene.get("names") or {}
                genes.append((gene["uid"], names.get("product", "")))
    return genes


def build_groups(genes):
    """Build clinker-style group entries, one per functional category."""
    members = {label: [] for label, _ in CATEGORIES}
    for uid, product in genes:
        members[classify(product)].append(uid)
    groups = []
    for index, (label, colour) in enumerate(CATEGORIES, start=1):
        if not members[label]:
            continue
        groups.append({
            "uid": "functional-%d" % index,
            "label": label,
            "genes": members[label],
            "hidden": False,
            "colour": colour,
        })
    return groups


def main():
    parser = argparse.ArgumentParser(description=__doc__,
                                     formatter_class=argparse.RawDescriptionHelpFormatter)
    parser.add_argument("input_html", help="HTML file produced by clinker")
    parser.add_argument("output_html", help="re-coloured HTML file to write")
    parser.add_argument("--table", help="optional CSV listing every CDS and its "
                                        "assigned category, for manual review")
    args = parser.parse_args()

    html, data, start, end = read_clinker_html(args.input_html)
    genes = collect_genes(data)
    data["groups"] = build_groups(genes)

    with open(args.output_html, "w", encoding="utf-8") as handle:
        handle.write(html[:start] + json.dumps(data) + html[end:])

    if args.table:
        with open(args.table, "w", newline="", encoding="utf-8") as handle:
            writer = csv.writer(handle)
            writer.writerow(["gene_uid", "product", "functional_category"])
            for uid, product in genes:
                writer.writerow([uid, product, classify(product)])

    counts = {group["label"]: len(group["genes"]) for group in data["groups"]}
    print("Wrote %s" % args.output_html)
    for label, _ in CATEGORIES:
        if label in counts:
            print("  %-30s %d" % (label, counts[label]))


if __name__ == "__main__":
    main()
