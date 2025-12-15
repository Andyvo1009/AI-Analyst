from odoo import fields, models


class ResConfigSettings(models.TransientModel):
    _inherit = "res.config.settings"

    ai_analyst_bot_user_id = fields.Many2one(
        "res.users",
        string="Analyst Bot User",
        help="User that will act as the analyst chatbot in Discuss.",
        config_parameter="ai_analyst_bot.user_id",
    )

    ai_analyst_bot_endpoint = fields.Char(
        string="Analyst Service Endpoint",
        default="http://localhost:5000/ask",
        help="HTTP endpoint that receives {'question': ...} and returns an answer.",
        config_parameter="ai_analyst_bot.endpoint",
    )

    ai_analyst_bot_timeout = fields.Integer(
        string="HTTP Timeout (seconds)",
        default=10,
        help="Timeout for calling the analyst service.",
        config_parameter="ai_analyst_bot.timeout",
    )

    ai_analyst_bot_prefix = fields.Char(
        string="Optional Trigger Prefix",
        default="",
        help=(
            "If set, the bot only responds when the message starts with this prefix. "
            "Example: /ask"
        ),
        config_parameter="ai_analyst_bot.prefix",
    )
