import smtplib
import threading

# from background_task import background
from django.conf import settings
from django.core.mail.backends.smtp import EmailBackend
from django.core.mail.message import sanitize_address
from django.db.models import QuerySet

from django.core.mail import EmailMultiAlternatives
from django.template.loader import get_template
import logging
# from home.models import EmailMessageLog, EmailGroupMessageLog

standard_logger = logging.getLogger(__name__)

class CustomEmailBackend(EmailBackend):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _send(self, email_message):
        """A helper method that does the actual sending."""
        if not email_message.recipients():
            return False
        encoding = email_message.encoding or settings.DEFAULT_CHARSET
        from_email = sanitize_address(email_message.from_email, encoding)
        recipients = [sanitize_address(addr, encoding) for addr in email_message.recipients()]
        message = email_message.message()
        try:
            self.connection.sendmail(from_email, recipients, message.as_bytes(linesep='\r\n'))
            email_message.message_obj.set_as_sent()
        except smtplib.SMTPException as e:
            email_message.message_obj.set_as_fail(e)
            if not self.fail_silently:
                raise
            return False
        return True

    def send_messages(self, email_messages, total=0):
        """
        Send one or more EmailMessage objects and return the number of email
        messages sent.
        """
        # if not email_messages:
        #     return
        with self._lock:
            new_conn_created = self.open()
            if not self.connection or new_conn_created is None:
                # We failed silently on open().
                # Trying to send would be pointless.
                return
            num_sent = 0
            index = 0
            for message in email_messages:
                index += 1
                sent = self._send(message)
                if sent:
                    num_sent += 1
                # Sets group message log to completed
                if index == total and message.message_obj.group_log:
                    message.message_obj.group_log.set_as_completed()

            if new_conn_created:
                self.close()
        return num_sent

if __name__ == '__main__':
    print('Done')
