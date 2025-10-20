import argparse
import inspect
from functools import wraps
from typing import Any, Type, get_type_hints

from jupytergis import GISDocument
from mcp.server.fastmcp import FastMCP


def get_mcp_server() -> FastMCP:
    mcp = FastMCP(name="JupyterGIS MCP Server")

    @mcp.tool()
    def get_current_gis_document(jgis_path: str) -> str:
        """Read the current content of a JGIS (JupyterGIS) document.

        Use this tool to understand the current state of a JGIS file before modifying it.

        :param jgis_path: The path to the JGIS file.
        :return: The current content of the JGIS file.
        """
        with open(jgis_path, "r") as f:
            return f.read()

    def expose_method(cls: Type[Any], method_name: str) -> None:
        """Expose a method of a class as an MCP tool."""
        method = getattr(cls, method_name)

        @wraps(method)
        def _wrapper(jgis_path: str, **kwargs: Any) -> None:
            # Import current .jgis document
            doc = GISDocument.import_from_file(jgis_path)

            # Update doc
            getattr(doc, method_name)(**kwargs)

            # Write updates to the same filepath
            doc.save(jgis_path)

        # Remove 'self' from signature
        type_hints = get_type_hints(method, globalns=method.__globals__)
        orig_sig = inspect.signature(method)
        new_params = [
            param.replace(annotation=type_hints.get(param.name, param.annotation))
            for param in orig_sig.parameters.values()
            if param.name != "self"
        ]

        # Add 'jgis_path' to signature
        jgis_path_param = inspect.Parameter("jgis_path", inspect.Parameter.POSITIONAL_OR_KEYWORD, annotation=str)
        new_params.insert(0, jgis_path_param)
        _wrapper.__signature__ = orig_sig.replace(  # type: ignore
            parameters=new_params,
            return_annotation=inspect.Signature.empty,  # remove return type (to prevent pydantic errors)
        )

        # Register it with MCP
        mcp.add_tool(_wrapper)

    # Add GISDocument tools
    expose_method(cls=GISDocument, method_name="sidecar")
    expose_method(cls=GISDocument, method_name="export_to_qgis")
    expose_method(cls=GISDocument, method_name="add_raster_layer")
    expose_method(cls=GISDocument, method_name="add_vectortile_layer")
    expose_method(cls=GISDocument, method_name="add_geojson_layer")
    expose_method(cls=GISDocument, method_name="add_image_layer")
    expose_method(cls=GISDocument, method_name="add_video_layer")
    expose_method(cls=GISDocument, method_name="add_tiff_layer")
    expose_method(cls=GISDocument, method_name="add_hillshade_layer")
    expose_method(cls=GISDocument, method_name="add_heatmap_layer")
    # expose_method(cls=GISDocument, method_name="add_geoparquet_layer")
    expose_method(cls=GISDocument, method_name="remove_layer")
    expose_method(cls=GISDocument, method_name="create_color_expr")
    expose_method(cls=GISDocument, method_name="add_filter")
    expose_method(cls=GISDocument, method_name="update_filter")
    expose_method(cls=GISDocument, method_name="clear_filters")
    expose_method(cls=GISDocument, method_name="to_py")

    return mcp


def main() -> None:
    parser = argparse.ArgumentParser(description="Start a MCP server for JupyterGIS.")
    parser.add_argument(
        "transport",
        nargs="?",
        default="stdio",
        choices=["stdio", "streamable-http"],
        help="Transport type (stdio or streamable-http)",
    )
    args = parser.parse_args()

    # Run server
    mcp = get_mcp_server()
    mcp.run(transport=args.transport)


if __name__ == "__main__":
    main()
