import datetime

from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy import Column
from sqlalchemy import Integer
from sqlalchemy import String
from sqlalchemy import DateTime
from sqlalchemy import Boolean
from sqlalchemy import Float


Base = declarative_base()

class ZQRaw(Base):
    __tablename__ = 'zq_raw'
    notification_type = Column(String)
    notification_no = Column(String,nullable=False, primary_key=True, index=True)
    notification_date = Column(DateTime(timezone=False), nullable=False, index=True)
    contract_acct = Column(String, nullable=False, index=True)
    cause_code = Column(String)
    meter_no = Column(String, nullable=False, index=True)
    prediction = Column(Boolean)
    probability = Column(Float, nullable=True)

    def __repr__(self):
        return "<ZQRaw(notification_no='{}', meter_no='{}'>".format(self.notification_no, self.meter_no)

    def to_dict(self):
        d = {}
        for column in self.__table__.columns:
            d[column.name] = getattr(self, column.name)
        return d


class Cell(Base):
    __tablename__ = 'notificationlist'
    notification_type = Column(String)
    notification_no = Column(String,nullable=False, primary_key=True, index=True)
    notification_date = Column(DateTime(timezone=False), nullable=False, index=True)
    contract_acct = Column(String, nullable=False, index=True)
    cause_code = Column(String)
    meter_no = Column(String, nullable=False, index=True)
    prediction = Column(Boolean)
    probability = Column(Float, nullable=True)
    consecutive_false = Column(Integer)

    def __repr__(self):
        return "<NotificationList(notification_no='{}', meter_no='{}'>".format(self.notification_no, self.meter_no)

    def to_dict(self):
        d = {}
        for column in self.__table__.columns:
            d[column.name] = getattr(self, column.name)
        return d
