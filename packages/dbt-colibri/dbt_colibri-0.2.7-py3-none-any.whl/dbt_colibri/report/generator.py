import json
from pathlib import Path
from typing import Dict, List, Optional
from datetime import datetime, timezone


from ..lineage_extractor.extractor import DbtColumnLineageExtractor

import base64


class DbtColibriReportGenerator:
    """
    Generates dbt-colibri report data from lineage extraction results.
    
    Uses composition with DbtColumnLineageExtractor to separate concerns:
    - Lineage extraction (DbtColumnLineageExtractor)
    - Report generation (DbtColibriReportGenerator)
    """
    
    def __init__(self, extractor: DbtColumnLineageExtractor, light_mode: bool = False):
        self.extractor = extractor
        self.manifest = extractor.manifest
        self.catalog = extractor.catalog
        self.logger = extractor.logger
        self.colibri_version = extractor.colibri_version
        self.dialect = extractor.dialect
        self.light_mode = light_mode

    def detect_model_type(self, node_id: str) -> str:
        """Detect model type based on naming conventions."""
        slug = node_id.split('.')[-1]
        if slug.startswith("dim_"):
            return "dimension"
        if slug.startswith("fact_"):
            return "fact"
        if slug.startswith("int_"):
            return "intermediate"
        if slug.startswith("stg_"):
            return "staging"
        return "unknown"
    
    def _get_node_display_name(self, node_id: str) -> str:
        """Return a human-friendly node name.

        For versioned dbt models (e.g. "model.project.model_name.v2"), include the
        version suffix in the name as "model_name_v2". For all other nodes, use the
        last segment of the node_id.
        """
        parts = node_id.split(".")
        if len(parts) >= 4 and parts[0] == "model":
            version_segment = parts[-1]
            if isinstance(version_segment, str) and version_segment.startswith("v") and version_segment[1:].isdigit():
                base_name = parts[-2]
                return f"{base_name}_{version_segment}"
        return parts[-1]
    
    def build_manifest_node_data(self, node_id: str) -> dict:
        """Build node metadata from manifest and catalog data."""
        node_data = (
            self.manifest.get("nodes", {}).get(node_id) or 
            self.manifest.get("sources", {}).get(node_id)
        )
        catalog_data = (
            self.catalog.get("nodes", {}).get(node_id) or 
            self.catalog.get("sources", {}).get(node_id)
        )

        if not node_data:
            node_type = "unknown"
            if node_id.startswith("_HARDCODED_REF___"):
                node_type = "hardcoded"
            elif node_id.startswith("_NOT_FOUND___."):
                node_type = "not_found"
            return {
                "nodeType": node_type,
                "materialized": None,
                "rawCode": None,
                "compiledCode": None,
                "schema": None,
                "description": None,
                "path": None,
                "contractEnforced": None,
                "refs": [],
                "columns": {},
                "database": None,
            }

        # Build columns based ONLY on catalog columns (real table),
        # enriching with manifest metadata when available.
        columns = {}
        manifest_columns = {}
        if node_data and node_data.get("columns"):
            for col, val in node_data["columns"].items():
                manifest_columns[col.lower()] = {
                    "contractType": val.get("data_type"),
                    "description": val.get("description"),
                }
        if catalog_data and catalog_data.get("columns"):
            for col, val in catalog_data["columns"].items():
                col_lc = col.lower()
                entry = {"dataType": val.get("type")}
                if col_lc in manifest_columns:
                    if manifest_columns[col_lc].get("contractType") is not None:
                        entry["contractType"] = manifest_columns[col_lc]["contractType"]
                    if manifest_columns[col_lc].get("description") is not None:
                        entry["description"] = manifest_columns[col_lc]["description"]
                columns[col_lc] = entry

        if node_data:
            node_type = node_data.get("resource_type", "unknown")
            materialized = node_data.get("config", {}).get("materialized", "unknown")
        else:
            node_type = materialized = "unknown"

        return {
            "nodeType": node_type,
            "materialized": materialized,
            "rawCode": node_data.get("raw_code") or node_data.get("raw_sql"),
            "compiledCode": node_data.get("compiled_code") or node_data.get("compiled_sql"),
            "schema": node_data.get("schema"),
            "path": node_data.get("original_file_path"),
            "description": node_data.get("description"),
            "contractEnforced": node_data.get("config", {}).get("contract", {}).get("enforced"),
            "refs": node_data.get("refs", []),
            "columns": columns,
            "database": node_data.get("database")
        }
    
    def build_full_lineage(self) -> dict:
        """Build complete lineage report with nodes and edges in a human-readable structure."""
        # Extract lineage data from the extractor
        lineage_data = self.extractor.extract_project_lineage()
        parents_map = lineage_data["lineage"]["parents"]
        children_map = lineage_data["lineage"]["children"]

        # Build nodes dictionary (keyed by node_id for easy lookup)
        nodes: Dict[str, dict] = {}
        edges: List[dict] = []
        edge_id_counter = 1

        def ensure_node(node_id: str) -> dict:
            """Ensure a node exists in the nodes dict, creating if necessary."""
            if node_id not in nodes:
                meta = self.build_manifest_node_data(node_id)
                
                # Build columns dictionary (keyed by column name)
                columns_dict = {}
                for col_name, col_meta in meta["columns"].items():
                    columns_dict[col_name] = {
                        "columnName": col_name,
                        "hasLineage": False,  # Will be updated when we process lineage
                        **{k: v for k, v in col_meta.items() if v is not None}
                    }
                
                nodes[node_id] = {
                    "id": node_id,
                    "name": self._get_node_display_name(node_id),
                    "fullName": node_id,
                    "nodeType": meta["nodeType"],
                    "materialized": meta["materialized"],
                    "modelType": self.detect_model_type(node_id),
                    "database": meta.get("database"),
                    "schema": meta["schema"],
                    "path": meta.get("path"),
                    "description": meta["description"],
                    "contractEnforced": meta["contractEnforced"],
                    "rawCode": meta["rawCode"],
                    "compiledCode": meta["compiledCode"],
                    "refs": meta["refs"],
                    "columns": columns_dict,
                }
            return nodes[node_id]

        def add_edge(src_id: str, src_col: str, tgt_id: str, tgt_col: str):
            """Add an edge between two columns."""
            nonlocal edge_id_counter
            edges.append({
                "id": edge_id_counter,
                "source": src_id,
                "target": tgt_id,
                "sourceColumn": src_col,
                "targetColumn": tgt_col,
            })
            edge_id_counter += 1

        # Traverse all edges from parents_map
        def _normalize_col_name(col: str) -> str:
            """Normalize a column name for display and matching.

            - Strip wrapping single or double quotes if they wrap the entire name.
            - Preserve internal characters, including spaces.
            """
            if isinstance(col, str) and len(col) >= 2 and col[0] == col[-1] and col[0] in {'"', "'"}:
                return col[1:-1]
            return col

        for tgt_id, mapping in parents_map.items():
            for tgt_col, sources in mapping.items():
                # Ensure target node exists and normalize target column once
                tgt_node = ensure_node(tgt_id)
                norm_tgt_col = _normalize_col_name(tgt_col)

                # Aggregate lineage type for the target column
                # If multiple parents -> "transformation"; otherwise use the sole parent's lineage_type
                aggregated_lineage = "unknown"
                if isinstance(sources, list) and len(sources) >= 2:
                    aggregated_lineage = "transformation"
                elif isinstance(sources, list) and len(sources) == 1:
                    aggregated_lineage = sources[0].get("lineage_type") or "unknown"

                if norm_tgt_col in tgt_node["columns"]:
                    tgt_node["columns"][norm_tgt_col]["lineageType"] = aggregated_lineage

                for src in sources:
                    src_id, src_col = src["dbt_node"], src["column"]
                    # Normalize only the source column name to avoid quoted values like "\"order item_id\""
                    norm_src_col = _normalize_col_name(src_col)

                    # Ensure source node exists
                    src_node = ensure_node(src_id)

                    # Update column lineage flags
                    if norm_src_col in src_node["columns"]:
                        src_node["columns"][norm_src_col]["hasLineage"] = True
                    if norm_tgt_col in tgt_node["columns"]:
                        tgt_node["columns"][norm_tgt_col]["hasLineage"] = True

                    add_edge(src_id, norm_src_col, tgt_id, norm_tgt_col)

        # Traverse all depends_on nodes to add model-level relationships
        for node_id, node_data in self.manifest.get("nodes", {}).items():
            if node_data.get("resource_type") in {"test", "macro"}:
                continue  # Skip test and macro nodes
            
            for dep_node_id in node_data.get("depends_on", {}).get("nodes", []):
                # Ensure both nodes exist in your graph
                ensure_node(dep_node_id)
                ensure_node(node_id)

                edges.append({
                    "id": edge_id_counter,
                    "source": dep_node_id,
                    "target": node_id,
                    "sourceColumn": "",
                    "targetColumn": "",
                })
                edge_id_counter += 1

        # Build all nodes (even if disconnected)
        all_ids = {
            node_id
            for node_id, data in self.manifest.get("nodes", {}).items()
            if data.get("resource_type") not in {"test", "macro"}
        }.union({source_id for source_id in self.manifest.get("sources", {}).keys()})

        for node_id in all_ids:
            ensure_node(node_id)

        # Build database -> schema -> models tree (store only node IDs)
        db_tree: Dict[str, Dict[str, List[str]]] = {}
        for node in nodes.values():
            # Only include non-test, non-macro nodes (already filtered above),
            # but keep both models and sources in the tree
            if self.dialect == "snowflake":
                database = (node.get("database") or "unknown").upper()
                schema = (node.get("schema") or "unknown").upper()
            else:
                database = (node.get("database") or "unknown").lower()
                schema = (node.get("schema") or "unknown").lower()

            db_tree.setdefault(database, {}).setdefault(schema, []).append(node["id"])

        # Sort items within schemas by node name
        for database, schemas in db_tree.items():
            for schema, node_ids in schemas.items():
                schemas[schema] = sorted(node_ids, key=lambda node_id: nodes[node_id]["name"].lower())

        # Sort databases and schemas alphabetically
        db_tree = {
            db: {
                schema: db_tree[db][schema]
                for schema in sorted(db_tree[db].keys())
            }
            for db in sorted(db_tree.keys())
        }


        # Build a tree based on file path (e.g., models/area/subarea/model.sql)
        # Structure: { rootSegment: { nextSegment: { ... }, __items__: [node_ids] } }
        path_tree: Dict[str, dict] = {}
        for node in nodes.values():
            node_path = node.get("path")
            if not node_path:
                # Put items without path under a special bucket
                path_tree.setdefault("__no_path__", {}).setdefault("__items__", []).append(node["id"])
                continue

            # Normalize and split path into segments
            parts = [p for p in str(node_path).replace("\\", "/").split("/") if p]
            cursor = path_tree
            for segment in parts[:-1]:
                cursor = cursor.setdefault(segment, {})
            # Leaf item: append only the node id
            cursor.setdefault("__items__", []).append(node["id"])

        # Sort items within each folder node by name
        def sort_path_tree(folder: dict):
            # Sort the items in this folder
            if "__items__" in folder:
                folder["__items__"].sort(key=lambda node_id: nodes[node_id]["name"].lower())

            # Recursively sort child folders
            for key, val in list(folder.items()):
                if key == "__items__":
                    continue
                if isinstance(val, dict):
                    folder[key] = sort_path_tree(val)

            # Rebuild dict with sorted folder keys first, then __items__ last
            sorted_folder = {}
            for key in sorted(k for k in folder.keys() if key != "__items__"):
                sorted_folder[key] = folder[key]
            if "__items__" in folder:
                sorted_folder["__items__"] = folder["__items__"]

            return sorted_folder

        sort_path_tree(path_tree)

        # Build the final structure
        result = {
            "metadata": {
                "colibri_version": self.colibri_version,
                "generated_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
                "adapter_type": self.manifest.get("metadata", {}).get("adapter_type"),
                "dbt_version": self.manifest.get("metadata", {}).get("dbt_version"),
                "dbt_schema_version": self.manifest.get("metadata", {}).get("dbt_schema_version"),
                "dbt_invocation_id": self.manifest.get("metadata", {}).get("invocation_id"),
                "dbt_project_name": self.manifest.get("metadata", {}).get("project_name"),
                "dbt_project_id": self.manifest.get("metadata", {}).get("project_id"),
            },
            "nodes": nodes,  # Dictionary keyed by node_id
            "lineage": {
                "edges": edges,
                "parents": parents_map,
                "children": children_map
            },
            "tree": {
                "byDatabase": db_tree,
                "byPath": path_tree
            }
        }

        # Apply light mode filtering before returning
        if self.light_mode:
            self._apply_light_mode_filter(result)

        return result
    
    def _apply_light_mode_filter(self, result: dict) -> None:
        """
        Apply light mode filtering to the result dictionary in-place.
        Removes compiled_code from all nodes to reduce file size.
        
        This method can be extended to filter out additional fields if needed.
        
        Args:
            result: The complete lineage result dictionary
        """
        nodes = result.get("nodes", {})
        for node_id, node_data in nodes.items():
            # Remove compiledCode field if it exists
            if "compiledCode" in node_data:
                del node_data["compiledCode"]
    
    def generate_report(self, output_dir: str = "dist") -> dict:
        """
        Generate the complete dbt-colibri report with both JSON and HTML output.
        
        Args:
            output_dir: Directory to save both JSON and HTML files (default: "dist")
            
        Returns:
            dict: Complete report data
        """
        lineage = self.build_full_lineage()
        
        # Create target directory
        target_path = Path(output_dir)
        target_path.mkdir(parents=True, exist_ok=True)
        
        # Save full JSON data (with parents and children)
        json_path = target_path / "colibri-manifest.json"
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(lineage, f, indent=2)
        
        # Create a stripped version for HTML injection (without parents and children)
        lineage_stripped = {
            "metadata": lineage["metadata"],
            "nodes": lineage["nodes"],
            "lineage": {
                "edges": lineage["lineage"]["edges"]
                # Omit parents and children
            },
            "tree": lineage["tree"]
        }
        
        # Save stripped version to a temporary file for HTML injection
        json_path_stripped = target_path / "colibri-manifest-temp.json"
        with open(json_path_stripped, "w", encoding="utf-8") as f:
            json.dump(lineage_stripped, f, indent=2)
        
        # Delete lineage from memory to free up space before HTML injection
        del lineage
        del lineage_stripped

        # Generate HTML with injected data
        html_template_path = Path(__file__).parent / "index.html"
        html_output_path = target_path / "index.html"
        
        # Inject stripped data into HTML
        injected_html_path = inject_data_into_html(
            json_data_path=str(json_path_stripped),
            template_html_path=str(html_template_path),
            output_html_path=str(html_output_path)
        )

        self.logger.debug(f"Injected data into HTML: {injected_html_path}")
        
        # Clean up the temporary stripped JSON file
        json_path_stripped.unlink()
        
        return None



def inject_data_into_html(
    json_data_path: str,
    template_html_path: str = "dist/index.html",
    output_html_path: Optional[str] = None,
) -> str:
    """
    Inject JSON data into the compiled HTML file in a streaming fashion to avoid
    loading or re-encoding the full JSON in memory.
    """
    # Read the template (expected to be much smaller than the data)
    with open(template_html_path, "r", encoding="utf-8") as f:
        template_html = f.read()

    # Find insertion point
    head_close_idx = template_html.find("</head>")
    if head_close_idx != -1:
        insert_at = head_close_idx
    else:
        body_open_idx = template_html.find("<body>")
        insert_at = body_open_idx + len("<body>") if body_open_idx != -1 else 0

    # Determine output path
    if output_html_path is None:
        output_dir = Path(template_html_path).parent
        output_html_path = output_dir / "index_with_data.html"

    # Write output HTML while streaming base64-encoded JSON bytes
    with open(output_html_path, "w", encoding="utf-8") as out_f:
        # Prefix (before insert point)
        out_f.write(template_html[:insert_at])

        # Script preamble
        out_f.write('<script>window.colibriData = JSON.parse(atob("')

        # Stream base64 of the JSON file with 3-byte boundary handling
        with open(json_data_path, "rb") as jf:
            leftover = b""
            chunk_size = 1024 * 1024  # 1MB chunks
            while True:
                chunk = jf.read(chunk_size)
                if not chunk:
                    break
                buf = leftover + chunk
                to_encode_len = len(buf) - (len(buf) % 3)
                if to_encode_len:
                    out_f.write(base64.b64encode(buf[:to_encode_len]).decode("ascii"))
                leftover = buf[to_encode_len:]
            if leftover:
                out_f.write(base64.b64encode(leftover).decode("ascii"))

        # Script postamble
        out_f.write('"));</script>')

        # Suffix (after insert point)
        out_f.write(template_html[insert_at:])

    return str(output_html_path)
