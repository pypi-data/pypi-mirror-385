from __future__ import annotations

import io
import os
import zipfile
from datetime import datetime, timezone
from typing import TypedDict

from flask import Blueprint, Response, jsonify, send_file
from flask.views import MethodView

import ckan.plugins.toolkit as tk

from ckanext.tables.shared import GenericTableView
from ckanext.tables.views import AjaxURLView

from ckanext.logs.config import get_logs_folder

bp = Blueprint("logs", __name__, url_prefix="/ckan-admin/logs")


class LogFileInfo(TypedDict):
    name: str
    size: int
    mtime: datetime


def before_request() -> None:
    try:
        tk.check_access("sysadmin", {"user": tk.current_user.name})
    except tk.NotAuthorized:
        tk.abort(403, tk._("Need to be system administrator to administer"))


class LogsDashboardView(MethodView):
    def get(self):
        logs_folder = get_logs_folder()
        all_log_files = self.get_logs_files(logs_folder)
        total_size = sum(f["size"] for f in all_log_files)
        logs_files = [f for f in all_log_files if f["name"].endswith(".log")]
        logs_sizes = self._calculate_logs_sizes(all_log_files, logs_files)

        return tk.render(
            "logs/dashboard.html",
            {
                "logs_folder": logs_folder,
                "logs_files": logs_files,
                "total_size": total_size,
                "logs_sizes": logs_sizes,
            },
        )

    def get_logs_files(self, logs_folder: str | None) -> list[LogFileInfo]:
        if not logs_folder or not os.path.exists(logs_folder):
            return []

        files = []

        for name in os.listdir(logs_folder):
            path = os.path.join(logs_folder, name)
            if os.path.isfile(path):
                size = os.path.getsize(path)
                mtime = os.path.getmtime(path)
                files.append(
                    LogFileInfo(
                        name=name,
                        size=size,
                        mtime=datetime.fromtimestamp(mtime, tz=timezone.utc),
                    )
                )

        return sorted(files, key=lambda x: x["mtime"], reverse=True)

    def _calculate_logs_sizes(self, all_files: list[LogFileInfo], log_files: list[LogFileInfo]) -> dict[str, int]:
        result = {}

        for log_file in log_files:
            base_name = log_file["name"].strip(".log")
            total_size = log_file["size"]

            for file in all_files:
                if file["name"].startswith(base_name) and file["name"] != log_file["name"]:
                    total_size += file["size"]

            result[log_file["name"]] = total_size

        return result


class LogsDownloadView(MethodView):
    def get(self) -> Response:
        logs_folder = get_logs_folder()

        if not logs_folder or not os.path.exists(logs_folder):
            tk.abort(404, "Logs directory not found")

        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for name in os.listdir(logs_folder):
                path = os.path.join(logs_folder, name)
                if os.path.isfile(path):
                    zf.write(path, arcname=name)

        zip_buffer.seek(0)

        return send_file(zip_buffer, as_attachment=True, download_name="logs_archive.zip", mimetype="application/zip")


class LogsExportTableView(MethodView):
    def get(self, log_file: str) -> Response:
        logs_folder = get_logs_folder()
        log_base_name = log_file.strip(".log")

        if not logs_folder or not os.path.exists(logs_folder):
            tk.abort(404, "Logs directory not found")

        zip_buffer = io.BytesIO()

        with zipfile.ZipFile(zip_buffer, "w", zipfile.ZIP_DEFLATED) as zf:
            for name in os.listdir(logs_folder):
                if not name.startswith(log_base_name):
                    continue

                path = os.path.join(logs_folder, name)

                if os.path.isfile(path):
                    zf.write(path, arcname=name)

        zip_buffer.seek(0)

        return send_file(zip_buffer, as_attachment=True, download_name="logs_archive.zip", mimetype="application/zip")


class LogsGenericTableView(GenericTableView):
    def get(self, log_file: str) -> str | Response:  # type: ignore
        table = self.table_class(log_file=log_file)  # type: ignore

        return table.render_table(breadcrumb_label=self.breadcrumb_label, page_title=self.page_title)


class LogsAjaxURLView(AjaxURLView):
    def get(self, table_name: str, log_file: str) -> Response:  # type: ignore
        table_class = tk.h.tables_get_table(table_name)

        if not table_class:
            return tk.abort(404, tk._(f"Table {table_name} not found"))

        params = self.build_params()
        table_instance = table_class(log_file=log_file)
        data = table_instance.get_data(params)
        total = table_instance.get_total_count(params)

        return jsonify({"data": data, "last_page": (total + params.size - 1) // params.size})

    def post(self, table_name: str, log_file: str) -> Response:  # type: ignore
        table_class = tk.h.tables_get_table(table_name)

        if not table_class:
            return tk.abort(404, tk._(f"Table {table_name} not found"))

        row_action = tk.request.form.get("row_action")
        table_action = tk.request.form.get("table_action")
        bulk_action = tk.request.form.get("bulk_action")
        row = tk.request.form.get("row")
        rows = tk.request.form.get("rows")

        table = table_class(log_file=log_file)

        if table_action:
            return self._apply_table_action(table, table_action)

        if row_action:
            return self._apply_row_action(table, row_action, row)

        return self._apply_bulk_action(table, bulk_action, rows)


bp.before_request(before_request)

bp.add_url_rule("/dashboard", view_func=LogsDashboardView.as_view("dashboard"))
bp.add_url_rule("/export", view_func=LogsDownloadView.as_view("download"))
bp.add_url_rule("/export_log_file/<log_file>", view_func=LogsExportTableView.as_view("export_log_file"))
bp.add_url_rule("/table/<log_file>", view_func=LogsGenericTableView.as_view("table", table="logs"))
bp.add_url_rule("/ajax-url/<table_name>/<log_file>", view_func=LogsAjaxURLView.as_view("ajax_url"))
