""" This is the main program of Z-curve Encoder """
# PASS 2025-03-03
from _ZcurvePy import BatchZcurveEncoder
from ZcurvePy import __version__
from ZcurvePy.Util import download_acc, extract_CDS
from Bio.SeqIO import parse
import argparse
import json
import time
import sys

# program information
prog_infor = \
f"""
Z-curve Encoder -- Extract Z-curve Features From Nucleotide Sequences

Authors:    Zhang Zetong, Gao Feng
Version:    {__version__}
Contact:    fgao@tju.edu.cn
Copyright:  Bioinformatic Center, Tianjin University, China
"""

# appendix information
epilog_infor = \
"""
The content of setting file should be like:

{
    "encoder": {
        "hyper_params": [
            {"k": 1, "phase": 3, "freq": true, "local": true},
            {"k": 2, "phase": 3, "freq": true, "local": true},
            {"k": 3, "phase": 3, "freq": true, "local": true}
        ],
        "n_jobs": 8
    }
}

Tips: Use the Z-curve method more flexibly through our Python APIs! 
"""

# help information
arg_fasta = "    input sequence file as FASTA format (*.fa; *.fasta; *.fna)"
arg_gbk   = "    input sequence file as GenBank format (*.gb; *.genbank; *.gbk; *.gbff)"
arg_acc   = "    input sequence file as NCBI accession number (*.txt)"
arg_set   = "    hyper-parameter setting file as json (*.json)"
arg_ext   = "    extract protein genes as samples from annotated sequence file"
arg_out   = "    output z-curve features as comma-splited table (*.csv)"

def mergeInputs(
    fasta: str, 
    genbank: str, 
    accession: str, 
    extract: bool,
    command_name=__name__
):
    """
    Merge inputs from different source
    
    Args:
        fasta (str):        comma-splited paths to fasta files
        genbank (str):      comma-splited paths to genbank files
        accession (str):    comma-splited NCBI accession numbers
        extract (bool):     extract protein genes
        command_name (str): command_name
    """
    records = []
    try:
        # read fastas
        if fasta is not None:
            single_fastas = fasta.split(',')
            for single_fasta in single_fastas:
                records += list(parse(single_fasta, "fasta"))

        # read genbanks
        if genbank is not None:
            single_genbanks = genbank.split(',')
            for single_genbank in single_genbanks:
                if extract:
                    records += extract_CDS(single_genbank)
                else:
                    records += list(parse(single_genbank, "genbank"))
        
        # read accesions
        if accession is not None:
            form = 'gb' if extract else 'fasta'
            single_records = download_acc(accession, command_name, form)
            for single_record in single_records:
                if extract:
                    records += extract_CDS(single_record)
                else:
                    records += list(parse(single_record, "fasta"))
        
    except Exception as exception:
        print(f"Biopython: [error] failed to read input files! ")
        print(exception)
    
    if len(records) == 0:
        print(f"{command_name}: [error] none valid input provided! ")
        sys.exit(0)
    
    return records


def main():
    start_time = time.time()
    # program name (command name)
    command_name = 'zcurve-encoder'

    # create arguments parser and parse arguments
    parser = argparse.ArgumentParser(
        prog=command_name,
        description=prog_infor,
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=epilog_infor
    )
    parser.add_argument('-f', '--fasta', metavar='\b', required=False, type=str, default=None, help=arg_fasta)
    parser.add_argument('-g', '--genbank', metavar='\b', required=False, type=str, default=None, help=arg_gbk)
    parser.add_argument('-a', '--accession', metavar='\b', required=False, type=str, default=None, help=arg_acc)
    parser.add_argument('-e', '--extract', metavar='\b', required=False, default=False, type=bool, help=arg_ext)
    parser.add_argument('-s', '--setting', metavar='\b', required=True, type=str, help=arg_set)
    parser.add_argument('-o', '--output', metavar='\b', required=True, type=str, help=arg_out)
    args = vars(parser.parse_args())

    # extract/download sequences and merge inputs
    records = mergeInputs(
        fasta=args['fasta'], 
        genbank=args['genbank'],
        accession=args['accession'],
        extract=args['extract'],
        command_name=command_name
    )
    count = len(records)

    # load setting file and create encoder
    with open(args['setting'], 'r', encoding='utf-8') as file:
        setting = json.load(file)['encoder']

    if 'hyper_params' not in setting.keys():
        print(f"{command_name}: [error] Hyper-param settings are needed to complete the process. ")
        sys.exit()
    
    n_jobs = int(setting['n_jobs']) if 'n_jobs' in setting.keys() else -1
    encoder = BatchZcurveEncoder(hyper_params=setting['hyper_params'], n_jobs=n_jobs)

    # run coding process
    output_file = args['output']
    result = encoder.dump(records, output_file)
    used_time = time.time() - start_time

    if result:
        print(f"{command_name}: Successfully encoded {count} sequences in {round(used_time, 3)} s")
    else: 
        print(f"{command_name}: Unable to open {output_file}")
