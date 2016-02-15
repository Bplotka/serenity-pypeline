import numpy as np

from serenity_pypeline.logger import log
from serenity_pypeline.db.important_consts import DATA_FIELD
from serenity_pypeline.filters.filter import Filter
from serenity_pypeline.filters.pca_finisher import PcaFinisher


class PcaExecutor(Filter):

    def __init__(self, conf):
        super(PcaExecutor, self).__init__(conf)

    def run(self, **kwargs):
        input_matrix = []
        key_list = []
        data_to_test = kwargs[DATA_FIELD]

        spotted_length = -1
        log.info('Counting PCA... from ' + str(len(data_to_test)) + " dimensions.")
        for key, val in data_to_test.iteritems():
            points = list(val[0].get_points())
            if len(points) == 0:
                log.error("No data points for measurement: " + str(key))
                continue
            values = self._post_effect_output(points, val[1])
            log.debug("Last value in series:" + str(values[-1]))
            log.info(str(key) + " has length " + str(len(values)))
            if spotted_length == -1:
                spotted_length = len(values)
            elif spotted_length != len(values):
                raise ValueError("Measurements have different lengths!")

            input_matrix.append(values)
            key_list.append(key)

        corr_matrix = np.corrcoef(input_matrix)

        log.info(corr_matrix)
        return {PcaFinisher.KEY_FOR_DATA: self._prepare_data(key_list,
                                                     corr_matrix.tolist()),
                PcaFinisher.KEY_NAME: 'correlations'}

    def _post_effect_output(self, output, field):
        values = list()
        for i in xrange(0, len(output)):
            output[i]['value'] = float(output[i]['value'])
            if i == 0:
                continue

            if field["cumulated"]:
                output[i]['value'] -= output[i-1]['value']

            if field["mul"] != 1:
                output[i]['value'] *= field["mul"]

            if output[i]['value'] == 0.0:
                output[i]['value'] = 1.0

            values.append(output[i]['value'])

        return values

    def _prepare_data(self, key_list, corr_matrix):
        result = {}
        for key in key_list:
            index = key_list.index(key)
            result[key] = {}

            for val in corr_matrix[index]:
                val_index = corr_matrix[index].index(val)
                result[key][key_list[val_index]] = val

        log.info(result)
        return result

