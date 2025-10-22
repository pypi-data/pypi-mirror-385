
""" This is the main program of Z-curve Plotter (3D) """
import numpy as np
import pkg_resources
import json
import sys
import argparse
from Bio import SeqIO
from ZcurvePy import __version__
from ZcurvePy.Util import download_acc, has_gui
import matplotlib
HAS_GUI = has_gui()
matplotlib.use("TkAgg" if HAS_GUI else "Agg")
from matplotlib import pyplot as plt
from operator import methodcaller
from _ZcurvePy import ZcurvePlotter

# curve names
names = {
    "RY" : "RY disparity",
    "MK" : "MK disparity",
    "WS" : "WS disparity",
    "AT" : "AT disparity",
    "GC" : "GC disparity",
    "XP" : "x' curve",
    "YP" : "y' curve",
    "ZP" : "z' curve",
    "AP" : "AT' curve",
    "GP" : "GC' curve",
    "CG" : "CpG' curve",
}

prog_infor = \
f"""
Z-curve Plotter -- A program to plot visual Z-curves

Authors:    Zhang Zetong, Gao Feng
Version:    {__version__}
Contact:    fgao@tju.edu.cn
Copyright:  Bioinformatic Center, Tianjin University, China
"""

epilog_infor = \
"""
The content of setting file should be like:

{
    "plotter": [
        {   // The first sequence
            "start": 1000,         // Plotting start point (index starts from 0)
            "stop": 30000,         // Plotting stop point (index starts from 0)
            "comp": false,         // Plot reverse complement
            "window": 100,         // Mean smoothing window
            "intv": 10,            // Sampling interval
            "curve2d": "RY,MK",    // 2D-curves type
            "curve3d": "RY:MK:ZP"  // 3D-curve types
        }
        {   // The second sequence
            "start": 500,
            "stop": 40000,
            "comp": true,
            "window": 100,
            "intv": 5,
            "curve2d": "XP,YP,ZP"
        },
        // ...
    ]
}

The valid curve type codes and their names are listed below:

"""

for index, (key, value) in enumerate(names.items()):
    epilog_infor += f"({index + 1})\t{key} - {value}\n"

epilog_infor += \
"""

Note: 1. If any of the param is not existing, the programs will use defaults.
      2. When the 'stop' value is larger than 'start' value, the program
         will default the topology property of the sequence to ring and go on.
      3. 'intv' only effects the sampling interval when plotting visual curves.

Tips: Use the Z-curve method more flexibly through our ZcurvePy's APIs! 
"""

arg_fasta = "    input genome files as FASTA format (*.fa; *.fasta; *.fna)"
arg_gbk   = "    input genome files as GenBank format (*.gb; *.genbank; *.gbk; *.gbff)"
arg_acc   = "    input NCBI accession number (comma-splited; *.txt)"
arg_set   = "    external setting file as JSON format (*.json)"
arg_out   = "    output data file of all curves as JSON (*.json)"
arg_png   = "    output graphic file as PNG picture (*.png)"
arg_show  = "    show graphic user interface or not (default: False)"

# curve types
types = {
    "RY"  : "RY_disparity",
    "MK"  : "MK_disparity",
    "WS"  : "WS_disparity",
    "AT"  : "AT_disparity",
    "GC"  : "GC_disparity",
    "XP"  : "x_prime_curve",
    "YP"  : "y_prime_curve",
    "ZP"  : "z_prime_curve",
    "AP"  : "AT_prime_curve",
    "GP"  : "GC_prime_curve",
    "CG"  : "CpG_prime_curve"
}

def checkInputs(args: dict, command_name: str):
    records, fasta, genbank, acc = [], args['fasta'], args['genbank'], args['accession']

    try:
        # read fastas
        if fasta is not None:
            single_fastas = fasta.split(',')
            for single_fasta in single_fastas:
                records += list(SeqIO.parse(single_fasta, "fasta"))
        
        # read local or downloaded genbanks
        if genbank is not None:
            single_genbanks = genbank.split(',')
            for single_genbank in single_genbanks:
                records += list(SeqIO.parse(single_genbank, "genbank"))

        # read download files
        if acc is not None:
            downloads = download_acc(acc, command_name)
            for download in downloads:
                records += list(SeqIO.parse(download, "fasta"))
    except Exception as exception:
        print(f"Biopython: [error] failed to read input files! ")
        print(exception)
        sys.exit()

    num_records = len(records)
    
    if num_records == 0:
        print(f"{command_name}: [error] no input files was found!")
        sys.exit()
    else:
        print(f"{command_name}: [infor] detected {num_records} sequences. ")
    
    return records


def handleInputs3D(
    records: list, 
    args: dict, 
    command_name: str,
):
    with open(args['settings'], 'r', encoding='utf-8') as file:
        settings = json.load(file)['plotter']
    num_settings, curve_list = len(settings), []

    for i, record in enumerate(records):
        if i < num_settings:
            setting = settings[i]

            start, stop = 0, len(record)
            if 'start' in setting.keys():
                start = int(setting['start'])
            if 'stop' in setting.keys():
                stop = int(setting['stop'])
            
            if start > stop:
                record = record[start:] + record[:stop]
            elif start < stop:
                record = record[start:stop]
            else:
                print(f"{command_name}: [error] The slice length of {record.id} is zero!")
                sys.exit()

            if "comp" in setting.keys() and setting['comp']:
                record = record.reverse_complement()
            
            intv = int(setting['intv'] if "intv" in setting.keys() 
                       else max(len(record)/ 1E7, 1))
            curve_types = ['RY', 'MK', 'WS']

            if "curve3d" in setting.keys():
                curve_types = setting['curve3d'].split(":")
                if len(curve_types) != 3:
                    print(f"{command_name}: [error] The number of componets must be 3 in 3D-mode!")
                    sys.exit()
            else:
                print(f"{command_name}: [error] No valid settings found for 3D-mode !")
                sys.exit()
            
            curves = []
            plotter = ZcurvePlotter(record)

            for typ in curve_types:
                if typ not in types.keys():
                    print(f"{command_name}: [error] Invalid curve type {typ}")
                    sys.exit()
                window = int(setting['window']) if 'window' in setting.keys() else 0
                retrs = methodcaller(types[typ], window=window, return_n=False)(plotter)
                yvalues = retrs[0] if isinstance(retrs, tuple) else retrs
                curves.append(np.array(yvalues))
                
            curve_list.append((record.id, curves, intv))
    
    return curve_list
        

def visualize3D(curve_list: list, png: str, show: bool):
    plt.rc('font', family='Times New Roman')
    plt.rcParams.update({"font.size": 14})
    fig = plt.figure(figsize=(10,6))

    ax = fig.add_subplot(projection='3d')
    ax.set_title('Z-curve')

    for item in curve_list:
        label, (x, y, z), intv = item
        ax.plot(x[::intv], y[::intv], z[::intv], label=label)
        
    ax.set_xlabel("X Axis", labelpad=10)
    ax.set_ylabel("Y Axis", labelpad=10)
    ax.set_zlabel("Z Axis", labelpad=10)
    ax.legend()
    
    if png is not None:
        fig.savefig(png)
    if show and HAS_GUI:
        try:
            manager = plt.get_current_fig_manager()
            fig.canvas.manager.set_window_title("Z-curve Plotter (Powered by Matplotlib)")
            res_path = pkg_resources.resource_filename("ZcurvePy", "assets/image/icon.ico")
            manager.window.iconbitmap(res_path)
            plt.show()
        except Exception as exception:
            print("zcurve-plotter-3d: [error] unable to create GUI! ")
            print(exception)


def main():
    command_name = 'zcurve-plotter-3d'

    parser = argparse.ArgumentParser(
        prog=command_name,
        description=prog_infor,
        formatter_class=argparse.RawTextHelpFormatter,
        epilog=epilog_infor
    )

    parser.add_argument('-f', '--fasta', metavar='\b', required=False, type=str, help=arg_fasta)
    parser.add_argument('-g', '--genbank', metavar='\b', required=False, type=str, help=arg_gbk)
    parser.add_argument('-a', '--accession', metavar='\b', required=False, type=str, help=arg_acc)
    parser.add_argument('-s', '--settings', metavar='\b', required=True, type=str, help=arg_set)
    parser.add_argument('-o', "--output", metavar='\b', required=False, default=None, type=str, help=arg_out)
    parser.add_argument('-p', "--png", metavar='\b', required=False, type=str, default=None, help=arg_show)
    parser.add_argument('-v', "--show", metavar='\b', required=False, type=bool, default=True, help=arg_show)

    args = vars(parser.parse_args())

    records = checkInputs(args, command_name)
    curve_list = handleInputs3D(records, args, command_name)

    png, show = args['png'], args['show']
    if png is not None or show:
        visualize3D(curve_list, png, show)
    
    output = args['output']
    if output is not None:
        contents = []
        for curve in curve_list:
            name, (x, y, z), _ = curve
            contents.append({name: {
                'x': np.round(x, decimals=2).tolist(), 
                'y': np.round(y, decimals=2).tolist(), 
                'z': np.round(z, decimals=2).tolist()
            }})
        to_save = json.dumps(contents)
        with open(output, "w") as file:
            file.write(to_save)
