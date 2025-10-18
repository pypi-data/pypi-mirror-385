#TODO

table_mid_template = """
    \\begin{{table*}}
        \centering
        \\begin{{tabular}}{{{}}}
        \hline
        {}
        \end{{tabular}}
        \caption{{{}}}
        \label{{{}}}
    \end{{table*}}
    """
table_fp_template = """
    \\begin{{table*}}
        \\begin{{adjustbox}}{{width=1\\textwidth}}
        \\begin{{tabular}}{{{}}}
        \hline
        {}
        \end{{tabular}}
        \caption{{{}}}
        \label{{{}}}
        \end{{adjustbox}}
    \end{{table*}}
    """
table_env_template = """
    \\begin{{table*}}[h!]
        minipage
        \caption{{{}}}
        \label{{{}}}
    \end{{table*}}
    """
table_hm_template = """\\begin{{minipage}}{{.4\\linewidth}}
    \centering
    \label{{{}}}
    \pgfplotstabletypeset[
    color cells={{min={},max={}}},
    col sep=&,	% specify the column separation character
    row sep=\\\\,	% specify the row separation character
    columns/N/.style={{reset styles,string type}},
    /pgfplots/colormap={{whiteblue}}{{rgb255(0cm)=(255,255,255); rgb255(1cm)=(0,200,200)}},
    ]{{{}}}
    \end{{minipage}}"""
def latex_table(rep, rname, mdf, all_exps, sel_col, category, caption=""):
    maxval = {}
    for ii, exp in enumerate(all_exps): 
        exp = exp.replace("_","-")
        exp = _exp = exp.split("-")[0]
        if not sel_col in rep:
            continue
        if not exp in rep[sel_col]:
            continue
        for rel in mdf['prefix'].unique(): 
            if not rel in rep[sel_col][exp]:
                continue
            val = rep[sel_col][exp][rel]
            if type(val) == list:
                assert val, rel + "|"+ sel_col + "|"+ exp
                val = stat.mean(val)
            if not rel in maxval or val > maxval[rel]:
                maxval[rel] = val

    table_cont2=""
    table_cont2 += "method & "
    head2 = "|r|"
    for rel in mdf['prefix'].unique(): 
        table_cont2 += "\\textbf{" + rel + "} &"
        head2 += "r|"
    table_cont2 += " avg. " 
    head2 += "r|"
    table_cont2 = table_cont2.strip("&")
    table_cont2 += "\\\\\n"
    table_cont2 += "\\hline\n"
    for ii, exp in enumerate(all_exps): 
        exp = exp.replace("_","-")
        exp = _exp = exp.split("-")[0]
        if not sel_col in rep:
            continue
        if not exp in rep[sel_col]:
            continue

        table_cont2 += " \hyperref[fig:" + category + _exp + "]{" + _exp + "} &"
        for rel in mdf['prefix'].unique(): 
            if not rel in rep[sel_col][exp]:
                continue
            val = rep[sel_col][exp][rel]
            if type(val) == list:
                val = stat.mean(val)
            if val == maxval[rel]:
                table_cont2 += "\\textcolor{teal}{" +  f" $ {val:.1f} $ " + "} &"
            else:
                table_cont2 += f" $ {val:.1f} $ &"
        if "avg" in rep[sel_col][exp]:
            avg = rep[sel_col][exp]["avg"]
            if type(avg) == list and avg:
                avg = stat.mean(avg)
            if avg:
                avg = "{:.1f}".format(avg)
            table_cont2 += f" $ \\textcolor{{blue}}{{{avg}}} $ &"
        table_cont2 = table_cont2.strip("&")
        table_cont2 += "\\\\\n"
    table_cont2 += "\\hline \n"
    for head, cont in zip([head2],
            [table_cont2]):
        label = "table:" + rname + sel_col.replace("_","-") 
        capt = caption
        if not capt:
           capt = category + " \hyperref[table:show]{ Main Table } | " + label
        table = """
            \\begin{{table*}}[h!]
                \centering
                \\begin{{tabular}}{{{}}}
                \hline
                {}
                \end{{tabular}}
                \caption{{{}}}
                \label{{{}}}
            \end{{table*}}
            """
        table = table.format(head, cont, capt, label)
    return table

def create_latex(df, sel_cols)
    _dir = Path(__file__).parent
    doc_dir = "/home/ahmad/logs" #os.getcwd() 
    table_dir = "/home/ahmad/Documents/Papers/Applied_Int_paper/tables" #os.getcwd() 
    if len(score_cols) > 1:
        # m_report = f"{_dir}/report_templates/report_colored_template.tex"
        m_report = f"{_dir}/report_templates/report_template.tex"
    else:
        m_report = f"{_dir}/report_templates/report_template.tex"
    with open(m_report, "r") as f:
        report = f.read()
    #with open(os.path.join(doc_dir, "report.tex"), "w") as f:
    #    f.write("")
    backit(df, sel_cols)

    exprs, _ = get_sel_rows(df, from_main=False) 
    cond = False
    for exp in exprs:
        cond = cond | (group_df["eid"] == exp) 
    bdf = group_df[cond]
    pdf = summarize(bdf, score_col=score_col, rename=False, pcols=[])
    pdf.reset_index(drop=True)
    dfs = []
    if not selected_cols:
        selected_cols = ["model_base","model_temp","template"]
    for score_col in ["rouge_score","bert_score","bleu_score"]:
        sid = score_col[0:2] + "-"
        cols = [col for col in pdf.columns if col.startswith(sid)]
        tdf = pdf[selected_cols + cols]
        tdf.columns = [col.replace(sid, "") for col in tdf.columns]
        tdf["metric"] = score_col
        dfs.append(tdf)
    df = tdf = pd.concat(dfs, axis=0) #, ignore_index=True)
    sel_cols = list(tdf.columns)
    numeric_cols = [col for col in tdf.columns if pd.api.types.is_numeric_dtype(tdf[col])]
    max_values = tdf[numeric_cols].max()

    def format_with_bold_max(val, max_val, col):
        if val == max_val:
            if col == 'All':
                return r'\textbf{' + "{:.2f}".format(val) + '}'
            else:
                return r'\textbf{' + "{:.2f}".format(val) + '}'
        else:
            if col == 'All':
                return "{:.2f}".format(val)
            else:
                return "{:.2f}".format(val)            

    grouped = tdf.groupby('metric')


def open_latex():
    tdf = df
    cols = selected_cols if selected_cols else sel_cols
    latex_table=tabulate(tdf[cols],  #[rep_cols+score_cols], 
            headers='keys', tablefmt='latex_raw', showindex=False, floatfmt=".2f")
    def rotate_columns(latex_table, cols_to_rotate):
        for col in cols_to_rotate:
            latex_table = latex_table.replace(col, f"\\rot{{{col}}}")
        return latex_table
    #latex_table = latex_table.replace("tabular", "longtable")
    latex_table = latex_table.replace("_", "-")
    if "rot" in cmd:
        latex_table = rotate_columns(latex_table, rot_cols)
    latex_lines = latex_table.split('\n')
    modified_latex_lines = []

    for i, line in enumerate(latex_lines):
        if i > 0 and '\\multirow{' in line:  
            modified_latex_lines.append(r'\hline')  
            modified_latex_lines.append(line)
        else:
            modified_latex_lines.append(line)

    latex_table = '\n'.join(modified_latex_lines)
    pyperclip.copy(latex_table)
    # clipboard_content = pyperclip.paste()
    tname = rowinput("Table name:")
    table_dir = "/home/ahmad/tehran-thesis/tables"
    Path(table_dir).mkdir(exist_ok=True, parents=True)
    with open(os.path.join(table_dir, tname + ".tex"), "w") as f:
        f.write(latex_table)
    #report = report.replace("mytable", latex_table + "\n\n \\newpage mytable")
    #report = report.replace("mytable", "\n \\newpage mytable")
    # tdf = pdf
    # iiiiiiiiiiiii
    #report = report.replace("mytable","")
    #with open(m_report, "w") as f:
    #    f.write(main_report)
    mbeep()
    #subprocess.run(["pdflatex", tex])
    #subprocess.run(["okular", pdf])
if "getimage" in cmd or char == "Z":
    show_msg("Generating images ...", bottom=True, delay=2000)
    _dir = Path(__file__).parent
    doc_dir = "/home/ahmad/logs" #os.getcwd() 
    m_report = os.path.join(doc_dir, "report.tex")
    with open(m_report, "r") as f:
        report = f.read()

    image = """
        \\begin{{figure}}
            \centering
            \includegraphics[width=\\textwidth]{{{}}}
            \caption[image]{{{}}}
            \label{{{}}}
        \end{{figure}}
    """
    multi_image = """
        \\begin{figure}
            \centering
            \caption[image]{mycaption}
            mypicture 
            \label{fig:all}
        \end{figure}
    """
    graphic = "\includegraphics[width=\\textwidth]{{{}}}"
    pics_dir = doc_dir + "/pics"
    #ii = image.format(havg, "havg", "fig:havg")
    #report = report.replace("myimage", ii +"\n\n" + "myimage")
    Path(pics_dir).mkdir(parents=True, exist_ok=True)
    #pname = plot_bar(pics_dir, train_num)
    #ii = image.format(pname, "bar", "fig:bar")
    #report = report.replace("myimage", ii +"\n\n" + "myimage")
    all_exps = df["eid"].unique()
    experiment_images, fnames = get_images(df, all_exps, 'eid')
    all_images = {}
    kk = 0
    id = "other"
    images_str = ""
    cols = ["eid"] + rep_cols + score_cols
    img_string = ""
    for key, img_list in experiment_images.items():
        mkey = key
        caption_dict = {}
        if not df.loc[df['eid'] == key].empty:
            caption_dict = df.loc[df['eid'] == key, sel_cols].iloc[0].to_dict()
        caption = ""
        name = key
        key = str(key)
        for new_im in img_list:
            name = key + str(name)
            _exp = key.replace("_","-")
            _exp = _exp.split("-")[0]
            fname = fnames[kk]
            for k,v in caption_dict.items():
                if k in map_cols:
                    k = map_cols[k]
                if type(v) == float:
                    v = f"{v:.2f}"
                if k == "cat":
                    v = v.split("-")[0]
                caption += " \\textcolor{gray}{" + str(k).replace("_","-") \
                    + "}: \\textcolor{blue}{" + str(v).replace("_","-")+ "}" 
            ss = "_scores" if "score" in fname else "_sim"
            if "@" in fname:
                ss = "_" + fname.split("@")[1]
            pname = doc_dir + "/pics/" + id + name.strip("-") + ss + ".png" 
            dest = os.path.join(doc_dir, pname) 
            new_im.save(dest)
            label = "fig:" + key
            ii = image.format(pname, caption, label)
            if kk % 10 == 0:
                tex = f"{doc_dir}/hm_img_{kk}.tex"
                with open(tex, "w") as f:
                    f.write(img_string)
                img_string = ""
                report = report.replace("myimage", 
                        f"\clearpage \n \input{{hm_img_{kk}.tex}} \n myimage") 
            img_string +=  ii +"\n\n" 
            if not _exp in all_images:
                all_images[_exp] = {}
            all_images[_exp][ss] = pname
            kk += 1

    if img_string: 
        tex = f"{doc_dir}/hm_img_{kk}.tex"
        with open(tex, "w") as f:
            f.write(img_string)
        img_string = ""
        report = report.replace("myimage", 
                f"\clearpage \n \input{{hm_img_{kk}.tex}} \n myimage") 

    g1 = ["SIL","SILP","SIP"] 
    g2 = ["SILPI","SLPI","SLP", "SL"] 
    ii = 0
    multi_image3 = multi_image
    for k,v in all_images.items():
        if ii % 2 == 0:
            multi_image3 += f" \\newpage \n \\subsection{{{k}}}"
        ii += 1
        for p,q in v.items():
            multi_image3 += multi_image.replace("mypicture", 
                    graphic.format(q) + "\n").replace("mycaption",
                            str(p) + ":" + str(q))

    multi_image3 = multi_image3.replace("mypicture","")
    tex = f"{doc_dir}/scores_img.tex"
    with open(tex, "w") as f:
        f.write(multi_image3)
    #report = report.replace("myimage", 
    #        "\n\n \input{scores_img.tex} \n\n myimage") 
    #report = report.replace("myimage", "\n\n \input{sim_img.tex} \n\n myimage") 
    #report = report.replace("myimage", "\n\n \input{other_img.tex} \n\n") 
    ####################
    report = report.replace("mytable","")
    report = report.replace("myimage","")
    tex = f"{doc_dir}/report.tex"
    pdf = f"{doc_dir}/report.pdf"
    with open(tex, "w") as f:
        f.write(report)
    #with open(m_report, "w") as f:
    #    f.write(main_report)
    show_msg(pdf)
    mbeep()
    #subprocess.run(["pdflatex", tex])
    subprocess.run(["okular", pdf])
