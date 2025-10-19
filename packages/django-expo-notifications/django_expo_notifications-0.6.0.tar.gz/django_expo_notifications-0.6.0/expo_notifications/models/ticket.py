from django.db import models
from exponent_server_sdk import PushTicket

from expo_notifications.managers import TicketManager


class Ticket(models.Model):
    objects = TicketManager()

    message = models.ForeignKey(
        to="expo_notifications.Message",
        on_delete=models.CASCADE,
        related_name="tickets",
    )

    is_success = models.BooleanField()

    external_id = models.CharField(
        max_length=64,
        blank=True,
    )

    error_message = models.TextField(
        blank=True,
    )

    date_received = models.DateTimeField()

    def __str__(self) -> str:
        return f"Ticket #{self.pk}"

    def to_push_ticket(self) -> PushTicket:
        return PushTicket(
            push_message=self.message.to_push_message(),
            status=(
                PushTicket.SUCCESS_STATUS
                if self.is_success
                else PushTicket.ERROR_STATUS
            ),
            message=self.error_message or None,
            details=None,
            id=self.external_id,
        )

    def check_receipt(self) -> None:
        from expo_notifications.tasks import check_receipts

        check_receipts.delay_on_commit([self.pk])
