# ============================================================
# MOODBLOOM 4.0 — BACKUP & RECOVERY
# ============================================================
#
# This module was referenced by scheduler.py but did not exist,
# which crashed the whole bot on startup (ImportError). It backs
# up BOTH databases together:
#
#   • config.DATA_FILE      (legacy database.py store)
#   • v4_data.V4_DATA_FILE  (MoodBloom 4.0 store)
#
# Every backup is a folder containing a copy of both files plus
# a manifest describing what was captured.
# ============================================================

import json
import os
import shutil
from datetime import datetime

import config
import v4_data


# ============================================================
# PATHS
# ============================================================

BACKUP_ROOT = os.path.join(
    os.path.dirname(config.DATA_FILE) or ".",
    "full_backups",
)

MAIN_DB_FILE = config.DATA_FILE
V4_DB_FILE = v4_data.V4_DATA_FILE

MAX_BACKUPS_TO_KEEP = 14


# ============================================================
# HELPERS
# ============================================================

def _now_stamp():
    return datetime.now().strftime("%Y%m%d_%H%M%S")


def _ensure_backup_root():
    os.makedirs(BACKUP_ROOT, exist_ok=True)


def list_backups():
    """
    Returns backup folder names sorted newest-first.
    """

    _ensure_backup_root()

    try:
        entries = [
            name
            for name in os.listdir(BACKUP_ROOT)
            if os.path.isdir(os.path.join(BACKUP_ROOT, name))
        ]
    except Exception:
        entries = []

    entries.sort(reverse=True)

    return entries


def get_latest_backup():
    backups = list_backups()
    return backups[0] if backups else None


# ============================================================
# CREATE FULL BACKUP
# ============================================================

def create_full_backup():
    """
    Creates one timestamped backup folder containing a copy of
    the main database and the V4 database, plus a manifest.

    Returns the backup folder path on success, False on failure.
    """

    try:
        _ensure_backup_root()

        folder_name = f"backup_{_now_stamp()}"
        folder_path = os.path.join(BACKUP_ROOT, folder_name)
        os.makedirs(folder_path, exist_ok=True)

        manifest = {
            "created_at": datetime.now().isoformat(),
            "files": [],
        }

        for label, source in (
            ("main_database", MAIN_DB_FILE),
            ("v4_database", V4_DB_FILE),
        ):
            if source and os.path.exists(source):
                destination = os.path.join(
                    folder_path,
                    os.path.basename(source),
                )
                shutil.copy2(source, destination)
                manifest["files"].append({
                    "label": label,
                    "source": source,
                    "backup_name": os.path.basename(source),
                    "size": os.path.getsize(destination),
                })

        manifest_path = os.path.join(folder_path, "manifest.json")

        with open(manifest_path, "w", encoding="utf-8") as file:
            json.dump(manifest, file, indent=4, ensure_ascii=False)

        # Record the backup time inside the V4 database too.
        try:
            v4_data.create_v4_backup()
        except Exception:
            pass

        cleanup_old_backups()

        return folder_path

    except Exception as error:
        print("⚠️ Full backup error:", error)
        return False


# ============================================================
# CLEANUP OLD BACKUPS
# ============================================================

def cleanup_old_backups(keep=MAX_BACKUPS_TO_KEEP):
    """
    Keeps only the most recent `keep` full backups.

    Returns the number of backups removed.
    """

    try:
        keep = max(1, int(keep))
    except Exception:
        keep = MAX_BACKUPS_TO_KEEP

    backups = list_backups()

    removed = 0

    for name in backups[keep:]:

        try:
            shutil.rmtree(os.path.join(BACKUP_ROOT, name))
            removed += 1
        except Exception as error:
            print(f"⚠️ Could not remove old backup {name}:", error)

    return removed


# ============================================================
# VALIDATE A BACKUP
# ============================================================

def validate_backup(folder_name):
    """
    Confirms a backup folder has a manifest and matching files.
    """

    folder_path = os.path.join(BACKUP_ROOT, folder_name)

    if not os.path.isdir(folder_path):
        return {"valid": False, "errors": ["Backup folder not found."]}

    manifest_path = os.path.join(folder_path, "manifest.json")

    errors = []

    if not os.path.exists(manifest_path):
        errors.append("Missing manifest.json")
        return {"valid": False, "errors": errors}

    try:
        with open(manifest_path, "r", encoding="utf-8") as file:
            manifest = json.load(file)
    except Exception as error:
        return {"valid": False, "errors": [f"Manifest unreadable: {error}"]}

    for entry in manifest.get("files", []):
        backup_name = entry.get("backup_name")
        if not backup_name or not os.path.exists(
            os.path.join(folder_path, backup_name)
        ):
            errors.append(f"Missing file: {backup_name}")

    return {"valid": len(errors) == 0, "errors": errors}


# ============================================================
# RESTORE FROM BACKUP
# ============================================================

def restore_full_backup(folder_name):
    """
    Restores both databases from a given backup folder.

    A safety backup of the CURRENT state is created first.
    """

    folder_path = os.path.join(BACKUP_ROOT, folder_name)

    check = validate_backup(folder_name)

    if not check["valid"]:
        print("⚠️ Backup validation failed:", check["errors"])
        return False

    # Safety backup before touching anything.
    try:
        create_full_backup()
    except Exception:
        pass

    try:
        manifest_path = os.path.join(folder_path, "manifest.json")

        with open(manifest_path, "r", encoding="utf-8") as file:
            manifest = json.load(file)

        for entry in manifest.get("files", []):

            backup_name = entry.get("backup_name")
            source_path = entry.get("source")

            if not backup_name or not source_path:
                continue

            backup_file = os.path.join(folder_path, backup_name)

            os.makedirs(os.path.dirname(source_path) or ".", exist_ok=True)

            shutil.copy2(backup_file, source_path)

        print(f"♻️ Restored full backup: {folder_name}")

        return True

    except Exception as error:
        print("⚠️ Restore error:", error)
        return False


# ============================================================
# HEALTH CHECK
# ============================================================

def health_check():
    """
    Quick status report on both databases and backups.
    """

    report = {
        "main_database_exists": os.path.exists(MAIN_DB_FILE),
        "v4_database_exists": os.path.exists(V4_DB_FILE),
        "backup_count": len(list_backups()),
        "latest_backup": get_latest_backup(),
    }

    try:
        report["v4_validation"] = v4_data.validate_v4_database()
    except Exception as error:
        report["v4_validation"] = {"valid": False, "errors": [str(error)]}

    return report


# ============================================================
# EMERGENCY RECOVERY
# ============================================================

def emergency_recovery():
    """
    Attempts to restore the most recent valid backup.

    Used when the live databases are missing or corrupted.
    """

    for name in list_backups():

        check = validate_backup(name)

        if check["valid"]:
            print(f"🚨 Emergency recovery using backup: {name}")
            return restore_full_backup(name)

    print("🚨 Emergency recovery failed: no valid backup found.")
    return False
