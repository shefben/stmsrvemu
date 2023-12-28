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
        <h2>Account Information</h2>

        <p>Hello,</p>

        <p>Your username for <strong>{network_name}</strong> is: <strong>{username}</strong></p>

        <p>Requesting IP Address: <strong>{ipaddress}</strong>{ip_location_msg}</p>

        <p>If you did not request this information, please ignore and forward this email to <a href="mailto:{support_email}">{support_email}</a>.</p>

        <div class="footer">
            <p>Best regards,</p>
            <p>Your <strong>{network_name}</strong> Team</p>
        </div>
    </div>
</body>
</html>