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
Common email config objects
"""

import datetime
import sys
import socket
from traceback import format_exception

from rattail.mail import Email
from rattail.util import simple_error


class ProblemReportEmail(Email):
    """
    Base class for all "problem report" emails
    """
    abstract = True

    def obtain_sample_data(self, request):
        from rattail.problems import ProblemReport, get_problem_report_handler

        data = self.sample_data(request)
        handler = get_problem_report_handler(self.config)

        if 'report' not in data:
            reports = handler.get_all_problem_reports()
            email_key = self.__class__.__name__
            for report in reports:
                if report.email_key == email_key:
                    data['report'] = report(self.config)
                    break

            if 'report' not in data:
                report = ProblemReport(self.config)
                report.problem_title = "Generic Title (problem report not found)"
                data['report'] = report

        if 'system_title' not in data:
            system_key = data['report'].system_key or 'rattail'
            data['system_title'] = handler.get_system_title(system_key)

        return data


class datasync_error_watcher_get_changes(Email):
    """
    When any datasync watcher thread encounters an error trying to get changes,
    this email is sent out.
    """
    default_subject = "Watcher failed to get changes"

    def sample_data(self, request):
        from rattail.datasync import DataSyncWatcher
        try:
            raise RuntimeError("Fake error for preview")
        except:
            exc_type, exc, traceback = sys.exc_info()
        watcher = DataSyncWatcher(self.config, 'test')
        watcher.consumes_self = True
        return {
            'watcher': watcher,
            'error': exc,
            'traceback': ''.join(format_exception(exc_type, exc, traceback)).strip(),
            'datasync_url': '/datasyncchanges',
            'attempts': 2,
        }


class datasync_error_consumer_process_changes(Email):
    """
    When any datasync consumer thread encounters an error trying to process
    changes, this email is sent out.
    """
    default_subject = "Consumer failed to process changes"

    def sample_data(self, request):
        from rattail.datasync import DataSyncWatcher, DataSyncConsumer

        try:
            raise RuntimeError("Fake error for preview")
        except:
            exc_type, exc, traceback = sys.exc_info()

        watcher = DataSyncWatcher(self.config, 'testwatcher')
        consumer = DataSyncConsumer(self.config, 'testconsumer')
        return {
            'watcher': watcher,
            'consumer': consumer,
            'error': exc,
            'attempts': 2,
            'traceback': ''.join(format_exception(exc_type, exc, traceback)).strip(),
            'datasync_url': '/datasync/changes',
        }


class filemon_action_error(Email):
    """
    When any filemon thread encounters an error (and the retry attempts have
    been exhausted) then it will send out this email.
    """
    default_subject = "Error invoking action(s)"

    def sample_data(self, request):
        from rattail.filemon import Action
        action = Action(self.config)
        action.spec = 'rattail.filemon.actions:Action'
        action.retry_delay = 10
        try:
            raise RuntimeError("Fake error for preview")
        except:
            exc_type, exc, traceback = sys.exc_info()
        return {
            'hostname': socket.gethostname(),
            'path': '/tmp/foo.csv',
            'action': action,
            'attempts': 3,
            'error': exc,
            'traceback': ''.join(format_exception(exc_type, exc, traceback)).strip(),
        }


class new_email_requested(Email):
    """
    Sent when a new email address is requested for a customer,
    e.g. when entering a new customer order.
    """
    default_subject = "Email Update Request"

    def sample_data(self, request):
        app = request.rattail_config.get_app()
        model = app.model
        customer = model.Customer(name="Fred Flintstone")
        return {
            'user': request.user,
            'user_display': request.user.display_name,
            'contact': customer,
            'contact_id': '42',
            'email_address': "fred@mailinator.com",
        }


class new_phone_requested(Email):
    """
    Sent when a new phone number is requested for a customer,
    e.g. when entering a new customer order.
    """
    default_subject = "Phone Update Request"

    def sample_data(self, request):
        app = request.rattail_config.get_app()
        model = app.model
        customer = model.Customer(name="Fred Flintstone")
        return {
            'user': request.user,
            'user_display': request.user.display_name,
            'contact': customer,
            'contact_id': '42',
            'phone_number': "417-555-1234",
        }


class pos_feedback(Email):
    """
    Sent when a user submits feedback from the POS
    """
    default_subject = "Feedback from POS"

    def sample_data(self, request):
        return {
            'user_name': "Fred Flintstone",
            'message': "Hey there,\n\njust wondered what the heck was going on with this POS?  It's crap.\n\nFred",
        }


class postfix_summary(Email):
    """
    Sends a summary of Postfix mail activity.
    """
    default_subject = "Postfix Summary"

    def sample_data(self, request):
        return {
            'output': "(pflogsumm output goes here)",
        }


class ImporterEmail(Email):
    """
    Sent when a "version catch-up" import is performed, which involves changes.
    """
    abstract = True
    fallback_key = 'rattail_import_updates'
    handler_spec = None

    def get_handler(self, config):
        app = config.get_app()
        return app.load_object(self.handler_spec)(config)

    def get_default_subject(self, **data):
        host_title = data.get('host_title')
        local_title = data.get('local_title')
        if not (host_title and local_title):
            handler = self.get_handler(self.config)
            if not host_title:
                host_title = handler.host_title
            if not local_title:
                local_title = handler.local_title
        return "Changes for {} -> {}".format(host_title, local_title)

    def sample_data(self, request):
        app = request.rattail_config.get_app()
        handler = self.get_handler(request.rattail_config)
        obj = app.make_object()
        local_data = {
            'foo': 42,
            'bar': True,
            'baz': 'something',
        }
        host_data = {
            'foo': 42,
            'bar': False,
            'baz': 'something else',
        }
        return {
            'host_title': handler.host_title,
            'local_title': handler.local_title,
            'direction': 'import',
            'runtime': "1 second",
            'argv': ['bin/rattail', 'import-something'],
            'changes': {
                'Widget': (
                    [],                             # created
                    [(obj, local_data, host_data)], # updated
                    [],                             # deleted
                ),
            },
            'render_record': lambda x: str(x),
            'max_display': 15,
        }


class rattail_export_rattail_updates(ImporterEmail):
    """
    Sent when a full Rattail -> Rattail data export involves changes.
    """
    handler_spec = 'rattail.importing.rattail:FromRattailToRattailExport'
    abstract = False


class rattail_import_rattail_updates(ImporterEmail):
    """
    Sent when a full Rattail -> Rattail data import involves changes.
    """
    handler_spec = 'rattail.importing.rattail:FromRattailToRattailImport'
    abstract = False


class rattail_import_versions_updates(ImporterEmail):
    """
    Sent when a "version catch-up" import is performed, which involves changes.
    """
    handler_spec = 'rattail.importing.versions:FromRattailToRattailVersions'
    abstract = False


class person_merge_request(Email):
    """
    Sent when a request is submitted to merge two Person records.
    """
    default_subject = "Person Merge Request"

    def sample_data(self, request):
        return {
            'user_display': request.user.display_name,
            'removing_display': "Fred Flintstone",
            'removing_url': '#',
            'keeping_display': "Fred Flintstone",
            'keeping_url': '#',
            'merge_request_url': '#',
        }


class rattail_problems_mailmon_misses(ProblemReportEmail):
    """
    Nightly check to alert if incoming messages are noticed to have
    been "missed" by mailmon daemon.
    """
    default_subject = "Mailmon misses"
    abstract = False

    def sample_data(self, request):
        app = request.rattail_config.get_app()
        account = app.make_object(server='example.com')
        profile = app.make_object(imap_folder='TestFolder')
        return {
            'problems': [(account, profile, 1)],
        }


class rattail_problems_pending_products(ProblemReportEmail):
    """
    Shows a list of pending products, if any are present.
    """
    default_subject = "Pending products"
    abstract = False

    def sample_data(self, request):
        model = self.model

        key = '074305001321'
        pending = model.PendingProduct(item_id=key,
                                       scancode=key,
                                       upc=self.app.make_gpc(key),
                                       brand_name="Bragg's",
                                       description="Apple Cider Vinegar",
                                       size="32oz",
                                       status_code=self.enum.PENDING_PRODUCT_STATUS_PENDING)

        url = self.config.base_url()
        if url:
            url = f'{url}/products/pending/'

        return {
            'problems': [pending],
            'products_handler': self.app.get_products_handler(),
            'enum': self.enum,
            'url': url,
        }


class rattail_problems_stale_inventory_batch(ProblemReportEmail):
    """
    Nightly check for "stale" inventory batches, i.e. those created
    but not executed within a certain number of days.
    """
    default_subject = "Stale inventory batches"
    abstract = False

    def sample_data(self, request):
        app = request.rattail_config.get_app()
        model = app.model
        person = model.Person(display_name="Fred Flintstone")
        user = model.User(username='fred', person=person)
        batch = model.InventoryBatch(id=42, created=self.app.localtime(),
                                     created_by=user)
        return {
            'problems': [batch],
            'cutoff_days': 4,
            'render_time': lambda t: t,
        }


class CommandOutputEmail(Email):
    """
    Base class for command output emails.
    """
    abstract = True
    fallback_key = 'run_n_mail'

    def sample_data(self, request):
        runtime = datetime.timedelta(seconds=300)
        return {
            'cmd': ['/bin/sleep', '1'],
            'runtime': runtime,
            'runtime_pretty': self.app.render_duration(seconds=runtime.seconds),
            'retcode': 0,
            'output': '(output goes here)',
        }


class run_n_mail(CommandOutputEmail):
    """
    Emails output of an arbitrary command.
    """
    abstract = False
    fallback_key = None


class sendmail_failure(Email):
    """
    This alert is sent whenever sending of another "normal" message fails.
    """
    default_subject = "Email Send Failed"

    def sample_data(self, request):
        return {
            'attempt': "testing 1 2 3",
            'message': {'To': 'fred@mailinator.com'},
            'error': "Something went wrong!",
        }


class trainwreck_problems_current_needs_pruning(ProblemReportEmail):
    """
    Problem report to indicate if the "current" Trainwreck DB is in
    need of pruning (if rotation is used).
    """
    default_subject = "Trainwreck DB needs pruning"
    abstract = False

    def sample_data(self, request):
        return {
            'problems': [(42, datetime.date(2021, 1, 1))],
        }


class trainwreck_problems_missing_dbs(ProblemReportEmail):
    """
    Problem report to ensure next year's Trainwreck DB exists, before
    it's actually needed.
    """
    default_subject = "Trainwreck missing DB"
    abstract = False

    def sample_data(self, request):
        next_year = str(self.app.today().year + 1)
        return {
            'problems': [next_year],
        }


class uncaught_exception(Email):
    """
    Sent when an error happens which was not handled properly by the app.
    This is more (only?) for GUI apps and not the web apps.
    """
    default_subject = "Uncaught Exception"

    def sample_data(self, request):
        try:
            raise RuntimeError("Fake error for preview")
        except:
            exc_type, exc, traceback = sys.exc_info()

        return {
            'extra_context': {'foo': 'bar'},
            'error': simple_error(exc),
            'traceback': ''.join(format_exception(exc_type, exc, traceback)).strip(),
        }


class upgrade_failure(Email):
    """
    Sent when an app upgrade is attempted, but ultimately failed.
    """
    default_subject = "Upgrade failure for ${system_title}"

    def sample_data(self, request):
        upgrade = self.app.make_object(
            description="upgrade to the latest!",
            notes="nothing special",
            executed=self.app.make_utc(),
            executed_by="Fred Flintstone",
            exit_code=42,
        )
        return {
            'upgrade': upgrade,
            'upgrade_url': '#',
            'system_title': self.app.get_title(),
        }


class upgrade_success(Email):
    """
    Sent when an app upgrade is performed successfully.
    """
    default_subject = "Upgrade success for ${system_title}"

    def sample_data(self, request):
        upgrade = self.app.make_object(
            description="upgrade to the latest!",
            notes="nothing special",
            executed=self.app.make_utc(),
            executed_by="Fred Flintstone",
            exit_code=0,
        )
        return {
            'upgrade': upgrade,
            'upgrade_url': '#',
            'system_title': self.app.get_title(),
        }


class user_feedback(Email):
    """
    Sent when a user submits a Feedback form from the web UI.
    """
    default_subject = "User Feedback"

    def sample_data(self, request):
        return {
            'app_title': self.app.get_title(),
            'user': None,
            'user_name': "Fred Flintstone",
            'referrer': request.route_url('home'),
            'client_ip': '127.0.0.1',
            'please_reply_to': 'fred@mailinator.com',
            'message': "Hey there,\n\njust wondered what the heck was going on with this site?  It's crap.\n\nFred",
        }
