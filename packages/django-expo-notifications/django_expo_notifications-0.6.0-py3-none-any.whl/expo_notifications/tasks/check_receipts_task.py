from celery import shared_task
from django.utils import timezone
from exponent_server_sdk import (
    DeviceNotRegisteredError,
    PushClient,
    PushReceipt,
    PushServerError,
    PushTicketError,
)
from requests.exceptions import ConnectionError, HTTPError

from expo_notifications.conf import settings
from expo_notifications.models import Receipt, Ticket
from expo_notifications.tasks.session import session


@shared_task(
    bind=True,
    ignore_result=True,
    max_retries=settings.checking_task_max_retries,
    default_retry_delay=settings.checking_task_retry_delay.total_seconds(),
)
def check_receipts(self, ticket_pks: list[str]) -> None:
    tickets = Ticket.objects.filter(pk__in=ticket_pks).exclude(external_id="")

    push_tickets = [ticket.to_push_ticket() for ticket in tickets]

    push_client = PushClient(session=session)

    try:
        push_receipts: list[PushReceipt] = push_client.check_receipts_multiple(
            push_tickets
        )
    except PushServerError:
        raise self.retry()
    except (ConnectionError, HTTPError):
        raise self.retry()

    receipts: list[Receipt] = []

    for push_receipt in push_receipts:
        ticket = tickets.get(external_id=push_receipt.id)

        try:
            push_receipt.validate_response()
        except DeviceNotRegisteredError:
            ticket.message.device.is_active = False
            ticket.message.device.save()
        except PushTicketError:
            pass

        receipts.append(
            Receipt(
                ticket=ticket,
                is_success=push_receipt.is_success(),
                error_message=push_receipt.message,
                date_checked=timezone.now(),
            )
        )

    Receipt.objects.bulk_create(receipts)
