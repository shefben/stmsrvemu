<!DOCTYPE html>
<html>
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            color: #333333;
        }}
        .container {{
            padding: 20px;
        }}
        .footer {{
            font-size: 0.9em;
            margin-top: 20px;
            color: #666666;
        }}
        .header img {{
            width: 100px;  /* Adjust as needed */
            height: auto;
        }}
        .important {{
            color: red;
        }}
    </style>
<body>
    <div class="container">
        <div class="header">
            <a href="{network_url}">
                <img src="{logo_url}" alt="{network_name} Logo">
            </a>
        </div>
        <h2>Welcome to {network_name}, {username}!</h2>

        <p>We are excited to have you on board. Get ready to explore our services and features.</p>

        <p>This account was registered using the IP address: <strong>{ipaddress}</strong>{ip_location_msg}.</p>
        <p>If you did not create this account or believe this to be an error, please forward this email to <a href="mailto:{support_email}">{support_email}</a> and disregard this message.</p>

        <p>If you have any questions, feel free to contact us at {support_email}.</p>

        <div class="footer">
            <p>Warm regards,</p>
            <p>The {network_name} Team</p>
        </div>
    </div>
</body>
</html>