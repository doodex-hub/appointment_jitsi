{
    "name": "Appointment Jitsi",
    "summary": """
        Custom Module for Appointment, Integration With Jitsi API
    """,
    "description": """
        Custom Module for Appointment, Integration With Jitsi API.

        Features:
        1. **Automatic Link Generation**: When an appointment is created, a unique Jitsi meeting link is generated using the Jitsi API.
        2. **Link Storage**: The generated Jitsi meeting link is stored in a custom field within the appointment record in Odoo.
            - **Add Custom Field**: Adds a new text field `jitsi_link` to the `calendar.event` model.
        3. **Email Notification**: Customizes the appointment confirmation email template to include the Jitsi meeting link.
        4. **Security**: Each link is unique to the appointment, ensuring the privacy and security of the meetings.
    """,
    "author": "Doodex",
    "company": "Doodex",
    "website": "https://www.doodex.net/",
    "category": "Appointment",
    "license": "LGPL-3",
    "version": "17.0.1.0.0",
    "depends": [
        "base",
        "appointment",
        "calendar",
    ],
    "data": [
        "views/calendar_views.xml",
    ],
    "installable": True,
    "application": False,
    "auto_install": False,
    "images": [
       "static/description/banner.gif",
       "static/description/icon.png",
    ],
}
