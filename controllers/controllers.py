# -*- coding: utf-8 -*-
from odoo import http
from odoo.http import request 
from werkzeug.utils import redirect


class OtManagement(http.Controller):
    @http.route('/ot_management/ot_registration/',method=["GET"],website=True, auth='public')
    def index(self, **kw):
        ot=request.env["ot.registration"].sudo().search([])
        action_ot_registration_id=request.env.ref("ot_management.ot_registration_request_action")
        menu_ot_registration_id=request.env.ref("ot_management.ot_request")
        url=f"&action={action_ot_registration_id.id}&model=ot.registration&view_type=form&menu_id={menu_ot_registration_id.id}"
        print(f"url: {url}")
        return request.render("ot_management.ot_registration_page",{
            'ot':ot,
            "url": url
        })
    @http.route("/ot_management/ot_registration_detail/<int:id>", website=True, auth="public")
    def ot_registration_detail(self,id):
        action_ot_registration_id=request.env.ref("ot_management.ot_registration_request_action")
        menu_ot_registration_id=request.env.ref("ot_management.ot_request")
        url=f"/web?#id={id}&action={action_ot_registration_id.id}&model=ot.registration&view_type=form&menu_id={menu_ot_registration_id.id}"
        return redirect(url)