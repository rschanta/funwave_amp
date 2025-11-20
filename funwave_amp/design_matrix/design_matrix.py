# Inner module imports
from re import A
from ._add_params import add_dependent_values, add_required_params, add_load_params
from ._apply_filters import apply_filters
from ._make_summary import save_out_summary
from ._print_plot_sets import print_supporting_file, plot_supporting_file
from .combinations import find_combinations

from .parallel2 import simple_v1 as sparallel

# Outer module imports
from ..print_files import print_input_dot_text
from ..xarray_obj import get_net_cdf


"""
Main design matrix file
"""


# %%
def process_design_matrix(
    matrix_csv=None,
    matrix_dict=None,
    print_inputs=True,
    load_sets=None,
    function_set=None,
    filter_sets=None,
    print_sets=None,
    plot_sets=None,
    summary_formats=["parquet", "csv"],
):
    """
    Works through the design matrix process
        - Loads in and checks data from either csv or dictionary
        - Finds all possible combinations of parameters (cartesian product)
        - Loads in any other data that should be accesible (load_vars)
        - Loops through each possible combination
            - Merge each combination with load_vars
            - add on dependent values from pipeline
            - add on required parameters
            - apply filtering conditions
    """

    ## Initialization
    fail_data, pass_data = [], []
    k = 1

    ## Load in design matrix, parse variables, and group
    df_permutations = find_combinations(matrix_csv=matrix_csv, matrix_dict=matrix_dict)

    ## Load in data that should only be loaded once
    if load_sets:
        load_vars = add_load_params({}, load_sets)

    ## CORE LOOP ==============================================================
    for perm_i, row in df_permutations.iterrows():
        print(f"\nStarted processing permutation: {perm_i:05}...", flush=True)
        # Keep track of the combination index, regardless if it fails
        combo_num = perm_i + 1

        # Convert row to dictionary form
        var_dict = row.to_dict()

        # Merge with load set
        if load_sets:
            var_dict = {**var_dict, **load_vars}

        ## Add on dependent parameters
        var_dict = add_dependent_values(var_dict, function_set)

        ## Filtering conditions
        failed_params = apply_filters(var_dict, filter_sets)

        # FAILURE CASES -------------------------------------------------------
        if failed_params is not None:
            # Add on required parameters (just combo num)
            failed_params["COMBO_NUM"] = combo_num
            # Append to list
            fail_data.append(failed_params)
            print(f"Combination {combo_num:05} FAILED. Moving on.")
        # [END] FAILURE CASES -------------------------------------------------

        # SUCCESSFUL CASES ----------------------------------------------------
        elif failed_params is None:
            ##  Add on required parameters
            var_dict = add_required_params(var_dict, k, combo_num)

            # Create files other than input.txt
            if print_sets:
                var_dict = print_supporting_file(var_dict, print_sets)

            # Output plots for visualization of input
            if plot_sets:
                plot_supporting_file(var_dict, plot_sets)

            # Create xarray
            ds = get_net_cdf(var_dict)

            ## Print `input.txt` for this given trial
            if print_inputs:
                print_input_dot_text(ds.attrs)

            # Get data for summary
            pass_data.append(ds.attrs)

            ## End loop iteration
            print(f"SUCCESSFULLY PRINTED FILES FOR TRIAL: {k:05}", flush=True)
            print("#" * 40)
            k = k + 1

            ds.close()

        # [END] SUCCESSFUL CASES ----------------------------------------------
    ## [END] CORE LOOP ========================================================

    ## Save out summaries
    df_pass, df_fail = save_out_summary(pass_data, fail_data, summary_formats)
    print("FILE GENERATION SUCCESSFUL!")
    return df_pass, df_fail


def process_design_matrix_parallel(
    matrix_csv=None,
    matrix_dict=None,
    print_inputs=True,
    load_sets=None,
    function_set=None,
    filter_sets=None,
    print_sets=None,
    plot_sets=None,
    summary_formats=["parquet", "csv"],
    n_procs=1,
):
    """
    Works through the design matrix process
        - Loads in and checks data from either csv or dictionary
        - Finds all possible combinations of parameters (cartesian product)
        - Loads in any other data that should be accesible (load_vars)
        - Loops through each possible combination
            - Merge each combination with load_vars
            - add on dependent values from pipeline
            - add on required parameters
            - apply filtering conditions
    """

    ## Load in design matrix, parse variables, and group
    df_permutations = find_combinations(matrix_csv=matrix_csv, matrix_dict=matrix_dict)

    ## Load in data that should only be loaded once
    if load_sets:
        load_vars = add_load_params({}, load_sets)
    else:
        load_vars = None

    # Converting table to list of tuple of index and dict
    args = [(i + 1, row.to_dict()) for i, row in df_permutations.iterrows()]

    # Subdivding permutation into 'evenly sized sublists for each processor'
    slices = _even_divide_slices(len(args), n_procs)

    common_args = (load_vars, function_set, filter_sets)

    # Generating args for each parallel call
    args = [(args[s], *common_args) for s in slices]

    # Validating combinations in parallel
    permutations = sparallel(_validate_combinations, n_procs, args, p_desc="Validating")

    # Flattening list of lists to list
    permutations = [item for sublist in permutations for item in sublist]
    # Filtering combinations
    fail_data = [d for flag, *d in permutations if not flag]
    pass_data = [d for flag, *d in permutations if flag]

    for i, d in fail_data:
        d["COMBO_NUM"] = i
    fail_data = [d for _, d in fail_data]

    # Adding new simulation index seperate from combination number
    pass_data = [(k, *d) for k, d in enumerate(pass_data, start=1)]

    # Subdiving passed combinations for further post-processing in parallel
    slices = _even_divide_slices(len(pass_data), n_procs)
    common_args = (print_inputs, print_sets, plot_sets)

    # Generating args for each parallel call
    args = [(pass_data[s], *common_args) for s in slices]

    # post-processing passed combinations in parallel
    pass_data = sparallel(_generate_simulations, n_procs, args, p_desc="Generating")

    ## Save out summaries
    df_pass, df_fail = save_out_summary(pass_data, fail_data, summary_formats)
    print("FILE GENERATION SUCCESSFUL!")
    return df_pass, df_fail


def _even_divide_slices(num: int, div: int, off: int = 0) -> list[slice]:
    """Returns indices after dividing range into mostly even subsizes"""
    sub, rem = divmod(num, div)
    grps = [sub + (1 if i < rem else 0) for i in range(div)]

    idxs = [(off, off + grps[0])] * div
    for i in range(1, div):
        idxs[i] = (idxs[i - 1][1], idxs[i - 1][1] + grps[i])

    return [slice(i0, i1) for i0, i1 in idxs]


def _generate_simulations(
    args_sets: list[tuple[int, int, dict]],
    print_inputs: bool,
    print_sets: list,
    plot_sets: list,
) -> list[dict]:
    """Wrapper method for generating a slices of simulations"""
    common_args = (print_inputs, print_sets, plot_sets)

    return [_generate_simulation(*a, *common_args) for a in args_sets]


def _generate_simulation(
    index: int,
    combo_num: int,
    var_dict: dict,
    print_inputs: bool,
    print_sets: list,
    plot_sets: list,
) -> dict:
    """Wrapper method for generating a single  simulation"""
    ##  Add on required parameters
    var_dict = add_required_params(var_dict, index, combo_num)

    # Create files other than input.txt
    if print_sets:
        var_dict = print_supporting_file(var_dict, print_sets)

    # Output plots for visualization of input
    if plot_sets:
        plot_supporting_file(var_dict, plot_sets)

    # Create xarray
    ds = get_net_cdf(var_dict)

    ## Print `input.txt` for this given trial
    if print_inputs:
        print_input_dot_text(ds.attrs)

    return ds.attrs
    # Get data for summary
    pass_data.append(ds.attrs)

    ## End loop iteration
    print(f"SUCCESSFULLY PRINTED FILES FOR TRIAL: {k:05}", flush=True)
    print("#" * 40)
    k = k + 1

    ds.close()


def _validate_combinations(
    arg_sets: list[tuple[int, dict]],
    load_vars: dict,
    function_set: list,
    filter_sets: list,
) -> list[tuple[bool, int, dict]]:
    """
    Wrapper method for sublist/slices of combinations for reducing parallel overhead
    """

    common_args = (load_vars, function_set, filter_sets)
    return [_validate_combination(*a, *common_args) for a in arg_sets]


def _validate_combination(
    combo_num: int,
    var_dict: dict,
    load_vars: dict,
    function_set: list,
    filter_sets: list,
) -> tuple[bool, int, dict]:
    """
    Wrapper method for validating a single combination
    """
    # print(f"\nStarted processing permutation: {perm_i:05}...", flush=True)
    # Keep track of the combination index, regardless if it fails

    # Merge with load set
    if load_vars is not None:
        var_dict = {**var_dict, **load_vars}

    ## Add on dependent parameters
    var_dict = add_dependent_values(var_dict, function_set)

    ## Filtering conditions
    failed_params = apply_filters(var_dict, filter_sets)

    is_success = failed_params is None

    data = var_dict if is_success else failed_params

    return is_success, combo_num, data
