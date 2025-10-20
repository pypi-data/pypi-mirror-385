# D-Sites: Hybrid TFBS Predictor for Bacterial Genomes

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

A comprehensive computational tool for predicting transcription factor binding sites (TFBS) in bacterial genomes using hybrid PWM, DNA shape features, and Random Forest classification.

## 🚀 Quick Start

### Installation
```bash
## Quick Start
git clone https://github.com/pankaj357/D-Sites.git
cd dsites
pip install -r requirements.txt
```

### Basic Prediction
#### Minimal Command
```bash
python src/D-Sites.py --fasta <genome.fasta> \
                     --gff <annotation.gff> \
                     --motif <motif_file> \
                     --gene <TF_name> \
                     --genome_accession <accession_id>
```
#### Complete Example
```bash
python src/D-Sites.py \
    --fasta <path_to_genome.fasta> \
    --gff <path_to_annotation.gff> \
    --motif <path_to_motif_file> \
    --gene <TF_NAME> \
    --genome_accession <GENOME_ACCESSION> \
    --outdir results \
    --n_trees 300 \
    --neg_ratio 5 \
    --prob_cutoff 0.5 \
    --pad 10 \
    --seed 42 \
    --batch 10000 \
    --up 300 \
    --down 50 \
    --auto_cutoff
```
### Command Breakdown
#### Required Arguments
```bash
--fasta: Genome FASTA file path

--gff: Genome annotation file (GFF3 format)

--motif: TF motif file (JASPAR or MEME format)

--gene: Transcription factor name

--genome_accession: Genome accession ID
```
#### Optional Arguments with Defaults
``` bash
--outdir results: Output directory

--n_trees 300: Number of Random Forest trees

--neg_ratio 5: Negative:Positive ratio

--prob_cutoff 0.5: Probability cutoff

--pad 10: Window padding around known sites

--seed 42: Random seed

--batch 10000: Batch size for processing

--up 300: Upstream promoter size

--down 50: Downstream promoter size
```

## 📈 Performance
D-Sites demonstrates:
- 3-4× higher precision in top predictions  
- 3.02-3.42× enrichment in promoter regions  

## 📝 Citation
If you use D-Sites in your research, please cite:

Pankaj et al. (2025). *D-Sites: A hybrid machine-learning framework for prediction of transcription factor binding sites in bacterial genomes*. Information Sciences (Under Review),2024.

## 📄 License
MIT License - see LICENSE for details.

## 💬 Contact
For questions and support, contact:
- Pankaj: ft.pank@gmail.com
- Kanaka KK: kkokay07@gmail.com
