# Copyright (C) 2025 Cetmix OÜ
# License AGPL-3.0 or later (https://www.gnu.org/licenses/agpl).

from odoo import _, http
from odoo.exceptions import AccessError, MissingError
from odoo.http import request

from odoo.addons.project.controllers.portal import ProjectCustomerPortal


class PortalProjectTask(ProjectCustomerPortal):
    def _task_get_searchbar_inputs(self, milestones_allowed):
        inputs = super()._task_get_searchbar_inputs(milestones_allowed)
        if "ref" in inputs and "label" in inputs["ref"]:
            inputs["ref"]["label"] = _("Search in Task code")
        return inputs

    def _task_get_search_domain(self, search_in, search):
        domain = super()._task_get_search_domain(search_in, search)
        if search_in in ("ref", "all"):
            for i, item in enumerate(domain):
                if isinstance(item, tuple) and item[0] == "id":
                    domain[i] = ("code", item[1], item[2])
                    break
        return domain

    def get_accessible_task_by_code(self, task_code, access_token):
        task_id = (
            request.env["project.task"]
            .sudo()
            .search([("code", "=", task_code)], limit=1)
            .id
        )
        if not task_id:
            raise MissingError(_("No task with this code."))
        task_sudo = self._document_check_access("project.task", task_id, access_token)
        return task_sudo

    @http.route(
        ["/my/tasks/<string:task_code>"], type="http", auth="public", website=True
    )
    def portal_my_task(
        self,
        task_code,
        report_type=None,
        access_token=None,
        project_sharing=False,
        **kw
    ):
        try:
            task_sudo = self.get_accessible_task_by_code(task_code, access_token)
        except (AccessError, MissingError):
            return request.redirect("/my")

        if report_type in ("pdf", "html", "text"):
            return self._show_task_report(
                task_sudo, report_type, download=kw.get("download")
            )

        # ensure attachment are accessible with access token inside template
        task_sudo.attachment_ids.generate_access_token()
        if project_sharing is True:
            # Then the user arrives to the stat button shown in form view of project.task
            # and the portal user can see only 1 task
            # so the history should be reset.
            request.session["my_tasks_history"] = task_sudo.ids
        values = self._task_get_page_view_values(task_sudo, access_token, **kw)
        return request.render("project.portal_my_task", values)

    @http.route(
        "/my/projects/<int:project_id>/task/<string:task_code>",
        type="http",
        auth="public",
        website=True,
    )
    def portal_my_project_task(
        self, project_id=None, task_code=None, access_token=None, **kw
    ):
        try:
            project_sudo = self._document_check_access(
                "project.project", project_id, access_token
            )
            task_sudo = self.get_accessible_task_by_code(task_code, access_token)
        except (AccessError, MissingError):
            return request.redirect("/my")
        task_sudo.attachment_ids.generate_access_token()
        values = self._task_get_page_view_values(
            task_sudo, access_token, project=project_sudo, **kw
        )
        values["project"] = project_sudo
        return request.render("project.portal_my_task", values)
