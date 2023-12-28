<!DOCTYPE html>
<html>
<head>
    <style>
        body {
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            color: #333333;
        }
        .container {
            padding: 20px;
        }
        .footer {
            font-size: 0.9em;
            margin-top: 20px;
            color: #666666;
        }
        .header img {
            width: 100px;  /* Adjust as needed */
            height: auto;
        }
        .important {
            color: red;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <a href="{network_url}">
                <img src="{logo_url}" alt="{network_name} Logo">
            </a>
        </div>
        <h2>Password Reset Request</h2>

        <p>Hello,</p>

        <p>You have requested a password reset for the account <strong>{username}</strong>.</p>
        <p>Please see the following information to complete your password reset.</p>

        <p class="important">
            NOTE: If you believe this email was sent in error or if you did not request a password reset,
            please forward this email to <a href="mailto:{support_email}">{support_email}</a> and delete the email.
        </p>

        <p>Requesting IP Address: <strong>{ipaddress}</strong>{ip_location_msg}.</p>

        <p>The following recovery information is valid for 5 minutes. If after 5 minutes the code has not been used, you will need to request another code.</p>
        <p>Please note: You are allowed to request a Password Reset 3 times every 12 hours.</p>
        <p><strong>(Keep this information private!)</strong></p>

        <p><strong>Verification Code:</strong> {verification_code}</p>
        <p><strong>Secret Question:</strong> {question}</p>

        <div class="footer">
            <p>Best regards,</p>
            <p>Your <strong>{network_name}</strong> Team</p>
        </div>
    </div>
</body>
</html>