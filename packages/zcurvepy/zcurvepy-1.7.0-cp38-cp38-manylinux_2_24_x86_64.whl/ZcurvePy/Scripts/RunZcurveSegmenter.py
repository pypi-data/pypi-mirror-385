""" This is the main program of Z-curve Segmenter """
# PASS 2025-03-03
import sys
import pkg_resources
from ZcurvePy import ZcurveSegmenter, ZcurvePlotter, __version__
from Bio.SeqIO import parse
from ZcurvePy.Util import download_acc, has_gui
import matplotlib
HAS_GUI = has_gui()
matplotlib.use("TkAgg" if HAS_GUI else "Agg")
from matplotlib import pyplot as plt
from _ZcurvePy import ZcurvePlotter
from operator import methodcaller
import argparse

# program information
prog_infor = \
f"""
Z-curve Segmenter -- A program to segment Z-curves

Authors:    Zhang Zetong, Gao Feng
Version:    {__version__}
Contact:    fgao@tju.edu.cn
Copyright:  Bioinformatic Center, Tianjin University, China
"""

# appendix information
epilog_infor = \
"""
Modes:
(1) GN: segmentation for Genome        (S(P) = a^2 + t^2 + g^2 + c^2)
(2) RY: segmentation for RY-disparity  (S(P) = (a + t)^2 + (g + c)^2)
(3) MK: segmentation for MK-disparity  (S(P) = (a + c)^2 + (g + t)^2)
(4) WS: segmentation for WS-disparity  (S(P) = (a + t)^2 + (g + c)^2)
(5) AT: segmentation for AT-disparity  (S(P) = a^2 + t^2)
(6) GC: segmentation for GC-disparity  (S(P) = g^2 + c^2)
(7) CG: segmentation for CpG-profile   (S(P) = CpG^2 + (1-CpG)^2)

Tips: Use the Z-curve method more flexibly through our ZcurvePy's APIs! 
"""

# help information
arg_fasta = "    input sequence file as FASTA format (*.fa; *.fasta; *.fna)"
arg_gbk   = "    input sequence file as GenBank format (*.gb; *.genbank; *.gbk; *.gbff)"
arg_acc   = "    input sequence file as NCBI accession number (*.txt)"
arg_start = "    start point of the subsequence to be segmented. (Default: 0)"
arg_end   = "    end point of the subsequence to be segmented. (Default: [Sequence Length])"
arg_mode  = "    choose the mode of Z-curve Segmenter based on S(P) (Default: 'GN')"
arg_halt  = "    halting parameter for the segmenting recursion (Default: 100)"
arg_min   = "    the min length between two segmentation point (Default: 3000 bp)"
arg_depth = "    the max depth of the segmenting recursion (Default: 9999)"
arg_out   = "    output segmentation points as comma-splited table (*.csv)"
arg_png   = "    output graphic files as PNG picture (*.png)"
arg_show  = "    show the curve and segmentation points (Default: False)"

# curve types
types = {
    "GN"  : [("RY_disparity", "RY-disparity"), 
             ("MK_disparity", "MK-disparity"), 
             ("z_prime_curve", "z' curve")],
    "RY"  : [("x_prime_curve", "x' curve")],
    "MK"  : [("y_prime_curve", "y' curve")],
    "WS"  : [("z_prime_curve", "z' curve")],
    "AT"  : [("AT_prime_curve", "d'(AT) curve")],
    "GC"  : [("GC_prime_curve", "d'(GC) curve")],
    "CG"  : [("CpG_prime_curve", "CpG-profile")],
}

def handleInputs(
    fasta: str, 
    genbank: str, 
    accession: str, 
    command_name=__name__
):
    """
    Handle inputs from different source
    
    Args:
        fasta (str):        comma-splited paths to fasta files
        genbank (str):      comma-splited paths to genbank files
        accession (str):    comma-splited NCBI accession numbers
        extract (bool):     extract protein genes
        command_name (str): command_name
    """
    record = None
    try:
        if fasta is not None:
            record = next(parse(fasta, "fasta"))
        elif genbank is not None:
            record = next(parse(genbank, "gb"))
        elif accession is not None:
            ready = download_acc(accession, command_name)
            record = next(parse(ready[0], "fasta"))
    except Exception as exception:
        print(f"Biopython: [error] failed to read input files! ")
        print(exception)
    
    if record is not None:
        return record
    else:
        print(f"{command_name}: [error] no valid input was found! ")
        sys.exit(0)


def visualize(
    record,
    mode,
    plot_range,
    seg_points,
    show=False,
    save=None
):
    intv = 10
    plt.rc('font', family='Times New Roman')
    plt.rcParams.update({"font.size": 14})
    plotter = ZcurvePlotter(record)
    fig = plt.figure(figsize=(10, 6))
    ax = fig.add_subplot()
    ax.set_title(f'Mode = {mode}')
    ax.set_xlabel("n (bp)", labelpad=10)
    ax.set_ylabel("Component", labelpad=10)

    for typ, name in types[mode]:
        results = methodcaller(typ, return_n=False)(plotter)
        if "prime" in typ:
            results = results[0]
        ax.plot(plot_range[::intv], results[::intv], label=name)
    for point, _ in seg_points:
        ax.axvline(point, color='red')
    ax.legend()
    if save is not None:
        fig.savefig(save)
    if show and HAS_GUI:
        try:
            manager = plt.get_current_fig_manager()
            fig.canvas.manager.set_window_title("Z-curve Plotter (Powered by Matplotlib)")
            res_path = pkg_resources.resource_filename("ZcurvePy", "assets/image/icon.ico")
            manager.window.iconbitmap(res_path)
            plt.show()
        except Exception as exception:
            print("zcurve-plotter: [error] unable to create GUI! ")
            print(exception)

def main():
    # program name (command name)
    command_name = 'zcurve-segmenter'

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
    parser.add_argument('-s', '--start', metavar='\b', required=False, type=int, default=0, help=arg_start)
    parser.add_argument('-e', '--end', metavar='\b', required=False, type=int, default=-1, help=arg_end)
    parser.add_argument('-m', '--mode', metavar='\b', required=True, type=str, default='GN', help=arg_mode)
    parser.add_argument('-t', '--halting', metavar='\b', required=False, type=float, default=100, help=arg_halt)
    parser.add_argument('-l', '--minlen', metavar='\b', required=False, type=int, default=3000, help=arg_min)
    parser.add_argument('-d', '--maxdepth', metavar='\b', required=False, type=int, default=9999, help=arg_depth)
    parser.add_argument('-o', '--output', metavar='\b', required=True, type=str, help=arg_out)
    parser.add_argument('-p', '--png', metavar='\b', required=False, default=None, type=str, help=arg_png)
    parser.add_argument('-v', '--show', metavar='\b', required=False, type=bool, default=False, help=arg_show)
    args = vars(parser.parse_args())

    record = handleInputs(args['fasta'], args['genbank'], args['accession'])
    length, start, end = len(record), args['start'], args['end']
    end = length if end < 0 else end
    
    mode, halting, minlen, maxdepth = args['mode'], int(args['halting']), int(args['minlen']), args['maxdepth']

    plot_range = list(range(start - length, 0)) + list(range(0, end)) if start > end else list(range(start, end))
    record = record[start:] + record[:end] if start > end else record[start:end]
    
    if mode not in ZcurveSegmenter.func.keys():
        print(f"{command_name}: [error] unknown mode '{mode}'. ")
        sys.exit()
    
    segmenter = ZcurveSegmenter(mode=mode, halting=halting, min_len=minlen, max_depth=maxdepth)
    seg_points = segmenter.run(record)
    real_locs = [[plot_range[i], v] for i, v in seg_points]

    with open(args['output'], "w") as output:
        output.write("No,Seg_Point,dS_Value\n")
        for i, (point, value) in enumerate(real_locs):
            output.write(f"{i + 1},{point},{round(value, 2)}\n")
    
    png, show = args['png'], args['show']

    if png is not None or show:
        visualize(record, mode, plot_range, real_locs, show, png)
    
    print(f"Successfully segmented at {len(seg_points)} points on the genome.")
