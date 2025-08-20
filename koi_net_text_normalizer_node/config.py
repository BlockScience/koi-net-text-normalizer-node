from pydantic import Field
from koi_net_text_normalizer_node.rid_types import NormalizedText
from koi_net.config import NodeConfig, KoiNetConfig
from koi_net.protocol.node import NodeProfile, NodeProvides, NodeType

class TextNormalizerConfig(NodeConfig):
    koi_net: KoiNetConfig = Field(default_factory=lambda:
        KoiNetConfig(
            node_name="text_normalizer",
            node_profile=NodeProfile(
                node_type=NodeType.FULL,
                provides=NodeProvides(
                    event=[NormalizedText],
                    state=[NormalizedText]
                )
            )
        )
    )