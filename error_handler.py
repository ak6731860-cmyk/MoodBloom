# ============================================================
# MOODBLOOM 4.0 — ERROR HANDLER & LOGGING SYSTEM
# ============================================================

import logging
import traceback
from datetime import datetime
from pathlib import Path

import config


# ============================================================
# CONFIGURATION
# ============================================================

LOG_DIRECTORY = Path(
    getattr(
        config,
        "LOG_DIR",
        Path(config.DATA_FILE).parent / "logs"
    )
)

LOG_FILE = LOG_DIRECTORY / "moodbloom.log"
ERROR_LOG_FILE = LOG_DIRECTORY / "errors.log"

MAX_LOG_FILE_SIZE = 5 * 1024 * 1024  # 5 MB
BACKUP_COUNT = 5


# ============================================================
# ENSURE LOG DIRECTORY
# ============================================================

def ensure_log_directory():
    try:
        LOG_DIRECTORY.mkdir(
            parents=True,
            exist_ok=True
        )
        return True

    except Exception:
        return False


# ============================================================
# LOG FORMAT
# ============================================================

LOG_FORMAT = (
    "%(asctime)s | "
    "%(levelname)s | "
    "%(name)s | "
    "%(message)s"
)

DATE_FORMAT = "%Y-%m-%d %H:%M:%S"


# ============================================================
# LOGGER SETUP
# ============================================================

def _create_file_handler(
    filename,
    level=logging.INFO
):
    """
    Create a rotating file handler.
    """

    ensure_log_directory()

    try:

        from logging.handlers import RotatingFileHandler

        handler = RotatingFileHandler(
            filename,
            maxBytes=MAX_LOG_FILE_SIZE,
            backupCount=BACKUP_COUNT,
            encoding="utf-8"
        )

        handler.setLevel(level)

        formatter = logging.Formatter(
            LOG_FORMAT,
            datefmt=DATE_FORMAT
        )

        handler.setFormatter(
            formatter
        )

        return handler

    except Exception:

        return None


def setup_logging():
    """
    Configure MoodBloom logging system.
    """

    ensure_log_directory()

    root_logger = logging.getLogger()

    root_logger.setLevel(
        logging.INFO
    )

    # Prevent duplicate handlers
    existing_paths = set()

    for handler in root_logger.handlers:

        try:

            if hasattr(handler, "baseFilename"):
                existing_paths.add(
                    str(
                        Path(
                            handler.baseFilename
                        ).resolve()
                    )
                )

        except Exception:
            pass

    log_path = str(
        LOG_FILE.resolve()
    )

    error_path = str(
        ERROR_LOG_FILE.resolve()
    )

    # Main log
    if log_path not in existing_paths:

        main_handler = _create_file_handler(
            LOG_FILE,
            logging.INFO
        )

        if main_handler:
            root_logger.addHandler(
                main_handler
            )

    # Error log
    if error_path not in existing_paths:

        error_handler = _create_file_handler(
            ERROR_LOG_FILE,
            logging.ERROR
        )

        if error_handler:
            root_logger.addHandler(
                error_handler
            )

    # Console handler
    has_stream_handler = any(
        isinstance(
            handler,
            logging.StreamHandler
        )
        and not hasattr(
            handler,
            "baseFilename"
        )
        for handler
        in root_logger.handlers
    )

    if not has_stream_handler:

        console_handler = logging.StreamHandler()

        console_handler.setLevel(
            logging.INFO
        )

        formatter = logging.Formatter(
            LOG_FORMAT,
            datefmt=DATE_FORMAT
        )

        console_handler.setFormatter(
            formatter
        )

        root_logger.addHandler(
            console_handler
        )

    return root_logger


# Initialize logging.
logger = setup_logging()


# ============================================================
# SAFE STRING
# ============================================================

def _safe_string(
    value,
    default=""
):
    if value is None:
        return default

    try:
        return str(value)
    except Exception:
        return default


# ============================================================
# USER-FRIENDLY ERROR MESSAGES
# ============================================================

ERROR_MESSAGES = {
    "telegram":
        "Telegram se related temporary problem aa gayi. Please thodi der baad try karo.",

    "database":
        "MoodBloom ke data ko access karne me problem aa gayi. Please dobara try karo.",

    "network":
        "Network connection me temporary problem hai. Please thodi der baad try karo.",

    "permission":
        "MoodBloom ko is action ke liye required permission nahi mili.",

    "validation":
        "Input valid nahi hai. Please details check karke dobara try karo.",

    "not_found":
        "Requested information nahi mili.",

    "timeout":
        "Request ko complete hone me zyada time lag gaya. Please dobara try karo.",

    "unknown":
        "Oops! MoodBloom me temporary problem aa gayi. Please dobara try karo.",
}


# ============================================================
# ERROR CATEGORY DETECTION
# ============================================================

def detect_error_category(error):
    """
    Try to classify an exception.
    """

    if error is None:
        return "unknown"

    error_name = type(error).__name__.lower()

    error_text = _safe_string(
        error
    ).lower()

    combined = (
        error_name + " " + error_text
    )

    if any(
        word in combined
        for word in (
            "telegram",
            "badrequest",
            "forbidden",
            "chatnotfound",
            "retryafter",
        )
    ):
        return "telegram"

    if any(
        word in combined
        for word in (
            "database",
            "json",
            "sqlite",
            "storage",
            "file",
            "filenotfound",
        )
    ):
        return "database"

    if any(
        word in combined
        for word in (
            "network",
            "connection",
            "connect",
            "dns",
            "socket",
        )
    ):
        return "network"

    if any(
        word in combined
        for word in (
            "permission",
            "access",
            "forbidden",
        )
    ):
        return "permission"

    if any(
        word in combined
        for word in (
            "valueerror",
            "typeerror",
            "validation",
            "invalid",
        )
    ):
        return "validation"

    if any(
        word in combined
        for word in (
            "notfound",
            "does not exist",
            "not found",
        )
    ):
        return "not_found"

    if any(
        word in combined
        for word in (
            "timeout",
            "timed out",
        )
    ):
        return "timeout"

    return "unknown"


# ============================================================
# USER-FRIENDLY MESSAGE
# ============================================================

def get_user_friendly_message(
    error=None,
    category=None
):
    """
    Convert technical exception into a
    safe Telegram-friendly message.
    """

    if category is None:

        category = detect_error_category(
            error
        )

    return ERROR_MESSAGES.get(
        category,
        ERROR_MESSAGES["unknown"]
    )


# ============================================================
# ERROR DETAILS
# ============================================================

def get_error_details(error):
    """
    Return structured technical error details.
    """

    if error is None:

        return {
            "type": "None",
            "message": "",
            "category": "unknown",
        }

    category = detect_error_category(
        error
    )

    return {
        "type": type(error).__name__,
        "message": _safe_string(error),
        "category": category,
        "user_message":
            get_user_friendly_message(
                error,
                category
            ),
    }


# ============================================================
# FORMAT TRACEBACK
# ============================================================

def format_traceback(error=None):
    """
    Return traceback as text.
    """

    try:

        if error is not None:

            return "".join(
                traceback.format_exception(
                    type(error),
                    error,
                    error.__traceback__
                )
            )

        return traceback.format_exc()

    except Exception as exc:

        return (
            f"Traceback formatting failed: "
            f"{exc}"
        )


# ============================================================
# LOG FUNCTIONS
# ============================================================

def log_debug(
    message,
    *args
):
    logger.debug(
        message,
        *args
    )


def log_info(
    message,
    *args
):
    logger.info(
        message,
        *args
    )


def log_warning(
    message,
    *args
):
    logger.warning(
        message,
        *args
    )


def log_error(
    message,
    *args,
    exc_info=False
):
    logger.error(
        message,
        *args,
        exc_info=exc_info
    )


def log_exception(
    message="Unhandled exception"
):
    logger.exception(
        message
    )


# ============================================================
# EXCEPTION LOGGER
# ============================================================

def log_exception_details(
    error,
    context=None,
    user_id=None,
    chat_id=None
):
    """
    Log detailed exception information.
    """

    details = get_error_details(
        error
    )

    context_text = (
        _safe_string(context)
        if context
        else "No context"
    )

    user_text = (
        _safe_string(user_id)
        if user_id is not None
        else "Unknown"
    )

    chat_text = (
        _safe_string(chat_id)
        if chat_id is not None
        else "Unknown"
    )

    logger.error(
        "Exception | "
        "category=%s | "
        "type=%s | "
        "user_id=%s | "
        "chat_id=%s | "
        "context=%s | "
        "message=%s",
        details["category"],
        details["type"],
        user_text,
        chat_text,
        context_text,
        details["message"],
        exc_info=True,
    )

    return details


# ============================================================
# SAFE EXECUTION
# ============================================================

def safe_execute(
    function,
    *args,
    default=None,
    context=None,
    **kwargs
):
    """
    Execute a function safely.

    Instead of crashing the bot, return default.
    """

    try:

        return function(
            *args,
            **kwargs
        )

    except Exception as error:

        log_exception_details(
            error,
            context=context
        )

        return default


# ============================================================
# SAFE EXECUTION WITH RESULT
# ============================================================

def safe_execute_result(
    function,
    *args,
    context=None,
    **kwargs
):
    """
    Execute a function and return:
        {
            success: bool,
            result: ...,
            error: ...
        }
    """

    try:

        result = function(
            *args,
            **kwargs
        )

        return {
            "success": True,
            "result": result,
            "error": None,
        }

    except Exception as error:

        details = log_exception_details(
            error,
            context=context
        )

        return {
            "success": False,
            "result": None,
            "error": details,
        }


# ============================================================
# ASYNC SAFE EXECUTION
# ============================================================

async def safe_async_execute(
    function,
    *args,
    default=None,
    context=None,
    **kwargs
):
    """
    Safely execute an async function.
    """

    try:

        return await function(
            *args,
            **kwargs
        )

    except Exception as error:

        log_exception_details(
            error,
            context=context
        )

        return default


# ============================================================
# TELEGRAM ERROR HANDLER
# ============================================================

async def telegram_error_handler(
    update,
    context
):
    """
    Global python-telegram-bot error handler.

    This function will later be registered
    inside bot.py.
    """

    error = getattr(
        context,
        "error",
        None
    )

    user_id = None
    chat_id = None

    try:

        if update:

            user = getattr(
                update,
                "effective_user",
                None
            )

            chat = getattr(
                update,
                "effective_chat",
                None
            )

            if user:
                user_id = getattr(
                    user,
                    "id",
                    None
                )

            if chat:
                chat_id = getattr(
                    chat,
                    "id",
                    None
                )

    except Exception:
        pass

    details = log_exception_details(
        error,
        context="telegram_update",
        user_id=user_id,
        chat_id=chat_id
    )

    # Try sending a friendly message.
    try:

        if update:

            message = getattr(
                update,
                "effective_message",
                None
            )

            if message:

                await message.reply_text(
                    get_user_friendly_message(
                        error,
                        details.get(
                            "category"
                        )
                    )
                )

    except Exception as send_error:

        log_exception_details(
            send_error,
            context="sending_error_message",
            user_id=user_id,
            chat_id=chat_id
        )


# ============================================================
# ERROR REPORT
# ============================================================

def create_error_report(
    error,
    context=None,
    user_id=None,
    chat_id=None
):
    """
    Create a structured error report.
    """

    details = get_error_details(
        error
    )

    return {
        "timestamp":
            datetime.now().isoformat(),

        "category":
            details["category"],

        "type":
            details["type"],

        "message":
            details["message"],

        "user_message":
            details["user_message"],

        "context":
            _safe_string(
                context
            ),

        "user_id":
            user_id,

        "chat_id":
            chat_id,

        "traceback":
            format_traceback(
                error
            ),
    }


# ============================================================
# WRITE ERROR REPORT
# ============================================================

def save_error_report(
    error,
    context=None,
    user_id=None,
    chat_id=None
):
    """
    Save detailed error report to a separate file.
    """

    report = create_error_report(
        error,
        context=context,
        user_id=user_id,
        chat_id=chat_id
    )

    try:

        ensure_log_directory()

        timestamp = datetime.now().strftime(
            "%Y%m%d_%H%M%S_%f"
        )

        report_file = (
            LOG_DIRECTORY /
            f"error_{timestamp}.log"
        )

        with open(
            report_file,
            "w",
            encoding="utf-8"
        ) as file:

            file.write(
                "MOODBLOOM ERROR REPORT\n"
            )

            file.write(
                "=" * 60 + "\n\n"
            )

            file.write(
                f"Timestamp: "
                f"{report['timestamp']}\n"
            )

            file.write(
                f"Category: "
                f"{report['category']}\n"
            )

            file.write(
                f"Type: "
                f"{report['type']}\n"
            )

            file.write(
                f"Message: "
                f"{report['message']}\n"
            )

            file.write(
                f"Context: "
                f"{report['context']}\n"
            )

            file.write(
                f"User ID: "
                f"{report['user_id']}\n"
            )

            file.write(
                f"Chat ID: "
                f"{report['chat_id']}\n\n"
            )

            file.write(
                "TRACEBACK\n"
            )

            file.write(
                "-" * 60 + "\n"
            )

            file.write(
                report["traceback"]
            )

        return {
            "success": True,
            "file": str(report_file),
        }

    except Exception as exc:

        return {
            "success": False,
            "error": str(exc),
        }


# ============================================================
# CLEANUP OLD ERROR REPORTS
# ============================================================

def cleanup_error_reports(
    max_reports=100
):
    """
    Keep only the newest error reports.
    """

    ensure_log_directory()

    try:

        reports = list(
            LOG_DIRECTORY.glob(
                "error_*.log"
            )
        )

        reports.sort(
            key=lambda path: path.stat().st_mtime,
            reverse=True
        )

        deleted = []

        for report in reports[
            max_reports:
        ]:

            try:

                report.unlink()

                deleted.append(
                    report.name
                )

            except Exception:
                pass

        return {
            "success": True,
            "deleted": deleted,
            "remaining": len(
                list(
                    LOG_DIRECTORY.glob(
                        "error_*.log"
                    )
                )
            ),
        }

    except Exception as exc:

        return {
            "success": False,
            "error": str(exc),
        }


# ============================================================
# LOG STATISTICS
# ============================================================

def get_log_statistics():
    """
    Return logging system statistics.
    """

    ensure_log_directory()

    try:

        log_size = (
            LOG_FILE.stat().st_size
            if LOG_FILE.exists()
            else 0
        )

        error_size = (
            ERROR_LOG_FILE.stat().st_size
            if ERROR_LOG_FILE.exists()
            else 0
        )

        error_reports = len(
            list(
                LOG_DIRECTORY.glob(
                    "error_*.log"
                )
            )
        )

        return {
            "log_directory":
                str(LOG_DIRECTORY),

            "log_file":
                str(LOG_FILE),

            "error_log_file":
                str(ERROR_LOG_FILE),

            "log_size":
                log_size,

            "error_log_size":
                error_size,

            "error_reports":
                error_reports,
        }

    except Exception as exc:

        return {
            "error": str(exc)
        }


# ============================================================
# FORMAT LOG STATISTICS
# ============================================================

def format_log_statistics():
    stats = get_log_statistics()

    def format_size(size):
        try:
            size = int(size)
        except Exception:
            size = 0

        if size < 1024:
            return f"{size} B"

        if size < 1024 ** 2:
            return f"{size / 1024:.2f} KB"

        if size < 1024 ** 3:
            return f"{size / (1024 ** 2):.2f} MB"

        return f"{size / (1024 ** 3):.2f} GB"

    return (
        "🛡️ <b>MoodBloom Error System</b>\n\n"
        f"📁 Log Folder: "
        f"<code>{stats.get('log_directory', 'Unknown')}</code>\n"
        f"📄 Main Log: "
        f"{format_size(stats.get('log_size', 0))}\n"
        f"🚨 Error Log: "
        f"{format_size(stats.get('error_log_size', 0))}\n"
        f"🧾 Error Reports: "
        f"{stats.get('error_reports', 0)}"
    )


# ============================================================
# TEST LOGGER
# ============================================================

def test_logging():
    """
    Simple logging system test.
    """

    try:

        log_debug(
            "MoodBloom debug logging test."
        )

        log_info(
            "MoodBloom info logging test."
        )

        log_warning(
            "MoodBloom warning logging test."
        )

        return {
            "success": True,
            "message":
                "Logging system is working.",
        }

    except Exception as exc:

        return {
            "success": False,
            "error": str(exc),
        }


# ============================================================
# INITIALIZATION MESSAGE
# ============================================================

try:

    log_info(
        "MoodBloom 4.0 error handling system initialized."
    )

except Exception:
    pass


# ============================================================
# PUBLIC API
# ============================================================

__all__ = [
    "LOG_DIRECTORY",
    "LOG_FILE",
    "ERROR_LOG_FILE",

    "ERROR_MESSAGES",

    "ensure_log_directory",
    "setup_logging",

    "detect_error_category",
    "get_user_friendly_message",
    "get_error_details",
    "format_traceback",

    "log_debug",
    "log_info",
    "log_warning",
    "log_error",
    "log_exception",
    "log_exception_details",

    "safe_execute",
    "safe_execute_result",
    "safe_async_execute",

    "telegram_error_handler",

    "create_error_report",
    "save_error_report",
    "cleanup_error_reports",

    "get_log_statistics",
    "format_log_statistics",

    "test_logging",
]