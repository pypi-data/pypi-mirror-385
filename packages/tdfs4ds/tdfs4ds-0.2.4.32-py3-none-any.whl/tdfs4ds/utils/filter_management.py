import datetime
import numpy as np  # Needed for np.datetime64 handling in get_date_in_the_past
import teradataml as tdml
import tdfs4ds
from tdfs4ds import logger


def get_hidden_table_name(table_name):
    """
    Return the backing 'hidden' table name for a public view/table.

    Args:
        table_name (str): Public-facing table/view name.

    Returns:
        str: The corresponding hidden table name (suffix '_HIDDEN').
    """
    return table_name + "_HIDDEN"


class FilterManager:
    """
    Manage dynamic, filter-driven views over a Teradata table.

    This class maintains a hidden table that stores one or more *filters* (one row
    per filter definition) and exposes a public view whose SELECT projects the
    columns from the hidden table for the currently-active filter ID. You can load
    new filters, switch which filter the view points at, prune older filters, and
    (optionally) include a time dimension via a `BUSINESS_DATE` column.

    Attributes:
        schema_name (str): Database schema that contains the hidden table and public view.
        table_name (str): Hidden table name where filter rows are stored.
        view_name (str): Public view name pointing at the currently active filter row.
        filter_id_name (str): Column name containing the filter identifier (default 'filter_id').
        nb_filters (int | None): Number of filters currently stored (max filter_id). Populated when objects exist.
        col_names (list[str] | None): Columns projected by the view (excludes filter-id and time column).
        time_filtering (bool | None): Whether a `BUSINESS_DATE` column is present/used.
    """

    def __init__(self, table_name, schema_name, filter_id_name="filter_id", time_column=None):
        """
        Initialize the FilterManager.

        If the hidden table/view already exist, metadata (column names, maximum
        filter id, and time filtering status) are detected and cached. If they do
        not exist yet, attributes are initialized but no objects are created until
        `load_filter()` is called.

        Args:
            table_name (str): Public view name to maintain.
            schema_name (str): Schema where the view and hidden table live.
            filter_id_name (str, optional): Name of the filter id column. Defaults to 'filter_id'.
            time_column (str, optional): If provided, indicates the source column
                in incoming DataFrames to copy into `BUSINESS_DATE` during `load_filter()`.
                (Note: this parameter is remembered but the actual `BUSINESS_DATE`
                column is only created/used when `load_filter(time_column=...)` is called.)
        """
        self.schema_name = schema_name
        self.table_name = get_hidden_table_name(table_name)
        self.view_name = table_name
        self.filter_id_name = filter_id_name
        self.nb_filters = None
        self.col_names = None
        self.time_filtering = None
        self._init_time_column = time_column  # remember user hint for later `load_filter` calls

        logger.debug(
            "Initializing FilterManager",
            extra={
                "schema_name": self.schema_name,
                "view_name": self.view_name,
                "table_name": self.table_name,
                "filter_id_name": self.filter_id_name,
            },
        )

        if self._exists():
            logger.info(
                "Existing filter artifacts detected.",
                extra={"schema_name": self.schema_name, "view_name": self.view_name, "table_name": self.table_name},
            )
            df = tdml.DataFrame(tdml.in_schema(self.schema_name, self.table_name))
            # First column is assumed to be the filter id
            self.filter_id_name = df.columns[0]
            self.nb_filters = tdml.execute_sql(
                f"SEL MAX({self.filter_id_name}) AS nb_filters FROM {self.schema_name}.{self.table_name}"
            ).fetchall()[0][0]
            self.time_filtering = self._istimefiltering()
            self.col_names = df.columns[2:] if self.time_filtering else df.columns[1:]
            logger.debug(
                "Detected existing configuration.",
                extra={
                    "filter_id_name": self.filter_id_name,
                    "nb_filters": self.nb_filters,
                    "time_filtering": self.time_filtering,
                    "col_names": list(self.col_names),
                },
            )
        else:
            logger.info(
                "No existing filter artifacts found; will be created by load_filter().",
                extra={"schema_name": self.schema_name, "view_name": self.view_name, "table_name": self.table_name},
            )

    def _istimefiltering(self):
        """
        Determine if the hidden table includes a `BUSINESS_DATE` column.

        Returns:
            bool: True if the hidden table contains `BUSINESS_DATE`, else False.
        """
        df = tdml.DataFrame(tdml.in_schema(self.schema_name, self.table_name))
        has_time = "BUSINESS_DATE" in df.columns
        logger.debug("Time filtering detected: %s", has_time)
        return has_time

    def _exists(self):
        """
        Check if either the public view or hidden table already exist in the schema.

        Returns:
            bool: True if the hidden table or view exists, else False.
        """
        existing_tables = [
            x.lower().replace('"', "") for x in tdml.db_list_tables(schema_name=self.schema_name).TableName.values
        ]
        exists = self.view_name.lower() in existing_tables or self.table_name.lower() in existing_tables
        logger.debug("Existence check", extra={"exists": exists, "objects": existing_tables})
        return exists

    def load_filter(self, df, primary_index=None, time_column=None):
        """
        Load a new filter set into the hidden table and (re)point the public view at filter_id=1.

        Each row in `df` is assigned a deterministic `filter_id` based on ROW_NUMBER() over the
        ordered set of its columns (plus `BUSINESS_DATE` when time filtering is enabled). If
        `time_column` is provided, values from that column are copied into `BUSINESS_DATE` and the
        view will include that time dimension.

        Args:
            df (DataFrame): Incoming filter definitions (one row per filter).
            primary_index (list[str], optional): Primary index columns for the hidden table.
                Defaults to ['filter_id'] when omitted.
            time_column (str, optional): Name of the time column in `df` to map into `BUSINESS_DATE`.
                If provided, time-based filtering is enabled.

        Raises:
            ValueError: If `time_column` is provided but not present in `df`.
        """
        logger.info("Loading filters", extra={"rows": len(df), "time_column": time_column})

        if time_column and time_column not in df.columns:
            logger.error("Specified time_column not found in DataFrame.", extra={"time_column": time_column})
            raise ValueError(f"Specified time_column '{time_column}' not found in DataFrame columns.")

        # Determine projection and ordering columns
        if time_column is None:
            self.time_filtering = False
            self.col_names = df.columns
            all_columns = ",".join(df.columns)
            collect_stats = ",".join([f"COLUMN ({c})" for c in df.columns])
        else:
            self.time_filtering = True
            self.col_names = [c for c in df.columns if c != time_column]
            all_columns = ",".join(["BUSINESS_DATE"] + self.col_names)
            collect_stats = ",".join([f"COLUMN ({c})" for c in ["BUSINESS_DATE"] + self.col_names])

        logger.debug(
            "Computed load_filter columns",
            extra={"time_filtering": self.time_filtering, "col_names": list(self.col_names), "all_columns": all_columns},
        )

        # Build the filter rows with an ordered ROW_NUMBER()
        if time_column is None:
            df_filter = df.assign(
                **{
                    self.filter_id_name: tdml.sqlalchemy.literal_column(
                        f"ROW_NUMBER() OVER (PARTITION BY 1 ORDER BY {all_columns})", tdml.BIGINT()
                    )
                }
            )[[self.filter_id_name] + list(df.columns)]
        else:
            df_filter = df.assign(
                **{
                    self.filter_id_name: tdml.sqlalchemy.literal_column(
                        f"ROW_NUMBER() OVER (PARTITION BY 1 ORDER BY {all_columns})", tdml.BIGINT()
                    ),
                    "BUSINESS_DATE": df[time_column],
                }
            )[[self.filter_id_name, "BUSINESS_DATE"] + self.col_names]

        # Persist to hidden table
        if primary_index is None:
            primary_index = [self.filter_id_name]

        logger.debug("Writing hidden table", extra={"primary_index": primary_index})
        df_filter.to_sql(
            table_name=self.table_name,
            schema_name=self.schema_name,
            if_exists="replace",
            primary_index=primary_index,
        )

        # Create/replace public view with filter_id = 1
        view_sql = f"""
        REPLACE VIEW {self.schema_name}.{self.view_name} AS
        SEL {all_columns}
        FROM {self.schema_name}.{self.table_name}
        WHERE {self.filter_id_name} = 1
        """
        logger.debug("Replacing view for filter_id=1")
        tdml.execute_sql(view_sql)

        # Collect stats to help the optimizer
        stats_sql = f"""
        COLLECT STATISTICS USING NO SAMPLE AND NO THRESHOLD
               COLUMN ({self.filter_id_name})
        ,      {collect_stats}
        ON {self.schema_name}.{self.table_name}
        """
        logger.debug("Collecting statistics on hidden table")
        tdml.execute_sql(stats_sql)

        self.nb_filters = tdml.execute_sql(
            f"SEL MAX({self.filter_id_name}) AS nb_filters FROM {self.schema_name}.{self.table_name}"
        ).fetchall()[0][0]
        logger.info("Filters loaded", extra={"nb_filters": self.nb_filters})

    def _drop(self):
        """
        Drop the public view and (optionally) the hidden table.

        If this manager does not own the hidden table (default), only the view is dropped.
        """
        # Drop the view (in our schema)
        existing = [x.lower().replace('"', "") for x in tdml.db_list_tables(schema_name=self.schema_name).TableName.values]
        if self.view_name.lower() in existing:
            logger.warning("Dropping view.", extra={"schema_name": self.schema_name, "view_name": self.view_name})
            tdml.db_drop_view(schema_name=self.schema_name, table_name=self.view_name)
        else:
            logger.info("View not found; nothing to drop.", extra={"schema_name": self.schema_name, "view_name": self.view_name})

        # Drop the hidden table only if we own it
        if getattr(self, "_owns_hidden", False):
            schema_tbl = getattr(self, "schema_name_for_table", self.schema_name)
            logger.warning(
                "Dropping hidden table (ownership acknowledged).",
                extra={"schema_name": schema_tbl, "table_name": self.table_name},
            )
            tdml.db_drop_table(schema_name=schema_tbl, table_name=self.table_name)
        else:
            logger.info("Hidden table not dropped (not owned).")


    def update(self, filter_id):
        """
        Repoint the public view to a different filter id.

        Args:
            filter_id (int): Target filter id to apply.

        Raises:
            ValueError: If filter artifacts do not exist yet.
        """
        logger.info("Updating active filter", extra={"filter_id": filter_id})

        if not self._exists():
            logger.error("Filter artifacts not initialized.")
            raise ValueError("The filter has not been initialized with load_filter() or has been deleted.")

        if self.time_filtering:
            select_cols = ",".join(["BUSINESS_DATE"] + list(self.col_names))
        else:
            select_cols = ",".join(self.col_names)

        query = f"""
        REPLACE VIEW {self.schema_name}.{self.view_name} AS
        SEL {select_cols}
        FROM {self.schema_name}.{self.table_name}
        WHERE {self.filter_id_name} = {filter_id}
        """
        logger.debug("Replacing view with new filter", extra={"query": query})
        tdml.execute_sql(query)

    def display(self):
        """
        Retrieve the current view contents as a `teradataml.DataFrame`.

        Returns:
            teradataml.DataFrame: Rows projected by the public view (current filter).
        """
        logger.debug("Fetching current view contents")
        return tdml.DataFrame(tdml.in_schema(self.schema_name, self.view_name))

    def get_all_filters(self):
        """
        Retrieve all filter rows from the hidden table.

        Returns:
            teradataml.DataFrame: Full set of stored filters.
        """
        logger.debug("Fetching all filters from hidden table")
        return tdml.DataFrame(tdml.in_schema(self.schema_name, self.table_name))

    def get_date_in_the_past(self):
        """
        Return the earliest business date/time from the *current view*.

        The method reads the first `BUSINESS_DATE` value from the current view
        and normalizes it to a `%Y-%m-%d %H:%M:%S` string. Requires that time
        filtering is enabled.

        Returns:
            str: Earliest datetime as formatted string ('YYYY-MM-DD HH:MM:SS').

        Raises:
            ValueError: If time-based filtering is not enabled.
        """
        logger.debug("Computing earliest BUSINESS_DATE from current view")

        if not self._istimefiltering():
            logger.error("Time filtering requested but not enabled.")
            raise ValueError("The filter manager is not filtering on time.")

        date_obj = self.display().to_pandas().reset_index().BUSINESS_DATE.values[0]

        if isinstance(date_obj, datetime.datetime):
            datetime_obj = date_obj
        elif isinstance(date_obj, datetime.date):
            datetime_obj = datetime.datetime.combine(date_obj, datetime.time.min)
        elif isinstance(date_obj, np.datetime64):
            # normalize to datetime (ms precision to avoid timezone pitfalls)
            datetime_obj = date_obj.astype("datetime64[ms]").astype(datetime.datetime)
        else:
            logger.error(
                "Unsupported BUSINESS_DATE type.",
                extra={"value": str(date_obj), "type": str(type(date_obj))},
            )
            raise TypeError(f"Unsupported BUSINESS_DATE type: {type(date_obj)}")

        output_string = datetime_obj.strftime("%Y-%m-%d %H:%M:%S")
        logger.debug("Earliest date computed", extra={"earliest": output_string})
        return output_string

    def get_current_filterid(self):
        """
        Extract the currently active filter id from the view DDL.

        Returns:
            int: Filter id parsed from the view's definition.

        Raises:
            ValueError: If the filter id cannot be parsed from the DDL.
        """
        logger.debug("Reading view DDL to extract current filter id")
        txt = tdfs4ds.utils.lineage.get_ddl(schema_name=self.schema_name, view_name=self.view_name)
        try:
            current = int(txt.split("\n")[-1].split("=")[1])
            logger.info("Current filter id extracted", extra={"filter_id": current})
            return current
        except Exception as exc:
            logger.exception("Failed to parse filter id from view DDL")
            raise ValueError("Unable to parse current filter id from view DDL.") from exc

    def print_view_ddl(self):
        """
        Log the view definition (DDL) for troubleshooting/traceability.
        """
        ddl = tdfs4ds.utils.lineage.get_ddl(schema_name=self.schema_name, view_name=self.view_name)
        logger.info("View DDL:\n%s", ddl)

    def prune_filter(self, filter_id=None):
        """
        Remove all filters with ids lower than `filter_id` and renumber remaining ones.

        If `filter_id` is omitted, the method uses the current filter id from the view.
        After pruning, filter ids are normalized so the smallest remaining id becomes 1,
        and the public view is repointed to filter_id=1.

        Args:
            filter_id (int, optional): Threshold id; rows with `{filter_id_name} < filter_id` are deleted.

        Returns:
            FilterManager: Self, to allow method chaining.
        """
        if filter_id is None:
            filter_id = self.get_current_filterid()

        logger.info("Pruning filters", extra={"threshold_filter_id": filter_id})

        delete_sql = f"DELETE {self.schema_name}.{self.table_name} WHERE {self.filter_id_name} < {filter_id}"
        update_sql = f"UPDATE {self.schema_name}.{self.table_name} SET {self.filter_id_name} = {self.filter_id_name} - {filter_id} + 1"

        logger.debug("Executing prune delete", extra={"sql": delete_sql})
        tdml.execute_sql(delete_sql)

        logger.debug("Executing prune renumber", extra={"sql": update_sql})
        tdml.execute_sql(update_sql)

        self.update(1)
        logger.info("Prune complete; active filter set to 1.")
        return self

    def clone_filter(self, source_filtermanager, filter_id_to_apply=1, take_ownership=False, clone_mode="soft", if_exists="error"):
        """
        Clone filter definitions from another FilterManager.

        Supports:
        - soft clone (default): just point to source _HIDDEN table
        - hard clone: copy the source _HIDDEN table and own the copy

        Args:
            source_filtermanager (FilterManager): Source FilterManager to clone.
            filter_id_to_apply (int, optional): Filter ID to activate. Default: 1.
            take_ownership (bool, optional): Whether this manager owns the cloned table (soft mode only).
            clone_mode (str, optional): "soft" or "hard". Default: "soft".
            if_exists (str, optional): Behavior if target hidden table already exists
                - "error" (default): raise an exception
                - "replace": drop and recreate
                - "skip": reuse existing table

        Returns:
            FilterManager

        Raises:
            ValueError: On invalid clone_mode or missing source.
        """
        if clone_mode not in ("soft", "hard"):
            raise ValueError("clone_mode must be 'soft' or 'hard'")
        if if_exists not in ("error", "replace", "skip"):
            raise ValueError("if_exists must be 'error', 'replace', or 'skip'")

        src_schema = source_filtermanager.schema_name
        src_hidden = source_filtermanager.table_name

        logger.info(
            "Cloning filter",
            extra={
                "mode": clone_mode,
                "source": f"{src_schema}.{src_hidden}",
                "target_view": f"{self.schema_name}.{self.view_name}"
            },
        )

        # Validate source exists
        existing_src = [t.lower() for t in tdml.db_list_tables(schema_name=src_schema).TableName.values]
        if src_hidden.lower() not in existing_src:
            raise ValueError(f"Source hidden filter table {src_schema}.{src_hidden} does not exist.")

        if clone_mode == "hard":
            # Hard clone requires a NEW hidden table in this schema
            self.table_name = get_hidden_table_name(self.view_name)
            existing_dest = [t.lower() for t in tdml.db_list_tables(schema_name=self.schema_name).TableName.values]

            # Handle table existence
            if self.table_name.lower() in existing_dest:
                if if_exists == "error":
                    raise RuntimeError(f"Target table {self.schema_name}.{self.table_name} already exists.")
                elif if_exists == "replace":
                    logger.warning(f"Replacing existing table {self.schema_name}.{self.table_name}")
                    tdml.db_drop_table(schema_name=self.schema_name, table_name=self.table_name)
                elif if_exists == "skip":
                    logger.info(f"Skipping clone, using existing {self.schema_name}.{self.table_name}")
            if self.table_name.lower() not in existing_dest or if_exists == "replace":
                # Create cloned table
                logger.info(f"Creating cloned table {self.schema_name}.{self.table_name}")
                create_sql = f"""
                CREATE TABLE {self.schema_name}.{self.table_name} AS
                    (SELECT * FROM {src_schema}.{src_hidden})
                WITH DATA
                """
                tdml.execute_sql(create_sql)

            self._owns_hidden = True  # Hard clones always own their copy
            target_schema = self.schema_name

        else:
            # Soft clone: link to source
            logger.info("Soft clone: linking to source table")
            self.table_name = src_hidden
            self._owns_hidden = bool(take_ownership)
            target_schema = src_schema  # view selects from source schema

        # Load metadata
        df = tdml.DataFrame(tdml.in_schema(target_schema, self.table_name))
        self.filter_id_name = df.columns[0]
        self.time_filtering = "BUSINESS_DATE" in df.columns
        self.col_names = df.columns[2:] if self.time_filtering else df.columns[1:]
        self.nb_filters = df.shape[0]

        # Rebuild view
        select_cols = ",".join((["BUSINESS_DATE"] if self.time_filtering else []) + list(self.col_names))
        view_sql = f"""
        REPLACE VIEW {self.schema_name}.{self.view_name} AS
        SELECT {select_cols}
        FROM {target_schema}.{self.table_name}
        WHERE {self.filter_id_name} = {int(filter_id_to_apply)}
        """
        tdml.execute_sql(view_sql)

        logger.info(f"Clone complete → Active filter_id={filter_id_to_apply}")
        return self


    def take_ownership(self):
        """
        Take ownership of the currently linked hidden filter table.

        This enables this FilterManager instance to manage (and potentially drop)
        the hidden table via `_drop()` or future maintenance methods.

        Returns:
            FilterManager: self (for chaining)
        """
        logger.warning(
            "Ownership taken for hidden table. This manager may now drop or modify it.",
            extra={
                "schema_name": getattr(self, "schema_name_for_table", self.schema_name),
                "table_name": self.table_name
            }
        )
        self._owns_hidden = True
        return self
