#!/usr/bin/env python3
"""
Gmail SMTP Email Sender with Attachment Support

Sends emails via Gmail SMTP with support for:
- Multiple recipients
- File attachments
- HTML/plain text content
- Gmail app password authentication
- Verbose debugging

Author: Momotaro
Date: March 18, 2026
Version: 1.0
"""

import os
import sys
import argparse
import smtplib
import mimetypes
from pathlib import Path
from email.mime.text import MIMEText
from email.mime.base import MIMEBase
from email.mime.multipart import MIMEMultipart
from email.utils import formataddr, formatdate
from email import encoders


class GmailSender:
    """Send emails via Gmail SMTP"""

    GMAIL_SMTP = "smtp.gmail.com"
    GMAIL_PORT = 587

    def __init__(self, sender_email, app_password, verbose=False):
        """Initialize Gmail sender"""
        self.sender_email = sender_email
        self.app_password = app_password
        self.verbose = verbose

    def log(self, message):
        """Print verbose log messages"""
        if self.verbose:
            print(f"[Gmail] {message}", file=sys.stderr)

    def get_app_password(self):
        """Get Gmail app password from environment, file, or argument"""
        # Already set during init
        return self.app_password

    @staticmethod
    def load_app_password():
        """Load app password from environment variable or ~/.gmail_app_password file"""
        # Check environment variable
        password = os.environ.get("GMAIL_APP_PASSWORD")
        if password:
            return password.strip()

        # Check ~/.gmail_app_password file
        password_file = Path.home() / ".gmail_app_password"
        if password_file.exists():
            try:
                with open(password_file, "r") as f:
                    password = f.read().strip()
                    return password
            except Exception as e:
                print(f"Error reading {password_file}: {e}", file=sys.stderr)
                return None

        return None

    def connect(self):
        """Connect to Gmail SMTP server"""
        try:
            self.log(f"Connecting to {self.GMAIL_SMTP}:{self.GMAIL_PORT}...")
            server = smtplib.SMTP(self.GMAIL_SMTP, self.GMAIL_PORT, timeout=10)
            server.set_debuglevel(1 if self.verbose else 0)

            self.log("Starting TLS...")
            server.starttls()

            self.log(f"Authenticating as {self.sender_email}...")
            server.login(self.sender_email, self.app_password)

            self.log("✓ Connected and authenticated")
            return server

        except smtplib.SMTPAuthenticationError:
            print(
                "✗ Authentication failed. Check Gmail app password.",
                file=sys.stderr,
            )
            sys.exit(2)
        except smtplib.SMTPException as e:
            print(f"✗ SMTP error: {e}", file=sys.stderr)
            sys.exit(2)
        except Exception as e:
            print(f"✗ Connection error: {e}", file=sys.stderr)
            sys.exit(2)

    def build_message(
        self, recipients, subject, body=None, body_html=None, attachments=None, from_name=None
    ):
        """Build MIME email message"""
        # Create message
        msg = MIMEMultipart()
        msg["From"] = formataddr((from_name or self.sender_email, self.sender_email))
        msg["To"] = ", ".join(recipients) if isinstance(recipients, list) else recipients
        msg["Subject"] = subject
        msg["Date"] = formatdate(localtime=True)

        # Add body (HTML preferred over plain text)
        if body_html:
            self.log("Adding HTML body...")
            msg.attach(MIMEText(body_html, "html"))
        elif body:
            self.log("Adding plain text body...")
            msg.attach(MIMEText(body, "plain"))

        # Add attachments
        if attachments:
            for filepath in attachments:
                self._attach_file(msg, filepath)

        return msg

    def _attach_file(self, msg, filepath):
        """Attach a file to the message"""
        filepath = Path(filepath)

        if not filepath.exists():
            print(f"✗ File not found: {filepath}", file=sys.stderr)
            sys.exit(4)

        if not filepath.is_file():
            print(f"✗ Not a file: {filepath}", file=sys.stderr)
            sys.exit(4)

        self.log(f"Attaching: {filepath.name} ({filepath.stat().st_size} bytes)")

        # Guess the content type
        ctype, encoding = mimetypes.guess_type(str(filepath))
        if ctype is None or encoding is not None:
            ctype = "application/octet-stream"

        maintype, subtype = ctype.split("/", 1)

        try:
            if maintype == "text":
                with open(filepath, "r", encoding="utf-8") as f:
                    attachment = MIMEText(f.read(), _subtype=subtype)
            else:
                with open(filepath, "rb") as f:
                    if maintype == "image":
                        from email.mime.image import MIMEImage
                        attachment = MIMEImage(f.read(), _subtype=subtype)
                    elif maintype == "audio":
                        from email.mime.audio import MIMEAudio
                        attachment = MIMEAudio(f.read(), _subtype=subtype)
                    else:
                        attachment = MIMEBase(maintype, subtype)
                        attachment.set_payload(f.read())
                        encoders.encode_base64(attachment)

            attachment.add_header("Content-Disposition", "attachment", filename=filepath.name)
            msg.attach(attachment)

        except Exception as e:
            print(f"✗ Error attaching file {filepath}: {e}", file=sys.stderr)
            sys.exit(4)

    def send(self, server, msg, recipients):
        """Send the email"""
        try:
            self.log(f"Sending to {len(recipients)} recipient(s)...")
            server.send_message(msg)
            self.log("✓ Email sent successfully")
            return True
        except smtplib.SMTPException as e:
            print(f"✗ Failed to send email: {e}", file=sys.stderr)
            sys.exit(3)
        except Exception as e:
            print(f"✗ Error sending email: {e}", file=sys.stderr)
            sys.exit(3)


def main():
    """Main entry point"""
    parser = argparse.ArgumentParser(
        description="Send emails via Gmail SMTP with attachments",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  # Simple email
  %(prog)s --to user@example.com --subject "Hello" --body "Hi there" --from rdreilly2010@gmail.com

  # With attachments
  %(prog)s --to user@example.com --subject "Files" --body "See attached" \\
    --from rdreilly2010@gmail.com --attach file1.md file2.pdf

  # HTML email
  %(prog)s --to user@example.com --subject "HTML" \\
    --body-html "<h1>Hello</h1>" --from rdreilly2010@gmail.com
        """,
    )

    # Required arguments
    parser.add_argument("--to", required=True, help="Recipient email(s), comma-separated")
    parser.add_argument("--subject", required=True, help="Email subject")
    parser.add_argument("--from", required=True, dest="sender", help="Sender email address")

    # Content arguments
    parser.add_argument("--body", help="Plain text email body")
    parser.add_argument("--body-html", help="HTML email body (overrides --body)")

    # Optional arguments
    parser.add_argument("--from-name", help="Sender display name")
    parser.add_argument("--attach", nargs="*", help="Files to attach")
    parser.add_argument("--password", help="Gmail app password (env: GMAIL_APP_PASSWORD)")
    parser.add_argument("--verbose", action="store_true", help="Verbose output")
    parser.add_argument("--dry-run", action="store_true", help="Show what would be sent (no actual send)")

    args = parser.parse_args()

    # Validate arguments
    if not args.body and not args.body_html:
        print("✗ Error: Provide either --body or --body-html", file=sys.stderr)
        sys.exit(1)

    # Get Gmail app password
    password = args.password or GmailSender.load_app_password()
    if not password:
        print(
            "✗ Error: No Gmail app password found.\n"
            "   Set GMAIL_APP_PASSWORD env var, create ~/.gmail_app_password file,\n"
            "   or use --password argument.\n"
            "   See SKILL.md for setup instructions.",
            file=sys.stderr,
        )
        sys.exit(2)

    # Parse recipients
    recipients = [r.strip() for r in args.to.split(",")]

    # Create sender
    sender = GmailSender(args.sender, password, verbose=args.verbose)

    # Build message
    msg = sender.build_message(
        recipients=recipients,
        subject=args.subject,
        body=args.body,
        body_html=args.body_html,
        attachments=args.attach,
        from_name=args.from_name,
    )

    # Dry run mode
    if args.dry_run:
        print("\n" + "=" * 70)
        print("DRY RUN - Email would be sent with the following details:")
        print("=" * 70)
        print(f"From: {msg['From']}")
        print(f"To: {msg['To']}")
        print(f"Subject: {msg['Subject']}")
        print(f"Date: {msg['Date']}")
        print("\nBody preview:")
        print("-" * 70)
        if args.body_html:
            print(f"[HTML]\n{args.body_html[:200]}...")
        else:
            print(f"[Text]\n{args.body[:200]}...")
        if args.attach:
            print("\nAttachments:")
            for f in args.attach:
                print(f"  - {f}")
        print("=" * 70)
        print("\n✓ Dry run complete (no email sent)")
        sys.exit(0)

    # Send email
    print(f"📧 Sending email to {', '.join(recipients)}...", file=sys.stderr)
    server = sender.connect()
    try:
        sender.send(server, msg, recipients)
        print(f"✅ Email sent successfully!", file=sys.stderr)
    finally:
        server.quit()
        sender.log("Connection closed")


if __name__ == "__main__":
    main()
