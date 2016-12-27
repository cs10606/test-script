
from schematics.models import Model
from schematics.types import StringType, IntType
from schematics.types.compound import ListType

class GData(Model):
    host=StringType()
    newsHost=StringType()
    port=StringType()
    path=StringType()
    sep=StringType()
    reportFile=StringType()
    log=StringType()



class TData(Model):
    host=StringType()
    port=StringType()
    path=StringType()
    sep=StringType()


class emailData(Model):
    to_addr = ListType(StringType)
    mail_host = StringType()
    mail_user = StringType()
    mail_pass = StringType()
    port = IntType()
    headerMsg = StringType()
    report = StringType()
    log = StringType()
    file = StringType()
    exc_sum_time=StringType()