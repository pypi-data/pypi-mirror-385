import subprocess
import sys
import os
import re
from distutils.spawn import find_executable
import pandas as pd

def create_folder(output_path):
    """
        create emringer output folder inside va directory

    :return: model related path of strudel folder
    """

    fullname = '{}'.format(output_path)

    if not os.path.isdir(fullname):
        os.mkdir(fullname, mode=0o777)
    else:
        print('{} is exist'.format(fullname))


def run_phenixcc(full_modelpath, full_mappath, resolution, output_path, echo=True):
    """
    Run phenix.map_model_cc and parse stdout to collect:
      - overall CCs: CC_mask, CC_volume, CC_peaks, CC_box
      - per-chain local CCs
      - main/side chain summaries
      - resolution reported by Phenix
      - paths to Phenix log files (map_model_fsc.log, cc_per_residue.log)

    Returns:
      errlist, metrics_dict, stdout_text

    CHANGES:
      - CHANGED: create output dir via os.makedirs(exist_ok=True)
      - NEW: stream stdout to both terminal and file (tee behavior) when echo=True
      - NEW: still return the full aggregated stdout_text
      - (Assumes you have parse_phenix_map_model_cc_output(stdout_text) defined)
    """
    errlist = []
    metrics = {}
    stdout_text = ""

    try:
        assert find_executable('phenix.map_model_cc') is not None
        phenixpath = find_executable('phenix.map_model_cc')

        # CHANGED: native mkdir
        try:
            os.makedirs(output_path, exist_ok=True)
        except Exception as e:
            errlist.append(f"Could not create output dir {output_path}: {e}")
            return errlist, metrics, stdout_text

        # build command
        phenixcc_cmd = [
            phenixpath,
            full_modelpath,
            full_mappath,
            f"resolution={resolution}",
        ]
        print(" ".join(phenixcc_cmd), flush=True)

        # NEW: stream output to file AND stdout
        log_path = os.path.join(output_path, "map_model_cc.stdout")
        try:
            with open(log_path, "w", encoding="utf-8") as logf:
                # line-buffered text mode
                process = subprocess.Popen(
                    phenixcc_cmd,
                    cwd=output_path,
                    stdout=subprocess.PIPE,
                    stderr=subprocess.STDOUT,
                    stdin=subprocess.PIPE,
                    text=True,
                    bufsize=1,
                )

                # in case phenix prompts (previously you sent "n\n")
                try:
                    process.stdin.write("n\n")
                    process.stdin.flush()
                    process.stdin.close()
                except Exception:
                    pass  # stdin might not be needed

                lines = []
                for line in process.stdout:
                    lines.append(line)
                    logf.write(line)
                    if echo:                     # NEW: print live to terminal
                        print(line, end="", flush=True)

                ret = process.wait()
                stdout_text = "".join(lines)

                if ret != 0:
                    errlist.append(f"phenix.map_model_cc exited with code {ret}")

        except Exception as e:
            errlist.append(f"Failed running or teeing stdout: {e}")
            # Fallback: no streaming; try one-shot run so we still get output
            completed = subprocess.run(
                phenixcc_cmd,
                cwd=output_path,
                stdout=subprocess.PIPE,
                stderr=subprocess.STDOUT,
                text=True,
                input="n\n",
            )
            stdout_text = completed.stdout or ""
            # save & (optionally) print after the fact
            try:
                with open(log_path, "w", encoding="utf-8") as fh:
                    fh.write(stdout_text)
            except Exception as e2:
                errlist.append(f"Could not write {log_path}: {e2}")
            if echo:
                print(stdout_text, end="", flush=True)

        # Basic error scan (keep your semantics)
        if "error" in stdout_text.lower():
            ctx = [ln.strip() for ln in stdout_text.splitlines() if "error" in ln.lower()]
            errlist.extend(ctx)

        # Parse metrics (requires your helper)
        try:
            metrics = parse_phenix_map_model_cc_output(stdout_text)
        except Exception as e:
            errlist.append(f"Parsing stdout failed: {e}")

    except AssertionError as exerr:
        errlist.append('Phenix executable is not there.')
        sys.stderr.write(f'Phenix executable is not there: {exerr}\n')
    except subprocess.CalledProcessError as suberr:
        err = f'Phenix map_model_cc error: {suberr}.'
        errlist.append(err)
        sys.stderr.write(err + '\n')
    except Exception as e:
        errlist.append(f"Unexpected failure running phenix.map_model_cc: {e}")

    return errlist, metrics, stdout_text


def read_cc(cc_per_residue_log, errlist):
    """
        Read the residue-wise CCC from the output of Phenix results
    :param: cc_per_residue_log input file cc_per_residue.log file(full path name) from Phenix CC calculation
    :return:
    """

    if not errlist and os.path.isfile(cc_per_residue_log):
        df = pd.read_csv(cc_per_residue_log, delim_whitespace=True, header=None)
        print(df)
    else:
        df = None

    return df


def _floatohex(numlist):
    """
        Todo: make this function into utlis
        Produce hex color between red and green
    :param numlist: A list of RGB values
    :return: A list of hex value between R and G with B = 0
    """

    numlist = [-1 if i < 0 else i for i in numlist]
    rgbs = [[122, int(num * 255), int(num * 255)] if num >= 0 else [255, 0, 255] for num in numlist]
    resultlist = ['#%02X%02X%02X' % (rgb[0], rgb[1], rgb[2]) for rgb in rgbs]

    return resultlist

def ccdf_todict(ccdf):
    """
        Given the Phenix CC result in dataframe and output the dict to be save in json
    :param ccdf: phenix cc_per_residue.log result into dataframe
    :return: dict which contain CC per residue results
    """

    finaldict = {}
    averagecc = ccdf[3].mean()
    averagecc_color = _floatohex([averagecc])[0]
    numberofresidues = ccdf.shape[0]
    colors = _floatohex(ccdf[3])
    ccscores = ccdf[3]
    chain_ccscores = ccdf.groupby(0).agg(value=(3, 'mean'))
    chain_ccscores['color'] = chain_ccscores.apply(lambda x: _floatohex([x['value']])[0], axis=1)
    chain_ccdict = {str(row.name): {'value': row['value'], 'color': row['color']} for _, row in chain_ccscores.iterrows()}

    def abc(a, b, c):
        return '{}:{} {}'.format(a, b, c)
    residue = ccdf.apply(lambda x: abc(x[0], x[2], x[1]), axis=1)
    finaldict = {'averagecc': round(averagecc, 3), 'averagecc_color': averagecc_color,
                         'numberofresidues': numberofresidues, 'color': colors,
                         'ccscore': ccscores.tolist(), 'residue': residue.tolist(), 'chainccscore': chain_ccdict}

    return finaldict


def _safe_float(x):
    try:
        return float(x)
    except Exception:
        return None

def parse_phenix_map_model_cc_output(stdout_text):
    """
    Parse phenix.map_model_cc stdout and extract:
      - overall CCs: CC_mask, CC_volume, CC_peaks, CC_box
      - per-chain local CC table
      - (optional) main-chain / side-chain summaries
      - (optional) map resolution
      - paths to logs that Phenix says it saved
    Returns a dict; missing fields will be None or empty lists.
    """
    result = {
        "resolution": None,
        "overall": {"CC_mask": None, "CC_volume": None, "CC_peaks": None, "CC_box": None},
        "per_chain": [],          # list of {chain_id, CC, B, occ, n_atoms}
        "main_chain": None,       # {"CC", "B", "occ", "n_atoms"}
        "side_chain": None,       # {"CC", "B", "occ", "n_atoms"}
        "map_model_fsc_log": None,
        "cc_per_residue_log": None,
    }

    # resolution
    m = re.search(r"Map resolution:\s*\*+\s*[\r\n]+.*?Resolution:\s*([0-9.]+)", stdout_text, re.S)
    if m:
        result["resolution"] = _safe_float(m.group(1))

    # overall CC block
    # Matches lines like: "CC_mask  : 0.7647"
    for key in ("CC_mask", "CC_volume", "CC_peaks", "CC_box"):
        mm = re.search(rf"{key}\s*:\s*([0-9.]+)", stdout_text)
        if mm:
            result["overall"][key] = _safe_float(mm.group(1))

    # files mentioned
    mm = re.search(r"Model-map FSC\s*\*+\s*[\r\n]+.*?saved to:\s*([^\r\n]+)", stdout_text, re.S)
    if mm:
        result["map_model_fsc_log"] = mm.group(1).strip()

    mm = re.search(r"Per residue:\s*[\r\n]+\s*saved to:\s*([^\r\n]+)", stdout_text)
    if mm:
        result["cc_per_residue_log"] = mm.group(1).strip()

    # ---- Per chain table parsing ----
    # Find the "Per chain:" block; consume lines until "Main chain:" or "Per residue:" or a divider
    per_chain_block = None
    m = re.search(
        r"Map-model CC \(local\).*?Per chain:\s*([\s\S]*?)(?=Main chain:|Per residue:|=+\s*Job complete)",
        stdout_text,
        flags=re.S,  # <-- key change
    )
    if m:
        per_chain_block = m.group(1)

    if per_chain_block:
        # Lines look like: "A         0.7724   21.234 1.00    2893"
        # Be robust to variable spacing and longer chain IDs.
        line_re = re.compile(r"^\s*(\S+)\s+([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)\s+(\d+)\s*$")
        for line in per_chain_block.splitlines():
            line = line.strip()
            if not line or line.lower().startswith(("chain id", "cc", "<b>", "<occ>", "n atoms")):
                continue
            mline = line_re.match(line)
            if mline:
                chain_id, cc, b, occ, n_atoms = mline.groups()
                result["per_chain"].append({
                    "chain_id": chain_id,
                    "CC": _safe_float(cc),
                    "B": _safe_float(b),
                    "occ": _safe_float(occ),
                    "n_atoms": int(n_atoms),
                })

    # ---- Main chain / Side chain summaries ----
    def parse_one_line_block(start_label):
        # Block shape:
        # Main chain:
        #  CC       <B>    <occ>   N atoms
        #  0.7787   21.111 1.00    8518
        pat = rf"{start_label}:\s*[\r\n]+\s*CC\s*<B>\s*<occ>\s*N atoms\s*[\r\n]+\s*([0-9.]+)\s+([0-9.]+)\s+([0-9.]+)\s+(\d+)"
        mlocal = re.search(pat, stdout_text)
        if mlocal:
            cc, b, occ, n_atoms = mlocal.groups()
            return {"CC": _safe_float(cc), "B": _safe_float(b), "occ": _safe_float(occ), "n_atoms": int(n_atoms)}
        return None

    result["main_chain"] = parse_one_line_block("Main chain")
    result["side_chain"] = parse_one_line_block("Side chain")

    return result
