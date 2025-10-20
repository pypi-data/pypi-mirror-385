"""
Bulk data fetching with automatic pagination.

Fetch large datasets by breaking key lists into manageable chunks.
Handles thousands of keys efficiently with concurrent processing.
"""

import asyncio
import logging
import math
from typing import Any, Dict, List, Literal, Optional, Sequence, Tuple, Union, cast

from .client import SDAClient
from .exceptions import SoilDBError
from .query import Query, QueryBuilder
from .response import SDAResponse
from .sanitization import sanitize_sql_numeric, sanitize_sql_string_list
from .schema_system import SCHEMAS, get_schema

logger = logging.getLogger(__name__)

# Common SSURGO tables and their typical key columns
TABLE_KEY_MAPPING = {
    # Core tables
    "legend": "lkey",
    "mapunit": "mukey",
    "component": "cokey",
    "chorizon": "chkey",
    "chfrags": "chfragkey",
    "chtexturegrp": "chtgkey",
    "chtexture": "chtkey",
    # Spatial tables
    "mupolygon": "mukey",
    "sapolygon": "areasymbol",  # or lkey
    "mupoint": "mukey",
    "muline": "mukey",
    "featpoint": "featkey",
    "featline": "featkey",
    # Interpretation tables
    "cointerp": "cokey",
    "chinterp": "chkey",
    "copmgrp": "copmgrpkey",
    "corestrictions": "reskeyid",
    # Administrative
    "sacatalog": "areasymbol",
    "laoverlap": "lkey",
    "legendtext": "lkey",
}


class FetchError(SoilDBError):
    """Raised when key-based fetching fails."""

    def __str__(self) -> str:
        """Return helpful fetch error message."""
        if "Unknown table" in self.message:
            return f"{self.message} Supported tables include: {', '.join(TABLE_KEY_MAPPING.keys())}"
        elif "No responses to combine" in self.message:
            return "No data was returned from the fetch operation. This may indicate invalid keys or an empty result set."
        return self.message


async def fetch_by_keys(
    keys: Union[Sequence[Union[str, int]], str, int],
    table: str,
    key_column: Optional[str] = None,
    columns: Optional[Union[str, List[str]]] = None,
    chunk_size: int = 1000,
    include_geometry: bool = False,
    client: Optional[SDAClient] = None,
) -> SDAResponse:
    """
    Fetch data from a table using a list of key values with pagination.

    Similar to fetchSDA_spatial() in R soilDB, this function efficiently handles
    large lists of keys by breaking them into manageable chunks and combining results.

    Performance Notes:
    - Uses concurrent requests for chunked fetches (chunk_size < total_keys)
    - Recommended chunk_size: 500-2000 keys depending on key length and network
    - For very large datasets (>10,000 keys), consider processing in batches
    - Geometry inclusion increases response size significantly

    Args:
        keys: Key value(s) to fetch (single key or list of keys, e.g., mukeys, cokeys, areasymbols)
        table: Target SSURGO table name
        key_column: Column name for the key (auto-detected if None)
        columns: Columns to select (default: all columns)
        chunk_size: Number of keys to process per query (default: 1000, recommended: 500-2000)
        include_geometry: Whether to include geometry as WKT for spatial tables
        client: Optional SDA client instance

    Returns:
        SDAResponse with combined results from all chunks

    Examples:
        # Fetch map unit data for specific mukeys
        >>> mukeys = [123456, 123457, 123458]
        >>> response = await fetch_by_keys(mukeys, "mapunit")
        >>> df = response.to_pandas()

        # Fetch component data with specific columns
        >>> cokeys = ["12345:1", "12345:2", "12346:1"]
        >>> response = await fetch_by_keys(
        ...     cokeys, "component", columns=["cokey", "compname", "comppct_r"]
        ... )

        # Fetch spatial data with geometry
        >>> response = await fetch_by_keys(
        ...     mukeys, "mupolygon", include_geometry=True
        ... )
        >>> gdf = response.to_geodataframe()  # If GeoPandas available

        # Fetch survey area polygons by areasymbol
        >>> areas = ["IA109", "IA113", "MN001"]
        >>> response = await fetch_by_keys(areas, "sapolygon")
    """
    if isinstance(keys, (str, int)):
        keys = cast(List[Union[str, int]], [keys])

    keys_list = cast(List[Union[str, int]], keys)

    if not keys_list:
        raise FetchError("The 'keys' parameter cannot be an empty list.")

    if client is None:
        raise TypeError("client parameter is required")

    # Auto-detect key column if not provided
    if key_column is None:
        key_column = TABLE_KEY_MAPPING.get(table.lower())
        if key_column is None:
            raise FetchError(
                f"Unknown table '{table}'. Please specify key_column parameter."
            )

    if columns is None:
        select_columns = "*"
    elif isinstance(columns, list):
        select_columns = ", ".join(columns)
    else:
        select_columns = columns

    # Add geometry column for spatial tables if requested
    if include_geometry:
        geom_column = _get_geometry_column_for_table(table)
        if geom_column:
            if select_columns == "*":
                select_columns = f"*, {geom_column}.STAsText() as geometry"
            else:
                select_columns = (
                    f"{select_columns}, {geom_column}.STAsText() as geometry"
                )

    key_strings = [_format_key_for_sql(key) for key in keys_list]

    num_chunks = math.ceil(len(key_strings) / chunk_size)

    if num_chunks == 1:
        # Single query for small key lists
        return await _fetch_chunk(
            key_strings, table, key_column, select_columns, client
        )
    else:
        # Multiple queries for large key lists
        logger.debug(
            f"Fetching {len(keys_list)} keys in {num_chunks} chunks of {chunk_size}"
        )

        # Create chunks
        chunks = [
            key_strings[i : (i + chunk_size)]
            for i in range(0, len(key_strings), chunk_size)
        ]

        # Execute all chunks concurrently
        chunk_tasks = [
            _fetch_chunk(chunk_keys, table, key_column, select_columns, client)
            for chunk_keys in chunks
        ]

        chunk_responses = await asyncio.gather(*chunk_tasks)

        # Combine all responses
        return _combine_responses(chunk_responses)


async def _fetch_chunk(
    key_strings: List[str],
    table: str,
    key_column: str,
    select_columns: str,
    client: SDAClient,
) -> SDAResponse:
    """Fetch a single chunk of keys."""
    # Build IN clause
    keys_in_clause = ", ".join(key_strings)
    where_clause = f"{key_column} IN ({keys_in_clause})"

    # Build and execute query
    query = (
        Query()
        .select(*[col.strip() for col in select_columns.split(",")])
        .from_(table)
        .where(where_clause)
    )

    return await client.execute(query)


def _combine_responses(responses: List[SDAResponse]) -> SDAResponse:
    """Combine multiple SDAResponse objects into one."""
    if not responses:
        raise FetchError("No responses to combine")

    if len(responses) == 1:
        return responses[0]

    # Combine data from all responses
    combined_data = []
    for response in responses:
        combined_data.extend(response.data)

    # Create new response with combined data
    # Reconstruct the raw data format that SDAResponse expects
    first_response = responses[0]

    # Build the combined table in SDA format
    combined_table = []

    # Add the header row (column names)
    combined_table.append(first_response.columns)

    # Add the metadata row
    combined_table.append(first_response.metadata)

    # Add all the combined data rows
    combined_table.extend(combined_data)

    # Create new raw data structure
    combined_raw_data = {"Table": combined_table}

    # Create and return new SDAResponse
    return SDAResponse(combined_raw_data)


def _format_key_for_sql(key: Union[str, int]) -> str:
    """Format a key value for use in SQL IN clause."""
    if isinstance(key, str):
        # Escape single quotes and wrap in quotes
        escaped_key = key.replace("'", "''")
        return f"'{escaped_key}'"
    else:
        # Numeric keys don't need quotes
        return str(key)


def _get_geometry_column_for_table(table: str) -> Optional[str]:
    """Get the geometry column name for a spatial table."""
    geometry_columns = {
        "mupolygon": "mupolygongeo",
        "sapolygon": "sapolygongeo",
        "mupoint": "mupointgeo",
        "muline": "mulinegeo",
        "featpoint": "featpointgeo",
        "featline": "featlinegeo",
    }
    return geometry_columns.get(table.lower())


# Specialized functions for common use cases
async def fetch_mapunit_polygon(
    mukeys: Union[List[Union[str, int]], Union[str, int]],
    columns: Optional[Union[str, List[str]]] = None,
    include_geometry: bool = True,
    chunk_size: int = 1000,
    client: Optional[SDAClient] = None,
) -> SDAResponse:
    """
    Fetch map unit polygon data for a list of mukeys.

    Performance Notes:
    - Geometry data significantly increases response size and processing time
    - For large areas, consider using smaller chunk_size (500-1000)
    - Polygon geometries can be very large; consider bbox filtering first

    Args:
        mukeys: Map unit key(s) (single key or list of keys)
        columns: Columns to select (default: key columns from schema + geometry)
        include_geometry: Whether to include polygon geometry as WKT
        chunk_size: Chunk size for pagination (recommended: 500-1000 for geometry)
        client: Optional SDA client

    Returns:
        SDAResponse with map unit polygon data
    """
    # Handle single mukey values for convenience
    if not isinstance(mukeys, list):
        mukeys = [mukeys]

    if columns is None:
        # Use schema-based default columns for mupolygon table
        schema = get_schema("mupolygon")
        columns = schema.get_default_columns() if schema else []

    return await fetch_by_keys(
        mukeys, "mupolygon", "mukey", columns, chunk_size, include_geometry, client
    )


async def fetch_component_by_mukey(
    mukeys: Union[List[Union[str, int]], Union[str, int]],
    columns: Optional[Union[str, List[str]]] = None,
    chunk_size: int = 1000,
    client: Optional[SDAClient] = None,
    auto_schema: bool = False,
) -> SDAResponse:
    """
    Fetch component data for a list of mukeys with optional schema auto-registration.

    Performance Notes:
    - Components are the most numerous SSURGO entities (often 1000s per survey area)
    - Use chunk_size of 500-1000 for large mukey lists
    - Consider filtering for major components only if not needed

    Args:
        mukeys: Map unit key(s) (single key or list of keys)
        columns: Columns to select (default: key component columns from schema)
        chunk_size: Chunk size for pagination (recommended: 500-1000)
        client: Optional SDA client
        auto_schema: If True, automatically creates and registers schema from
                    SDA response metadata. Useful for custom tables or new columns

    Returns:
        SDAResponse with component data

    Examples:
        # Basic usage
        response = await fetch_component_by_mukey("123456")

        # With auto schema registration
        response = await fetch_component_by_mukey("123456", auto_schema=True)

        # Custom columns
        response = await fetch_component_by_mukey(
            "123456", columns=["cokey", "compname", "taxclname"]
        )
    """
    # Handle single mukey values for convenience
    if not isinstance(mukeys, list):
        mukeys = [mukeys]

    if columns is None:
        # Use schema-based default columns for component table
        schema = get_schema("component")
        if schema:
            columns = schema.get_default_columns() + ["mukey"]
        elif auto_schema:
            # If auto_schema is enabled and no schema exists, select all columns
            # to get complete metadata for schema inference
            columns = "*"
        else:
            columns = ["mukey"]

    response = await fetch_by_keys(
        mukeys, "component", "mukey", columns, chunk_size, False, client
    )

    if auto_schema and "component" not in SCHEMAS:
        from . import schema_inference

        schema_inference.auto_register_schema(response, "component")

    return response


async def fetch_chorizon_by_cokey(
    cokeys: Union[List[Union[str, int]], Union[str, int]],
    columns: Optional[Union[str, List[str]]] = None,
    chunk_size: int = 1000,
    client: Optional[SDAClient] = None,
) -> SDAResponse:
    """
    Fetch chorizon data for a list of cokeys.

    Performance Notes:
    - Horizon data includes detailed soil properties (texture, chemistry, etc.)
    - Each component typically has 3-7 horizons; expect large result sets
    - Use chunk_size of 200-500 for large cokey lists

    Args:
        cokeys: Component key(s) (single key or list of keys)
        columns: Columns to select (default: key chorizon columns from schema)
        chunk_size: Chunk size for pagination (recommended: 200-500)
        client: Optional SDA client

    Returns:
        SDAResponse with chorizon data
    """
    # Handle single cokey values for convenience
    if not isinstance(cokeys, list):
        cokeys = [cokeys]

    if columns is None:
        # Use schema-based default columns for chorizon table
        schema = get_schema("chorizon")
        columns = schema.get_default_columns() if schema else []

    return await fetch_by_keys(
        cokeys, "chorizon", "cokey", columns, chunk_size, False, client
    )


async def fetch_survey_area_polygon(
    areasymbols: Union[List[str], str],
    columns: Optional[Union[str, List[str]]] = None,
    include_geometry: bool = True,
    chunk_size: int = 1000,
    client: Optional[SDAClient] = None,
) -> SDAResponse:
    """
    Fetch survey area polygon data for a list of area symbols.

    Performance Notes:
    - Survey area boundaries are large polygons; geometry data is substantial
    - Most use cases only need a few survey areas at a time
    - Consider tabular queries first, then fetch geometry only when needed

    Args:
        areasymbols: Survey area symbol(s) (single symbol or list of symbols)
        columns: Columns to select (default: key columns + geometry)
        include_geometry: Whether to include polygon geometry as WKT
        chunk_size: Chunk size for pagination (usually not needed for survey areas)
        client: Optional SDA client

    Returns:
        SDAResponse with survey area polygon data
    """
    # Handle single areasymbol values for convenience
    if not isinstance(areasymbols, list):
        areasymbols = [areasymbols]

    if columns is None:
        columns = "areasymbol, spatialversion, lkey"

    return await fetch_by_keys(
        areasymbols,
        "sapolygon",
        "areasymbol",
        columns,
        chunk_size,
        include_geometry,
        client,
    )


async def fetch_pedons_by_bbox(
    bbox: Tuple[float, float, float, float],
    columns: Optional[List[str]] = None,
    chunk_size: int = 1000,
    return_type: Literal["sitedata", "combined", "soilprofilecollection"] = "sitedata",
    client: Optional[SDAClient] = None,
) -> Union[SDAResponse, Dict[str, Any], Any]:
    """
    Fetch pedon site data within a geographic bounding box with flexible return types.

    Similar to fetchLDM() in R soilDB, this function retrieves laboratory-analyzed
    soil profiles (pedons) within a specified geographic area. The return type
    can be customized to return site data only, combined site and horizon data,
    or a SoilProfileCollection object.

    Args:
        bbox: Bounding box as (min_lon, min_lat, max_lon, max_lat)
        columns: List of columns to return for site data. If None, returns basic pedon columns
        chunk_size: Number of pedons to process per query (for pagination when fetching horizons)
        return_type: Type of return value (default: "sitedata")
            - "sitedata": Returns only site data as SDAResponse
            - "combined": Returns dict with keys "site" (SDAResponse) and "horizons" (SDAResponse)
            - "soilprofilecollection": Returns a SoilProfileCollection object with site and horizon data
        client: Optional SDA client instance

    Returns:
        Depending on return_type:
        - "sitedata": SDAResponse containing pedon site data only
        - "combined": Dict with keys "site" (SDAResponse) and "horizons" (SDAResponse)
        - "soilprofilecollection": SoilProfileCollection object

    Raises:
        TypeError: If client parameter is required but not provided
        ImportError: If soilprofilecollection is requested but not installed
        ValueError: If return_type is invalid

    Examples:
        # Fetch pedons in California's Central Valley - site data only (default)
        >>> bbox = (-122.0, 36.0, -118.0, 38.0)
        >>> response = await fetch_pedons_by_bbox(bbox)
        >>> df = response.to_pandas()

        # Fetch site and horizon data separately
        >>> result = await fetch_pedons_by_bbox(bbox, return_type="combined")
        >>> site_df = result["site"].to_pandas()
        >>> horizons_df = result["horizons"].to_pandas()

        # Fetch complete pedon profiles as SoilProfileCollection
        >>> spc = await fetch_pedons_by_bbox(bbox, return_type="soilprofilecollection")
        >>> # spc is now a soilprofilecollection.SoilProfileCollection object

        # Get horizon data for returned pedons (manual approach)
        >>> site_response = await fetch_pedons_by_bbox(bbox)
        >>> pedon_keys = site_response.to_pandas()["pedon_key"].unique().tolist()
        >>> horizons = await fetch_pedon_horizons(pedon_keys, client=client)
    """
    if return_type not in ["sitedata", "combined", "soilprofilecollection"]:
        raise ValueError(
            f"Invalid return_type: {return_type!r}. Must be one of: "
            "'sitedata', 'combined', 'soilprofilecollection'"
        )

    min_lon, min_lat, max_lon, max_lat = bbox

    if client is None:
        raise TypeError("client parameter is required")

    # Fetch site data
    query = QueryBuilder.pedons_intersecting_bbox(
        min_lon, min_lat, max_lon, max_lat, columns
    )
    site_response = await client.execute(query)

    # If only site data is requested or response is empty, return early
    if return_type == "sitedata" or site_response.is_empty():
        return site_response

    # For "combined" or "soilprofilecollection", we need horizon data
    # Get pedon keys for horizon fetching
    site_df = site_response.to_pandas()
    pedon_keys = site_df["pedon_key"].unique().tolist()

    # Fetch horizons in chunks if needed
    all_horizons = []
    sample_cols = None
    sample_meta = None
    if len(pedon_keys) <= chunk_size:
        # Single query for small pedon lists
        horizons_response = await fetch_pedon_horizons(pedon_keys, client=client)
        if not horizons_response.is_empty():
            # Capture columns and metadata from the response
            sample_cols = horizons_response.columns
            sample_meta = horizons_response.metadata
            all_horizons.extend(horizons_response.data)
    else:
        # Multiple queries for large pedon lists
        logger.debug(
            f"Fetching horizons for {len(pedon_keys)} pedons in chunks of {chunk_size}"
        )
        for i in range(0, len(pedon_keys), chunk_size):
            chunk_keys = pedon_keys[i : i + chunk_size]
            chunk_response = await fetch_pedon_horizons(chunk_keys, client=client)
            if not chunk_response.is_empty():
                # Capture columns and metadata from first non-empty chunk
                if sample_cols is None:
                    sample_cols = chunk_response.columns
                    sample_meta = chunk_response.metadata
                all_horizons.extend(chunk_response.data)

    # Build horizons response object from combined data
    if all_horizons:
        # Reconstruct the raw data format that SDAResponse expects
        horizons_table = []
        horizons_table.append(sample_cols)
        horizons_table.append(sample_meta)
        horizons_table.extend(all_horizons)
        horizons_raw_data = {"Table": horizons_table}
        horizons_response = SDAResponse(horizons_raw_data)
    else:
        # Empty horizons response
        horizons_response = SDAResponse({})

    if return_type == "combined":
        return {"site": site_response, "horizons": horizons_response}

    elif return_type == "soilprofilecollection":
        # Convert to SoilProfileCollection
        if horizons_response.is_empty():
            raise ValueError(
                "No horizon data found. Cannot create SoilProfileCollection without horizons."
            )

        return horizons_response.to_soilprofilecollection(
            site_data=site_df,
            site_id_col="pedon_key",
            hz_id_col="layer_key",
            hz_top_col="hzn_top",
            hz_bot_col="hzn_bot",
        )

    # Fallback (shouldn't reach here due to validation above)
    return site_response


async def fetch_pedon_horizons(
    pedon_keys: Union[List[str], str],
    client: Optional[SDAClient] = None,
) -> SDAResponse:
    """
    Fetch horizon data for specified pedon keys.

    Args:
        pedon_keys: Single pedon key or list of pedon keys
        client: Optional SDA client instance

    Returns:
        SDAResponse containing horizon data
    """
    if isinstance(pedon_keys, str):
        pedon_keys = [pedon_keys]

    if client is None:
        raise TypeError("client parameter is required")

    query = QueryBuilder.pedon_horizons_by_pedon_keys(pedon_keys)
    return await client.execute(query)


# Bulk key extraction helpers
async def get_mukey_by_areasymbol(
    areasymbols: List[str], client: Optional[SDAClient] = None
) -> List[int]:
    """
    Get all mukeys for given area symbols.

    This is useful for getting all map units in specific survey areas
    before fetching detailed data.
    """
    if client is None:
        raise TypeError("client parameter is required")

    # Use the existing get_mapunits_by_legend pattern but for multiple areas
    key_strings = sanitize_sql_string_list(areasymbols)
    where_clause = f"l.areasymbol IN ({', '.join(key_strings)})"

    query = (
        Query()
        .select("m.mukey")
        .from_("mapunit m")
        .inner_join("legend l", "m.lkey = l.lkey")
        .where(where_clause)
    )

    response = await client.execute(query)
    df = response.to_pandas()

    return df["mukey"].tolist() if not df.empty else []


async def get_cokey_by_mukey(
    mukeys: Union[List[Union[str, int]], Union[str, int]],
    major_components_only: bool = True,
    client: Optional[SDAClient] = None,
) -> List[str]:
    """
    Get all cokeys for given mukeys.

    Args:
        mukeys: Map unit key(s) (single key or list of keys)
        major_components_only: Whether to only return major components
        client: Optional SDA client

    Returns:
        List of component keys
    """
    # Handle single mukey values for convenience
    if not isinstance(mukeys, list):
        mukeys = [mukeys]

    # At this point mukeys is guaranteed to be a list
    mukeys_list: List[Union[str, int]] = mukeys

    sanitized_keys = [sanitize_sql_numeric(k) for k in mukeys_list]
    where_clause = f"mukey IN ({', '.join(sanitized_keys)})"
    if major_components_only:
        where_clause += " AND majcompflag = 'Yes'"

    response = await fetch_by_keys(
        mukeys_list, "component", "mukey", "cokey", client=client
    )
    df = response.to_pandas()

    return df["cokey"].tolist() if not df.empty else []
