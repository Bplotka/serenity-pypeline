import numpy as np

from serenity_pypeline.logger import log
from serenity_pypeline.db.important_consts import DATA_FIELD
from serenity_pypeline.filters.filter import Filter


class PcaExecutor(Filter):

    def __init__(self, conf):
        super(PcaExecutor, self).__init__(conf)

    def run(self, **kwargs):
        log.info('Counting PCA...')

        input_matrix = []
        key_list = []
        data_to_test = kwargs[DATA_FIELD]
        for key, val in data_to_test.iteritems():
            g = val.get_points()
            l = list(g)
            log.info(str(key) + " has length " + str(len(l)))
            l = [x['value'] for x in l]
            input_matrix.append(l)
            key_list.append(key)

        corr_matrix = np.corrcoef(input_matrix)

        log.info(corr_matrix)
        return {'data_to_insert': self._prepare_data(key_list,
                                                     corr_matrix.tolist()),
                'measurement': 'correlations'}

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

