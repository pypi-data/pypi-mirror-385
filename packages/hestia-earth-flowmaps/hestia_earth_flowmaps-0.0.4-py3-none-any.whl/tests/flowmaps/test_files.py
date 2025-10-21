import os

from tests.utils import flowmaps_folder
from hestia_earth.flowmaps.RosettaFlow import FlowMap


def test_validate_csv_file():
    files = [f for f in os.listdir(flowmaps_folder) if f.endswith('.csv')]
    for file in files:
        file_mappings = FlowMap.read_flow_file(os.path.join(flowmaps_folder, file))
        results = FlowMap.validate_csv_file(file_mappings)
        assert len(results) > 0
