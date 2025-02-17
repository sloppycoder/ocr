import json
import logging
import os
from typing import Optional

from google.api_core.client_options import ClientOptions
from google.cloud.documentai import DocumentProcessorServiceClient, ProcessRequest, RawDocument  # type: ignore
from google.cloud.documentai_v1.types import Document
from google.cloud.documentai_v1.types.geometry import NormalizedVertex

logger = logging.getLogger(__name__)


def _get_gogle_client_(
    location: str = os.getenv("PROCESSOR_LOCATION", "us"),
    json_key: str = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON", "{}"),
):

    opts = ClientOptions(api_endpoint=f"{location}-documentai.googleapis.com")
    account_info = json.loads(json_key)

    if account_info:
        logger.info("using service account key from GOOGLE_APPLICATION_CREDENTIALS_JSON")
        return DocumentProcessorServiceClient.from_service_account_info(info=account_info, client_options=opts)
    else:
        logger.info("using default credentials")
        return DocumentProcessorServiceClient(client_options=opts)


def _processor_path_(
    google_client: DocumentProcessorServiceClient,
    project_id: str,
    location: str,
    processor_id: str,
    processor_version_id: Optional[str],
) -> str:
    if processor_version_id:
        # The full resource name of the processor version, e.g.:
        # `projects/{project_id}/locations/{location}/processors/{processor_id}/processorVersions/{processor_version_id}`
        return google_client.processor_version_path(
            project_id,
            location,
            processor_id,
            processor_version_id,
        )
    else:
        # The full resource name of the processor, e.g.:
        # `projects/{project_id}/locations/{location}/processors/{processor_id}`
        return google_client.processor_path(project_id, location, processor_id)


def process_document(
    _: int,  # used as context to async_ask, not used in processing logic
    image_content: bytes,
    content_sha: str,  # noqa: parameter used by joblib for caching, not used in processing
    mime_type: str = "application/octet-stream",
    field_mask: Optional[str] = None,
    project_id: str = os.getenv("PROJECT_ID", ""),
    location: str = os.getenv("PROCESSOR_LOCATION", "us"),
    processor_id: str = os.getenv("PROCESSOR_ID", ""),
    processor_version_id: Optional[str] = os.getenv("PROCESSOR_VERSION_ID"),
    json_key: str = os.getenv("GOOGLE_APPLICATION_CREDENTIALS_JSON", "{}"),
) -> Document:

    raw_document = RawDocument(content=image_content, mime_type=mime_type)

    google_client = _get_gogle_client_(location, json_key)
    processor_path = _processor_path_(
        google_client,
        project_id,
        location,
        processor_id,
        processor_version_id,
    )

    logger.info(f"processor path: {processor_path}")

    request = ProcessRequest(
        name=processor_path,
        raw_document=raw_document,
        field_mask=field_mask,
    )

    result = google_client.process_document(request=request)

    # For a full list of `Document` object attributes, reference this page:
    # https://cloud.google.com/document-ai/docs/reference/rest/v1/Document
    document = result.document

    logger.info(f"Processed: -> sha={content_sha[-7:]} {len(document.pages)} pages, {len(document.entities)} entities")

    return document


def find_overall_bounding_box(entity):
    # Initialize to maximum and minimum possible values
    min_x, min_y = 1.0, 1.0
    max_x, max_y = 0.0, 0.0

    if entity.properties:
        # Iterate through each box and its vertices
        for prop in entity.properties:
            page_ref = prop.page_anchor.page_refs[0]
            for vertex in page_ref.bounding_poly.normalized_vertices:
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
    else:
        page_ref = entity.page_anchor.page_refs[0]
        return page_ref.bounding_poly.normalized_vertices


def find_page_for_entity(entity):
    if entity.properties:
        return entity.properties[0].page_anchor.page_refs[0].page
    else:
        return entity.page_anchor.page_refs[0].page
