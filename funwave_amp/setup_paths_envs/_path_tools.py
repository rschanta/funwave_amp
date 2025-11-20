import os


# %%
def add_dirs_to_path(env_file, dirs_to_add):
    """
    Helper function to add key-value pairs to an .env file
    """
    with open(env_file, "a") as f:
        for key, path_name in dirs_to_add.items():
            f.write(f"{key}={path_name}\n")
            os.makedirs(path_name, exist_ok=True)


# %%
def get_key_dirs(tri_num=None):
    """
    For a given trial specified by `tri_num`, construct the file paths
    to each of the following .txt files:
        > input.txt
        > DEPTH_FILE     [ba] (bathy)
        > FRICTION_FILE  [fr] (friction)
        > RESULT_FOLDER  [or] (out_raw)
        > WAVE_COMP_FILE [sp] (spectra)

    and the relevant .nc files:
        > tri_XXXXX.nc     [nc] (tri)
        > tri_XXXXX_sta.nc [ns] (tri_sta)

    and time_dt
    """
    if tri_num is None:
        tri_num = int(os.getenv("TRI_NUM"))

    # Get the base path files
    base_paths = {}
    for file_type in ["in", "ba", "or", "sp", "st", "fr", "bw", "nc", "ns"]:
        base_path = os.getenv(file_type)
        if base_path:
            base_paths[file_type] = base_path

    # Specify file names and extensions of the key files
    name_ext = {
        "in": ["input", ".txt"],
        "ba": ["bathy", ".txt"],
        "fr": ["friction", ".txt"],
        "or": ["out_raw", "/"],
        "bw": ["breakwater", ".txt"],
        "sp": ["spectra", ".txt"],
        "st": ["stations", ".txt"],
        "nc": ["tri", ".nc"],
        "ns": ["tri_sta", ".nc"],
    }

    # Construct the paths
    trial_paths = {}
    for key, name_ext_ in name_ext.items():
        if key in base_paths:
            name = f"{name_ext_[0]}_{tri_num:05}{name_ext_[1]}"
            trial_paths[key] = os.path.join(base_paths[key], name)

    # Add on time_dt
    trial_paths["time_dt"] = os.path.join(f"{trial_paths['or']}", "time_dt.out")

    return trial_paths

