"""
Unified relationships management for IMAS relationship data.

This module provides a single, coherent dataclass for managing relationships.json with
intelligent cache management, dependency tracking, and automatic rebuilding.
"""

import json
import logging
from dataclasses import dataclass, field
from datetime import datetime
from pathlib import Path
from typing import Any

from imas_mcp import dd_version
from imas_mcp.embeddings.config import EncoderConfig
from imas_mcp.embeddings.encoder import Encoder
from imas_mcp.physics.relationship_engine import EnhancedRelationshipEngine
from imas_mcp.relationships import RelationshipExtractionConfig, RelationshipExtractor
from imas_mcp.resource_path_accessor import ResourcePathAccessor

logger = logging.getLogger(__name__)

# Optimal clustering parameters from Latin Hypercube optimization
OPTIMAL_CROSS_IDS_EPS = 0.0751
OPTIMAL_CROSS_IDS_MIN_SAMPLES = 2
OPTIMAL_INTRA_IDS_EPS = 0.0319
OPTIMAL_INTRA_IDS_MIN_SAMPLES = 2


@dataclass
class Relationships:
    """
    Unified relationships manager with intelligent cache management and auto-rebuild.

    Features:
    - Automatic dependency tracking (embeddings)
    - Cache busting when dependencies are newer
    - Lazy loading with error handling
    - Automatic rebuilding with optimal parameters
    - Consistent interface for both building and accessing relationships
    """

    encoder_config: EncoderConfig  # Required: encoder configuration for embeddings
    relationships_file: Path | None = None

    # Cache state
    _cached_data: dict[str, Any] | None = field(default=None, init=False, repr=False)
    _cached_mtime: float | None = field(default=None, init=False, repr=False)
    _enhanced_engine: EnhancedRelationshipEngine | None = field(
        default=None, init=False, repr=False
    )

    # Dependency tracking
    _last_dependency_check: float | None = field(default=None, init=False, repr=False)
    _dependency_check_interval: float = field(default=1.0, init=False, repr=False)

    def __post_init__(self):
        """Initialize computed fields after dataclass initialization."""
        if self.relationships_file is None:
            path_accessor = ResourcePathAccessor(dd_version=dd_version)
            self.relationships_file = path_accessor.schemas_dir / "relationships.json"

    @property
    def file_path(self) -> Path:
        """Get the relationships file path, guaranteed to be non-None after __post_init__."""
        assert self.relationships_file is not None, (
            "relationships_file should be set in __post_init__"
        )
        return self.relationships_file

    def _get_file_mtime(self, file_path: Path) -> float:
        """Get modification time of a file, returning 0 if file doesn't exist."""
        try:
            return file_path.stat().st_mtime
        except (FileNotFoundError, OSError):
            return 0.0

    def _get_embedding_cache_file(self) -> Path | None:
        """
        Get the specific embedding cache file that relationships will load from.

        Uses the encoder_config to determine the cache file path.
        """
        try:
            encoder = Encoder(self.encoder_config)
            cache_key = self.encoder_config.generate_cache_key()
            encoder._set_cache_path(cache_key)

            cache_path = encoder._cache_path
            return cache_path if cache_path and cache_path.exists() else None

        except Exception as e:
            logger.debug(f"Could not determine embedding cache file: {e}")
            return None

    def _check_dependency_freshness(self) -> bool:
        """
        Check if any dependency files are newer than the relationships file.

        Only checks the embedding cache file since relationships are computed from
        embeddings, not directly from schema files.

        Returns:
            True if relationships file should be regenerated, False otherwise.
        """
        if not self.file_path.exists():
            logger.debug("Relationships file does not exist")
            return True

        relationships_mtime = self._get_file_mtime(self.file_path)
        relationships_time = datetime.fromtimestamp(relationships_mtime)

        # Check the specific embedding cache file that will be loaded
        embedding_cache = self._get_embedding_cache_file()
        if embedding_cache:
            embedding_mtime = self._get_file_mtime(embedding_cache)
            if embedding_mtime > relationships_mtime:
                embedding_time = datetime.fromtimestamp(embedding_mtime)
                time_diff = embedding_mtime - relationships_mtime
                logger.info(
                    f"Embedding cache newer than relationships: {embedding_cache.name} "
                    f"(embedding: {embedding_time.isoformat()}, relationships: {relationships_time.isoformat()}, diff: {time_diff:.1f}s)"
                )
                return True
            else:
                logger.debug(
                    f"Embedding cache is up-to-date: {embedding_cache.name} "
                    f"(embedding: {datetime.fromtimestamp(embedding_mtime).isoformat()}, relationships: {relationships_time.isoformat()})"
                )
        else:
            # If no embedding cache exists, we need to rebuild
            logger.info(
                "No embedding cache file found - relationships rebuild required"
            )
            return True

        return False

    def _should_check_dependencies(self) -> bool:
        """Determine if we should check dependencies based on interval."""
        if self._last_dependency_check is None:
            return True

        current_time = datetime.now().timestamp()
        return (
            current_time - self._last_dependency_check
        ) > self._dependency_check_interval

    def _invalidate_cache(self) -> None:
        """Invalidate cached data and engine."""
        logger.debug("Invalidating relationships cache")
        self._cached_data = None
        self._cached_mtime = None
        self._enhanced_engine = None

    def _load_relationships_data(self) -> dict[str, Any]:
        """
        Load relationships data from file with dependency checking and auto-rebuild.

        Returns:
            Dictionary containing relationships data.

        Raises:
            FileNotFoundError: If relationships file doesn't exist and can't be built.
            json.JSONDecodeError: If file contains invalid JSON.
        """
        # Check if we should verify dependencies
        if self._should_check_dependencies():
            self._last_dependency_check = datetime.now().timestamp()

            if self._check_dependency_freshness():
                logger.info("Relationships file is outdated. Auto-rebuilding...")
                try:
                    self.build(force=True)
                except Exception as e:
                    logger.error(f"Auto-rebuild failed: {e}")
                    # Continue to try loading existing file if available

        # Check if cached data is still valid
        current_mtime = self._get_file_mtime(self.file_path)
        if (
            self._cached_data is not None
            and self._cached_mtime is not None
            and current_mtime == self._cached_mtime
        ):
            return self._cached_data

        # Load fresh data
        logger.debug(f"Loading relationships data from {self.file_path}")

        if not self.file_path.exists():
            logger.info("Relationships file not found. Building...")
            self.build(force=True)

        try:
            with self.file_path.open("r", encoding="utf-8") as f:
                data = json.load(f)

            # Cache the loaded data
            self._cached_data = data
            self._cached_mtime = current_mtime
            self._enhanced_engine = None  # Reset engine on data reload

            logger.debug(
                f"Loaded {len(data.get('clusters', []))} clusters from relationships file"
            )
            return data

        except UnicodeDecodeError:
            # Fallback to latin-1 encoding
            logger.warning("UTF-8 decode failed, trying latin-1 encoding")
            with self.file_path.open("r", encoding="latin-1") as f:
                data = json.load(f)

            self._cached_data = data
            self._cached_mtime = current_mtime
            self._enhanced_engine = None

            return data

    def build(self, force: bool = False, **config_overrides) -> bool:
        """
        Build relationships file using optimal parameters.

        Args:
            force: Force rebuild even if dependencies aren't newer
            **config_overrides: Override default optimal parameters

        Returns:
            True if rebuild was performed, False if skipped
        """
        # Check if rebuild is actually needed
        if not force and not self.needs_rebuild():
            logger.debug("Relationships rebuild not needed")
            return False

        logger.info("Building relationships with optimal parameters...")

        try:
            # Get version-specific paths using ResourcePathAccessor
            path_accessor = ResourcePathAccessor(dd_version=dd_version)
            input_dir = path_accessor.version_dir / "schemas" / "detailed"
            output_file = path_accessor.version_dir / "schemas" / "relationships.json"

            # Create configuration with optimal parameters
            default_config = {
                "encoder_config": self.encoder_config,
                "cross_ids_eps": OPTIMAL_CROSS_IDS_EPS,
                "cross_ids_min_samples": OPTIMAL_CROSS_IDS_MIN_SAMPLES,
                "intra_ids_eps": OPTIMAL_INTRA_IDS_EPS,
                "intra_ids_min_samples": OPTIMAL_INTRA_IDS_MIN_SAMPLES,
                "use_rich": True,
                "ids_set": self.encoder_config.ids_set,
                "input_dir": input_dir,
                "output_file": output_file,
            }
            default_config.update(config_overrides)

            config = RelationshipExtractionConfig(**default_config)

            # Build relationships using the extractor
            extractor = RelationshipExtractor(config)
            relationships = extractor.extract_relationships(force_rebuild=True)

            # Save relationships
            extractor.save_relationships(relationships)

            # Invalidate cache to pick up new data
            self._invalidate_cache()

            logger.info("Relationships build completed successfully")
            return True

        except Exception as e:
            logger.error(f"Failed to build relationships: {e}")
            raise

    def get_data(self) -> dict[str, Any]:
        """
        Get relationships data with caching and auto-rebuild.

        Returns:
            Dictionary containing relationships data.
        """
        return self._load_relationships_data()

    def get_enhanced_engine(self) -> EnhancedRelationshipEngine:
        """
        Get enhanced relationship engine with cached relationships data.

        Returns:
            EnhancedRelationshipEngine instance.
        """
        if self._enhanced_engine is None:
            relationships_data = self.get_data()
            self._enhanced_engine = EnhancedRelationshipEngine(relationships_data)
            logger.debug("Created enhanced relationship engine")

        return self._enhanced_engine

    def get_clusters(self) -> list[dict[str, Any]]:
        """Get relationship clusters."""
        data = self.get_data()
        return data.get("clusters", [])

    def get_metadata(self) -> dict[str, Any]:
        """Get relationships metadata."""
        data = self.get_data()
        return data.get("metadata", {})

    def get_unit_families(self) -> dict[str, Any]:
        """Get unit families information."""
        data = self.get_data()
        return data.get("unit_families", {})

    def get_cross_references(self) -> dict[str, Any]:
        """Get cross-references information."""
        data = self.get_data()
        return data.get("cross_references", {})

    def is_available(self) -> bool:
        """Check if relationships data is available."""
        try:
            self.get_data()
            return True
        except (FileNotFoundError, json.JSONDecodeError):
            return False

    def needs_rebuild(self) -> bool:
        """
        Check if relationships file needs rebuilding based on dependencies.

        Returns:
            True if rebuild is recommended, False otherwise.
        """
        return self._check_dependency_freshness()

    def get_cache_info(self) -> dict[str, Any]:
        """
        Get information about the current cache state.

        Returns:
            Dictionary with cache statistics and status.
        """
        info = {
            "file_path": str(self.file_path),
            "file_exists": self.file_path.exists(),
            "cached": self._cached_data is not None,
            "engine_cached": self._enhanced_engine is not None,
        }

        if self.file_path.exists():
            info["file_size_mb"] = self.file_path.stat().st_size / (1024 * 1024)
            info["file_mtime"] = datetime.fromtimestamp(
                self._get_file_mtime(self.file_path)
            ).isoformat()

        if self._cached_data:
            info["clusters_count"] = len(self._cached_data.get("clusters", []))
            info["has_metadata"] = "metadata" in self._cached_data
            info["has_unit_families"] = "unit_families" in self._cached_data

        info["needs_rebuild"] = self.needs_rebuild()

        return info

    def force_reload(self) -> None:
        """Force reload of relationships data, bypassing cache."""
        logger.info("Forcing reload of relationships data")
        self._invalidate_cache()
        # Next call to get_data() will reload from disk
