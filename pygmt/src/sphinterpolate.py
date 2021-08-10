"""
sphinterpolate - Spherical gridding in tension of data on a sphere
"""
import xarray as xr
from pygmt.clib import Session
from pygmt.exceptions import GMTInvalidInput
from pygmt.helpers import (
    GMTTempFile,
    build_arg_string,
    data_kind,
    dummy_context,
    fmt_docstring,
    kwargs_to_strings,
    use_alias,
)


@fmt_docstring
@use_alias(
    G="outgrid",
    I="increment",
    R="region",
    V="verbose",
)
@kwargs_to_strings(I="sequence", R="sequence")
def sphinterpolate(table, **kwargs):
    r"""
    Create spherical grid files in tension of data.

    Reads one or more ASCII [or binary] files (or standard input) containing
    *lon, lat, z* and performs a Delaunay triangulation to set up a spherical
    interpolation in tension. The final grid is saved to the specified file.
    Several options may be used to affect the outcome, such as choosing local
    versus global gradient estimation or optimize the tension selection to
    satisfy one of four criteria.

    {aliases}

    Parameters
    ----------
    outgrid : str or None
        The name of the output netCDF file with extension .nc to store the grid
        in.
    {I}
    {R}
    {V}

    Returns
    -------
    ret: xarray.DataArray or None
        Return type depends on whether the ``outgrid`` parameter is set:
        - :class:`xarray.DataArray` if ``outgrid`` is not set
        - None if ``outgrid`` is set (grid output will be stored in file set by
          ``outgrid``)
    """
    kind = data_kind(table)
    with GMTTempFile(suffix=".nc") as tmpfile:
        with Session() as lib:
            file_context = lib.virtualfile_from_data(check_kind="vector", data=table)
            with file_context as infile:
                if "G" not in kwargs.keys():  # if outgrid is unset, output to tempfile
                    kwargs.update({"G": tmpfile.name})
                outgrid = kwargs["G"]
                arg_str = build_arg_string(kwargs)
                arg_str = " ".join([infile, arg_str])
                lib.call_module("sphinterpolate", arg_str)

        if outgrid == tmpfile.name:  # if user did not set outgrid, return DataArray
            with xr.open_dataarray(outgrid) as dataarray:
                result = dataarray.load()
                _ = result.gmt  # load GMTDataArray accessor information
        else:
            result = None  # if user sets an outgrid, return None

        return result
