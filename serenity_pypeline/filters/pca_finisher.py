import datetime, math

from serenity_pypeline.logger import log
from serenity_pypeline.db.influxdb_connector import InfluxDbConnector
from serenity_pypeline.filters.filter import Filter


class PcaFinisherException(Exception):
    pass


class PcaFinisher(Filter):
    KEY_FOR_DATA = 'data_to_insert'
    KEY_NAME = 'measurement'
    DEFAULT_CORR_PREFIX = 'corr_'
    DEFAULT_SEPARATOR = '_'
    STATUS_CODE_SUCCESSFUL = 0

    def __init__(self, conf):
        super(PcaFinisher, self).__init__(conf)

        # TODO: type of database engine
        # should be loaded from the workflow configuration file
        self._dbConnector = InfluxDbConnector(conf)
        self._dbConnector.connect()

        self._result = None
        self.node = conf['default']['node']

    def run(self, **kwargs):
        if PcaFinisher.KEY_FOR_DATA in kwargs:
            self._insert_data(kwargs[PcaFinisher.KEY_FOR_DATA],
                    kwargs[PcaFinisher.KEY_NAME])
            return PcaFinisher.STATUS_CODE_SUCCESSFUL
        else:
            raise PcaFinisherException(
                'No data for insert retrieved from a previous step. Failing...')

    def _insert_data(self, data_to_insert, measurement):
        result = []
        for name, data in data_to_insert.iteritems():
            for key, val in data.iteritems():
                if math.isnan(val):
                    val = 0.00001
                elif val == 0.0:
                    val = 0.00001

                json_record = self._create_record_json(
                    measurement,
                    name,
                    key,
                    val)
                result.append(json_record)
        self._dbConnector.write_data(result)

    def _create_record_json(self, measurement, name, tag, value):

        name = name.replace('/', '_')
        tag = tag.replace('/', '_')

        record_json = {
            "measurement": measurement + '_' + self.node,
            "tags": {
                "corr_name": name,
                "corr_with": tag
            },
            "fields": {
                "value": value
            }
        }

        return record_json

