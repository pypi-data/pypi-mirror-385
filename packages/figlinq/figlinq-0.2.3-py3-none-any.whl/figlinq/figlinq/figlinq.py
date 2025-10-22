import figlinq
import os
import time
import uuid
from collections import Counter
from typing import Any, Dict, Optional, Union

from figlinq.utils import validate_fid, parse_file_id_args, ensure_path_exists
from figlinq.api import v2
from figlinq.analysis import (
    SUPPORTED_TESTS as _SUPPORTED_ANALYSIS_TESTS,
    build_analysis_payload,
    get_analysis_schema_markdown,
)
from io import BytesIO
from _plotly_utils.optional_imports import get_module


class ext_file_ops:
    """
    A class to handle external file operations.
    """

    @classmethod
    def download(cls, url_or_fid):
        """
        Download an external file from Figlinq.
        :param (str) url_or_fid: The file ID or URL of the file to download.
        :return: The downloaded file content as file-like object.
        """

        if validate_fid(url_or_fid):
            fid = url_or_fid
        else:
            fid = parse_file_id_args(None, url_or_fid)

        response = v2.external_files.content(fid)
        return BytesIO(response.content)

    @classmethod
    def upload(cls, file, filename=None, world_readable="false", return_type="url"):
        parent_path = None
        if filename:
            filename, new_parent_path = ensure_path_exists(filename)
            if new_parent_path:
                parent_path = new_parent_path

        resp_json = v2.external_files.create(
            file, filename, parent_path=parent_path, world_readable=world_readable
        )
        file_obj = resp_json.get("file", {}) if isinstance(resp_json, dict) else {}
        if return_type == "url":
            return file_obj.get("web_url")
        elif return_type == "fid":
            return file_obj.get("fid")
        return file_obj


class ext_images_ops:
    """
    A class to handle external image operations.
    """

    @classmethod
    def download(cls, url_or_fid):
        """
        Download an external image from Figlinq.
        :param (str) url_or_fid: The file ID or URL of the file to download.
        :return: The downloaded file content as file-like object.
        """

        if validate_fid(url_or_fid):
            fid = url_or_fid
        else:
            fid = parse_file_id_args(None, url_or_fid)

        response = v2.external_images.content(fid)
        return BytesIO(response.content)

    @classmethod
    def upload(
        cls,
        file,
        filename=None,
        world_readable="false",
        return_type="url",
        is_figure=False,
    ):
        parent_path = None
        if filename:
            filename, new_parent_path = ensure_path_exists(filename)
            if new_parent_path:
                parent_path = new_parent_path

        resp_json = v2.external_images.create(
            file,
            filename,
            parent_path=parent_path,
            world_readable=world_readable,
            is_figure=is_figure,
        )
        file_obj = resp_json.get("file", {}) if isinstance(resp_json, dict) else {}
        if return_type == "url":
            return file_obj.get("web_url")
        elif return_type == "fid":
            return file_obj.get("fid")
        return file_obj


class html_text_ops:
    """
    A class to handle HTML text operations.
    """

    @classmethod
    def download(cls, url_or_fid):
        """
        Download an HTML text from Figlinq.
        :param (str) url_or_fid: The file ID or URL of the file to download.
        :return: The downloaded file content as file-like object.
        """

        if validate_fid(url_or_fid):
            fid = url_or_fid
        else:
            fid = parse_file_id_args(None, url_or_fid)

        response = v2.html_text.content(fid)
        parsed_content = response.json()
        return BytesIO(parsed_content["content"].encode("utf-8"))

    @classmethod
    def upload(
        cls,
        file,
        filename=None,
        world_readable="false",
        return_type="url",
        category="text",
    ):
        parent_path = None
        if filename:
            filename, new_parent_path = ensure_path_exists(filename)
            if new_parent_path:
                parent_path = new_parent_path

        resp_json = v2.html_text.create(
            file,
            filename,
            parent_path=parent_path,
            world_readable=world_readable,
            category=category,
        )
        file_obj = resp_json.get("file", {}) if isinstance(resp_json, dict) else {}
        if return_type == "url":
            return file_obj.get("web_url")
        elif return_type == "fid":
            return file_obj.get("fid")
        return file_obj


class jupyter_notebook_ops:
    """
    A class to handle Jupyter notebook operations.
    """

    @classmethod
    def download(cls, url_or_fid):
        """
        Download a Jupyter notebook from Figlinq.
        :param (str) url_or_fid: The file ID or URL of the file to download.
        :return: The downloaded file content as file-like object.
        """

        if validate_fid(url_or_fid):
            fid = url_or_fid
        else:
            fid = parse_file_id_args(None, url_or_fid)

        response = v2.jupyter_notebooks.content(fid)
        parsed_content = response.json()
        return parsed_content

    @classmethod
    def upload(
        cls,
        file,
        filename=None,
        world_readable="false",
        return_type="url",
    ):
        parent_path = None
        if filename:
            filename, new_parent_path = ensure_path_exists(filename)
            if new_parent_path:
                parent_path = new_parent_path

        resp_json = v2.jupyter_notebooks.create(
            file, filename, parent_path=parent_path, world_readable=world_readable
        )
        file_obj = resp_json.get("file", {}) if isinstance(resp_json, dict) else {}
        if return_type == "url":
            return file_obj.get("web_url")
        elif return_type == "fid":
            return file_obj.get("fid")
        return file_obj


class analysis_ops:
    """Helpers for listing, creating, and deleting statistical analyses."""

    SUPPORTED_TESTS = _SUPPORTED_ANALYSIS_TESTS

    @classmethod
    def supported_tests(cls):
        """Return the canonical list of supported analysis test names."""

        return list(cls.SUPPORTED_TESTS)

    @classmethod
    def schema(cls, analysis_type: str) -> str:
        """Render Markdown guidance for a given statistical analysis."""
        key = (analysis_type or "").strip()
        if not key:
            raise ValueError("Analysis type is required.")

        try:
            return get_analysis_schema_markdown(key)
        except KeyError as exc:
            available = ", ".join(cls.supported_tests())
            raise ValueError(
                f"Unknown analysis type '{key}'. Available: {available}"
            ) from exc

    @classmethod
    def list(
        cls,
        *,
        fid: Optional[str] = None,
        analysis_type: Optional[str] = None,
        **query: Any,
    ) -> Any:
        """Return analysis records for the authenticated user."""

        response = v2.analysis.list(fid=fid, analysis_type=analysis_type, **query)
        return response.json()

    @classmethod
    def create(
        cls,
        *,
        test: str = "anova_oneway",
        mode: Optional[str] = None,
        data_mode: Optional[str] = None,
        value_col: Optional[str] = None,
        group_col: Optional[str] = None,
        x_col: Optional[str] = None,
        y_col: Optional[str] = None,
        value_col_a: Optional[str] = None,
        group_col_a: Optional[str] = None,
        value_col_b: Optional[str] = None,
        group_col_b: Optional[str] = None,
        group_a: Optional[str] = None,
        group_b: Optional[str] = None,
        alpha: Optional[Union[float, str]] = None,
        nan_policy: Optional[str] = None,
        alternative: Optional[str] = None,
        equal_var: Optional[Union[bool, str]] = None,
        post_hoc: Optional[str] = None,
        p_adjust: Optional[str] = None,
        effect_size: Optional[str] = None,
        zero_method: Optional[str] = None,
        computation_mode: Optional[str] = None,
        continuity_correction: Optional[Union[bool, str]] = None,
        hl_estimator: Optional[Union[bool, str]] = None,
        show_annotations: Optional[Union[bool, str]] = None,
        row_filter: Optional[Dict[str, Any]] = None,
    ) -> Any:
        """Create a new statistical analysis using the unified spec."""

        test_name = (test or "anova_oneway").strip() or "anova_oneway"

        overrides: Dict[str, Any] = {
            "test": test_name,
            "mode": mode,
            "data_mode": data_mode,
            "value_col": value_col,
            "group_col": group_col,
            "x_col": x_col,
            "y_col": y_col,
            "value_col_a": value_col_a,
            "group_col_a": group_col_a,
            "value_col_b": value_col_b,
            "group_col_b": group_col_b,
            "a": group_a,
            "b": group_b,
            "alpha": alpha,
            "nan_policy": nan_policy,
            "alternative": alternative,
            "equal_var": equal_var,
            "post_hoc": post_hoc,
            "p_adjust": p_adjust,
            "effect_size": effect_size,
            "zero_method": zero_method,
            "computation_mode": computation_mode,
            "continuity_correction": continuity_correction,
            "hl_estimator": hl_estimator,
            "show_annotations": show_annotations,
            "row_filter": row_filter,
        }

        payload = build_analysis_payload(test_name, overrides)
        response = v2.analysis.create(payload)
        return response.json()

    @classmethod
    def delete(cls, analysis_id: Union[str, int]) -> None:
        """Delete an analysis record by id."""

        v2.analysis.destroy(str(analysis_id))


def supported_analysis_tests():
    """Return the canonical list of supported analysis test names."""

    return analysis_ops.supported_tests()


def get_analysis_schema(analysis_type: str) -> str:
    """Return Markdown guidance for the requested statistical analysis."""

    return analysis_ops.schema(analysis_type)


def list_analyses(
    *,
    fid: Optional[str] = None,
    analysis_type: Optional[str] = None,
    **query: Any,
) -> Any:
    """Return analysis records for the authenticated user."""

    return analysis_ops.list(fid=fid, analysis_type=analysis_type, **query)


def create_analysis(
    *,
    test: str = "anova_oneway",
    mode: Optional[str] = None,
    data_mode: Optional[str] = None,
    value_col: Optional[str] = None,
    group_col: Optional[str] = None,
    x_col: Optional[str] = None,
    y_col: Optional[str] = None,
    value_col_a: Optional[str] = None,
    group_col_a: Optional[str] = None,
    value_col_b: Optional[str] = None,
    group_col_b: Optional[str] = None,
    group_a: Optional[str] = None,
    group_b: Optional[str] = None,
    alpha: Optional[Union[float, str]] = None,
    nan_policy: Optional[str] = None,
    alternative: Optional[str] = None,
    equal_var: Optional[Union[bool, str]] = None,
    post_hoc: Optional[str] = None,
    p_adjust: Optional[str] = None,
    effect_size: Optional[str] = None,
    zero_method: Optional[str] = None,
    computation_mode: Optional[str] = None,
    continuity_correction: Optional[Union[bool, str]] = None,
    hl_estimator: Optional[Union[bool, str]] = None,
    show_annotations: Optional[Union[bool, str]] = None,
    row_filter: Optional[Dict[str, Any]] = None,
) -> Any:
    """Create a new statistical analysis using the unified spec."""

    return analysis_ops.create(
        test=test,
        mode=mode,
        data_mode=data_mode,
        value_col=value_col,
        group_col=group_col,
        x_col=x_col,
        y_col=y_col,
        value_col_a=value_col_a,
        group_col_a=group_col_a,
        value_col_b=value_col_b,
        group_col_b=group_col_b,
        group_a=group_a,
        group_b=group_b,
        alpha=alpha,
        nan_policy=nan_policy,
        alternative=alternative,
        equal_var=equal_var,
        post_hoc=post_hoc,
        p_adjust=p_adjust,
        effect_size=effect_size,
        zero_method=zero_method,
        computation_mode=computation_mode,
        continuity_correction=continuity_correction,
        hl_estimator=hl_estimator,
        show_annotations=show_annotations,
        row_filter=row_filter,
    )


def delete_analysis(analysis_id: Union[str, int]) -> None:
    """Delete an analysis record by id."""

    analysis_ops.delete(analysis_id)


def upload(
    file,
    filetype,
    filename=None,
    world_readable=False,
    return_type="url",
    **kwargs,
):
    """
    Upload an file to Figlinq. A wrapper around the Plotly API v2 upload functions for all file types.

    :param (file) file: The file to upload. This can be a file-like object
    (e.g., open(...), Grid, JSON or BytesIO).
    :param (str) filetype: The type of the file being uploaded. This can be "plot", "grid", "image", "figure", "notebook", "html_text", "other"
    :param (str) filename: The name of the file to upload.
    :param (bool) world_readable: If True, the file will be publicly accessible.
    :param (str) return_type: The type of response to return.
    Can be "url" or "fid". If "url", the URL of the uploaded file will be returned.
    If "fid", the file ID will be returned.
    :return: The URL or file ID of the uploaded file, depending on the return_type.
    """

    world_readable_header = "true" if world_readable else "false"

    if filetype not in [
        "plot",
        "grid",
        "image",
        "figure",
        "jupyter_notebook",
        "html_text",
        "external_file",
    ]:
        raise ValueError(
            "Invalid filetype. Must be one of: 'plot', 'grid', 'image', 'figure', 'jupyter_notebook', 'html_text', 'external_file'."
        )
    if filetype == "plot":
        # Support update-by-fid using layout.meta["plotly_plot"]["fid"], with validation of grid references.
        # Fallback to legacy behavior (plotly.plot) when no fid hint provided.
        return _upload_plot_with_optional_update(
            file,
            filename=filename,
            world_readable=world_readable,
            return_type=return_type,
            **kwargs,
        )
    elif filetype == "grid":
        pd = get_module("pandas")

        if pd and isinstance(file, pd.DataFrame):
            grid_meta = (
                getattr(file, "attrs", {}).get("figlinq")
                if hasattr(file, "attrs")
                else None
            )
            file, headers_changed, _ = _normalize_dataframe_for_grid_upload(file, pd)
            if headers_changed:
                grid_meta = None

            if grid_meta and isinstance(grid_meta, dict):
                fid = grid_meta.get("fid")
                col_ids = grid_meta.get("col_ids") or {}
                cols = []
                for name in file.columns:
                    series = file[name]
                    data_list = series.tolist()
                    col = figlinq.grid_objs.Column(data_list, name)
                    uid = col_ids.get(name)
                    if uid and fid and isinstance(uid, str):
                        col.id = f"{fid}:{uid}"
                    cols.append(col)
                grid = figlinq.grid_objs.Grid(cols)
                if fid:
                    grid.id = fid
                file = grid
            else:
                file = figlinq.grid_objs.Grid(file)
        elif isinstance(file, figlinq.grid_objs.Grid):
            _normalize_grid_for_upload(file)
        else:
            raise ValueError(
                "Invalid file type for grid upload. Must be Grid or DataFrame."
            )

        return figlinq.plotly.plotly.grid_ops.upload(
            file,
            filename=filename,
            world_readable=world_readable,
            return_type=return_type,
            **kwargs,
        )
    elif filetype == "image":
        return ext_images_ops.upload(
            file,
            filename=filename,
            world_readable=world_readable_header,
            return_type=return_type,
            **kwargs,
        )
    elif filetype == "figure":
        return ext_images_ops.upload(
            file,
            filename=filename,
            world_readable=world_readable_header,
            return_type=return_type,
            is_figure=True,
        )
    elif filetype == "jupyter_notebook":
        return jupyter_notebook_ops.upload(
            file,
            filename=filename,
            world_readable=world_readable_header,
            return_type=return_type,
        )
    elif filetype == "html_text":
        return html_text_ops.upload(
            file,
            filename=filename,
            world_readable=world_readable_header,
            return_type=return_type,
        )
    elif filetype == "external_file":
        return ext_file_ops.upload(
            file,
            filename=filename,
            world_readable=world_readable_header,
            return_type=return_type,
        )


def download(fid_or_url, raw=False):
    """
    Download a file from Figlinq.

    :param (str) fid_or_url: The file ID or URL of the file to download.
    :param (bool) raw: If True, return the raw content of the file.
    :return: The downloaded file content or a Grid instance.
    """

    # Check if is fid or url
    if validate_fid(fid_or_url):
        fid = fid_or_url
    else:
        fid = parse_file_id_args(None, fid_or_url)

    # Get the file object first to determine the filetype
    response = v2.files.retrieve(fid)
    file_obj = response.json()
    file_type = file_obj["filetype"]

    if file_type == "grid":  # Returns Grid object
        grid = figlinq.plotly.plotly.get_grid(fid_or_url, raw=raw)
        grid = Grid(grid, fid)
        if raw:
            grid_json = figlinq.plotly.plotly.get_grid(fid_or_url, raw=True)
            return _coerce_raw_grid_numbers(grid_json)

        grid = figlinq.plotly.plotly.get_grid(fid_or_url, raw=False)
        grid = _coerce_grid_numbers(grid)
        return _ensure_figlinq_grid(grid)
    elif file_type == "plot":  # Returns Plotly figure object (dict-like)
        split_fid = fid.split(":")
        owner = split_fid[0]
        idlocal = int(split_fid[1])
        fig = figlinq.plotly.plotly.get_figure(owner, idlocal, raw=raw)
        # Coerce to plain dict if a Plotly Figure-like is returned
        if not isinstance(fig, dict):
            try:
                if hasattr(fig, "to_plotly_json"):
                    fig = fig.to_plotly_json()
                elif hasattr(fig, "to_dict"):
                    fig = fig.to_dict()
            except Exception:
                pass
        # Inject fid hint into layout.meta.plotly_plot so clients can perform update-by-fid later.
        try:
            if isinstance(fig, dict):
                layout = fig.get("layout")
                if not isinstance(layout, dict):
                    layout = {}
                    fig["layout"] = layout
                meta = layout.get("meta")
                if not isinstance(meta, dict):
                    meta = {}
                    layout["meta"] = meta
                pp = meta.get("plotly_plot")
                if not isinstance(pp, dict):
                    pp = {}
                pp["fid"] = fid
                meta["plotly_plot"] = pp
        except Exception:
            # best-effort injection only
            pass
        return fig
    elif file_type == "external_image":  # Returns BytesIO object
        return ext_images_ops.download(fid_or_url)
    elif file_type == "jupyter_notebook":  # Returns JSON object
        return jupyter_notebook_ops.download(fid_or_url)
    elif file_type == "html_text":  # Returns BytesIO object
        return html_text_ops.download(fid_or_url)
    elif file_type == "external_file":  # Returns BytesIO object
        return ext_file_ops.download(fid_or_url)
    else:
        raise ValueError(
            "Invalid filetype. Must be one of: 'plot', 'grid', 'image', 'jupyter_notebook', 'html_text', 'external_file'."
        )


def get_plot_template(template_name):
    """
    Get the plot template for the current user.

    :return: The plot template as a dictionary.
    """

    return figlinq.tools.get_template(template_name)


def apply_plot_template(fig, template_name):
    """
    Apply the plot template to a Plotly figure.

    :param fig: The Plotly figure to apply the template to.
    :param template_name: The name of the template to apply.
    :return: The modified Plotly figure.
    """

    template = get_plot_template(template_name)
    fig.update_layout(template["layout"])
    return fig

def apply_template(fig, template_name):
    """
    Apply the plot template to a Plotly figure dict.

    :param fig: The Plotly figure dict to apply the template to.
    :param template_name: The name of the template to apply.
    :return: The modified Plotly figure dict.
    """

    template = get_plot_template(template_name)
    fig["layout"]["template"] = template
    return fig

def _coerce_grid_numbers(grid):
    """
    Coerce numbers in the grid to their appropriate types.
    :param grid: The grid to coerce numbers in. Plotly Grid object.
    :return: The modified grid with coerced numbers. Plotly Grid object.
    """
    for col in grid:
        col.data = [_coerce_number_or_keep(s) for s in col.data]
    return grid


def _coerce_raw_grid_numbers(grid):
    """
    e.g. {'cols': {'time': {'data': ['1', '2', '3'], 'order': 0, 'uid': '188549'}, 'voltage': {'data': [4, 2, 5], 'order': 1, 'uid': '4b9e4d'}}}

    Coerce numbers in the grid to their appropriate types.
    :param grid: The grid to coerce numbers in.
    :return: The modified grid with coerced numbers.
    """

    for col, meta in grid.get("cols", {}).items():
        meta["data"] = [_coerce_number_or_keep(x) for x in meta.get("data", [])]

    return grid


def _ensure_figlinq_grid(grid):
    """Ensure returned grid uses figlinq Grid/Column subclasses without losing IDs."""
    if not isinstance(grid, _Grid):
        return grid

    if not isinstance(grid, Grid):
        try:
            grid.__class__ = Grid
        except TypeError:
            pass

    for idx, column in enumerate(grid):
        if isinstance(column, _Column) and not isinstance(column, Column):
            try:
                column.__class__ = Column
            except TypeError:
                replacement = Column(column.data, column.name)
                replacement.id = getattr(column, "id", "")
                grid._columns[idx] = replacement
    return grid


def _coerce_number_or_keep(s):
    if not isinstance(s, str):
        return s  # Pass through non-strings unchanged
    s = s.strip().replace(",", "")  # handle commas
    try:
        return int(s)
    except ValueError:
        try:
            return float(s)
        except ValueError:
            return s


# def get_svg_node_string(fid, filetype, x, y, width, height):

#     fid_split = fid.split(":")
#     owner = fid_split[0]
#     idlocal = int(fid_split[1])
#     url_part = f"~{owner}/{idlocal}"
#     svg_id = f"svg_{fid}"
#     return f"""<image xmlns="http://www.w3.org/2000/svg" preserveAspectRatio="none" id="{svg_id}" class="fq-{filetype}" xlink:href="https://plotly.local/{url_part}.svg" width="{width}" height="{height}" x="{x}" y="{y}" data-original_dimensions="{width},{height}" data-fid="{fid}" data-content_href="https://plotly.local/{url_part}.embed"></image>
# """

from figlinq.grid_objs import Grid as _Grid, Column as _Column


class Grid(_Grid):
    """Plotly Grid object exposed in figlinq module.

    Inherits from figlinq.grid_objs.grid_objs.Grid.
    """


class Column(_Column):
    """Plotly Column object exposed in figlinq module.

    Inherits from figlinq.grid_objs.grid_objs.Column.
    """
    
    # Set module to 'chart_studio.grid_objs' so Plotly's validators recognize it
    __module__ = 'chart_studio.grid_objs'


# ---------------
# Grid utilities
# ---------------


def _excel_column_name(index):
    """Return Excel-style column label (A, B, ..., AA, AB, ...)."""

    if index < 0:
        raise ValueError("Column index must be non-negative")

    label = []
    remainder = index
    while True:
        remainder, offset = divmod(remainder, 26)
        label.append(chr(ord("A") + offset))
        if remainder == 0:
            break
        remainder -= 1
    return "".join(reversed(label))


def _excel_column_headers(count):
    return [_excel_column_name(i) for i in range(count)]


def _normalize_dataframe_for_grid_upload(df, pd_module):
    """Normalize DataFrame column headers for grid upload.

    - Ensures column names are strings.
    - Promotes duplicate column headers to the first data row.
    - Applies Excel-style column names when headers are missing/duplicate.

    Returns the normalized DataFrame, a boolean indicating whether headers changed,
    and a boolean indicating whether a header row was promoted into the data.
    """

    df_norm = df.copy()
    original_columns = list(df_norm.columns)

    normalized = []
    for name in original_columns:
        if isinstance(name, str):
            coerced = name.strip()
        elif name is None:
            coerced = ""
        else:
            coerced = str(name)
        normalized.append(coerced)

    counts = Counter(normalized)
    has_blank = counts.get("", 0) > 0
    has_duplicates = any(count > 1 for count in counts.values())
    duplicate_non_blank = any(
        name != "" and count > 1 for name, count in counts.items()
    )

    header_promoted = False
    if duplicate_non_blank:
        data_rows = [list(original_columns)] + df_norm.values.tolist()
        df_norm = pd_module.DataFrame(data_rows)
        header_promoted = True

    headers_changed = False
    if has_blank or has_duplicates:
        df_norm.columns = _excel_column_headers(df_norm.shape[1])
        headers_changed = True
    else:
        coerced_names = [str(col) for col in original_columns]
        if coerced_names != list(df_norm.columns):
            df_norm.columns = coerced_names
            headers_changed = True

    return df_norm, headers_changed or header_promoted, header_promoted


def _normalize_grid_for_upload(grid):
    """Normalize Grid headers, mirroring DataFrame behavior."""

    column_info = []
    normalized_names = []

    for column in grid:
        raw_name = column.name
        if isinstance(raw_name, str):
            normalized = raw_name.strip()
        elif raw_name is None:
            normalized = ""
        else:
            normalized = str(raw_name)
        column_info.append((column, raw_name, normalized))
        normalized_names.append(normalized)

    counts = Counter(normalized_names)
    has_blank = counts.get("", 0) > 0
    has_duplicates = any(count > 1 for count in counts.values())
    duplicate_non_blank = any(
        name != "" and count > 1 for name, count in counts.items()
    )

    header_promoted = False
    if duplicate_non_blank:
        for column, raw_name, _ in column_info:
            header_value = raw_name if raw_name not in (None, "") else ""
            column.data = [header_value] + list(column.data)
        header_promoted = True

    headers_changed = False
    if has_blank or has_duplicates:
        for idx, (column, _, _) in enumerate(column_info):
            column.name = _excel_column_name(idx)
        headers_changed = True
    else:
        for column, raw_name, _ in column_info:
            if not isinstance(column.name, str):
                column.name = str(raw_name)
                headers_changed = True

    return headers_changed or header_promoted, header_promoted


# ---------------
# Internal helpers
# ---------------


def _to_figure_dict(obj):
    """Coerce common Plotly figure types into a plain dict suitable for API calls."""
    # Plotly graph_objects.Figure and BaseFigure have to_plotly_json
    try:
        if hasattr(obj, "to_plotly_json"):
            return obj.to_plotly_json()
    except Exception:
        pass
    if isinstance(obj, dict):
        return obj
    # plotly.tools return might be lists/dicts already; fallback to as-is
    return obj


def _extract_plot_fid_hint(fig_dict):
    try:
        layout = fig_dict.get("layout")
        if isinstance(layout, dict):
            meta = layout.get("meta")
            if isinstance(meta, dict):
                pp = meta.get("plotly_plot")
                if isinstance(pp, dict):
                    fid = pp.get("fid")
                    if validate_fid(fid):
                        return fid
    except Exception:
        return None
    return None


def _iter_src_values(obj):
    """Yield all values of keys that end with 'src' in a nested dict/list graph."""
    if isinstance(obj, dict):
        for k, v in obj.items():
            if isinstance(k, str) and k.endswith("src") and isinstance(v, str):
                yield v
            else:
                for x in _iter_src_values(v):
                    yield x
    elif isinstance(obj, list):
        for item in obj:
            for x in _iter_src_values(item):
                yield x


def _parse_src(src):
    """Return (fid, uid) from a src string like 'user:123:abc123' or 'user:123:...:uid'."""
    if not isinstance(src, str) or ":" not in src:
        return None, None
    parts = src.split(":")
    if len(parts) < 3:
        return None, None
    uid = parts[-1]
    fid = ":".join(parts[:-1])
    return fid, uid


def _validate_plot_grid_refs_exist(fig_dict):
    """Ensure all grid/column references (src) point to existing grids and uids."""
    checked_fids = {}
    missing = []
    for src in _iter_src_values(fig_dict.get("data", [])):
        fid, uid = _parse_src(src)
        if not fid or not uid:
            continue
        try:
            if fid not in checked_fids:
                res = v2.grids.content(fid)
                grid = res.json()
                # map of uid presence
                uids = {info.get("uid") for info in grid.get("cols", {}).values()}
                checked_fids[fid] = uids
            if uid not in checked_fids[fid]:
                missing.append(f"{fid}:{uid}")
        except Exception:
            missing.append(f"{fid}:{uid}")
    if missing:
        raise ValueError(
            "One or more grid column references in figure do not exist: "
            + ", ".join(missing)
        )


def _strip_inline_data_where_src_present(obj):
    """Remove inline data arrays when a sibling '*src' key exists at the same level.

    Example: if a trace has both 'x' and 'xsrc', drop 'x'. Applies recursively for nested dicts.
    """
    if isinstance(obj, list):
        for item in obj:
            _strip_inline_data_where_src_present(item)
        return
    if not isinstance(obj, dict):
        return
    # First remove sibling data when '*src' exists
    keys = list(obj.keys())
    for k in keys:
        if isinstance(k, str) and k.endswith("src"):
            base = k[:-3]
            if base in obj:
                try:
                    del obj[base]
                except Exception:
                    pass
    # Then recurse into values
    for v in obj.values():
        _strip_inline_data_where_src_present(v)


def _upload_plot_with_optional_update(
    file,
    filename=None,
    world_readable=False,
    return_type="url",
    **kwargs,
):
    """Upload or update a Plot, updating by fid when available in layout.meta.plotly_plot.

    - If layout.meta.plotly_plot.fid is present and valid, update that plot in place after
      verifying all grid column src references exist on the server.
    - Otherwise, fall back to legacy behavior using figlinq.plotly.plot which will
      create or update based on filename and can auto-extract grids from arrays.
    """
    # Fallback path quickly if user asked for legacy behavior explicitly
    # Normalize figure to dict
    fig_dict = _to_figure_dict(file)

    fid_hint = _extract_plot_fid_hint(fig_dict) if isinstance(fig_dict, dict) else None

    if not fid_hint:
        # Use legacy plot upload which handles grid extraction & filename-based updates
        # If parent folder is set and no filename is provided, generate a safe default
        if filename is None and os.getenv("PARENT_FOLDER_PATH"):
            filename = f"untitled-plot-{int(time.time())}-{uuid.uuid4().hex[:6]}"
        plot_kwargs = dict(
            world_readable=world_readable,
            return_type=return_type,
            auto_open=False,
            **kwargs,
        )
        if filename is not None:
            plot_kwargs["filename"] = filename
        return figlinq.plotly.plot(
            file,
            validate=False,
            **plot_kwargs,
        )

    # We have a fid hint; perform update
    # Ensure any referenced grids/columns exist to avoid server-side errors
    # Work on a deep copy so we don't mutate the caller's figure
    fig_for_update = fig_dict
    try:
        import copy as _copy

        if isinstance(fig_dict, dict):
            fig_for_update = _copy.deepcopy(fig_dict)
    except Exception:
        pass

    if isinstance(fig_dict, dict):
        _validate_plot_grid_refs_exist(fig_dict)
    if isinstance(fig_for_update, dict):
        # Only strip inline arrays within traces; avoid touching layout keys
        _strip_inline_data_where_src_present(fig_for_update.get("data", []))
        # Remove the fid hint from the outgoing payload; server doesn't need it
        try:
            layout = fig_for_update.get("layout")
            if isinstance(layout, dict):
                meta = layout.get("meta")
                if isinstance(meta, dict):
                    pp = meta.get("plotly_plot")
                    if isinstance(pp, dict):
                        pp.pop("fid", None)
                        if not pp:
                            meta.pop("plotly_plot", None)
                    if not meta:
                        layout.pop("meta", None)
        except Exception:
            pass

    parent_path = None
    if filename:
        filename, new_parent_path = ensure_path_exists(filename)
        if new_parent_path:
            parent_path = new_parent_path

    body = {
        "figure": fig_for_update,
        "world_readable": bool(world_readable),
    }
    if filename:
        body["filename"] = filename
    if parent_path:
        body["parent_path"] = parent_path

    response = v2.plots.update(fid_hint, body)
    # API returns file meta JSON
    file_obj = response.json()

    if return_type == "url":
        return file_obj.get("web_url")
    elif return_type == "fid":
        return file_obj.get("fid")
    return file_obj
