import click
import debugpy
import expview.mylogs as mylogs
import glob
import json
from pathlib import Path
import os
import itertools
import os.path as op
import logging
from expview.utils import * 
# from deepdiff import DeepDiff #TODO
logger = logging.getLogger(__name__)
import pandas as pd


def sync_cols_with_df(df, main_cols=None, base_cols=None, path="cols.json"):
    """
    Synchronize cols.json with the DataFrame and main/base columns.
    Ensures all DataFrame columns are reflected in cols.json,
    while preserving order and avoiding duplication.
    """
    import os, json
    import pandas as pd

    # Helper: preserve order, remove duplicates
    def unique_preserve_order(seq):
        seen = set()
        result = []
        for x in seq:
            if x not in seen:
                seen.add(x)
                result.append(x)
        return result

    # Defaults
    main_cols = list(main_cols or [])
    base_cols = list(base_cols or ["expid", "output_dir", "trial", "label"])

    # Auto-resolve path relative to this script
    if path is None:
        base_dir = os.path.dirname(os.path.abspath(__file__))
        path = os.path.join(base_dir, "cols.json")

    df_cols = list(df.columns)

    # Load existing config or initialize
    if os.path.exists(path):
        with open(path) as f:
            cols = json.load(f)
    else:
        cols = {}

    # Ensure all expected list keys exist
    def ensure_list(key):
        if key not in cols or not isinstance(cols[key], list):
            cols[key] = []
    for k in [
        "exp_cols_sum", "sel_cols", "ex_cols", "dim_cols",
        "measure_cols", "rep_cols", "ee", "extra_cols",
        "info_cols", "index_cols", "score_cols"
    ]:
        ensure_list(k)

    # --- Core columns ---
    df_cols_set = set(df_cols)
    base_cols_set = set(base_cols)
    main_cols_set = set(main_cols)
    all_cols = df_cols_set | base_cols_set | main_cols_set

    # Compute "other" columns (not main/base)
    other_cols = [c for c in df_cols if c not in base_cols_set and c not in main_cols_set]

    # --- Smart defaults ---
    if "accuracy" in all_cols and "accuracy" not in cols["score_cols"]:
        cols["score_cols"].append("accuracy")

    # --- Merge updates (preserve order, avoid duplicates) ---
    cols["sel_cols"] = unique_preserve_order(
            cols["sel_cols"] + ["expid"] + main_cols + other_cols)
    cols["rep_cols"] = unique_preserve_order(cols["rep_cols"] + main_cols + base_cols)
    cols["extra_cols"] = unique_preserve_order(cols["extra_cols"] + other_cols)

    # --- Pick initial column ---
    if not cols.get("init_col") or cols["init_col"] not in all_cols:
        cols["init_col"] = next(iter(main_cols), "")

    # --- Identify numeric measures ---
    #num_cols = [c for c in df_cols if pd.api.types.is_numeric_dtype(df[c])]
    #cols["measure_cols"] = unique_preserve_order(cols["measure_cols"] + num_cols)

    # --- Save updated configuration ---
    with open(path, "w") as f:
        json.dump(cols, f, indent=2, ensure_ascii=False)

    return cols

def map_param(param_map, x, key=False):
    k, v = x, ""
    if "=" in x:
        k, v = x.split("=")
    k = k.strip("--")
    pre = ""
    if k.startswith("@"):
        k = k.strip("@")
    pre += "@"
    if k.startswith("^"):
        k = k.strip("^")
        pre += "^"
    vm = v
    if v.startswith("/") or v.startswith("@"):
        first_char = v[0]  # Store the first character
        key = v[1:]  # Remove the first character
        vm = param_map["/" + key]  # Lookup value in param_map
        vm = first_char.join(vm.split("/"))  # Split and rejoin with '@'

    m = param_map[k] if k in param_map else k
    if key is True or not v: 
        return m
    else:
        return pre + m + "=" + vm 

@click.group()
def cli():
    pass

def experiment(func=None):
    if func is None:
        # used as @experiment()
        return lambda f: experiment(f)

    @cli.command(context_settings=dict(
                ignore_unknown_options=True,
                allow_extra_args=True,))

    @click.argument('cfg_pat')
    @click.option(
        "--experiment",
        "-exp",
        default="exp",
        type=str,
        help="Experiment name"
    )
    @click.option(
        "--exp_folder",
        "-e",
        "-to",
        default="all",
        type=str,
        help="The name of a new directory for experiment when loading an existing config file"
    )
    @click.option(
        "--exp_conf",
        "-cfg",
        default="",
        type=str,
        help="A file containing configs"
    )
    @click.option(
        "--break_point",
        "-bp",
        default="",
        type=str,
        help="Stop on breakpoints equal to the value"
    )
    @click.option(
        "--preview",
        "-pv",
        type=str,
        help="Show only experiment configuraton or some data"
    )
    @click.option(
        "--exp_vars",
        "-ev",
        type=str,
        default="",
        help="The name of experiment multi-valued variables for which you want to check the difference of their values, if not given it runs all combinations"
    )
    @click.option(
        "--main_vars",
        "-mv",
        type=str,
        default="",
        help="The name of one multi-valued variable for which you want to check the difference of their values, if not given it runs all combinations e.g. var1@var2@var3"
    )
    @click.option(
        "--log_var",
        "-lv",
        type=str,
        default="",
        help="The name of an experiment multi-valued variables for which you want to log some data in a logfile names varied with the different values of the varibale"
    )
    @click.option(
        "--last_var",
        "-last",
        type=str,
        default="",
        help="The name of multi-valued variable you want to be the most nesting loop in combination of expeiments."
    )
    @click.option(
        "--debug",
        "-d",
        default="",
        type=str,
        help="Enable debugpy, you can specify a breakpoint too"
    )
    @click.option(
        "--trial",
        "-t",
        default="1",
        type=str,
        help="You can set it for repeating experiments with different identities"
    )
    @click.option(
        "--version",
        "-v",
        default="1",
        type=str,
        help="You can set it for continueing experiments with different versions (after some changes)"
    )
    @click.option(
        "--skip",
        "-skip",
        is_flag=True,
        help="Skip existing experiments"
    )
    @click.option(
        "--save_conf",
        "-conf",
        default="",
        type=str,
        help="Save config for using later"
    )
    @click.option(
        "--rem",
        "-rem",
        is_flag=True,
        help="Remove the existing experiment folder"
    )
    @click.option(
        "--label",
        "-l",
        default="",
        type=str,
        help="label for experiment"
    )
    @click.option(
        "--repeat",
        "-rep",
        is_flag=True,
        help="Repeat an experiment even if the folder already exists",
    )
    @click.option(
        "--deep_check",
        "-dc",
        is_flag=True,
        help="Check complete json confiturations for checking existing exps"
    )
    @click.option(
        "--merge",
        "-merge",
        default="",
        type=str,
        help="Merge experiments in one folder"
    )
    @click.option(
        "--copy_prev_exp",
        "-cp",
        is_flag=True,
        help="Don't copy the experiment of the source config to new experiment"
    )
    @click.option(
        "--reval",
        "-reval",
        is_flag=True,
        help="Evaluation without training"
    )
    @click.option(
        "--test",
        "-test",
        is_flag=True,
        help="Evaluation without training"
    )
    @click.option(
        "--use_wandb",
        "-uw",
        is_flag=True,
        help="Evaluation without training"
    )
    @click.option(
        "--download_model",
        "-mod",
        is_flag=True,
        help="Whether download pretrained model or load it from a directory"
    )
    @click.option(
        "--max_exp",
        "-max",
        default=0,
        type=int,
        help="Max number of experiments to do (0 means all)"
    )
    @click.option(
        "--inc_run_id",
        "-new",
        "-inc",
        is_flag=True,
        help="Whether to increase run id or use the last run id"
    )
    @click.option(
        "--copy_to",
        "-copy",
        default="",
        type=str,
        help="The name of directory to copy done experiments."
    )
    @click.option(
        "--inp_log_path",
        "-lp",
        default="logs",
        type=str,
        help="The directory to save all experiments"
    )
    @click.pass_context
    def run(ctx, cfg_pat, experiment, exp_folder, exp_conf, break_point, preview, exp_vars, 
            log_var, last_var, main_vars, 
            debug, version, trial, skip, save_conf, rem, repeat, 
            label, deep_check, merge, copy_prev_exp, 
            reval, test, use_wandb, download_model, max_exp, 
            inc_run_id, copy_to, inp_log_path):
       if debug:
           port = "1234"
           if not break_point: break_point = debug
           debugpy.listen(('0.0.0.0', int(port)))
           print("Waiting for client at run...port:", port)
           debugpy.wait_for_client()  # blocks execution until client is attached
       if break_point:
           mylogs.setbp(break_point)
       if inc_run_id:
           mylogs.get_run_id(increase = True)
       exclude_list = []
       exp_args = {}
       save_path = ""
       prev_exp_folder = ""
       prev_save_path = ""
       log_path = inp_log_path
       if not log_path.startswith("/"):
           log_path = os.path.join(mylogs.logPath, log_path)
       if exp_conf or cfg_pat:
            print("Experiment pattern:", cfg_pat)
            cur_path = os.getcwd()
            print("Cur path:", cur_path)
            confs = glob.glob(f"*{cfg_pat}*")
            print("Experiment matched confs:", confs)
            if not exp_conf and confs:
                exp_conf = confs[0]
            print("Experiment config:", exp_conf)
            try:
                with open(exp_conf) as f:
                    exp_args = json.load(f)
            except FileNotFoundError as e:
                print(e)
                raise ValueError( f"Looking for *{cfg_pat}* {confs} were matched: " + exp_conf)
            prev_exp_folder = exp_args["load_model_dir"] if "load_model_dir" in exp_args else ""
            prev_save_path = exp_args.get("save_path","")
            copy_prev_exp = copy_prev_exp or exp_args.get("copy_prev_exp", False)
            exp_conf_name = Path(exp_conf).stem
            exp_args["conf"] = exp_conf_name
            _expid = str(exp_args["expid"]).split("-")[-1] if "expid" in exp_args else "0"
            exp_args["trial"] = str(trial) + "-ret-" + _expid 
            if experiment == "exp":
                experiment = _expid + "_" + mylogs.now 
            if test:
                exp_args["do_train"] = False
                exp_args["do_test"] = True 
            if reval:
                exp_args["load_model_dir"] = prev_exp_folder 
                exp_args["do_train"] = False
                exp_args["do_test"] = True 
                exp_args["reval"] = True
                exp_args["trial"] = str(trial) + "-rev-" + str(exp_args["expid"].split("-")[-1])

       mylogs.bp("start")
       experiment = experiment.replace("#","-").replace("@","-").replace(":","-")
       if exp_conf and "experiment" in exp_args:
           cc = 1
           exp_name = experiment
           while exp_name == exp_args["experiment"]:
               exp_name = experiment + "-" + str(cc)
               cc += 1
           experiment = exp_name

       #if exp_conf and not exp_folder: 
       #   log_folder = experiment 
          #ans = input("Do you want save the results in (otherwise enter new folder) "+log_folder+ "[yes]:")
          #if ans and ans != "yes":
          #    exp_folder = ans
          #else:
       #   exp_folder = log_folder 

       mylogs.bp("start") 
       if experiment == "self":
           save_path = os.path.join(os.getcwd(), "output")
       #if prev_exp_folder and not exp_folder:
       #    save_path = prev_save_path
       elif not reval or exp_folder:
           if exp_folder and save_path:
              relative_path = os.path.relpath(save_path, log_path)
              parts = relative_path.split(os.path.sep)
              parts[0] = exp_folder 
              new_path =  os.path.sep.join(parts)
              save_path = os.path.join(mylogs.resPath, new_path) 
              # save_path = os.path.join(str(Path(save_path).parent), experiment)
           elif exp_folder:
              save_path = os.path.join(log_path, exp_folder)
           else:
              save_path = os.path.join(log_path, experiment)
           if Path(save_path).exists():
              #if not rem:
              #     while Path(save_path).exists():
              #        ans = "u" #input("Do you want to delete '" + save_path + \
              #                  #"'? d)delete u)use  newname)")
              #        if ans == "d": 
              #            rem = True
              #        elif ans == "u":
              #            break
              #        else:
              #            experiment = ans
              #            save_path = os.path.join(log_path, experiment)
              if rem:
                   main_folder = save_path
                   ans = "yes" #input("Do you want to remove " + main_folder + ":")
                   if ans == "yes":
                       main_folder = main_folder.rstrip("/")
                       dirs = glob.glob(main_folder + '/*/')
                       for d in dirs:
                            shutil.rmtree(d)

           if Path(save_path).is_file():
               os.remove(save_path)

       if not save_path:
           save_path = prev_save_path if prev_save_path else os.getcwd()
       Path(save_path).mkdir(exist_ok=True, parents=True)
       if copy_to:
          copy_to = os.path.join(log_path, copy_to)
          Path(copy_to).mkdir(exist_ok=True, parents=True)

       args = {}
       args["conf"] = exp_conf
       args["save_path"] = save_path

       args["exp_folder"] = exp_folder
       args["copy_prev_exp"] = copy_prev_exp
       args["load_path"] = "" 
       args["label"] = label
       args["is_debug"] = debug
       if not reval:
          args["trial"] = trial
       if not download_model:
          args["load_path"] = mylogs.pretPath 
       if not experiment.startswith("%"):
           experiment = "%" + experiment # % forces to reserve the value as it is  
       args["experiment"] = experiment 
       args["version"] = version 
       args["break_point"] = break_point 
       args["preview"] = preview 
       args["repeat"] = repeat 
       args["reval"] = reval 
       use_wandb = True #TODO: Get rid of it
       args["use_wandb"] = use_wandb 
       tags = exp_args["tag"] if "tag" in exp_args else ["expid"] 
       full_tags = exp_args["full_tag"] if "full_tag" in exp_args else ["expid"] 

       mylogs.bp("start")
       _dir = Path(__file__).parent
       param_map = {}
       param_file = os.path.join("", "params.json")
       if Path(param_file).is_file():
           with open(param_file) as f:
              param_map = json.load(f)

       all_vars = []
       for x in ctx.args:
           if x.startswith("--"):
              _xx = x.strip("--")
              if not "--" in _xx:
                  all_vars.append(map_param(param_map,x,key=False))
              else:
                  x1, x2 = _xx.split("--")
                  all_vars.append(map_param(param_map,x1,key=False))
                  all_vars.append(map_param(param_map,"^" + x2,key=False))

       # all_vars = [x.strip("--") for x in ctx.args]
       mylogs.bp("vars")
       var_names = [x.split("=")[0] for x in all_vars] 
              # if not (x.split("=")[0].startswith("@comment") 
              #     or x.split("=")[0].startswith("@c-"))]
       values = []
       for x in all_vars:
           _vv = x.split("=")
           if len(_vv) < 2:
               assert False, "invalid argument " + str(x) + "|" + str(_vv)
           if not (_vv[0].startswith("@comment") or _vv[0].startswith("@c-")):
               _vv = _vv[1].strip("/")
               _vvv = _vv.split("/")
           else:
               _vvv = [_vv[1]]
              #  continue
           values.append(_vvv)

       priority_keys = ['@d_seed']
       var_dict = {k: n for k, n in zip(var_names, values)}
       var_dict = {k: var_dict[k] for k in priority_keys if k in var_dict} | {k: v for k, v in var_dict.items() if k not in priority_keys}

       if last_var:
           last_var = map_param(param_map, last_var)
           last_var = "@" + last_var
           var_dict[last_var] = var_dict.pop(last_var)

       _mvars = []
       mylogs.bp("mvar")
       if main_vars and "--" in main_vars:
           main_vars = main_vars.split("--")
       if not main_vars:
           main_vars = [vv.strip("@") for vv in var_names if vv.endswith("@")]
       if not main_vars:
           main_vars = []
           for x in ctx.args:
               if x.startswith("--"):
                  _xx = x.strip("--")
                  if not "--" in _xx:
                      main_vars.append(map_param(param_map,x,key=True))
                  else:
                      x1, x2 = _xx.split("--")
                      main_vars.append(map_param(param_map,x1,key=True))
                      main_vars.append(map_param(param_map,"^" + x2,key=True))
                      
       for var in main_vars:
           if not var: continue
           var = map_param(param_map, var)
           if "=" in var:
               var_name = var.split("=")[0].strip("@")
               if False: #TODO temporary 
                   assert var_name in exp_args, var_name +" must be in experiment variables (config)"
               var_item = var.split("=")[1]
               if not var_name.startswith("comment") or var_name.startswith("c"):
                   var_item = var_item.strip("/").split("/")
               var_dict["@" + var_name] = var_item
               _mvars.append(var_name)
           else:
               _mvars.append(var)
       if _mvars: main_vars = _mvars

       
       mylogs.bp("prev")
       if prev_exp_folder and not "prompts_prefix" in main_vars:
           args["prompt_encoders_dir"] = prev_exp_folder
       if prev_exp_folder and not "task_name" in main_vars and copy_prev_exp and not repeat:
           prev_folder = Path(prev_exp_folder)
           prev_exp_id = prev_folder.name
           eval_folders = glob.glob(
                   os.path.join(prev_folder.parent, "Eval-" + prev_exp_id + "**"))
           try:
               shutil.copytree(prev_exp_folder, 
                       os.path.join(save_path, Path(prev_exp_folder).name))
           except (FileNotFoundError, FileExistsError):
               pass
           for folder in eval_folders:
               try:
                   shutil.copytree(folder, os.path.join(save_path, Path(folder).name))
               except (FileNotFoundError, FileExistsError):
                   pass


       for key,value in var_dict.items():
           extra = []
           for val in value:
               if "multi-" in val or "multir-" in val:
                   first = []
                   second = []
                   use_second = False
                   for m in value:
                       if m == val:
                           use_second = True
                           continue
                       var = map_param(param_map, "/" + m)
                       var = [x for x in var.split("/") if x]
                       if use_second:
                           second.extend(var)
                       else:
                           first.extend(var)
                   _, l = val.split("-")
                   l = len(second) if l == "all" else int(l)
                   if "multir" in val:
                       comb = all_nonempty_subsets_upto_l(second, l)
                   else:
                       comb = itertools.combinations(second, l)
                   comb = [c for c in comb]
                   if first:
                       comb = itertools.product(first, comb)
                       result = ['@'.join((x, *ys)) for x, ys in comb]
                   else:
                       result = ['@'.join(x) for x in comb]
                   extra.extend(result)
           if extra:
              var_dict[key] = extra
       var_names = list(var_dict.keys())
       values = list(var_dict.values())
       inp_exp_vars = exp_vars
       mylogs.bp("start")
       mylogs.bp("mvar")
           # main_vars = "--".join([x.strip("@") for x in main_vars])

       if not exp_vars:
           #if main_vars:
           #    exp_vars = main_vars
           #else:
           exp_vars = [vv.strip("@") for vv in var_names if vv.startswith("@")]
       elif type(exp_vars) != list:
           exp_vars = inp_exp_vars = [exp_vars]
       full_tags.extend([x for x in exp_vars if not "^" in x])
       args["log_var"] = log_var 
       for ii, (vv, cc) in enumerate(zip(var_names, values)):
          if len(cc) > 1:
               if vv.startswith("@") or vv.endswith("@"):
                   vv = vv.strip("@")
                   tags.append(vv.strip("^"))
               full_tags.append(vv.strip("^"))
               values[ii] = [x for x in cc if not x.startswith("!")] 
               #if (exp_vars and not vv in exp_vars) or (main_vars and not vv in main_vars):
               #    values[ii] = [values[ii][0]] # ignore the rest of values for this item 
          if len(values[ii]) == 1:
               if not vv.startswith("@"):
                   exclude_list.append(vv)
               vv = vv.strip("@")
       var_names = [vv.strip("@") for vv in var_names]

       full_tags = list(set(full_tags))
       mylogs.bp("full_tags")
       for pv in inp_exp_vars:
           assert pv in full_tags, f"Eror: {pv} must be 'all' or one of {full_tags} which have multiple values"

       existing_exps = glob.glob(op.join(save_path, "*.json"))
       not_conf = ["break_point","copy","expid", "total_exp", "full_tag", "tag", "preview", "output_dir", "experiment", "use_cache_file", "use_cache", "trial", "exp_number", "num_target_prompts", "prompt_masking", "per_device_train_batch_size","comment"] + [v for v in var_names if v.startswith("comment") or v.startswith("c-")]
       # args["full_tag"] = full_tags 
       tot_comb = [dict(zip(var_names, comb)) for comb in itertools.product(*values)]
       ii = len(existing_exps) if not reval else 0 
       kk = 0
       exps_done = 0
       orig_args = args.copy()
       total = len(tot_comb)
       args["total_exp"] = total
       logger.info("Total experiments:%s", total)
       mylogs.bp("comb")
       old_comb = None
       ctags = []
       if False: #TODO check values changed among two combination
           for comb in tot_comb:
               if old_comb is not None:
                   diff_comb = DeepDiff(comb, old_comb) 
                   if "values_changed" in diff_comb:
                       vc = diff_comb["values_changed"]
                       for item in vc:
                           val = item.replace("root['","").replace("']","")
                           if not val in ctags:
                               ctags.append(val)
               old_comb = comb.copy()

       args["tag"] = ctags 
       mylogs.bp("merge")
       args["merge"] = merge
       args["save_conf"] = save_conf 
       y_labels = []
       exp_number = 1
       if "output_dir" in exp_args:
           exp_output_dir = exp_args["output_dir"]
       else:
           exp_output_dir = "" #current folder

       for counter, comb in enumerate(tot_comb, start=1):
           _output_dir = []
           prev_name = ""
           prev_item = ""
           conflict = "" 
           mvars = {}
           for kk, (var_name,var_item) in enumerate(comb.items()):
               if var_name.startswith("^") and prev_name:
                   prev_vals = values[kk-1]
                   cur_vals = values[kk]
                   assert len(prev_vals) == len(cur_vals), str(prev_vals) + " " + str(cur_vals) + "Pair variables must have same number"
                   pairs = zip(prev_vals, cur_vals)
                   if not (prev_item, var_item) in pairs:
                       conflict = prev_name + ":" + prev_item + " "+ var_name + ":" + var_item
                       break
               var_name = var_name.strip("^")
               args[var_name]=var_item
               if var_name in main_vars:
                   mvars[var_name] = strval(var_item)
               if not var_name in exclude_list:
                   _output_dir.append(var_name + "_" + str(var_item))
               prev_name = var_name
               prev_item = var_item
           if conflict:
               print(f"Dep var observed {conflict} ignored")
               continue
           ii += 1
           mylogs.bp("expid")
           if max_exp > 0 and exps_done > max_exp:
               print(f"Max number of exp reached {max_exp} ")
               return
           ee = mylogs.get_run_id(only_num=True) # + counter
           exp_dir = str(ee)
           mylogs.bp("merge")
           if merge:
               merge = map_param(param_map, merge, key=True)
           if not "expid" in exp_args or merge: 
               if merge:
                   for (nn, vv) in mvars.items():
                       if nn != merge and not nn in not_conf:
                           exp_dir += "_" + nn + "-" + str(vv)
                   # exp_dir = str(hash(exp_dir))
                   h =  str(str2int(exp_dir)) 
                   hash_dir = h[:3] + str(len(exp_dir)) + h[-2:]
                   args["expid"] = hash_dir
               else:
                   args["expid"] = ii 
           elif "-" in str(exp_args["expid"]):
               expid = str(exp_args["expid"]).replace("-rep","")
               expid = expid.strip("-")
               args["expid"] = expid.split("-")[-1] + "." + str(ii)
           else:
               args["expid"] = ii 

           # args["main_vars"] = mvars
           args["cat"] = experiment.split("/")[-1] 
           args = {**exp_args, **args}
           #_output_dir.append(str(args["expid"]))
           output_dir = save_path 
           if exp_conf and not exp_folder:
                output_dir = exp_output_dir 
           if merge:
               ee = args["expid"]
               # ee = mylogs.get_run_id(only_num=True) + counter
               exp_file = args[merge]
               _output_dir = label + "-" + str(ee)
               _output_dir = _output_dir.strip("-")
               output_dir = os.path.join(save_path, _output_dir)
               if glob.glob(op.join(output_dir, f"*{exp_file}{trial}*.tsv")): 
                   if skip is True:
                       print("The experiment already exists, skipping!!")
                       print(exp_dir)
                       print(output_dir)
                       if copy_to:
                          print("Copying to ", copy_to)
                          shutil.copytree(output_dir, 
                               os.path.join(copy_to, Path(output_dir).name))
                       print("-----------------------------------------")
                       continue
                   print("Merging to ", output_dir)
           else:
               # ee = round(float(args["expid"]))
               ee = 1 #mylogs.get_run_id(only_num=True)
               eee = ee
               _output_dir = label + "-" + str(ee) + "_" + str(counter)
               _output_dir = _output_dir.strip("-")
               output_dir = os.path.join(save_path, _output_dir)
               #if Path(output_dir).exists() and not repeat:
               #    mylogs.minfo(f"The folder {output_dir} already exists....")
               #    ans = input("Do you want to skip the experiment?")
               #    if True: #ans == "y":
               #        continue
               if not reval:
                   while Path(output_dir).exists():
                       ee += 1 
                       _output_dir = label + "-" + str(ee) + "_" + str(counter)
                       _output_dir = _output_dir.strip("-")
                       output_dir = os.path.join(save_path, _output_dir)
               #if label:
               #    expid = experiment.split("/")[-1] + "-" + label + "-run_" + str(eee)
               #    expid = expid.strip("-")
               #    args["expid"] = expid
               #else:
               #    # expid = experiment.split("/")[-1] + "-run_" + str(eee)
               #    # expid =  expid.strip("-")
           args["expid"] = _output_dir
           if repeat:
              args["expid"] += "-rep"
           args["output_dir"] = "%" + output_dir 
           if not reval or not "load_model_dir" in exp_args:
               exp_args["load_model_dir"] = output_dir 
               args["load_model_dir"] = output_dir 
           _conf = json.dumps(args, indent=2)
           if preview == "conf":
               print(f"================ {counter + 1}/{total} =====================")
               print(_conf)
               out_conf_file = os.path.join(save_path, "logs", "exp_" + str(ii) + ".json")
               Path(os.path.join(save_path, "logs")).mkdir(exist_ok = True, parents=True)
               with open(out_conf_file,"w") as f:
                   print(_conf, file=f)
               continue
           # break point before running to check arguments (breakpoint must be check)
           mylogs.bp("check")
           tags_dict = mylogs.get_tag(tags, args)
           full_tags_dict = mylogs.get_tag(full_tags, args)
           #title = "@".join(list(tags_dict.values()))
           title =  mylogs.get_tag(tags, args, as_str=True)
           exp_exists = False
           exp_path = os.path.join(save_path, str(args["expid"]))
           Path(exp_path).mkdir(exist_ok=True, parents=True)
           conf_fname = os.path.join(exp_path, "conf.json")
           if not exp_conf and existing_exps:
               for ee in existing_exps:
                   if preview == "ex-why":
                       print("Checking existaince for ", ee)
                   with open(ee) as f:
                       jj = json.load(f)
                       if reval and ee == conf_fname: 
                           args = jj.copy()
                           args["do_train"] = False
                           args["do_test"] = True 
                           args["trial"] = str(jj["trial"]) + "-re"
                           args["reval"] = True
                           break

                       if "output_dir" in jj:
                           output_dir = jj["output_dir"].strip("%")
                           if glob.glob(op.join(output_dir, "*.tsv")):
                               trial = int(jj["trial"]) + 1 if "trial" in jj else 2
                               exp_exists = True
                       are_equal = True
                       for k,v in args.items():
                           if not k in not_conf: 
                               if not k in jj or strval(v) != strval(jj[k]):
                                   are_equal =False
                                   if preview == "ex-why":
                                       print("It's not equal to because ", k, " is ",v, " against ", strval(jj[k]))
                                   break
                   if are_equal:
                      print(ii, " is equal to ", ee)
                   if deep_check:
                      exp_exists = exp_exists and are_equal
                      break
           if preview == "tag":
               print(f"=#============== {ii}/{total} =====================")
               conf_str = json.dumps(full_tags_dict, indent=2)
               print(conf_str)
               if exp_exists:
                   print("=============== DONE ===========")
               with open("logs/exp_" + str(ii) + ".tag","w") as f:
                   print(conf_str, file=f)
               continue
           if exp_exists and not reval:
               args["output_dir"] = "%" + output_dir 
               print("Skipping experiment ", ii, ": The experiment already exists!")
               if not preview and not repeat:
                  continue 
           # preview existing experiments 
           if preview in ["ex","ex-why","exists","run"]: #
               #print(f"========== Experiment {ii} pf {total},  Input Vars: ===============")
               #all_var_str = json.dumps(var_dict, indent=2)
               #print(all_var_str)
               print(f"========== Experiment {ii} pf {total},  Main Vars: ===============")
               main_var_str = json.dumps(mvars, indent=2)
               print(main_var_str)
               print("==================================================================")
               if preview != "run":
                   ans = input("Continue preview? [yes]:")
                   if not ans or ans == "yes":
                       continue
                   else:
                       print("Stop!")
                       return
           done = "na"
           args["exp_number"] = exp_number
           cur_path = os.getcwd()
           df_columns = ["expid", "output_dir", "trial", "label"] + main_vars
           df = pd.DataFrame(columns=df_columns)
           base_vars = {
               "expid": args.get("expid", ""),
               "src_path": cur_path,
               "output_dir": args.get("output_dir", "").strip("%"),
               "trial": args.get("trial", ""),
               "label": args.get("label", ""),
           }
           all_vars = {}
           for k, v in base_vars.items():
               all_vars[k] = str(v)  # ensure values are string or numeric
           for k, v in mvars.items():
               all_vars[k] = str(v)  

           df = pd.concat([df, pd.DataFrame([all_vars])], ignore_index=True)
           main_cols = set(mvars.keys())
           base_cols = set(base_vars.keys())

           exp_number += 1
           if debug:
               func(args, df)
           else:
               try:
                   if preview == "run":
                       ans = input("Run this? [yes/stop/next] [yes]:")
                       if not ans or ans == "yes":
                           done = func(args, mvars, df)
                       elif ans == "stop":
                           print("Stop!")
                           return
                       else:
                           continue
                   else:
                       done = func(args, mvars, df)
                   y_labels.append(args["expid"])
                   if done != "has_conflict" and done != "is_repeated":
                       with open(conf_fname, "w") as f:
                           print(_conf, file=f)
                       exps_done += 1
                   elif preview == "lict":
                       c = input("check for conflicts!")
               except Exception as e:
                   print(f"================ {ii}/{total} =====================")
                   _conf = json.dumps(args, indent=2)
                   print(_conf)
                   raise Exception("An error occured in the experiment")

           sync_cols_with_df(df, main_cols, base_cols) 
           df.to_csv(os.path.join(exp_path, "results.csv"), index=False)
           if preview == "one" or (preview == "data" and done == "data_preview"):
               print("return due preview:", preview, " done:",  done)
               return
    return run

if __name__ == "__main__":
    cli()

