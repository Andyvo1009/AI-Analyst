import logging
import re
import requests
import html
from bs4 import BeautifulSoup
import sqlparse
from markupsafe import Markup

from odoo import api, models, _
from odoo.tools import html2plaintext

_logger = logging.getLogger(__name__)


class MailMessage(models.Model):
    _inherit = "mail.message"

    @api.model_create_multi
    def create(self, vals_list):
        messages = super().create(vals_list)

        # Prevent infinite bot reply loops
        if self.env.context.get("ai_analyst_bot_skip"):
            return messages

        icp = self.env["ir.config_parameter"].sudo()
        bot_user_id = int(icp.get_param("ai_analyst_bot.user_id") or 168)
        endpoint = icp.get_param("ai_analyst_bot.endpoint") or "http://localhost:5000/ask"
        timeout = int(icp.get_param("ai_analyst_bot.timeout") or 300)
        prefix = icp.get_param("ai_analyst_bot.prefix") or ""

        if not bot_user_id:
            return messages

        bot_user = self.env["res.users"].browse(bot_user_id).exists()
        if not bot_user:
            return messages

        bot_partner = bot_user.partner_id

        for msg in messages:
            try:
                # Only react to direct chat or channel messages
                # if msg.model == "discuss.channel" or not msg.res_id:
                #     continue
                
                # # Ignore system & non-comment messages
                if msg.message_type != "comment":
                    continue
                
                # # Ignore bot’s own messages
                if msg.author_id and msg.author_id.id == bot_partner.id:
                    continue

                channel = self.env["discuss.channel"].browse(msg.res_id).sudo().exists()
                if not channel:
                    continue
                if channel.channel_type != "chat":
                    continue
                # Bot must be a member of the channel
                partners = channel.channel_partner_ids

                # if bot_partner not in members:
                #     continue
                if bot_partner not in partners:
                    continue
                # Extract clean text
                body_text = html2plaintext(msg.body or "").strip()
                if not body_text:
                    continue

                # Optional prefix logic
                if prefix:
                    if not body_text.startswith(prefix):
                        continue
                    question = body_text[len(prefix):].strip()
                else:
                    question = body_text

                if not question:
                    continue

                # AI backend call
                answer = self._ai_analyst_bot_call(
                    question=question,
                    endpoint=endpoint,
                    timeout=timeout,
                )

                if not answer:
                    answer = _("Sorry, I couldn't get a response from the analyst service.")

                # FORMAT nicely so it renders correctly in Odoo Discuss
                

                # Send bot reply
                channel.with_user(bot_user).with_context(
                    ai_analyst_bot_skip=True
                ).message_post(
                    body=Markup(answer),
                    message_type="comment",
                    subtype_xmlid="mail.mt_comment",
                    content_subtype="html"
                )

            except Exception:
                _logger.exception("AI Analyst Bot failed for message id %s", msg.id)

        return messages

    

    # --------------------------------------------------------------------------
    # HTML → Plain Text (tables + SQL)
    # --------------------------------------------------------------------------
    def html_table_to_plain_text(self, html_string: str) -> str:
        text = html_string

        # Convert markdown ### heading → <p><b>Heading</b></p>
        text = re.sub(r"^###\s*(.*)$", r"<p><b>\1</b></p>", text, flags=re.MULTILINE)

        # Convert markdown ## heading
        text = re.sub(r"^##\s*(.*)$", r"<p><b>\1</b></p>", text, flags=re.MULTILINE)

        # Convert markdown # heading
        text = re.sub(r"^#\s*(.*)$", r"<p><b>\1</b></p>", text, flags=re.MULTILINE)

        # Convert **bold** → <b>bold</b>
        text = re.sub(r"\*\*(.*?)\*\*", r"<b>\1</b>", text)

        # Convert *italic* → <i>italic</i>
        text = re.sub(r"\*(.*?)\*", r"<i>\1</i>", text)

        # Convert markdown bullet points (- or *)
        text = re.sub(r"^- (.*)$", r"<p>• \1</p>", text, flags=re.MULTILINE)

        # Convert line breaks → <br>
        text = text.replace("\n", "<br>")

        return text   # raw HTML, not escaped  

    # --------------------------------------------------------------------------
    # Call backend AI
    # --------------------------------------------------------------------------
    def _ai_analyst_bot_call(self, question, endpoint, timeout):
        payload = {"question": question}

        try:
            resp = requests.post(endpoint, json=payload, timeout=timeout)
            resp.raise_for_status()

            data = {}
            try:
                data = resp.json()
            except Exception:
                return resp.text.strip()

            answer = data.get("answer") or ""
            return self.html_table_to_plain_text(answer)

        except Exception as e:
            _logger.warning("AI Analyst Bot HTTP call failed: %s", e)
            return ""
