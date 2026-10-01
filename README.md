# clinker functional grouping

A small Python utility that re-colours a
[clinker](https://github.com/gamcil/clinker) comparative genome figure by
**broad functional category** instead of by clinker homology group.

clinker embeds its figure data as a JSON object inside the HTML file it
generates. This script reads that object, keeps the clusters, genes, links and
alignment statistics exactly as clinker produced them, and replaces only the
`groups` entries, which control how genes are coloured. Each coding sequence is
assigned to a functional category by keyword matching on its GenBank `product`
annotation.

The clinker alignments, homology assignments and the original GenBank
annotations are never modified.

## Scope and limitations

Category assignment is a **heuristic based on product names only**. It is not an
automated functional annotation method, and every assignment should be reviewed
before a figure is published. Use the `--table` option to export the full list
of CDSs and their assigned categories for manual inspection.

## Requirements

Python 3.8 or newer. No third-party packages are required.

## Usage

```bash
# 1. Run clinker on your GenBank records
clinker example_data/*.gb -p ESKpn13_clinker.html

# 2. Re-colour the resulting figure by functional category
python src/clinker_functional_grouping.py \
    ESKpn13_clinker.html \
    ESKpn13_clinker_functional_grouped.html \
    --table ESKpn13_CDS_functional_categories.csv
```

Open either HTML file in a modern web browser. The figure can be exported to SVG
from within clinker's own interface.

## Functional categories

| Category | Example product annotations |
| --- | --- |
| DNA replication / metabolism | DNA primase, helicase, methyltransferase, exonuclease VIII |
| Transcription / regulation | transcriptional regulator |
| DNA packaging | terminase large subunit, head and packaging protein |
| Head / capsid | major head protein, portal protein, capsid decoration protein |
| Tail / structural | major tail protein, tail length tape measure protein, neck protein |
| Host recognition | tail fiber protein, tail protein depolymerase |
| Lysis | holin, endolysin, Rz-like spanin |
| Other characterized | head maturation protease, site-specific recombinase, membrane protein |
| Hypothetical / unknown | hypothetical protein |

Keyword rules are evaluated in order, so that more specific terms are matched
first. For example, *head maturation protease* is assigned to
**Other characterized** rather than **Head / capsid**, and *head and packaging
protein* is assigned to **DNA packaging**. The rules and colours are defined at
the top of `src/clinker_functional_grouping.py` and can be edited directly.

## Example data

`example_data/` contains the three GenBank records compared in the accompanying
study:

| File | Accession | Phage |
| --- | --- | --- |
| `Klebsiella_phage_ES-Kpn13.gb` | PX550016 | *Klebsiella* phage ES-Kpn13 |
| `Klebsiella_phage_vB_Kp_IME328.gb` | NC_105155 | *Klebsiella* phage vB_Kp_IME328 |
| `Klebsiella_phage_vB_KpnS-VAC70.gb` | NC_110359 | *Klebsiella* phage vB_KpnS-VAC70 |

`example_output/` contains the original clinker figure, the re-coloured figure,
and the CDS category table used for manual review.

## Reproducibility

For a publication, preserve the exact GenBank records and the clinker version
used, together with the release of this repository. A GitHub release can be
archived in Zenodo to obtain a DOI for a specific version.

## Citing clinker

If you use this script, please cite clinker itself:

> Gilchrist, C.L.M. & Chooi, Y.-H. (2021) clinker & clustermap.js: automatic
> generation of gene cluster comparison figures. *Bioinformatics* 37, 2473-2475.

## Development note

This tool was developed by Berna Erdoğdu with assistance from a large language
model for code generation and refinement. The author reviewed and validated the
code and is responsible for its scientific use.

## License

MIT License. See `LICENSE`.
