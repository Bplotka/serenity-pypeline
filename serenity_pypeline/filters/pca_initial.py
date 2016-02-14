from serenity_pypeline.logger import log
from serenity_pypeline.db.influxdb_connector import InfluxDbConnector
from serenity_pypeline.db.important_consts import DATABASE_METRICS_CONF_FILE, \
    SERENITY_METRICS_CONF_FILE, DATA_FIELD

from sqlbuilder.smartsql import Q, compile
from serenity_pypeline.filters.filter import Filter


class PcaInitial(Filter):

    def __init__(self, conf):
        super(PcaInitial, self).__init__(conf)

        # TODO: type of the database engine
        # should be loaded from the workflow configuration file
        self._dbConnector = InfluxDbConnector(conf)
        self._dbConnector.connect()
        self._result = None
        self.source = conf['default']['node']

    def run(self, **kwargs):
        self._result = kwargs

        # data filtered from Serenity input...
        data_to_test = self._filter_data_from_serenity(kwargs)

        # ... will be updated by database data
        metrics_to_query = self._get_which_metrics_query()
        for metric, field in metrics_to_query.iteritems():
            # TODO: How big set of data we should analyze?
            # In the meaning of time (where statement)
            where_clause = "time > now() - 1h" +\
            " and source = \'%s\'" % self.source
            query_to_execute = compile(
                Q().tables('"' + metric + '"').
                    fields(field).where(where_clause)
            )
            log.info(self._format_query_to_string(query_to_execute))
            database_output = self._get_data_from_database(
                self._format_query_to_string(query_to_execute)
            )
            data_to_test[metric] = database_output

        self._result[DATA_FIELD] = data_to_test
        return self._result

    def _filter_data_from_serenity(self, serenity_data):
        metric_value = dict()

        conf_file = open(SERENITY_METRICS_CONF_FILE, 'r')
        for record in conf_file:
            if record.startswith('#'):  # it's just a comment, move along
                continue
            if record in serenity_data:
                metric_value[record] = serenity_data[record]

        return metric_value

    def _get_which_metrics_query(self):
        table_field_dict = dict()

        conf_file = open(DATABASE_METRICS_CONF_FILE, 'r')
        for record in conf_file:
            if record.startswith('#'):  # it's just a comment, move along
                continue
            key_value = record.split()
            table_field_dict[key_value[0]] = key_value[1]

        return table_field_dict

    def _format_query_to_string(self, query):
        return query[0] % tuple(query[1])

    def _get_data_from_database(self, query_to_execute):
        return self._dbConnector.query_data(query_to_execute)
