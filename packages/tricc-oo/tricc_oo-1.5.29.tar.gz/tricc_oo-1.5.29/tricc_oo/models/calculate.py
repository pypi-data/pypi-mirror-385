from typing import List, Optional, Union
import logging
from tricc_oo.models.base import (
    TriccBaseModel, TriccOperation, TriccStatic, TriccReference, Expression, TriccNodeType
)

from tricc_oo.models.tricc import (
    TriccNodeCalculateBase, TriccNodeBaseModel,
)

from tricc_oo.converters.utils import get_rand_name

logger = logging.getLogger(__name__)

ACTIVITY_END_NODE_FORMAT = "aend_{}"


class TriccNodeDisplayCalculateBase(TriccNodeCalculateBase):
    save: Optional[str] = None  # contribute to another calculate
    hint: Optional[str] = None  # for diagnostic display
    help: Optional[str] = None  # for diagnostic display
    trigger: Optional[Union[Expression, TriccOperation, TriccReference]] = None
    applicability: Optional[Union[Expression, TriccOperation, TriccReference]] = None

    # no need to copy save
    def to_fake(self):
        data = vars(self)
        del data["hint"]
        del data["help"]
        del data["save"]
        fake = TriccNodeFakeCalculateBase(**data)
        self.replace_node(fake)
        return fake

    def __str__(self):
        return self.get_name()

    def __repr__(self):
        return self.get_name()


class TriccNodeCalculate(TriccNodeDisplayCalculateBase):
    tricc_type: TriccNodeType = TriccNodeType.calculate
    remote_reference: Optional[Union[Expression, TriccOperation, TriccReference]] = None


class TriccNodeAdd(TriccNodeDisplayCalculateBase):
    tricc_type: TriccNodeType = TriccNodeType.add
    datatype: str = "number"


class TriccNodeCount(TriccNodeDisplayCalculateBase):
    tricc_type: TriccNodeType = TriccNodeType.count
    datatype: str = "number"


class TriccNodeProposedDiagnosis(TriccNodeDisplayCalculateBase):
    tricc_type: TriccNodeType = TriccNodeType.proposed_diagnosis
    severity: str = None
    remote_reference: Optional[Union[Expression, TriccOperation, TriccReference]] = None


class TriccNodeFakeCalculateBase(TriccNodeCalculateBase):
    ...


class TriccNodeInput(TriccNodeFakeCalculateBase):
    tricc_type: TriccNodeType = TriccNodeType.input


class TriccNodeDisplayBridge(TriccNodeDisplayCalculateBase):
    tricc_type: TriccNodeType = TriccNodeType.bridge


class TriccNodeBridge(TriccNodeFakeCalculateBase):
    tricc_type: TriccNodeType = TriccNodeType.bridge


class TriccRhombusMixIn:

    def make_mixin_instance(self, instance, instance_nb, activity, **kwargs):
        # shallow copy
        reference = []
        expression_reference = None
        instance.path = None
        if isinstance(
            self.expression_reference,
            (str, TriccOperation, TriccReference, TriccStatic),
        ):
            expression_reference = self.expression_reference.copy()
            reference = list(expression_reference.get_references())
        if isinstance(self.reference, (str, TriccOperation, TriccReference, TriccStatic)):
            expression_reference = self.reference.copy()
            reference = list(expression_reference.get_references())
        elif isinstance(self.reference, list):
            for ref in self.reference:
                if issubclass(ref.__class__, TriccBaseModel):
                    pass
                    # get the reference
                    if self.activity == ref.activity:
                        for sub_node in activity.nodes.values():
                            if sub_node.base_instance == ref:
                                reference.append(sub_node)
                    else:  # ref from outside
                        reference.append(ref)
                        logger.warning("new instance of a rhombus use the reference of the base one")
                elif isinstance(ref, TriccReference):
                    reference.append(ref)
                elif isinstance(ref, str):
                    logger.debug("passing raw reference {} on node {}".format(ref, self.get_name()))
                    reference.append(ref)
                else:
                    logger.critical("unexpected reference {} in node {}".format(ref, self.get_name()))
                    exit(1)
        instance.reference = reference
        instance.expression_reference = expression_reference
        instance.name = get_rand_name(self.id)
        return instance


class TriccNodeRhombus(TriccNodeCalculateBase, TriccRhombusMixIn):
    tricc_type: TriccNodeType = TriccNodeType.rhombus
    path: Optional[TriccNodeBaseModel] = None
    reference: Union[
        List[TriccNodeBaseModel],
        Expression,
        TriccOperation,
        TriccReference,
        List[TriccReference],
    ]
    remote_reference: Optional[Union[Expression, TriccOperation, TriccReference]] = None

    def make_instance(self, instance_nb, activity, **kwargs):
        instance = super(TriccNodeRhombus, self).make_instance(instance_nb, activity, **kwargs)
        instance = self.make_mixin_instance(instance, instance_nb, activity, **kwargs)
        return instance

    def __init__(self, **data):
        data["name"] = get_rand_name(data.get("id", None))
        super().__init__(**data)


class TriccNodeDiagnosis(TriccNodeDisplayCalculateBase):
    tricc_type: TriccNodeType = TriccNodeType.diagnosis
    severity: str = None

    def __init__(self, **data):
        data["reference"] = f'"final.{data["name"]}" is true'
        super().__init__(**data)

        # rename rhombus
        self.name = get_rand_name(f"d{data.get('id', None)}")


class TriccNodeExclusive(TriccNodeFakeCalculateBase):
    tricc_type: TriccNodeType = TriccNodeType.exclusive


def get_node_from_id(activity, node, edge_only):
    node_id = getattr(node, "id", node)
    if not isinstance(node_id, str):
        logger.critical("can set prev_next only with string or node")
        exit(1)
    if issubclass(node.__class__, TriccBaseModel):
        return node_id, node
    elif node_id in activity.nodes:
        node = activity.nodes[node_id]
    elif not edge_only:
        logger.critical(f"cannot find {node_id} in  {activity.get_name()}")
        exit(1)
    return node_id, node


class TriccNodeWait(TriccNodeFakeCalculateBase, TriccRhombusMixIn):
    tricc_type: TriccNodeType = TriccNodeType.wait
    path: Optional[TriccNodeBaseModel] = None
    reference: Union[List[TriccNodeBaseModel], Expression, TriccOperation]

    def make_instance(self, instance_nb, activity, **kwargs):
        instance = super(TriccNodeWait, self).make_instance(instance_nb, activity, **kwargs)
        instance = self.make_mixin_instance(instance, instance_nb, activity, **kwargs)
        return instance


class TriccNodeActivityEnd(TriccNodeFakeCalculateBase):
    tricc_type: TriccNodeType = TriccNodeType.activity_end

    def __init__(self, **data):
        super().__init__(**data)
        # FOR END
        self.set_name()

    def set_name(self):
        self.name = ACTIVITY_END_NODE_FORMAT.format(self.activity.id)


class TriccNodeEnd(TriccNodeDisplayCalculateBase):
    tricc_type: TriccNodeType = TriccNodeType.end
    process: str = None
    priority: int = 1000

    def __init__(self, **data):
        if data.get("name", None) is None:
            data["name"] = "tricc_end_" + data.get("process", "")
        super().__init__(**data)
        # FOR END

    def set_name(self):
        if self.name is None:
            self.name = self.get_reference()
        # self.name = END_NODE_FORMAT.format(self.activity.id)

    def get_reference(self):
        return "tricc_end_" + (self.process or "")


class TriccNodeActivityStart(TriccNodeFakeCalculateBase):
    tricc_type: TriccNodeType = TriccNodeType.activity_start
    relevance: Optional[Union[Expression, TriccOperation]] = None


def get_node_from_list(in_nodes, node_id):
    nodes = list(filter(lambda x: x.id == node_id, in_nodes))
    if len(nodes) > 0:
        return nodes[0]


# qualculate that saves quantity, or we may merge integer/decimals
class TriccNodeQuantity(TriccNodeDisplayCalculateBase):
    tricc_type: TriccNodeType = TriccNodeType.quantity


TriccNodeCalculate.update_forward_refs()
