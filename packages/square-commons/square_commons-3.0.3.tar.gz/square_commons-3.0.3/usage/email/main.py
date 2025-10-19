from square_commons import send_email_using_mailgun

print(
    send_email_using_mailgun(
        from_email="home@domain.com",
        from_name="Administrator",
        to_email="username@domain.com",
        to_name="user",
        subject="Test Email",
        body="This is a test email",
        api_key="api_key",
        domain_name="domain.com",
    )
)
