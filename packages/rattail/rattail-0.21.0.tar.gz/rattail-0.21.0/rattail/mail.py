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
Email Framework
"""

import importlib
import os
import smtplib
import logging
import warnings
from email.charset import Charset
from email.message import Message
from email.mime.multipart import MIMEMultipart
from email.mime.application import MIMEApplication
from email.mime.text import MIMEText

from mako.template import Template
from mako.lookup import TemplateLookup
from mako.exceptions import TopLevelLookupException

from wuttjamaican.email import EmailHandler as WuttaEmailHandler

from rattail import exceptions
from rattail.core import UNSPECIFIED
from rattail.files import resource_path
from rattail.util import load_entry_points
from rattail.time import localtime


# NOTE: this bit of magic was stolen from Django
# Don't BASE64-encode UTF-8 messages so that we avoid unwanted attention from
# some spam filters.
utf8_charset = Charset('utf-8')
utf8_charset.body_encoding = None  # Python defaults to BASE64

log = logging.getLogger(__name__)


def send_email(config, key, data={}, attachments=[],
               fallback_key=None, default_subject=None,
               enabled=UNSPECIFIED, **kwargs):
    """
    Send an email message of the given type, per config, with the given data
    and/or attachments.
    """
    app = config.get_app()
    handler = app.get_email_handler()
    email = handler.get_email(key, fallback_key=fallback_key,
                              default_subject=default_subject)

    if enabled is UNSPECIFIED:
        enabled = handler.email_is_enabled(email)

    if enabled:
        kwargs['attachments'] = attachments
        handler.send_message(email, data, **kwargs)
    else:
        log.debug("skipping email of type '%s' per config", key)


class EmailHandler(WuttaEmailHandler):
    """
    Base class and default implementation for email handlers.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.enum = self.app.enum

        # only assign model attribute if db libs are installed
        try:
            import sqlalchemy
        except ImportError:
            pass
        else:
            self.model = self.app.model

    def use_entry_points(self):
        """
        Returns a boolean indicating if the app should get its list of
        available emails from the setuptools entry points, instead of
        the (legacy) ``[rattail.mail] emails`` config setting.
        """
        return self.config.getbool('rattail.mail', 'emails.use_entry_points',
                                   default=True)

    def should_record_attempts(self):
        """
        Returns a boolean indicating if the app should make a record
        of all attempts to send email.
        """
        return self.config.getbool('rattail.mail', 'record_attempts',
                                   default=False)

    def should_send_email_on_failure(self):
        """
        Returns a boolean indicating if the app should send an email
        alert whenever sending of an email message fails.
        """
        return self.config.getbool('rattail.mail', 'send_email_on_failure',
                                   default=False)

    def get_all_emails(self, **kwargs):
        """
        Retrieve the complete set of all Email profiles exposed by the
        app and installed packages.
        """
        # TODO: maybe deprecate this at some point?
        if not self.use_entry_points():
            # nb. this is the legacy behavior
            return dict([(email.key or email.__name__, email)
                         for email in self.iter_emails(warn=False)])

        # this is the future..
        emails = {}

        # first get *all* email modules, per entry points
        all_modules = load_entry_points('rattail.emails').values()

        # but maybe the app config says only to use certain modules
        app_modules = self.config.getlist('rattail.mail', 'emails.modules')
        if not app_modules:
            app_modules = self.config.getlist('rattail.mail', 'emails',
                                              ignore_ambiguous=True)
            if app_modules:
                warnings.warn(f"URGENT: instead of 'rattail.mail.emails', "
                              f"you should set 'rattail.mail.emails.modules'",
                              DeprecationWarning, stacklevel=2)

        # figure out which modules we should actually use
        if app_modules:
            modules = [importlib.import_module(m)
                       for m in app_modules]
        else:
            modules = all_modules

        # and collect all email profiles from those modules
        for module in modules:
            mod_emails = self.get_emails_from_module(module)
            emails.update(dict([(email.key or email.__name__, email)
                                for email in mod_emails]))
        return emails

    def get_emails_from_module(self, module, **kwargs):
        """
        Return all Email profiles from the given Python module.
        """
        emails = []
        for name in dir(module):
            obj = getattr(module, name)
            if (isinstance(obj, type) and issubclass(obj, Email)
                and not obj.abstract and obj is not Email):
                emails.append(obj)
        return emails

    def get_available_emails(self, **kwargs):
        """
        Retrieve the set of "available" Email profiles, i.e. those
        which should be exposed to the app users.
        """
        emails = self.get_all_emails()
        for key in list(emails):
            if not self.email_is_available(key):
                emails.pop(key)
        return emails

    def iter_emails(self, warn=True):
        """
        Iterate over all available email types.
        """
        if warn:
            warnings.warn("`iter_emails()` method is deprecated!  please "
                          "use `get_available_emails()` instead",
                          DeprecationWarning, stacklevel=2)

        for module in self.config.getlist('rattail.mail', 'emails', default=['rattail.emails']):
            module = importlib.import_module(module)
            for email in self.get_emails_from_module(module):
                yield email

    def get_email(self, key, fallback_key=None, **kwargs):
        """
        Return an email instance of the given type.
        """
        factory = Email
        emails = self.get_all_emails()
        if key in emails:
            factory = emails[key]
        return factory(self.config, key, fallback_key, **kwargs)

    def email_is_available(self, email):
        """
        Returns boolean indicating if the Email profile for the given
        key is "available" and should be exposed to users.
        """
        return not self.email_is_hidden(email)

    def email_is_hidden(self, email):
        """
        Returns boolean indicating if the given Email profile is
        "hidden" and should not be exposed to users.

        :param email: Either an :class:`Email` instance, or the
           :attr:`~Email.key` value for one.
        """
        key = getattr(email, 'key', email)
        hidden = self.config.getbool('rattail.mail',
                                     '{}.hidden'.format(key),
                                     default=False)
        return hidden

    def email_is_enabled(self, email):
        """
        Returns boolean indicating if the given Email profile is
        "enabled" - that is, emails of its type should be sent as
        opposed to being suppressed.

        :param email: An :class:`Email` instance.
        """
        return email.get_enabled()

    def get_enabled(self, email):
        warnings.warn("`get_enabled()` method is deprecated!  please "
                      "use `email_is_enabled()` instead",
                      DeprecationWarning, stacklevel=2)

        return self.email_is_enabled(email)

    def send_message(self, email, data, **kwargs):
        msg = self.make_message(email, data, **kwargs)

        if self.should_record_attempts():
            attempt = self.record_attempt(email, msg)
            try:
                self.deliver_message(email, msg)
            except Exception as e:
                self.record_failure(email, msg, attempt, e)
                raise
            else:
                self.record_success(email, msg, attempt)

        else: # don't record attempts
            self.deliver_message(email, msg)

    def record_attempt(self, email, msg):
        model = self.model
        session = self.app.make_session()

        attempt = model.EmailAttempt()
        attempt.key = email.key
        attempt.sender = msg['From']
        attempt.to = msg.get_all('To')
        attempt.cc = msg.get_all('Cc')
        attempt.bcc = msg.get_all('Bcc')
        attempt.subject = msg['Subject']
        attempt.sent = self.app.make_utc()
        attempt.status_code = self.enum.EMAIL_ATTEMPT_CREATED
        session.add(attempt)

        session.commit()
        session.close()
        # session.expunge(attempt)
        return attempt

    def record_failure(self, email, message, attempt, error):
        session = self.app.make_session()
        attempt = session.merge(attempt)
        attempt.status_code = self.enum.EMAIL_ATTEMPT_FAILURE
        attempt.status_text = str(error)
        session.commit()
        session.close()

        if self.should_send_email_on_failure():
            self.app.send_email('sendmail_failure', {
                'email': email,
                'message': message,
                'attempt': attempt,
                'error': error,
            })

    def record_success(self, email, message, attempt):
        session = self.app.make_session()
        attempt = session.merge(attempt)
        attempt.status_code = self.enum.EMAIL_ATTEMPT_SUCCESS
        session.commit()
        session.close()

    def make_message(self, email, data, **kwargs):
        context = self.make_context(**data)
        return email.make_message(context, **kwargs)

    def make_context(self, **context):
        context['rattail_config'] = self.config
        context['app'] = self.app
        context['app_title'] = self.app.get_title()
        # TODO: deprecate / remove this
        context['localtime'] = localtime
        return context

    def sending_is_enabled(self):
        """ """
        # TODO: our default is true but wuttjamaican's is false
        return self.config.get_bool('rattail.mail.send_emails',
                                    default=True)

    def deliver_message(self, email, msg, recipients=UNSPECIFIED):
        """
        Deliver an email message using the given SMTP configuration.
        """
        if recipients is UNSPECIFIED:
            recips = set()

            # nb. we use original recip lists, contained in X_RATTAIL
            # headers, instead of the simple strings which e.g. the
            # To: header contains.  but we also then remove custom
            # headers b/c they don't belong in the final msg

            to = msg['X_RATTAIL_TO']
            del msg['X_RATTAIL_TO']
            if to:
                recips = recips.union(set(to))

            cc = msg['X_RATTAIL_CC']
            del msg['X_RATTAIL_CC']
            if cc:
                recips = recips.union(set(cc))

            bcc = msg['X_RATTAIL_BCC']
            del msg['X_RATTAIL_BCC']
            if bcc:
                recips = recips.union(set(bcc))

        else:
            recips = set(recipients)

        if not recips:
            raise RuntimeError("No recipients for email: {0}".format(repr(msg)))

        server = self.config.get('rattail.mail', 'smtp.server', default='localhost')
        username = self.config.get('rattail.mail', 'smtp.username')
        password = self.config.get('rattail.mail', 'smtp.password')

        if self.config.getbool('rattail.mail', 'send_feedback_only', usedb=False, default=False):
            send = email.key == 'user_feedback'
        else:
            send = self.sending_is_enabled()

        if send:

            log.debug("attempting to send mail of type: %s", email.key)
            log.debug("connecting to server: %s", server)
            session = smtplib.SMTP(server)
            if username and password:
                result = session.login(username, password)
                log.debug("login() result is: %s", repr(result))

            result = session.sendmail(msg['From'], recips, msg.as_string())
            log.debug("sendmail() result is: %s", repr(result))
            session.quit()
            return True

        log.debug("config says no emails for '%s', but would have sent one to: %s", email.key, recips)
        return False


def get_email_handler(config):
    """
    Creates and returns the configured mail handler.
    """
    warnings.warn("`get_email_handler()` is deprecated!  please "
                  "use `AppHandler.get_email_handler()` instead",
                  DeprecationWarning, stacklevel=2)

    app = config.get_app()
    return app.get_email_handler()


class Email(object):
    # Note: The docstring of an email is leveraged by code, hence this odd one.
    """
    (This email has no description.)
    """
    key = None
    fallback_key = None
    abstract = False
    default_prefix = "[rattail]"
    default_subject = "Automated message"
    universal_subject = "Automated message"

    # Whether or not the email's :attr:`to` attribute is dynamically determined
    # at run-time, i.e. via some logic other than typical reading from config.
    dynamic_to = False
    dynamic_to_help = None

    def __init__(self, config, key=None, fallback_key=None, default_subject=None):
        self.config = config
        self.app = config.get_app()
        self.enum = config.get_enum()

        # only assign model attribute if db libs are installed
        try:
            import sqlalchemy
        except ImportError:
            pass
        else:
            self.model = self.app.model

        if key:
            self.key = key
        elif not self.key:
            self.key = self.__class__.__name__
            if self.key == 'Email':
                raise exceptions.ConfigurationError("Email instance has no key: {0}".format(repr(self)))

        if fallback_key:
            self.fallback_key = fallback_key
        if default_subject:
            self.default_subject = default_subject

        templates = config.getlist('rattail.mail', 'templates',
                                   default=['rattail:templates/mail'])
        if templates:
            templates = [resource_path(p) for p in templates]
        self.txt_templates = TemplateLookup(directories=templates)
        self.html_templates = TemplateLookup(directories=templates,
                                             # nb. this escapes HTML special chars
                                             default_filters=['h'])

    def obtain_sample_data(self, request):
        """
        This method is responsible for obtaining the full set of sample data,
        to be used as context when generating a preview for the email.

        Note, you normally should not override this method!  Please see also
        the :meth:`sample_data()` method.
        """
        return self.sample_data(request)

    def sample_data(self, request):
        """
        This method can return a dict of sample data, to be used as context
        when generating a preview for the email.  Subclasses are welcome to
        override this method.
        """
        return {}

    def get_enabled(self):
        """
        Get the enabled flag for the email's message type.
        """
        enabled = self.config.getbool('rattail.mail', '{0}.enabled'.format(self.key))
        if enabled is not None:
            return enabled
        enabled = self.config.getbool('rattail.mail', 'default.enabled')
        if enabled is not None:
            return enabled
        return self.config.getbool('rattail.mail', 'send_emails', default=True)

    def get_sender(self):
        """
        Returns the value for the message's ``From:`` header.

        :rtype: str
        """
        sender = self.config.get('rattail.mail', '{0}.from'.format(self.key))
        if not sender:
            sender = self.config.get('rattail.mail', 'default.from')
            if not sender:
                raise exceptions.SenderNotFound(self.key)
        return sender

    def get_replyto(self):
        """
        Get the Reply-To address for the message.
        """
        replyto = self.config.get('rattail.mail', '{0}.replyto'.format(self.key))
        if not replyto:
            replyto = self.config.get('rattail.mail', 'default.replyto')
        return replyto

    def get_recips(self, type_='to'):
        """
        Returns a list of recipients of the given type for the message.

        :param type_: Must be one of: ``('to', 'cc', 'bcc', 'all')``.
           If you specify ``'all'`` then all recipients will be
           returned as a single list, with no indication as to which
           "slot" (to, cc, bcc) each came from.

        :rtype: list
        """
        try:
            if type_.lower() not in ('to', 'cc', 'bcc', 'all'):
                raise Exception
        except:
            raise ValueError("Recipient type must be one of ('to', 'cc', 'bcc', 'all'); "
                             "not: {0}".format(repr(type_)))
        type_ = type_.lower()
        if type_ == 'all':
            recips = []
            for typ in ('to', 'cc', 'bcc'):
                recips.extend(self.get_recips(typ))
        else:
            recips = self.config.getlist('rattail.mail', '{0}.{1}'.format(self.key, type_))
            if not recips:
                recips = self.config.getlist('rattail.mail', 'default.{0}'.format(type_))
        return recips or []

    def get_prefix(self, data={}, magic=True):
        """
        Returns a string to be used as the subject prefix for the message.

        :rtype: str
        """
        # first look for prefix specific to this email type
        prefix = self.config.get('rattail.mail', '{0}.prefix'.format(self.key))
        if not prefix:

            # next look for global default prefix
            prefix = self.config.get('rattail.mail', 'default.prefix')
            if not prefix:

                # otherwise just use app node title
                prefix = self.app.get_node_title()
                if prefix:
                    prefix = f"[{prefix}]"

        # fall back to hard-coded default if no prefix yet
        # TODO: not sure that's possible since we try node title above
        prefix = prefix or self.default_prefix

        # force the [DEV] prefix unless running in production
        if magic and not self.config.production():
            prefix = "[DEV] {}".format(prefix)

        return prefix

    def get_default_subject(self, **data):
        return self.default_subject

    def get_subject_template(self, **data):
        """
        Returns the template to be used to build the subject.
        """
        # use explicitly configured subject if there is one
        template = self.config.get('rattail.mail', '{}.subject'.format(self.key))
        if template:
            return template

        # or if this email defines a custom default, use that
        default = self.get_default_subject(**data)
        if default != self.universal_subject:
            return default

        # otherwise fall back to the global configured default
        return self.config.get('rattail.mail', 'default.subject',
                               default=self.universal_subject)

    def get_subject(self, data={}, render=True, template=UNSPECIFIED):
        """
        Returns the base value for the message's subject header, i.e. minus
        prefix.

        :rtype: str
        """
        if template is UNSPECIFIED:
            template = self.get_subject_template(**data)
        if template and render:
            return Template(template).render(**data)
        return template

    def get_complete_subject(self, data={}, render=True, prefix=UNSPECIFIED, template=UNSPECIFIED):
        """
        Returns the value for the message's ``Subject:`` header, i.e. the base
        subject with the prefix applied.  Note that config may provide the
        complete subject also, in which case the prefix and base subject are
        not considered.

        :rtype: str
        """
        if prefix is UNSPECIFIED:
            prefix = self.get_prefix(data)
        prefix = (prefix or "").rstrip()
        if prefix:
            prefix = "{} ".format(prefix)
        return "{}{}".format(prefix, self.get_subject(data, render=render, template=template))

    def get_template(self, type_):
        """
        Locate and return the Mako email template of the given type
        (e.g. 'html'), or ``None`` if no such template can be found.
        """
        if type_ == 'txt':
            templates = self.txt_templates
        else:
            assert type_ == 'html'
            templates = self.html_templates

        try:
            return templates.get_template(f'{self.key}.{type_}.mako')
        except TopLevelLookupException:
            if self.fallback_key:
                try:
                    return templates.get_template(f'{self.fallback_key}.{type_}.mako')
                except TopLevelLookupException:
                    pass

    def normalize_attachments(self, attachments):
        normalized = []
        for attachment in attachments:
            if isinstance(attachment, str):
                attachment = self.normalize_attachment(attachment)
            normalized.append(attachment)
        return normalized

    ATTACHMENT_MIME_MAP = {
        '.doc': 'application/msword',
        '.pdf': 'pdf',
        '.xls': 'vnd.ms-excel',
        '.xlsx': 'vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    }

    def normalize_attachment(self, path):
        root, ext = os.path.splitext(path)
        ext = ext.lower()
        if ext == '.csv':
            with open(path, 'rb') as f:
                part = MIMEText(f.read(), 'csv', 'utf_8')
            filename = os.path.basename(path)
            part.add_header('Content-Disposition', 'attachment; filename="{}"'.format(filename))
            return part
        else:
            mimetype = self.ATTACHMENT_MIME_MAP.get(ext)
            if mimetype:
                with open(path, 'rb') as f:
                    part = MIMEApplication(f.read(), mimetype)
                filename = os.path.basename(path)
                part.add_header('Content-Disposition', 'attachment; filename="{}"'.format(filename))
                return part
        raise ValueError("Magic is not (yet) supported, please construct your own attachments for file: {}".format(path))

    def make_message(self, data={}, attachments=[], inlines=[],
                     subject_prefix=UNSPECIFIED, subject_template=UNSPECIFIED,
                     sender=UNSPECIFIED, replyto=UNSPECIFIED,
                     to=UNSPECIFIED, cc=UNSPECIFIED, bcc=UNSPECIFIED):
        """
        Returns a proper email ``Message`` instance which may be sent via SMTP.
        """
        txt_template = self.get_template('txt')
        html_template = self.get_template('html')
        attachments = self.normalize_attachments(attachments)

        # TODO: provide more defaults?
        data.setdefault('app', self.app)

        if txt_template and html_template:

            txt_part = MIMEText(txt_template.render(**data), _charset='utf_8')

            html_part = MIMEText(html_template.render(**data), _subtype='html', _charset='utf_8')
            if inlines:
                html_part = MIMEMultipart(_subtype='related', _subparts=[html_part] + inlines)

            msg = MIMEMultipart(_subtype='alternative', _subparts=[txt_part, html_part])
            if attachments:
                msg = MIMEMultipart(_subtype='mixed', _subparts=[msg] + attachments)

        elif txt_template:

            msg = MIMEText(txt_template.render(**data), _charset='utf_8')
            if attachments:
                msg = MIMEMultipart(_subtype='mixed', _subparts=[msg] + attachments)

        elif html_template:

            msg = SafeMIMEText(html_template.render(**data), 'html', utf8_charset)
            if inlines:
                msg = MIMEMultipart(_subtype='related', _subparts=[msg] + inlines)
            if attachments:
                msg = MIMEMultipart(_subtype='mixed', _subparts=[msg] + attachments)

        else:
            raise exceptions.MailTemplateNotFound(self.key)

        self.add_headers(msg, data=data,
                         subject_prefix=subject_prefix, subject_template=subject_template,
                         sender=sender, replyto=replyto, to=to, cc=cc, bcc=bcc)
        return msg

    def add_headers(self, msg, data={},
                    subject_prefix=UNSPECIFIED, subject_template=UNSPECIFIED,
                    sender=UNSPECIFIED, replyto=UNSPECIFIED,
                    to=UNSPECIFIED, cc=UNSPECIFIED, bcc=UNSPECIFIED):
        """
        Adds headers for to/from addresses etc. to message
        """
        # subject/from
        msg['Subject'] = self.get_complete_subject(data, prefix=subject_prefix,
                                                   template=subject_template)
        if sender is UNSPECIFIED:
            sender = self.get_sender()
        msg['From'] = sender

        # reply-to
        if replyto is UNSPECIFIED:
            replyto = self.get_replyto()
        if replyto:
            msg.add_header('Reply-To', replyto)

        # recipients
        force_to = self.config.getlist('rattail.mail', 'force_to', usedb=False)
        if force_to:
            to = force_to
            cc = None
            bcc = None
        else:
            if to is UNSPECIFIED:
                to = self.get_recips('to')
            if cc is UNSPECIFIED:
                cc = self.get_recips('cc')
            if bcc is UNSPECIFIED:
                bcc = self.get_recips('bcc')
        if not (to or cc or bcc):
            raise exceptions.RecipientsNotFound(self.key)

        # nb. we preserve the original lists within X_RATTAIL headers,
        # for easier SMTP sending later on
        if to:
            msg['To'] = ', '.join(to)
            msg['X_RATTAIL_TO'] = to
        if cc:
            msg['Cc'] = ', '.join(cc)
            msg['X_RATTAIL_CC'] = cc
        if bcc:
            msg['Bcc'] = ', '.join(bcc)
            msg['X_RATTAIL_BCC'] = bcc


# NOTE: this bit of magic was stolen from Django
class SafeMIMEText(MIMEText):

    def __init__(self, text, subtype, charset):
        self.encoding = charset
        if charset == 'utf-8':
            # Unfortunately, Python doesn't support setting a Charset instance
            # as MIMEText init parameter (http://bugs.python.org/issue16324).
            # We do it manually and trigger re-encoding of the payload.
            MIMEText.__init__(self, text, subtype, None)
            del self['Content-Transfer-Encoding']
            # TODO: i don't personally need this yet, if ever?
            # # Workaround for versions without http://bugs.python.org/issue19063
            # if (3, 2) < sys.version_info < (3, 3, 4):
            #     payload = text.encode(utf8_charset.output_charset)
            #     self._payload = payload.decode('ascii', 'surrogateescape')
            #     self.set_charset(utf8_charset)
            # else:
            #     self.set_payload(text, utf8_charset)
            self.set_payload(text, utf8_charset)
            self.replace_header('Content-Type', 'text/%s; charset="%s"' % (subtype, charset))
        else:
            MIMEText.__init__(self, text, subtype, charset)
