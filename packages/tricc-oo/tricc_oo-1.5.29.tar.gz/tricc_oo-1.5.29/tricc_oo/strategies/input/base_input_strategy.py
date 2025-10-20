import abc

from tricc_oo.models.tricc import (
    TriccNodeMainStart,
    TriccNodeActivity,
)
from tricc_oo.converters.utils import generate_id
from tricc_oo.visitors.tricc import (
    get_activity_wait,
    set_prev_next_node,
    export_proposed_diags,
    create_determine_diagnosis_activity,
)
import logging

logger = logging.getLogger("default")


class BaseInputStrategy:
    input_path = None
    project = None
    processes = ["main"]

    def execute_linked_process(self, project):
        # create an overall activity only if not specified
        if "main" not in project.start_pages:
            page_processes = [
                (
                    p.root.process,
                    p,
                )
                for p in list(project.pages.values())
                if getattr(p.root, "process", None)
            ]
            sorted_pages = {}
            diags = []
            for a in project.pages.values():
                diags += export_proposed_diags(a, [])
            seen_diags = set()
            unique_diags = []
            for diag in diags:
                if diag.name not in seen_diags:
                    unique_diags.append(diag)
                    seen_diags.add(diag.name)
            severity_order = {"severe": 3, "moderate": 2, "mild": 1, "light": 0}
            unique_diags = sorted(
                unique_diags,
                key=lambda x: (
                    -getattr(severity_order, x.severity or "light", 0),
                    x.label,
                ),
            )
            for process in self.processes:
                if process in [p[0] for p in page_processes]:
                    sorted_pages[process] = [p[1] for p in page_processes if p[0] == process]
                elif process == "determine-diagnosis" and diags:
                    diags_activity = create_determine_diagnosis_activity(unique_diags)
                    sorted_pages[process] = [diags_activity]
                    project.start_pages["determine-diagnosis"] = diags_activity
            root_process = sorted_pages[list(sorted_pages.keys())[0]][0].root
            root = TriccNodeMainStart(
                id=generate_id("s-main"),
                form_id=root_process.form_id,
                label=root_process.label,
                process="main",
            )
            nodes = {}
            nodes[root.id] = root
            app = TriccNodeActivity(id=generate_id("a-main"), name=root_process.name, root=root, nodes=nodes)
            root.activity = app
            # loop back to app to avoid None
            app.activity = app
            app.group = app
            # setting the activity/group to main
            prev_bridge = root
            prev_process = None
            for process in self.processes:
                if process in sorted_pages:
                    nodes = {page.id: page for page in sorted_pages[process]}
                    if prev_process:
                        prev_bridge = get_activity_wait(
                            prev_bridge,
                            sorted_pages[prev_process],
                            nodes.values(),
                            activity=app,
                        )
                    else:
                        for a in nodes:
                            set_prev_next_node(prev_bridge, a, edge_only=True)
                    app.nodes[prev_bridge.id] = prev_bridge

                    for n in nodes.values():
                        n.activity = app
                        n.group = app
                        app.nodes[n.id] = n
                    prev_process = process

            return app
        else:
            return project.start_pages["main"]

    def __init__(self, input_path):
        self.input_path = input_path

    # walking function
    @abc.abstractmethod
    def execute(in_filepath, media_path):
        pass
