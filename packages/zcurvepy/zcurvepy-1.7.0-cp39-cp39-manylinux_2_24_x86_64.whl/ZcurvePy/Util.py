from ZcurvePy import __version__
f"""
    This is the util module of ZcurvePy

    We are happy to see that the APIs provided here are also
    useful for your project, so you can just use it in your
    Python scripts.

    Authors:    Zetong Zhang, Feng Gao
    Version:    { __version__ }
    Copyright:  Copyright 2025 TUBIC
    License:    MIT License
    Date:       2025-02-26
"""
import io
import os
import sys
from Bio.SeqIO import parse, read, write
from Bio.SeqRecord import SeqRecord
from Bio import Entrez
from _ZcurvePy import find_island, get_orfs

Entrez.email = "flypigaround@163.com"
Entrez.api_key = "24a9ecda42217cd6d8f24058a4d6df456c09"

# where the downloaded files saved
CACHE_PATH = "ncbi_cache"

def download_acc(acc, command_name=__name__, form='fasta'):
    """
    Download genome files as genbank from NCBI database
    by accession using ncbi-acc-download

    Args:
        acc (str):          comma-splited accesions (or a
                            text files stores accessions)
        command_name (str): the name of command. If the
                            script is not called by console
                            commands, it is set as the name
                            of the module defaultly. 
        form (str):         the format of to-download files
    Returns:
        ready (list):       The save paths of the files 
                            downloaded and are ready to use.
    """
    to_download, ready = None, []

    if not os.path.exists(CACHE_PATH):
        os.mkdir(CACHE_PATH)
    
    if acc.endswith(".txt"):
        file = open(acc, 'r')
        to_download = file.readlines()
        file.close()
    else:
        to_download = acc.split(',')
    
    for item in to_download:
        item = item.strip()

        if len(item) == 0:
            continue
            
        file_name = item + ('.fa' if form == 'fasta' else '.gbk')
        save_path = os.path.join(CACHE_PATH, file_name)

        if not os.path.exists(save_path):
            try:
                handle = Entrez.efetch(
                    db="nucleotide",
                    id=item,
                    rettype=form,
                    retmode="text")
                record = read(handle, form)
                handle.close()
                write(record, save_path, form)
            except Exception as e:
                print(f"{command_name}:{e}")
                sys.exit(0)

        ready.append(save_path)
    return ready

def extract_CDS(genome):
    """
    Extract all the CDSs sequence from annotated genome files.
    Usually a GenBank file.

    Args:
        genome (str):   path to the genome file
    
    Returns:
        CDSs (list):    a list of CDS records
    """
    CDSs, records = [], parse(genome, "genbank")

    for record in records:
        for feature in record.features:
            if feature.type == "CDS":
                name = feature.qualifiers['locus_tag'][0]
                CDS_seq = feature.extract(record.seq)
                CDS_record = SeqRecord(CDS_seq, id=name)
                CDSs.append(CDS_record)
    
    return CDSs


def has_gui():
    """
    Check whether the current system has GUI

    Returns:
        bool: whether the current system has GUI
    """
    # Linux
    if sys.platform.startswith('linux'):
        if not os.environ.get('DISPLAY'):
            return False
        try:
            import tkinter as tk
            root = tk.Tk()
            root.withdraw()
            root.update()
            root.destroy()
            return True
        except Exception:
            return False
    # Windows
    elif sys.platform == 'win32':
        try:
            import tkinter as tk
            tk.Tk().withdraw()
            return True
        except Exception:
            try:
                from ctypes import windll
                return windll.user32.GetSystemMetrics(0) != 0
            except Exception:
                return False
    # Unsupported OS
    else:
        return False

def countFasta(fasta_file: str):
    """
    Count the number of sequences in the FASTA file

    Args:
        fasta_file (str): The path to the FASTA file
    
    Returns:
        int: The number of sequences
    """
    count = 0
    with open(fasta_file, "r") as handle:
        while True:
            line = handle.readline()
            if not line:
                break
            elif len(line) > 0 and line[0] == ">":
                count += 1
    return count
