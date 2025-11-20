import numpy as np
import xarray as xr
import funwave_amp as fpy
import warnings
import xarray


def ensure_net_cdf_type(nc_data):
    """
    Enforces type compatibility for NETCDF:
    """

    print("\tStarting type enforcement on NETCDF")

    # DATA VARIABLES ----------------------------------------------------------
    for var_name in nc_data.data_vars:
        # Get the type
        dtype = nc_data[var_name].dtype

        # Convert floats
        if np.issubdtype(dtype, np.floating):
            nc_data[var_name] = nc_data[var_name].astype(np.float32)
        # Convert integers
        elif np.issubdtype(dtype, np.integer):
            nc_data[var_name] = nc_data[var_name].astype(np.int32)
    # [END] DATA VARIABLES ----------------------------------------------------

    # COORDINATES -------------------------------------------------------------
    for coord_name in nc_data.coords:
        # Get the type
        dtype = nc_data.coords[coord_name].dtype

        # Convert floats
        if np.issubdtype(dtype, np.floating):
            nc_data.coords[coord_name] = nc_data.coords[coord_name].astype(np.float32)
        # Convert integers
        elif np.issubdtype(dtype, np.integer):
            nc_data.coords[coord_name] = nc_data.coords[coord_name].astype(np.int32)
    # [END] COORDINATES -------------------------------------------------------

    # ATTRIBUTES --------------------------------------------------------------
    # Initialize new dictionary
    new_attrs = {}
    # Loop through all attributes
    for attr_name, attr_value in nc_data.attrs.items():
        # Convert floats
        if isinstance(attr_value, (float, np.floating)):
            new_attrs[attr_name] = np.float32(attr_value)
        # Convert integers
        elif isinstance(attr_value, (int, np.integer)):
            new_attrs[attr_name] = np.int32(attr_value)
        # Maintain strings
        elif isinstance(attr_value, str):
            new_attrs[attr_name] = attr_value
        # Convert to string otherwise
        else:
            new_attrs[attr_name] = str(attr_value)
            print(f"\t\tUnsupported Type: Converted attribute '{attr_name}' to string")

    nc_data.attrs = new_attrs
    # [END] ATTRIBUTES --------------------------------------------------------

    return nc_data


def get_net_cdf(var_dict):
    """
    Coerces input data into a NETCDF file
    """
    print("\nStarted compressing data to NETCDF...")

    ## XARRAY HANDLING --------------------------------------------------------
    # Initialize a list of xarray objects
    xr_datasets = []

    # Loop through all keys
    for key, value in var_dict.items():
        # Get list of any xarrays (ie- DomainObject, WaveMaker Object)
        if isinstance(value, xr.Dataset):
            xr_datasets.append(value)
        # Raise warning for things that aren't xarrays/ints/floats/strings
        elif not isinstance(value, (int, float, str)):
            print(f"Warning: {key} not saved to .nc due to type {type(value)}")

    # Merge any datasets that may exist
    nc_data = xr.merge(xr_datasets)
    ## [END] XARRAY HANDLING --------------------------------------------------

    ## ATTRIBUTE HANDLING -----------------------------------------------------
    # Loop through all things in var_dict
    for key, value in var_dict.items():
        # Store ints, floats, and strings as attributes
        if isinstance(value, (int, float, str)):
            nc_data.attrs[key] = value

        # Raise warning if the variable can't be stored
        elif not isinstance(value, xr.Dataset):
            print(
                f"Warning: {key} cannot be saved to NetCDF since it is of type {type(value).__name__}"
            )
    ## [END] ATTRIBUTE HANDLING -----------------------------------------------

    ## ASSERT AND SAVE OUT ----------------------------------------------------
    # One last double check on types
    nc_data = ensure_net_cdf_type(nc_data)

    # Get the file path and save
    ITER = int(var_dict["ITER"])
    ptr = fpy.get_key_dirs(tri_num=ITER)
    nc_path = ptr["nc"]

    # xarray.backends.file_manager.FILE_CACHE.clear()
    #

    nc_data.to_netcdf(nc_path)  # , engine="scipy")
    ## [END] ASSERT AND SAVE OUT ----------------------------------------------

    print("NETCDF for input data successful!")
    return nc_data
