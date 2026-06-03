def build_support_email_template(
    category: str,
    severity: str,
    user_id: str,
    ticket_id: str,
    query_summary: str,
    ai_response: str,
):

    return f"""
    <html>
    <head>
        <style>
            body {{
                font-family: Arial, sans-serif;
                background-color: #f4f4f4;
                padding: 20px;
                color: #333333;
            }}

            .container {{
                background-color: #ffffff;
                border-radius: 10px;
                padding: 24px;
                max-width: 700px;
                margin: auto;
                box-shadow: 0 2px 10px rgba(0,0,0,0.1);
            }}

            .header {{
                background-color: #1f2937;
                color: white;
                padding: 16px;
                border-radius: 8px;
                font-size: 22px;
                font-weight: bold;
            }}

            .section {{
                margin-top: 24px;
            }}

            .label {{
                font-weight: bold;
                color: #111827;
            }}

            .box {{
                background-color: #f9fafb;
                border-left: 4px solid #2563eb;
                padding: 16px;
                margin-top: 10px;
                border-radius: 6px;
                white-space: pre-wrap;
            }}

            .footer {{
                margin-top: 30px;
                font-size: 13px;
                color: #6b7280;
            }}

            .severity {{
                color: #dc2626;
                font-weight: bold;
            }}
        </style>
    </head>

    <body>

        <div class="container">

            <div class="header">
                Resolve AI Support Alert
            </div>

            <div class="section">

                <p>Hello Support Team,</p>

                <p>
                    A support ticket requires immediate attention.
                </p>

            </div>

            <div class="section">

                <div>
                    <span class="label">Category:</span>
                    {category}
                </div>

                <div>
                    <span class="label">Severity:</span>

                    <span class="severity">
                        {severity}
                    </span>
                </div>

                <div>
                    <span class="label">User ID:</span>
                    {user_id}
                </div>

                <div>
                    <span class="label">Ticket ID:</span>
                    {ticket_id}
                </div>

            </div>

            <div class="section">

                <div class="label">
                    Customer Summary
                </div>

                <div class="box">
                    {query_summary}
                </div>

            </div>

            <div class="section">

                <div class="label">
                    AI Response
                </div>

                <div class="box">
                    {ai_response}
                </div>

            </div>

            <div class="section">

                <p>
                    Please review and take the necessary action.
                </p>

            </div>

            <div class="footer">

                Resolve AI System
                <br/>
                Automated Support Notification

            </div>

        </div>

    </body>

    </html>
    """
