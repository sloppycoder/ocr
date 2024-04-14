import hashlib
import logging
import pickle

from django_q.tasks import async_task

import ocr_engine.gcp  # noqa: F401

from .models import ApiResponse, Statement

logger = logging.getLogger(__name__)


# async_task cannot handle exceptions thrown by the function
# this wraps the function we want to invoke, catches its exceptions
# and returns the result and exception as a tuple
def task_wrapper(func):
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs), None
        except Exception as e:
            return None, e

    return wrapper


process_document_wrapper = task_wrapper(ocr_engine.gcp.process_document)


def save_file(file_name: str, mime_type: str, file_content: bytes):
    statement = Statement.objects.create(
        name=file_name,
        mime_type=mime_type,
        content=file_content,
        content_sha=hashlib.sha1(file_content).hexdigest(),
    )

    logger.info(f"saved Statement({statement.id}) for {file_name} {mime_type}")

    if match_existing_response(statement):
        return

    # no existing API response matches the new document
    # need to invoke API to parse the document
    #
    # 1. make sure the match parameters carefully
    #
    #   def process_document(
    #       _: int,  # used as context to async_ask, not used in processing logic
    #       image_content: bytes,
    #       content_sha: str,  # noqa: parameter used by joblib for caching, not used in processing
    #       mime_type: str = "application/octet-stream",
    #
    # 2. async_task cannot resolve a simple function name
    #    without module name, so we need to use module.function

    async_task(
        f"{__name__}.process_document_wrapper",
        statement.id,
        statement.content,
        statement.content_sha,
        statement.mime_type,
        hook=save_api_response,
    )


def match_existing_response(statement):
    """
    find existing api response that matches the new document's content
    and mime_type return the response if found
    """
    response = ApiResponse.objects.filter(
        content_sha=statement.content_sha,
        mime_type=statement.mime_type,
        errors__isnull=True,
    ).first()

    if response is None:
        return False

    statement.api_response = response
    statement.save()

    logger.info(f"found existing ApiResponse({response.id}) for Statement({statement.id})")

    return True


def save_api_response(task):
    """save api response to database and assoicate to the corresponding statement"""
    if not task.success:
        logger.error(f"task failed: {task.result}")
        return

    try:
        api_response, ex = task.result

        statement_id = task.args[0]
        statement = Statement.objects.get(id=statement_id)
        statement.api_response = ApiResponse.objects.create(
            content_sha=task.args[2],
            mime_type=task.args[3],
            response=pickle.dumps(api_response),
            errors=str(ex) if ex else None,
        )
        statement.save()

        logger.info(f"Received API response for Documen({statement_id})")

    except Statement.DoesNotExist:
        logger.error(f"statement({statement_id}) not found, api response abandoned")
