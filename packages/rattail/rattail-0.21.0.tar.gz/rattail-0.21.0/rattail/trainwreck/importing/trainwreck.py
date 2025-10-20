# -*- coding: utf-8; -*-
################################################################################
#
#  Rattail -- Retail Software Framework
#  Copyright © 2010-2023 Lance Edgar
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
TrainWreck -> Trainwreck data importing
"""

import datetime
from collections import OrderedDict

from rattail.importing.handlers import FromSQLAlchemyHandler, ToSQLAlchemyHandler
from rattail.importing.sqlalchemy import FromSQLAlchemySameToSame
from rattail.trainwreck.db import Session as TrainwreckSession
from rattail.time import localtime, make_utc
from rattail.trainwreck.importing import model
from rattail.trainwreck.importing.util import ToOrFromTrainwreck


class FromTrainwreckHandler(FromSQLAlchemyHandler):
    """
    Base class for import handlers which have a Trainwreck DB as data source on the host side.
    """
    host_key = 'trainwreck'
    generic_host_title = "Trainwreck"
    host_title = "Trainwreck"

    def make_host_session(self):
        return TrainwreckSession()


class ToTrainwreckHandler(ToSQLAlchemyHandler):
    """
    Base class for import handlers which target a Trainwreck DB on the local side.
    """
    local_key = 'trainwreck'
    generic_local_title = "Trainwreck"
    local_title = "Trainwreck"

    def make_session(self):
        return TrainwreckSession()


class TrainwreckImportExportBase(FromTrainwreckHandler, ToTrainwreckHandler):
    """
    Shared base class for Trainwreck <-> Trainwreck handlers
    """

    def get_importers(self):
        importers = OrderedDict()
        importers['Transaction'] = TransactionImporter
        importers['TransactionOrderMarker'] = TransactionOrderMarkerImporter
        importers['TransactionItem'] = TransactionItemImporter
        importers['TransactionItemDiscount'] = TransactionItemDiscountImporter
        return importers


class FromTrainwreckToTrainwreckImport(TrainwreckImportExportBase):
    """
    Handler for Trainwreck (other) -> Trainwreck (local) data import.

    .. attribute:: direction

       Value is ``'import'`` - see also
       :attr:`rattail.importing.handlers.ImportHandler.direction`.
    """
    dbkey = 'host'
    local_title = "Trainwreck (default)"

    @property
    def host_title(self):
        return "Trainwreck ({})".format(self.dbkey)

    def make_host_session(self):
        return TrainwreckSession(bind=self.config.trainwreck_engines[self.dbkey])


class FromTrainwreckToTrainwreckExport(TrainwreckImportExportBase):
    """
    Handler for Trainwreck (local) -> Trainwreck (other) data export.

    .. attribute:: direction

       Value is ``'export'`` - see also
       :attr:`rattail.importing.handlers.ImportHandler.direction`.
    """
    direction = 'export'
    host_title = "Trainwreck (default)"

    @property
    def local_title(self):
        return "Trainwreck ({})".format(self.dbkey)

    def make_session(self):
        return TrainwreckSession(bind=self.config.trainwreck_engines[self.dbkey])


class FromTrainwreck(FromSQLAlchemySameToSame):
    """
    Base class for Trainwreck -> Trainwreck data importers.
    """


class TransactionImporter(FromTrainwreck, model.TransactionImporter):
    """
    Base class for Transaction data importer
    """

    def query(self):
        query = super(TransactionImporter, self).query()
        query = self.filter_date_range(query)
        return query

    def filter_date_range(self, query):
        return query.filter(self.model_class.end_time >= make_utc(self.start_time))\
                    .filter(self.model_class.end_time < make_utc(self.end_time))


class TransactionOrderMarkerImporter(FromTrainwreck, model.TransactionOrderMarkerImporter):
    """
    Base class for Transaction order marker data importer
    """

    def query(self):
        query = super(TransactionOrderMarkerImporter, self).query()
        query = self.filter_date_range(query)
        return query

    def filter_date_range(self, query):
        time_field = getattr(self.transaction_class, self.match_on_time_field)
        return query.join(self.transaction_class)\
                    .filter(time_field >= self.app.make_utc(self.start_time))\
                    .filter(time_field < self.app.make_utc(self.end_time))


class TransactionItemImporter(FromTrainwreck, model.TransactionItemImporter):
    """
    Base class for Transaction item data importer
    """

    def query(self):
        query = super(TransactionItemImporter, self).query()
        query = self.filter_date_range(query)
        return query

    def filter_date_range(self, query):
        return query.join(self.transaction_class)\
                    .filter(self.transaction_class.end_time >= make_utc(self.start_time))\
                    .filter(self.transaction_class.end_time < make_utc(self.end_time))


class TransactionItemDiscountImporter(FromTrainwreck, model.TransactionItemDiscountImporter):
    """
    Base class for item discount data importer
    """

    def query(self):
        query = super(TransactionItemDiscountImporter, self).query()
        trainwreck = self.config.get_trainwreck_model()

        query = query.join(trainwreck.TransactionItem)\
                     .join(trainwreck.Transaction)

        time_field = getattr(trainwreck.Transaction, self.match_on_time_field)
        query = query.filter(time_field >= self.app.make_utc(self.start_time))\
                     .filter(time_field < self.app.make_utc(self.end_time))

        return query
