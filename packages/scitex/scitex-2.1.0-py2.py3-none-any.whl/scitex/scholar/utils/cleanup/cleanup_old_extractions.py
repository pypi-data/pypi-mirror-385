#!/usr/bin/env python3
"""Clean up old extraction artifacts from MASTER directories."""

import argparse
from pathlib import Path
from scitex.scholar.config import ScholarConfig
from scitex import logging

logger = logging.getLogger(__name__)


def cleanup_master_extractions(library_dir: Path, dry_run: bool = True) -> dict:
    """Clean up old extraction artifacts.

    Removes:
    - extracted_text directories
    - page_X_img_X.jpg files (old format without zero-padding)

    Args:
        library_dir: Library directory path
        dry_run: If True, only report what would be deleted

    Returns:
        Dictionary with cleanup statistics
    """
    stats = {
        "directories_removed": 0,
        "files_removed": 0,
        "total_size_freed": 0
    }

    master_dir = library_dir / "MASTER"
    if not master_dir.exists():
        logger.warning(f"MASTER directory not found: {master_dir}")
        return stats

    for paper_dir in master_dir.iterdir():
        if not paper_dir.is_dir():
            continue

        # Remove extracted_text directories
        extracted_text_dir = paper_dir / "extracted_text"
        if extracted_text_dir.exists() and extracted_text_dir.is_dir():
            size = sum(f.stat().st_size for f in extracted_text_dir.rglob("*") if f.is_file())
            if dry_run:
                logger.info(f"Would remove: {extracted_text_dir} ({size} bytes)")
            else:
                import shutil
                shutil.rmtree(extracted_text_dir)
                logger.info(f"Removed: {extracted_text_dir} ({size} bytes)")
            stats["directories_removed"] += 1
            stats["total_size_freed"] += size

        # Remove old-format image files (page_X_img_X.jpg without zero-padding)
        for img_file in paper_dir.glob("page_*_img_*.jpg"):
            # Check if it's old format (no zero-padding)
            # Old: page_1_img_0.jpg, page_10_img_0.jpg
            # New would be: FILENAME_img_00.jpg
            if img_file.name.startswith("page_"):
                size = img_file.stat().st_size
                if dry_run:
                    logger.info(f"Would remove: {img_file} ({size} bytes)")
                else:
                    img_file.unlink()
                    logger.info(f"Removed: {img_file} ({size} bytes)")
                stats["files_removed"] += 1
                stats["total_size_freed"] += size

    return stats


def main():
    """Main entry point."""
    parser = argparse.ArgumentParser(
        description="Clean up old extraction artifacts from Scholar library"
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        default=True,
        help="Only report what would be deleted (default: True)"
    )
    parser.add_argument(
        "--execute",
        action="store_true",
        help="Actually delete files (overrides --dry-run)"
    )

    args = parser.parse_args()

    config = ScholarConfig()
    library_dir = config.get_library_dir()

    dry_run = not args.execute

    if dry_run:
        logger.warning("DRY RUN MODE - No files will be deleted")
        logger.warning("Use --execute to actually delete files")
    else:
        logger.warning("EXECUTE MODE - Files will be permanently deleted!")

    logger.info(f"Scanning library: {library_dir}")

    stats = cleanup_master_extractions(library_dir, dry_run=dry_run)

    logger.info("\nCleanup Summary:")
    logger.info(f"  Directories removed: {stats['directories_removed']}")
    logger.info(f"  Files removed: {stats['files_removed']}")
    logger.info(f"  Total size freed: {stats['total_size_freed']:,} bytes ({stats['total_size_freed']/1024/1024:.2f} MB)")

    if dry_run:
        logger.warning("\nThis was a DRY RUN - no files were actually deleted")
        logger.warning("Run with --execute to perform the cleanup")


if __name__ == "__main__":
    main()
