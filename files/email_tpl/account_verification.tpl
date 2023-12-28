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
        <h2>Account Validation</h2>

        <p>Hello {username},</p>

        <p>Thank you for registering with {network_name}. To complete your account setup, please verify your email address.</p>

        <p><strong>Verification Code:</strong> {verification_code}</p>

        <div class="footer">
            <p>Best regards,</p>
            <p>Your {network_name} Team</p>
        </div>
    </div>
</body>
</html>