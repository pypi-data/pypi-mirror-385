from pathlib import Path
from .annotator import MeasurementAnnotator, WorkflowAnnotator, WorkflowToolAnnotator


class Annotator:
    measurement_annotator = MeasurementAnnotator
    workflow_annotator = WorkflowAnnotator
    workflow_tool_annotator = WorkflowToolAnnotator

    def __init__(self, dataset_path):
        self.root = Path(dataset_path)

    def measurements(self, mode="default"):
        """
        :param mode: string, "default" for default mode, "update" for update mode
        :return:
        """
        return self.measurement_annotator(self.root, mode)

    def workflow(self):
        return self.workflow_annotator(self.root)

    def workflow_tool(self):
        return self.workflow_tool_annotator(self.root)
