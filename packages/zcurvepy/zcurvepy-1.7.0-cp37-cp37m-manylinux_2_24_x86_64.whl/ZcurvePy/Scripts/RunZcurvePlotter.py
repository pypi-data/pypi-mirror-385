from ZcurvePy.Scripts.RunZcurvePlotter3D import *

def handleInputs2D(
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
                record_id = record.id
                record = record.reverse_complement()
                record.id = record_id
            
            intv = int(setting['intv'] if "intv" in setting.keys() 
                       else max(len(record)/ 1E7, 1))
            curve_types = ['RY', 'MK', 'WS']

            if "curve2d" in setting.keys():
                curve_types = setting['curve2d'].split(",")
            else:
                print(f"{command_name}: [error] No valid settings found for 2D-mode !")
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
                curves.append((yvalues, typ))
                
            curve_list.append((record.id, curves, intv, len(record)))
    
    return curve_list


def visualize2D(curve_list: list, png: str, show: bool):
    plt.rc('font', family='Times New Roman')
    plt.rcParams.update({"font.size": 14})
    fig = plt.figure(figsize=(10, 6))

    ax = fig.add_subplot()
    ax.set_title('Z-curve')

    for item in curve_list:
        name, curves, intv, length = item
        n = np.arange(1, length + 1, intv)
        for y, typ in curves:
            ax.plot(n, y[::intv], label=f"{name} | {names[typ]}")
        
    ax.set_xlabel("n (bp)", labelpad=10)
    ax.set_ylabel("Component", labelpad=10)
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
            print("zcurve-plotter: [error] unable to create GUI! ")
            print(exception)


def main():
    command_name = 'zcurve-plotter'

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
    parser.add_argument('-p', "--png", metavar='\b', required=False, type=str, default=None, help=arg_png)
    parser.add_argument('-v', "--show", metavar='\b', required=False, type=bool, default=True, help=arg_show)

    args = vars(parser.parse_args())

    records = checkInputs(args, command_name)
    curve_list = handleInputs2D(records, args, command_name)

    png, show = args['png'], args['show']
    if png is not None or show:
        visualize2D(curve_list, png, show)
    
    output = args['output']
    if output is not None:
        contents = []
        for item in curve_list:
            name, curves, _, _ = item
            contents.append({name: {typ: np.round(curve, decimals=2).tolist() for curve, typ in curves}})
        to_save = json.dumps(contents)
        with open(output, "w") as file:
            file.write(to_save)