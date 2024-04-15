import base64
import hashlib
import logging
import pickle
from io import BytesIO

from django_q.tasks import async_task
from google.cloud.documentai_v1.types.geometry import NormalizedVertex
from PIL import Image, ImageDraw

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


def get_page_image(statement, page_no):
    try:
        api_response = pickle.loads(statement.api_response.response)
        logger.info(f"statement {statement.name} page {page_no} has {len(api_response.entities)} entities")

        image = Image.open(BytesIO(api_response.pages[page_no - 1].image.content))
        draw = ImageDraw.Draw(image)

        for entity in api_response.entities:
            if entity.type_ == "acct":
                color = "blue"
                bounding_box = _find_overall_bounding_box_(entity, page_no)
            elif entity.type_ == "trx":
                color = "red"
                bounding_box = _find_overall_bounding_box_(entity, page_no)
            elif entity.type_ == "begin_of_table":
                color = "grey"
                bounding_box = entity.page_anchor.page_refs[0].bounding_poly.normalized_vertices
            else:
                next

            vertices = [(vertex.x * image.width, vertex.y * image.height) for vertex in bounding_box]
            draw.polygon(vertices, outline=color, width=2)

        next_page = page_no + 1 if page_no < len(api_response.pages) else 0
        prev_page = page_no - 1 if page_no > 1 else 0

        output_bytes = BytesIO()
        image.save(output_bytes, format="PNG")

        return base64.b64encode(output_bytes.getvalue()).decode("utf-8"), prev_page, next_page

    except Exception as e:
        logger.error(f"failed to get page image: {e}")
        return None


def _find_overall_bounding_box_(entity, page_no):
    """page_no is 1 based, not 0 based"""
    # Initialize to maximum and minimum possible values
    min_x, min_y = 1.0, 1.0
    max_x, max_y = 0.0, 0.0

    # Iterate through each box and its vertices
    for prop in entity.properties:
        page_ref = prop.page_anchor.page_refs[0]
        for vertex in page_ref.bounding_poly.normalized_vertices:
            if page_ref.page == page_no - 1:
                min_x = min(min_x, vertex.x)
                max_x = max(max_x, vertex.x)
                min_y = min(min_y, vertex.y)
                max_y = max(max_y, vertex.y)

    # Return the overall bounding box
    return [
        NormalizedVertex(x=min_x, y=min_y),
        NormalizedVertex(x=max_x, y=min_y),
        NormalizedVertex(x=max_x, y=max_y),
        NormalizedVertex(x=min_x, y=max_y),
    ]
