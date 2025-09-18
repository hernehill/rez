"""Sends a post-release email"""

# Standard
import smtplib
from email.mime.text import MIMEText

# Rez
from rez.release_hook import ReleaseHook
from rez.system import system
from rez.utils.logging_ import print_error
from rez.utils.scope import scoped_formatter
from rez.vendor.schema.schema import Or


class HHEmailReleaseHook(ReleaseHook):

    schema_dict = {
        "subject": str,
        "body": str,
        "smtp_host": str,
        "smtp_port": int,
        "sender": str,
        "recipients": Or(str, [str])
    }

    @classmethod
    def name(cls):
        return "hh_emailer"

    def __init__(self, source_path):
        super(HHEmailReleaseHook, self).__init__(source_path)

    def post_release(self,
                     user,
                     install_path,
                     variants,
                     release_message=None,
                     changelog=None,
                     previous_version=None,
                     **kwargs):

        # ---------------------------------------------
        # Bail if not enough information
        if not variants: return
        if not self.settings.smtp_host: return

        # ---------------------------------------------
        # Recipients
        fixed_recipients = [
            "marcelo.sercheli@hernehill.com",
        ]
        recipients = self.settings.recipients or []
        for fixed_recipient in fixed_recipients:
            if fixed_recipient not in recipients:
                recipients.append(fixed_recipient)

        # ---------------------------------------------
        # Email body
        release_dict = dict(
            path=install_path,
            previous_version=previous_version or "None.",
            message=release_message or "No release message.",
            changelog=changelog or "No changelog."
        )

        variants_dict = dict(
            count=len(variants),
            paths='<br />'.join(x.root for x in variants)
        )

        formatter = scoped_formatter(
            release=release_dict,
            variants=variants_dict,
            system=system,
            package=self.package
        )

        body = formatter.format(self.settings.body)
        body = body.strip()
        body = body.replace("\n\n\n", "\n\n")

        # ---------------------------------------------
        # Subject
        subject = formatter.format(self.settings.subject)

        # ---------------------------------------------
        # Send email
        print("Sending HH release email to:")
        print('\n'.join("- %s" % x for x in recipients))

        msg = MIMEText(body, "html")
        msg["Subject"] = subject
        msg["From"] = self.settings.sender
        msg["To"] = str(',').join(recipients)

        try:
            s = smtplib.SMTP(self.settings.smtp_host, self.settings.smtp_port)
            s.sendmail(
                from_addr=self.settings.sender,
                to_addrs=recipients,
                msg=msg.as_string()
            )
            print('Email(s) sent.')
        except Exception as e:
            print_error("HH release email delivery failed: %s" % str(e))


def register_plugin():
    return HHEmailReleaseHook
