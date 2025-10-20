# dsites/main.py
import argparse
import logging
from .predictor import run  # our main pipeline is in predictor.py

def cli():
    logging.basicConfig(level=logging.INFO)
    parser = argparse.ArgumentParser(
        description="D-Sites: Hybrid TFBS predictor (PWM + DNA shape + RF)"
    )
    # Mirror the arguments your script expects:
    parser.add_argument('--fasta', required=True, help="Genome FASTA file path")
    parser.add_argument('--motif', required=True, help="TF motif file (JASPAR or MEME PFM)")
    parser.add_argument('--gene', required=True, help="TF name")
    parser.add_argument('--genome_accession', required=True, help="Genome accession ID in FASTA")
    parser.add_argument('--output', dest='outdir', default='results', help="Output directory")
    parser.add_argument('--n_trees', default=300, type=int, help="Number of trees in Random Forest")
    parser.add_argument('--neg_ratio', default=5, type=int, help="Ratio of negative to positive examples")
    parser.add_argument('--prob_cutoff', default=0.5, type=float, help="Probability cutoff for candidate site")
    parser.add_argument('--pad', default=10, type=int, help="Window padding around known sites")
    parser.add_argument('--seed', default=42, type=int, help="Random seed for reproducibility")
    parser.add_argument('--batch', default=10000, type=int, help="Batch size for genome scanning")
    parser.add_argument('--auto_cutoff', action='store_true', help="Automatically select probability cutoff using PR curve")
    parser.add_argument("--up", default=300, type=int, help="Upstream window size for promoter region")
    parser.add_argument("--down", default=50, type=int, help="Downstream window size for promoter region")
    parser.add_argument("--gff", required=True, help="Genome annotation in GFF3 format (used to define promoter regions)")
    parser.add_argument("--known", help="Known binding sequences (plain txt, one sequence per line)")
    parser.add_argument("--full_genome", action='store_true', help="Enable full-genome scanning instead of promoter-only")

    args = parser.parse_args()
    run(args)

if __name__ == "__main__":
    cli()

