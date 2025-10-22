"""
Data management tools for Weaviate operations.
"""

import logging
from typing import Any

from weaviate.classes.query import Filter

from ..app import mcp  # Import from central app module
from ..services.weaviate_service import WeaviateService

logger = logging.getLogger(__name__)


# --- Data Management Tool Functions --- #


@mcp.tool(
    name="weaviate_insert_object",
    description="Insert a new object into a Weaviate collection.",
)
async def weaviate_insert_object(
    collection_name: str,
    data: dict[str, Any],
    unique_properties: list[str] | None = None,
) -> dict[str, Any]:
    """
    Insert a new object into a Weaviate collection.

    Args:
        collection_name: Name of the collection to insert into
        data: Object data as key-value pairs
        unique_properties: Optional list of property names that should be unique.
                          If provided, will check for existing objects with same values
                          and return existing object ID instead of creating duplicate.

    Returns:
        Dictionary with success status, object_id, and message or error details.

    Example:
        ```python
        await weaviate_insert_object(
            collection_name="Product",
            data={
                "title": "Wireless Headphones",
                "price": 99.99,
                "category": "Electronics"
            },
            unique_properties=["title"]  # Prevent duplicate products with same title
        )
        ```
    """
    service = WeaviateService()
    try:
        result = await service.insert_object(
            collection_name=collection_name,
            data=data,
            unique_properties=unique_properties,
        )

        logger.info(f"Object insertion result: {result}")
        return result

    except Exception as e:
        logger.error(f"Error in weaviate_insert_object: {e}")
        return {"error": True, "message": str(e)}
    finally:
        await service.close()


@mcp.tool(
    name="weaviate_get_object",
    description="Get a specific object from a Weaviate collection by its UUID.",
)
async def weaviate_get_object(
    collection_name: str,
    uuid: str,
    include_vector: bool = False,
    return_properties: list[str] | None = None,
) -> dict[str, Any]:
    """
    Get a specific object from a Weaviate collection by its UUID.

    Args:
        collection_name: Name of the collection
        uuid: UUID of the object to retrieve
        include_vector: Whether to include the vector in the response
        return_properties: Optional list of specific properties to return.
                          If None, returns all properties.

    Returns:
        Dictionary containing the object data or error details.

    Example:
        ```python
        await weaviate_get_object(
            collection_name="Product",
            uuid="12345678-1234-1234-1234-123456789abc",
            return_properties=["title", "price"]
        )
        ```
    """
    service = WeaviateService()
    try:
        result = await service.get_object(
            collection_name=collection_name,
            uuid=uuid,
            include_vector=include_vector,
            return_properties=return_properties,
        )

        logger.info(f"Object retrieval result: {result}")
        return result

    except Exception as e:
        logger.error(f"Error in weaviate_get_object: {e}")
        return {"error": True, "message": str(e)}
    finally:
        await service.close()


@mcp.tool(
    name="weaviate_get_objects",
    description="Get multiple objects from a Weaviate collection with optional filtering and pagination.",
)
async def weaviate_get_objects(
    collection_name: str,
    limit: int = 20,
    offset: int = 0,
    where_filter: dict[str, Any] | None = None,
    return_properties: list[str] | None = None,
    include_vector: bool = False,
) -> dict[str, Any]:
    """
    Get multiple objects from a Weaviate collection.

    Args:
        collection_name: Name of the collection
        limit: Maximum number of objects to return (default: 20)
        offset: Number of objects to skip for pagination (default: 0)
        where_filter: Optional filter criteria as a dictionary with:
            - property: Property name to filter on
            - operator: Operator ("equal", "not_equal", "greater_than", "less_than", "like")
            - value: Value to compare against
        return_properties: Optional list of specific properties to return
        include_vector: Whether to include vectors in the response

    Returns:
        Dictionary containing objects array, count, and metadata or error details.

    Example:
        ```python
        await weaviate_get_objects(
            collection_name="Product",
            limit=10,
            where_filter={
                "property": "category",
                "operator": "equal",
                "value": "Electronics"
            },
            return_properties=["title", "price"]
        )
        ```
    """
    service = WeaviateService()
    try:
        # Convert simple filter dict to Weaviate Filter object if provided
        filters = None
        if where_filter:
            property_name = where_filter.get("property")
            operator = where_filter.get("operator", "equal")
            value = where_filter.get("value")

            # Validate filter format
            if not property_name:
                return {
                    "error": True,
                    "message": "Invalid filter format: missing 'property' field. "
                    "Expected format: {'property': 'field_name', 'operator': 'equal', 'value': 'some_value'}",
                }
            if value is None:
                return {
                    "error": True,
                    "message": "Invalid filter format: missing 'value' field. "
                    "Expected format: {'property': 'field_name', 'operator': 'equal', 'value': 'some_value'}",
                }

            if operator == "equal":
                filters = Filter.by_property(property_name).equal(value)
            elif operator == "not_equal":
                filters = Filter.by_property(property_name).not_equal(value)
            elif operator == "greater_than":
                filters = Filter.by_property(property_name).greater_than(value)
            elif operator == "less_than":
                filters = Filter.by_property(property_name).less_than(value)
            elif operator == "like":
                filters = Filter.by_property(property_name).like(value)
            else:
                return {
                    "error": True,
                    "message": f"Unsupported operator: {operator}. "
                    "Supported: equal, not_equal, greater_than, less_than, like",
                }

        result = await service.get_objects(
            collection_name=collection_name,
            filters=filters,
            limit=limit,
            offset=offset,
            return_properties=return_properties,
            include_vector=include_vector,
        )

        logger.info(f"Objects retrieval result: {result}")
        return result

    except Exception as e:
        logger.error(f"Error in weaviate_get_objects: {e}")
        return {"error": True, "message": str(e)}
    finally:
        await service.close()


@mcp.tool(
    name="weaviate_vector_search",
    description="Perform semantic vector search in a Weaviate collection.",
)
async def weaviate_vector_search(
    collection_name: str,
    query_text: str,
    limit: int = 10,
    offset: int = 0,
    where_filter: dict[str, Any] | None = None,
    return_properties: list[str] | None = None,
    include_vector: bool = False,
) -> dict[str, Any]:
    """
    Perform semantic vector search in a Weaviate collection.

    Args:
        collection_name: Name of the collection to search
        query_text: Text query for semantic search
        limit: Maximum number of results to return (default: 10)
        offset: Number of results to skip for pagination (default: 0)
        where_filter: Optional filter criteria (same format as weaviate_get_objects)
        return_properties: Optional list of specific properties to return
        include_vector: Whether to include vectors in the response

    Returns:
        Dictionary containing search results with similarity scores or error details.

    Example:
        ```python
        await weaviate_vector_search(
            collection_name="Product",
            query_text="wireless bluetooth headphones",
            limit=5,
            where_filter={
                "property": "price",
                "operator": "less_than",
                "value": 200
            }
        )
        ```
    """
    service = WeaviateService()
    try:
        # Convert simple filter dict to Weaviate Filter object if provided
        filters = None
        if where_filter:
            property_name = where_filter.get("property")
            operator = where_filter.get("operator", "equal")
            value = where_filter.get("value")

            # Validate filter format
            if not property_name:
                return {
                    "error": True,
                    "message": "Invalid filter format: missing 'property' field. "
                    "Expected format: {'property': 'field_name', 'operator': 'equal', 'value': 'some_value'}",
                }
            if value is None:
                return {
                    "error": True,
                    "message": "Invalid filter format: missing 'value' field. "
                    "Expected format: {'property': 'field_name', 'operator': 'equal', 'value': 'some_value'}",
                }

            if operator == "equal":
                filters = Filter.by_property(property_name).equal(value)
            elif operator == "not_equal":
                filters = Filter.by_property(property_name).not_equal(value)
            elif operator == "greater_than":
                filters = Filter.by_property(property_name).greater_than(value)
            elif operator == "less_than":
                filters = Filter.by_property(property_name).less_than(value)
            elif operator == "like":
                filters = Filter.by_property(property_name).like(value)
            else:
                return {
                    "error": True,
                    "message": f"Unsupported operator: {operator}. "
                    "Supported: equal, not_equal, greater_than, less_than, like",
                }

        result = await service.search(
            collection_name=collection_name,
            query_text=query_text,
            filters=filters,
            limit=limit,
            offset=offset,
            return_properties=return_properties,
            include_vector=include_vector,
        )

        logger.info(f"Vector search result: {result}")
        return result

    except Exception as e:
        logger.error(f"Error in weaviate_vector_search: {e}")
        return {"error": True, "message": str(e)}
    finally:
        await service.close()


@mcp.tool(
    name="weaviate_hybrid_search",
    description="Perform hybrid search (semantic + keyword) in a Weaviate collection.",
)
async def weaviate_hybrid_search(
    collection_name: str,
    query_text: str,
    alpha: float = 0.5,
    limit: int = 10,
    where_filter: dict[str, Any] | None = None,
    return_properties: list[str] | None = None,
    include_vector: bool = False,
) -> dict[str, Any]:
    """
    Perform hybrid search (combining semantic and keyword search) in a Weaviate collection.

    Args:
        collection_name: Name of the collection to search
        query_text: Text query for hybrid search
        alpha: Balance between semantic (0.0) and keyword (1.0) search.
               0.5 gives equal weight to both. (default: 0.5)
        limit: Maximum number of results to return (default: 10)
        where_filter: Optional filter criteria (same format as weaviate_get_objects)
        return_properties: Optional list of specific properties to return
        include_vector: Whether to include vectors in the response

    Returns:
        Dictionary containing search results with hybrid scores or error details.

    Example:
        ```python
        await weaviate_hybrid_search(
            collection_name="Product",
            query_text="wireless bluetooth headphones",
            alpha=0.7,  # Favor keyword search slightly
            limit=5
        )
        ```
    """
    service = WeaviateService()
    try:
        # Convert simple filter dict to Weaviate Filter object if provided
        filters = None
        if where_filter:
            property_name = where_filter.get("property")
            operator = where_filter.get("operator", "equal")
            value = where_filter.get("value")

            # Validate filter format
            if not property_name:
                return {
                    "error": True,
                    "message": "Invalid filter format: missing 'property' field. "
                    "Expected format: {'property': 'field_name', 'operator': 'equal', 'value': 'some_value'}",
                }
            if value is None:
                return {
                    "error": True,
                    "message": "Invalid filter format: missing 'value' field. "
                    "Expected format: {'property': 'field_name', 'operator': 'equal', 'value': 'some_value'}",
                }

            if operator == "equal":
                filters = Filter.by_property(property_name).equal(value)
            elif operator == "not_equal":
                filters = Filter.by_property(property_name).not_equal(value)
            elif operator == "greater_than":
                filters = Filter.by_property(property_name).greater_than(value)
            elif operator == "less_than":
                filters = Filter.by_property(property_name).less_than(value)
            elif operator == "like":
                filters = Filter.by_property(property_name).like(value)
            else:
                return {
                    "error": True,
                    "message": f"Unsupported operator: {operator}. "
                    "Supported: equal, not_equal, greater_than, less_than, like",
                }

        result = await service.hybrid_search(
            collection_name=collection_name,
            query_text=query_text,
            filters=filters,
            limit=limit,
            alpha=alpha,
            return_properties=return_properties,
            include_vector=include_vector,
        )

        logger.info(f"Hybrid search result: {result}")
        return result

    except Exception as e:
        logger.error(f"Error in weaviate_hybrid_search: {e}")
        return {"error": True, "message": str(e)}
    finally:
        await service.close()


@mcp.tool(
    name="weaviate_update_object",
    description="Update an existing object in a Weaviate collection.",
)
async def weaviate_update_object(
    collection_name: str,
    uuid: str,
    data: dict[str, Any],
) -> dict[str, Any]:
    """
    Update an existing object in a Weaviate collection.

    Args:
        collection_name: Name of the collection
        uuid: UUID of the object to update
        data: Updated object data as key-value pairs

    Returns:
        Dictionary with success status and message or error details.

    Example:
        ```python
        await weaviate_update_object(
            collection_name="Product",
            uuid="12345678-1234-1234-1234-123456789abc",
            data={
                "price": 89.99,  # Updated price
                "category": "Electronics & Audio"  # Updated category
            }
        )
        ```
    """
    service = WeaviateService()
    try:
        result = await service.update_object(
            collection_name=collection_name,
            uuid=uuid,
            data=data,
        )

        logger.info(f"Object update result: {result}")
        return result

    except Exception as e:
        logger.error(f"Error in weaviate_update_object: {e}")
        return {"error": True, "message": str(e)}
    finally:
        await service.close()


@mcp.tool(
    name="weaviate_delete_object",
    description="Delete an object from a Weaviate collection.",
)
async def weaviate_delete_object(
    collection_name: str,
    uuid: str,
) -> dict[str, Any]:
    """
    Delete an object from a Weaviate collection.

    Args:
        collection_name: Name of the collection
        uuid: UUID of the object to delete

    Returns:
        Dictionary with success status and message or error details.

    Example:
        ```python
        await weaviate_delete_object(
            collection_name="Product",
            uuid="12345678-1234-1234-1234-123456789abc"
        )
        ```
    """
    service = WeaviateService()
    try:
        result = await service.delete_object(
            collection_name=collection_name,
            uuid=uuid,
        )

        logger.info(f"Object deletion result: {result}")
        return result

    except Exception as e:
        logger.error(f"Error in weaviate_delete_object: {e}")
        return {"error": True, "message": str(e)}
    finally:
        await service.close()


@mcp.tool(
    name="weaviate_batch_insert_objects",
    description="Insert multiple objects into a Weaviate collection in batches.",
)
async def weaviate_batch_insert_objects(
    collection_name: str,
    objects: list[dict[str, Any]],
    unique_properties: list[str] | None = None,
    batch_size: int = 100,
) -> dict[str, Any]:
    """
    Insert multiple objects into a Weaviate collection in batches.

    Args:
        collection_name: Name of the collection to insert into
        objects: List of object data dictionaries
        unique_properties: Optional list of property names that should be unique
        batch_size: Number of objects to process in each batch (default: 100)

    Returns:
        Dictionary with success status, inserted_ids, count, and message or error details.

    Example:
        ```python
        await weaviate_batch_insert_objects(
            collection_name="Product",
            objects=[
                {"title": "Product 1", "price": 10.99},
                {"title": "Product 2", "price": 20.99},
                {"title": "Product 3", "price": 30.99}
            ],
            unique_properties=["title"],
            batch_size=50
        )
        ```
    """
    service = WeaviateService()
    try:
        result = await service.batch_insert_objects(
            collection_name=collection_name,
            objects=objects,
            unique_properties=unique_properties,
            batch_size=batch_size,
        )

        logger.info(f"Batch insertion result: {result}")
        return result

    except Exception as e:
        logger.error(f"Error in weaviate_batch_insert_objects: {e}")
        return {"error": True, "message": str(e)}
    finally:
        await service.close()


@mcp.tool(
    name="weaviate_batch_check_existing_files",
    description="Efficiently check which files from a list already exist in a Weaviate collection. Returns files split into 'new' and 'existing' categories in a single query.",
)
async def weaviate_batch_check_existing_files(
    collection_name: str,
    file_keys: list[str],
    source_field: str = "source_pdf",
) -> dict[str, Any]:
    """
    Check which files from a list already exist in Weaviate.

    This tool enables efficient batch checking of multiple files against a Weaviate
    collection to determine which files are already indexed and which are new.
    Instead of querying Weaviate once per file, this tool makes ONE query to check
    all files at once, dramatically improving performance.

    IMPORTANT: This tool requires the collection schema to have a field that stores
    file identifiers (like 'source_pdf', 'source_file', 'file_key', etc.).

    Args:
        collection_name: Name of the Weaviate collection to check against
        file_keys: Array of file keys/identifiers to check (e.g., S3 keys, file paths).
                  Example: ['document1.pdf', 'document2.pdf', 'document3.pdf']
        source_field: Name of the field in Weaviate that contains the source file
                     identifier (default: "source_pdf"). This field must exist in
                     your collection schema.

    Returns:
        Dictionary containing:
            - new_files: Array of file keys that do NOT exist in Weaviate
            - existing_files: Array of file keys that already exist in Weaviate
            - new_count: Count of new files
            - existing_count: Count of existing files
            - total_checked: Total number of files checked
            - error: True if an error occurred, with 'message' field

    Performance Benefits:
        - 20-100x faster than checking files individually
        - Single network round-trip instead of N round-trips
        - Reduces API call overhead and costs

    Example:
        ```python
        # Check 100 files in one query
        result = await weaviate_batch_check_existing_files(
            collection_name="ResearchPapers",
            file_keys=[
                "papers/document1.pdf",
                "papers/document2.pdf",
                "papers/document3.pdf",
                # ... 97 more files
            ],
            source_field="source_pdf"
        )

        # Use results to process only new files
        if not result.get("error"):
            print(f"Found {result['new_count']} new files to process")
            print(f"Skipping {result['existing_count']} existing files")
            for file_key in result['new_files']:
                # Process only new files
                pass
        ```

    Typical Workflow Usage:
        1. List files from S3 or filesystem
        2. Use this tool to check which are already in Weaviate
        3. Process only the 'new_files' array
        4. Avoids re-processing and duplicate ingestion
    """
    service = WeaviateService()
    try:
        result = await service.batch_check_existing_files(
            collection_name=collection_name,
            file_keys=file_keys,
            source_field=source_field,
        )

        logger.info(
            f"Batch check result for collection '{collection_name}': "
            f"{result.get('new_count', 0)} new, "
            f"{result.get('existing_count', 0)} existing, "
            f"{result.get('total_checked', 0)} total"
        )
        return result

    except Exception as e:
        logger.error(f"Error in weaviate_batch_check_existing_files: {e}")
        return {"error": True, "message": str(e)}
    finally:
        await service.close()
