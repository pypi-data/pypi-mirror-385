# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2024 Lance Edgar
#
#  This file is part of Rattail.
#
#  Rattail is free software: you can redistribute it and/or modify it under the
#  terms of the GNU General Public License as published by the Free Software
#  Foundation, either version 3 of the License, or (at your option) any later
#  version.
#
#  Rattail is distributed in the hope that it will be useful, but WITHOUT ANY
#  WARRANTY; without even the implied warranty of MERCHANTABILITY or FITNESS
#  FOR A PARTICULAR PURPOSE.  See the GNU General Public License for more
#  details.
#
#  You should have received a copy of the GNU General Public License along with
#  Rattail.  If not, see <http://www.gnu.org/licenses/>.
#
################################################################################
"""
Report Handlers
"""

import datetime
import decimal

from wuttjamaican.util import load_entry_points

from rattail.time import localtime


class ReportHandler(object):
    """
    Base class for all report handlers.  Also provides default implementation,
    which is assumed to be sufficient for most needs.
    """
    entry_point_section = 'rattail.reports'

    def __init__(self, config=None, **kwargs):
        self.config = config
        self.app = config.get_app()
        self.enum = config.get_enum() if config else None
        for key, value in kwargs.items():
            setattr(self, key, value)

    def get_reports(self):
        """
        Returns a dict of all available reports, keyed by the report
        type key.

        By default this includes all reports which are properly
        registered via setuptools entry points.  It also will include
        any custom Poser reports, although that can be disabled via
        config if desired.
        """
        # properly registered reports
        reports = load_entry_points(self.entry_point_section)

        # maybe also include poser reports
        if self.config.getbool('rattail.reporting',
                               'include_poser_reports',
                               default=True):

            # these come back in different format so must normalize
            poser_handler = self.app.get_poser_handler()
            for report_info in poser_handler.get_all_reports():
                if not report_info.get('error'):
                    report = report_info['report']
                    reports[report.type_key] = report

        return reports

    def get_report(self, key):
        """
        Fetch a report by key.  If the report can be located, this will return an
        instance thereof; otherwise returns ``None``.
        """
        report = self.get_reports().get(key)
        if report:
            return report(self.config)

    def generate_output(self, session, report, params, user, progress=None, **kwargs):
        """
        Generate and return output for the given report and params.
        """
        model = self.app.model
        data = report.make_data(session, params, progress=progress, **kwargs)

        output = model.ReportOutput()
        output.id = self.app.next_counter_value(session, 'batch_id')
        output.report_name = report.make_report_name(session, params, data, **kwargs)
        output.report_type = report.type_key
        output.params = self.safe_params(**params)
        output.filename = report.make_filename(session, params, data, **kwargs)
        output.created_by = user
        session.add(output)
        session.flush()

        # nb. stash data for the report
        # TODO: this is an undocumented feature...
        output._generated_data = data

        path = output.filepath(self.config, makedirs=True)
        report.write_file(session, params, data, path, progress=progress, **kwargs)
        return output

    def safe_params(self, **kwargs):
        params = {}
        for key, value in kwargs.items():
            if isinstance(value, datetime.date):
                value = str(value)
            elif isinstance(value, decimal.Decimal):
                value = float(value)
            params[key] = value
        return params

    def email_output(self, report, output, mailkey,
                     fallback_mailkey='common_report', extra_data={}, **kwargs):
        """
        Send an email (using the given :paramref:`mailkey`) with the report
        output as an attachment.

        :param report: The relevant :class:`Report` instance.
        :param output: The relevant :class:`ReportOutput` instance.
        :param mailkey: Config key which identifies the type of email to be
           sent.
        :param fallback_mailkey: Config key to be used as fallback, should the
           :paramref:`mailkey` not point to a valid email config.
        :param extra_data: Additional context data to be passed along to the
           email template.
        :param kwargs: Additional kwargs to be passed directly to
           :meth:`~rattail.app.AppHandler.send_email()`.
        """
        if 'attachments' not in kwargs:
            path = output.filepath(self.config)
            kwargs['attachments'] = [path]

        data = {
            'config': self.config,
            'handler': self,
            'report': report,
            'output': output,
            'localtime': localtime,
        }

        if extra_data:
            data.update(extra_data)

        if 'params' not in data:
            data['params'] = output.params

        self.app.send_email(mailkey, data, fallback_key=fallback_mailkey,
                            **kwargs)


def get_report_handler(config, **kwargs):
    """
    Create and return the configured :class:`ReportHandler` instance.
    """
    app = config.get_app()
    spec = config.get('rattail.reports', 'handler')
    if spec:
        return app.load_object(spec)(config)
    return ReportHandler(config)
