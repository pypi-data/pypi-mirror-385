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
Models for POS transaction batch
"""

import sqlalchemy as sa
from sqlalchemy import orm
from sqlalchemy.ext.declarative import declared_attr
from sqlalchemy.orm.collections import attribute_mapped_collection

from rattail.db.model import Base, BatchMixin, BatchRowMixin, uuid_column
from rattail.db.types import GPCType


class POSBatch(BatchMixin, Base):
    """
    Hopefully generic batch used for entering new purchases into the system, etc.?
    """
    batch_key = 'pos'
    __tablename__ = 'batch_pos'
    __batchrow_class__ = 'POSBatchRow'
    model_title = "POS Batch"
    model_title_plural = "POS Batches"

    @declared_attr
    def __table_args__(cls):
        return cls.__batch_table_args__() + (
            sa.ForeignKeyConstraint(['store_uuid'], ['store.uuid'],
                                    name='batch_pos_fk_store'),
            sa.ForeignKeyConstraint(['customer_uuid'], ['customer.uuid'],
                                    name='batch_pos_fk_customer'),
            sa.ForeignKeyConstraint(['cashier_uuid'], ['employee.uuid'],
                                    name='batch_pos_fk_cashier'),
        )

    STATUS_OK                           = 1
    STATUS_SUSPENDED                    = 2

    STATUS = {
        STATUS_OK                       : "ok",
        STATUS_SUSPENDED                : "suspended",
    }

    store_id = sa.Column(sa.String(length=10), nullable=True, doc="""
    ID of the store where the transaction occurred.
    """)

    store_uuid = sa.Column(sa.String(length=32), nullable=True)
    store = orm.relationship(
        'Store',
        doc="""
        Reference to the store where the transaction ocurred.
        """)

    terminal_id = sa.Column(sa.String(length=20), nullable=True, doc="""
    Terminal ID from which the transaction originated, if known.
    """)

    # receipt_number = sa.Column(sa.String(length=20), nullable=True, doc="""
    # Receipt number for the transaction, if known.
    # """)

    # cashier_id = sa.Column(sa.String(length=20), nullable=True, doc="""
    # ID of the cashier who rang the transaction.
    # """)

    # cashier_name = sa.Column(sa.String(length=255), nullable=True, doc="""
    # Name of the cashier who rang the transaction.
    # """)

    # start_time = sa.Column(sa.DateTime(), nullable=True, doc="""
    # UTC timestamp when the transaction began.
    # """)

    # customer_id = sa.Column(sa.String(length=20), nullable=True, doc="""
    # ID of the customer account for the transaction.
    # """)

    # customer_number = sa.Column(sa.String(length=20), nullable=True, doc="""
    # Number of the customer account for the transaction.
    # """)

    # customer_name = sa.Column(sa.String(length=255), nullable=True, doc="""
    # Name of the Customer account for the transaction.
    # """)

    cashier_uuid = sa.Column(sa.String(length=32), nullable=True)
    cashier = orm.relationship(
        'Employee',
        doc="""
        Reference to the employee (cashier) who rang up the transaction.
        """)

    customer_uuid = sa.Column(sa.String(length=32), nullable=True)
    customer = orm.relationship(
        'Customer',
        doc="""
        Reference to the customer account for the transaction.
        """)

    customer_is_member = sa.Column(sa.Boolean(), nullable=True, doc="""
    Flag indicating the customer was a "member" at time of sale.
    """)

    customer_is_employee = sa.Column(sa.Boolean(), nullable=True, doc="""
    Flag indicating the customer was an employee at time of sale.
    """)

    # shopper_number = sa.Column(sa.String(length=20), nullable=True, doc="""
    # Number of the shopper account for the transaction, if applicable.
    # """)

    # shopper_name = sa.Column(sa.String(length=255), nullable=True, doc="""
    # Name of the shopper account for the transaction, if applicable.
    # """)

    # shopper_uuid = sa.Column(sa.String(length=32), nullable=True)
    # shopper = orm.relationship(
    #     'CustomerShopper',
    #     doc="""
    #     Reference to the shopper account for the transaction.
    #     """)

    sales_total = sa.Column(sa.Numeric(precision=9, scale=2), nullable=True, doc="""
    Sales total for the transaction.
    """)

    fs_total = sa.Column(sa.Numeric(precision=9, scale=2), nullable=True, doc="""
    Portion of the sales total which is foodstamp-eligible.
    """)

    tax_total = sa.Column(sa.Numeric(precision=9, scale=2), nullable=True, doc="""
    Tax total for the transaction.
    """)

    fs_tender_total = sa.Column(sa.Numeric(precision=9, scale=2), nullable=True, doc="""
    Foodstamp tender total for the transaction.
    """)

    tender_total = sa.Column(sa.Numeric(precision=9, scale=2), nullable=True, doc="""
    Tender total for the transaction.
    """)

    void = sa.Column(sa.Boolean(), nullable=False, default=False, doc="""
    Flag indicating if the transaction was voided.
    """)

    training_mode = sa.Column(sa.Boolean(), nullable=False, default=False, doc="""
    Flag indicating if the transaction was rang in training mode,
    i.e. not real / should not go on the books.
    """)

    def get_balance(self):
        return ((self.sales_total or 0)
                + (self.tax_total or 0)
                + (self.tender_total or 0))

    def get_fs_balance(self):
        return ((self.fs_total or 0)
                + (self.fs_tender_total or 0))


class POSBatchTax(Base):
    """
    A tax total for a POS batch.

    Each row in the batch may be associated with a tax (or not).
    Those which are must be aggregated, to determine overall tax total
    for the batch.  Arbitrary number of taxes may be involved, hence
    we store them in this table.
    """
    __tablename__ = 'batch_pos_tax'
    __table_args__ = (
        sa.ForeignKeyConstraint(['batch_uuid'], ['batch_pos.uuid'],
                                name='batch_pos_tax_fk_batch'),
        sa.ForeignKeyConstraint(['tax_uuid'], ['tax.uuid'],
                                name='batch_pos_tax_fk_tax'),
    )

    uuid = uuid_column()

    batch_uuid = sa.Column(sa.String(length=32), nullable=False)
    batch = orm.relationship(
        POSBatch,
        backref=orm.backref(
            'taxes',
            collection_class=attribute_mapped_collection('tax_code'),
        ))

    tax_uuid = sa.Column(sa.String(length=32), nullable=True)
    tax = orm.relationship('Tax')

    tax_code = sa.Column(sa.String(length=30), nullable=False, doc="""
    Unique "code" for the tax rate.
    """)

    tax_rate = sa.Column(sa.Numeric(precision=7, scale=5), nullable=False, doc="""
    Percentage rate for the tax, e.g. 8.25.
    """)

    tax_total = sa.Column(sa.Numeric(precision=9, scale=2), nullable=True, doc="""
    Total for the tax.
    """)


class POSBatchRow(BatchRowMixin, Base):
    """
    Row of data within a POS batch.
    """
    __tablename__ = 'batch_pos_row'
    __batch_class__ = POSBatch

    @declared_attr
    def __table_args__(cls):
        return cls.__batchrow_table_args__() + (
            sa.ForeignKeyConstraint(['user_uuid'], ['user.uuid'],
                                    name='batch_pos_row_fk_user'),
            sa.ForeignKeyConstraint(['product_uuid'], ['product.uuid'],
                                    name='batch_pos_row_fk_item'),
            sa.ForeignKeyConstraint(['tender_uuid'], ['tender.uuid'],
                                    name='batch_pos_row_fk_tender'),
        )

    STATUS_OK                           = 1

    STATUS = {
        STATUS_OK                       : "ok",
    }

    timestamp = sa.Column(sa.DateTime(), nullable=True, doc="""
    UTC timestamp when this item was added to transaction.
    """)

    user_uuid = sa.Column(sa.String(length=32), nullable=True)
    user = orm.relationship(
        'User',
        doc="""
        Reference to the user who added this row to the batch.
        """)

    row_type = sa.Column(sa.String(length=32), nullable=True, doc="""
    Type of item represented by this row, e.g. "item" or "return" or
    "tender" etc.

    .. todo::
       need to figure out how to manage/track POSBatchRow.row_type
    """)

    item_entry = sa.Column(sa.String(length=32), nullable=True, doc="""
    Raw/original entry value for the item, if applicable.
    """)

    upc = sa.Column(GPCType(), nullable=True, doc="""
    UPC for the product associated with the row.
    """)

    item_id = sa.Column(sa.String(length=20), nullable=True, doc="""
    Generic ID string for the product associated with the row.
    """)

    product_uuid = sa.Column(sa.String(length=32), nullable=True)
    product = orm.relationship(
        'Product',
        doc="""
        Reference to the associated product, if applicable.
        """)

    brand_name = sa.Column(sa.String(length=100), nullable=True, doc="""
    Brand name of the product.
    """)

    description = sa.Column(sa.String(length=255), nullable=True, doc="""
    Description of the product.
    """)

    size = sa.Column(sa.String(length=255), nullable=True, doc="""
    Size of the product, as string.
    """)

    full_description = sa.Column(sa.String(length=255), nullable=True, doc="""
    Full description for the line item.
    """)

    department_number = sa.Column(sa.Integer(), nullable=True, doc="""
    Number of the department to which the product belongs.
    """)

    department_name = sa.Column(sa.String(length=30), nullable=True, doc="""
    Name of the department to which the product belongs.
    """)

    subdepartment_number = sa.Column(sa.Integer(), nullable=True, doc="""
    Number of the subdepartment to which the product belongs.
    """)

    subdepartment_name = sa.Column(sa.String(length=30), nullable=True, doc="""
    Name of the subdepartment to which the product belongs.
    """)

    foodstamp_eligible = sa.Column(sa.Boolean(), nullable=True, doc="""
    Flag indicating the item was eligible for purchase with food
    stamps or equivalent.
    """)

    sold_by_weight = sa.Column(sa.Boolean(), nullable=True, doc="""
    Flag indicating the item was sold by weight.
    """)

    quantity = sa.Column(sa.Numeric(precision=8, scale=2), nullable=True, doc="""
    Quantity for the item.
    """)

    cost = sa.Column(sa.Numeric(precision=8, scale=3), nullable=True, doc="""
    Internal cost for the item sold.

    NOTE: this may need to change at some point, hence the "generic"
    naming so far.  would we need to record multiple kinds of costs?
    """)

    reg_price = sa.Column(sa.Numeric(precision=8, scale=3), nullable=True, doc="""
    Regular price for the item.
    """)

    cur_price = sa.Column(sa.Numeric(precision=8, scale=3), nullable=True, doc="""
    Current price for the item.
    """)

    cur_price_type = sa.Column(sa.Integer(), nullable=True, doc="""
    Type code for the current price, if applicable.
    """)

    cur_price_start = sa.Column(sa.DateTime(), nullable=True, doc="""
    Start date for current price, if applicable.
    """)

    cur_price_end = sa.Column(sa.DateTime(), nullable=True, doc="""
    End date for current price, if applicable.
    """)

    txn_price = sa.Column(sa.Numeric(precision=8, scale=3), nullable=True, doc="""
    Actual price paid for the item.
    """)

    txn_price_adjusted = sa.Column(sa.Boolean(), nullable=True, doc="""
    Flag indicating the actual price was manually adjusted.
    """)

    sales_total = sa.Column(sa.Numeric(precision=9, scale=2), nullable=True, doc="""
    Sales total for the item.
    """)

    tax_code = sa.Column(sa.String(length=30), nullable=True, doc="""
    Unique "code" for the item tax rate, if applicable.
    """)

    tender_total = sa.Column(sa.Numeric(precision=9, scale=2), nullable=True, doc="""
    Tender total for the item.
    """)

    tender_uuid = sa.Column(sa.String(length=32), nullable=True)
    tender = orm.relationship(
        'Tender',
        doc="""
        Reference to the associated tender, if applicable.
        """)

    void = sa.Column(sa.Boolean(), nullable=False, default=False, doc="""
    Flag indicating the line item was voided.
    """)
