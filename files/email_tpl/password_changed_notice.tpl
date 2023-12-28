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
            width: 100px; /* Adjust as needed */
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
        <h2>Password Change Notification</h2>

        <p>Hello {username},</p>

        <p>This is a notification to inform you that your password for {network_name} has recently been changed. If you initiated this change, you can safely disregard this message.</p>

        <p>This password change was initiated using the IP address: <strong>{ipaddress}</strong>{ip_location_msg}.</p>

        <p class="important">If you did not request this change, please immediately contact our support team at <a href="mailto:{support_email}">{support_email}</a> for assistance. It is important to ensure the security of your account.</p>

        <div class="footer">
            <p>Best regards,</p>
            <p>Your {network_name} Team</p>
        </div>
    </div>
</body>
</html>