from .models import (
    DataView,
    DataViewAnalysisFilterSpec,
    DataViewColumnSpec,
    DataViewFileSpec,
    DataViewGroupBy,
    DataViewGroupByColumn,
    DataViewNameFilterSpec,
    DataViewZipFilterSpec,
)


class ViewBuilder(object):
    """Builder class that assists in constructing a DataView object.

    :param str label: The optional label, if saving this data view.
    :param bool public: Whether or not to make this data view public when saving it.
    :param str match: The file match type, one of: first, last, newest, oldest, all
    :param str zip_files: The zip file filter, see the zip_member_filter function
    :param list columns: The columns or column groups to add
    :param bool process_files: Whether or not to process files, default is true
    :param bool include_ids: Whether or not to include id columns, default is true
    :param bool include_labels: Whether or not to include label columns, default is true
    :param bool error_column: Whether or not to include errors column, default is true
    :param Union[str, list, DataViewGroupBy] group_by: The Columns or column to group by
    :param str filter: The dataview pagination filter to save on the spec
    :param str container: When matching files, the container to match on
    :param str filename: When matching files, the filename pattern to match
    :param str analysis_label: When matching analysis files, the label match string
    :param str analysis_gear_name: When matching analysis files, the gear name match string
    :param str analysis_gear_version: When matching analysis files, the gear version match string
    :param bool sort: Option to sort results
    """

    def __init__(
        self,
        label=None,
        description=None,
        match=None,
        zip_files=None,
        columns=None,
        process_files=True,
        include_ids=True,
        include_labels=True,
        error_column=None,
        group_by=None,
        filter=None,
        container=None,
        filename=None,
        analysis_label=None,
        analysis_gear_name=None,
        analysis_gear_version=None,
        sort=True,
    ):
        self._label = label
        self._description = description
        self._columns = []
        self._file_columns = []
        self._file_container = None
        self._file_filter = None
        self._file_zip_filter = None
        self._file_format = None
        self._file_format_opts = {}
        self._file_match = match
        self._filter = filter

        if isinstance(group_by, str):
            self._group_by = DataViewGroupBy(columns=[DataViewGroupByColumn(src=group_by)])
        elif isinstance(group_by, list):
            self._group_by = DataViewGroupBy(columns=[DataViewGroupByColumn(src=col) for col in group_by])
        elif isinstance(group_by, DataViewGroupBy):
            self._group_by = group_by
        else:
            self._group_by = None

        self._process_files = process_files
        self._analysis_filter = None
        self._include_ids = include_ids
        self._include_labels = include_labels
        self._error_column = error_column
        self._missing_data_strategy = None
        self._sort = sort

        if zip_files is not None:
            self.zip_member_filter(zip_files)

        if filename is not None:
            self.files(
                container,
                filename,
                analysis_label=analysis_label,
                analysis_gear_name=analysis_gear_name,
                analysis_gear_version=analysis_gear_version,
            )

        # Add column/columns
        if isinstance(columns, list):
            for column in columns:
                if isinstance(column, tuple):
                    self.column(*column)
                else:
                    self.column(column)
        elif isinstance(columns, tuple):
            self.column(*columns)
        elif columns is not None:
            self.column(columns)

    def build(self):
        """Build the DataView constructed with this builder.

        :return: The constructed DataView
        """
        file_spec = None
        if self._file_container and self._file_filter:
            file_spec = DataViewFileSpec(
                container=self._file_container,
                analysis_filter=self._analysis_filter,
                filter=self._file_filter,
                zip_member=self._file_zip_filter,
                match=self._file_match,
                format=self._file_format,
                format_options=self._file_format_opts,
                process_files=self._process_files,
                columns=self._file_columns,
            )
        elif (
            self._file_container
            or self._file_filter
            or self._file_columns
            or self._file_zip_filter
            or self._file_format
            or self._analysis_filter
        ):
            raise ValueError("Both file_container and file_filter are required to process files!")
        self._check_missing_data_strategy_and_error_column(self._missing_data_strategy, self._error_column)
        return DataView(
            label=self._label,
            description=self._description,
            columns=self._columns,
            group_by=self._group_by,
            file_spec=file_spec,
            filter=self._filter,
            include_ids=self._include_ids,
            include_labels=self._include_labels,
            error_column=self._error_column,
            missing_data_strategy=self._missing_data_strategy,
            sort=self._sort,
        )

    def label(self, label):
        """Set the label for this data view.

        :param str label: The new label for the data view.
        :return: self
        """
        self._label = label

    def description(self, description):
        """Set the description for this data view.

        :param str description: The new description for the data view.
        :return: self
        """
        self._description = description
        return self

    def public(self, value=True):
        """Set whether or not this data view should be made public.

        :param bool value: True if the data view should be public. (default)
        :return: self
        """
        self._public = value
        return self

    def filter(self, filter):
        """Set the filter for this data view.

        :param str filter: The dataview pagination filter to save on the spec.
        :return: self
        """
        self._filter = filter
        return self

    def group_by(self, src, dst=None):
        """Define a column for this data view.

        :param str src: The source field, or column alias name.
        :param str dst: The optional destination field (defaults to source)
        :return: self
        """
        src, dst, _ = self._preprocess_column(src, dst, None)
        if self._group_by is None:
            self._group_by = DataViewGroupBy(columns=[])
        self._group_by.columns.append(DataViewGroupByColumn(src=src, dst=dst))
        return self

    def column(self, src, dst=None, type=None, accumulator=None, expr=None):
        """Define a column for this data view.

        :param str src: The source field, or column alias name.
        :param str dst: The optional destination field (defaults to source)
        :param str type: The optional type for this column, one of: int, float, string bool.
        :param str accumulator: The optional accumulation operation for group by aggregation.
        :param str expr: The optional expression to apply
        :return: self
        """
        src, dst, type = self._preprocess_column(src, dst, type)
        self._columns.append(DataViewColumnSpec(src=src, dst=dst, type=type, accumulator=accumulator, expr=expr))
        return self

    def files(
        self,
        container,
        filename,
        analysis_label=None,
        analysis_gear_name=None,
        analysis_gear_version=None,
    ):
        """Set filter for matching files

        Container is one of project, subject, session, acquisition
        Filename filters can use the ``(*, ?)`` wildcards
        Analysis filters also support wildcards

        :param str container: When matching files, the container to match on: one of project, subject, session, acquisition
        :param str filename: When matching files, the filename pattern to match
        :param str analysis_label: When matching analysis files, the label match string
        :param str analysis_gear_name: When matching analysis files, the gear name match string
        :param str analysis_gear_version: When matching analysis files, the gear version match string
        :return: self
        """
        if not container or not filename:
            raise ValueError("Both container and filename are required for file matching")

        self._file_container = container
        self._file_filter = DataViewNameFilterSpec(value=filename)

        if analysis_label or analysis_gear_name or analysis_gear_version:
            self.analysis_filter(
                label=analysis_label,
                gear_name=analysis_gear_name,
                gear_version=analysis_gear_version,
            )

        return self

    def file_column(self, src, dst=None, type=None):
        """Define a column to extract from a file.

        :param str src: The source field.
        :param str dst: The optional destination field (defaults to source)
        :param str type: The optional type for this column, one of: int, float, string bool.
        :return: self
        """
        self._file_columns.append(DataViewColumnSpec(src=src, dst=dst, type=type))
        return self

    def file_container(self, container):
        """Set the container where files should be matched.

        :param str container: The container name, one of: project, subject, session, acquisition
        :return: self
        """
        self._file_container = container
        return self

    def file_match(self, match_value):
        """Set the resolution strategy if multiple matching files or analyses are encountered.

        :param str match_value: The file match type, one of: first, last, newest, oldest, all
        :return: self
        """
        self._file_match = match_value
        return self

    def analysis_filter(self, label=None, gear_name=None, gear_version=None, regex=False):
        """Set the filter to use for matching analyses. If this is set, then analyses files will be matched instead of container.

        :param str label: The label match string, wildcards ``(*, ?)`` are supported.
        :param str gear_name: The gear name match string, wildcards ``(*, ?)`` are supported.
        :param str gear_version: The gear version match string, wildcards ``(*, ?)`` are supported.
        :param bool regex: Whether to treat the match string as a regular expression (default is False)
        :return: self
        """
        if not self._analysis_filter:
            self._analysis_filter = DataViewAnalysisFilterSpec()

        if label:
            self._analysis_filter.label = DataViewNameFilterSpec(value=label, regex=regex)
        if gear_name:
            self._analysis_filter.gear_name = DataViewNameFilterSpec(value=gear_name, regex=regex)
        if gear_version:
            self._analysis_filter.gear_version = DataViewNameFilterSpec(value=gear_version, regex=regex)
        return self

    def file_filter(self, value=None, regex=False):
        """Set the filter to use for matching files.

        :param str value: The filename match string, wildcards ``(*, ?)`` are supported.
        :param bool regex: Whether to treat the match string as a regular expression (default is False)
        :return: self
        """
        self._file_filter = DataViewNameFilterSpec(value=value, regex=regex)
        return self

    def zip_member_filter(self, value=None, regex=False, match=None):
        """Set the filter to use for matching members of a zip file.

        :param str value: The filename match string, wildcards ``(*, ?)`` are supported.
        :param bool regex: Whether to treat the match string as a regular expression (default is False)
        :param str match: The file match type, one of: first, last, newest, oldest, all
        :return: self
        """
        self._file_zip_filter = DataViewZipFilterSpec(value=value, regex=regex, match=match)
        return self

    def file_format(self, format_name):
        """Set the expected format of files to read.

        NOTE: This shouldn't be needed very often. If not specified, autodetect will be used for processing files.

        :param str format_name: The expected file format, one of: csv, tsv, json.
        :return: self
        """
        self._file_format = format_name
        return self

    def file_format_options(self, **kwargs):
        """Set additional options for the file format. (e.g. arguments to be passed to csv reader function)

        :param dict kwargs: Arguments to pass to the file reader
        :return: self
        """
        self._file_format_opts.update(kwargs)
        return self

    def process_files(self, value):
        """Set whether or not to process files (default is True)

        By default, files will be read and return a row for each row in the file. If you just want file attributes or info
        instead, you can set this to False.

        :param bool value: Whether or not to process files
        :return: self
        """
        self._process_files = value
        return self

    def include_labels(self, value=True):
        """Set whether or not to include the label columns by default.

        :param bool value: Whether or not to include labels (default is true)
        :return: self
        """
        self._include_labels = value
        return self

    def include_ids(self, value=True):
        """Set whether or not to include the id columns by default.

        :param bool value: Whether or not to include ids (default is true)
        :return: self
        """
        self._include_ids = value
        return self

    def error_column(self, value=True):
        """Set whether or not to include error column by default.

        :param bool value: Whether or not to include errors (default is true)
        :return: self
        """
        self._error_column = value
        return self

    def missing_data_strategy(self, value):
        """Set the resolution strategy if rows are missing data for a column. The default is to replace the column value with None.

        :param str value: The strategy to use for missing data, one of: none, drop-row
        :return: self
        """
        self._missing_data_strategy = value
        return self

    def sort(self, value=True):
        """Set the option to opt out of sorting the rows by setting false

        :param bool value: Opt out of sorting
        :return: self
        """
        self._sort = value
        return self

    def _check_missing_data_strategy_and_error_column(self, missing_data_strategy=None, error_column=None):
        """
        If missing_data_strategy is 'drop-row' and if the user doesn't explicitly
        set 'error_column'" to True, 'error_column' should be 'False'.
        """
        if error_column is None:
            self._error_column = missing_data_strategy != "drop-row"

    def _preprocess_column(self, src, dst, type):
        """If file is in src name, then select but don't process files"""
        src_parts = src.split(".")
        file_idx = src_parts.index("file") if "file" in src_parts else -1
        if file_idx < 1:
            return src, dst, type

        analysis_container = False
        file_container = src_parts[0]
        if file_idx > 1:
            analysis_container = True

        # If we currently have a file filter, validate
        if self._file_container:
            if file_container != self._file_container:
                raise ValueError(
                    "Can only select files one one container ({} already selected)".format(self._file_container)
                )
            if analysis_container and not self._analysis_filter:
                raise ValueError(
                    "Can only select files one one container ({} already selected)".format(self._file_container)
                )
            elif self._analysis_filter and not analysis_container:
                raise ValueError(
                    "Can only select files one one container ({} analyses already selected)".format(
                        self._file_container
                    )
                )
        else:
            # Setup the file matches.
            # In this mode, we match all files, and drop any rows with missing data
            self._file_container = file_container
            self._file_filter = DataViewNameFilterSpec(value="*")
            if analysis_container:
                label_filter = DataViewNameFilterSpec(value="*")
                self._analysis_filter = DataViewAnalysisFilterSpec(label=label_filter)

            self._file_match = "all"
            self._error_column = False
            self._missing_data_strategy = "drop-row"
            self._process_files = False

        if not dst:
            dst = src
        src = ".".join(src_parts[file_idx:])

        return src, dst, type
