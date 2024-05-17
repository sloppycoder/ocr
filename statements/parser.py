import json
import pickle
from dataclasses import dataclass
from datetime import datetime
from decimal import Decimal
from typing import Any, Iterator, Optional

from google.cloud.documentai_v1.types.geometry import NormalizedVertex

from ocr_engine.gcp import find_overall_bounding_box

from .models import Statement, Transaction


class NormalizedVertexEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, NormalizedVertex):
            return obj.to_dict()
        return super().default(obj)


@dataclass
class TextEntity:
    type_: str
    props: dict[str, Any]
    page: int
    bounding_box: list[NormalizedVertex]


def props2dict(entity) -> dict[str, Any]:
    return {prop.type_: prop.mention_text for prop in entity.properties}


def prop2date(date_str):
    if date_str is None:
        return None
    else:
        try:
            return datetime.strptime(date_str.replace(" ", "").strip().upper(), "%d%b%Y").date()
        except Exception as e:
            print(f"*** {date_str}, {e}")


def prop2decimal(value) -> Optional[Decimal]:
    if value is None:
        return value
    else:
        return Decimal(value.split(" ")[0].replace(",", ""))


def enumerate_entities(document, sort_entities: bool = True) -> Iterator[TextEntity]:
    entities: list[TextEntity] = []

    for entity in document.entities:
        if entity.type_ == "begin_of_table":
            page_ref = entity.page_anchor.page_refs[0]
            entities.append(
                TextEntity(
                    type_=entity.type_,
                    props={"text", entity.mention_text},
                    page=page_ref.page,
                    bounding_box=page_ref.bounding_poly.normalized_vertices,
                ),
            )

        elif entity.type_ in ["acct", "trx"]:
            entities.append(
                TextEntity(
                    type_=entity.type_,
                    props=props2dict(entity),
                    page=entity.properties[0].page_anchor.page_refs[0].page,  # all props should be on the same page
                    bounding_box=find_overall_bounding_box(entity),
                )
            )

    if sort_entities:
        # sort by the y coordinate of the upper left point.
        # add page number to ensure text on lower pages are considered smaller
        entities.sort(key=lambda e: e.page * 10.0 + e.bounding_box[0].y)

    for entity in entities:
        yield entity


def parse_statement(statement: Statement) -> None:
    table_found = False
    account_num = None

    # Delete all transactions related to the statement
    statement.transactions.all().delete()

    document = pickle.loads(statement.api_response.response)
    for entity in enumerate_entities(document, sort_entities=True):
        if entity.type_ == "begin_of_table":
            table_found = True
            continue

        if not table_found:
            print(f"--- ignored {entity}")
            continue

        elif entity.type_ == "acct":
            new_account_type = entity.props["type"] if entity.props.get("type") else "unknown"
            new_account_num = entity.props["num"]

            if new_account_type.startswith("CURRENT") or new_account_type.startswith("SAVING"):
                if account_num is None or account_num != new_account_num:
                    account_num = new_account_num

        elif entity.type_ == "trx":
            if account_num is None:
                print(f"=== ignore trx before account in document {statement.name} {entity}")
                continue

            trx = Transaction(
                trx_date=prop2date(entity.props.get("date")),
                account_num=account_num,
                deposit_amount=prop2decimal(entity.props.get("deposit_amount")),
                withdraw_amount=prop2decimal(entity.props.get("withdraw_amount")),
                balance=prop2decimal(entity.props.get("balance")),
                description=entity.props.get("desc"),
                statement=statement,
                raw_entity=pickle.dumps(entity),
            )
            trx.save()
            print(f"extracted transaction {trx}")

        else:
            print(f"==== ignored in document {statement.name} {entity}")


def extract_from_statements(name_filter: str):
    for statement in Statement.objects.filter(name__icontains=name_filter):
        print(f"extracting from {statement.name}")
        parse_statement(statement)
