from labfreed.pac_attributes.pythonic.py_attributes import pyAttributes
from labfreed.pac_attributes.server.attribute_data_sources import Dict_DataSource


class pyDict_DataSource(Dict_DataSource):
    def __init__(self, data:dict[str, pyAttributes], *args, **kwargs):
        if not all([isinstance(e, pyAttributes) for e in data.values()]):
            raise ValueError('Invalid data')
        d = {k: v.to_payload_attributes() for k,v in data.items()}
        super().__init__(data=d, *args, **kwargs)

        
    