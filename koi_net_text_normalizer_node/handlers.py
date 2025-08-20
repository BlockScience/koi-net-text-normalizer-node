from datetime import datetime
import logging
from rid_lib.ext import Bundle
from rid_lib.types import KoiNetNode, SlackMessage, SlackUser
from koi_net.context import HandlerContext
from koi_net.processor.handler import HandlerType
from koi_net.processor.knowledge_object import KnowledgeObject
from koi_net.protocol.node import NodeProfile
from koi_net.protocol.edge import EdgeType, generate_edge_bundle
from .rid_types import NormalizedText
from .models import NormalizedTextObject
from .core import node

logger = logging.getLogger(__name__)


@node.pipeline.register_handler(HandlerType.Bundle, 
    rid_types=[SlackMessage])
def normalized_text_handler(ctx: HandlerContext, kobj: KnowledgeObject):
    def get_author_name(msg_data: dict) -> str | None:
        user_rid = SlackUser(
            user_id=msg_data["user"],
            team_id=msg_data["team"]
        )
        user_bundle = node.effector.deref(user_rid, use_network=True)
        if not user_bundle: return
        
        return user_bundle["real_name"]
    
    if type(kobj.rid) is SlackMessage:
        n_text_obj = NormalizedTextObject(
            text=kobj.contents.get("text"),
            author=get_author_name(kobj.contents),
            created_at=datetime.fromtimestamp(float(kobj.rid.ts))
        )
        n_text_rid = NormalizedText(kobj.rid)
        
        n_text_bundle = Bundle.generate(
            rid=n_text_rid,
            contents=n_text_obj.model_dump(mode="json")
        )
        ctx.handle(bundle=n_text_bundle)

@node.pipeline.register_handler(HandlerType.Network, rid_types=[KoiNetNode])
def greedy_contact(ctx: HandlerContext, kobj: KnowledgeObject):
    # when I found out about a new node
    
    if kobj.rid == ctx.identity.rid:
        return
    
    node_profile = kobj.bundle.validate_contents(NodeProfile)
    
    if ctx.graph.get_edge(
        source=kobj.rid,
        target=ctx.identity.rid,
    ) is not None:
        logger.debug("already have edge with node")
        return
    
    if SlackMessage not in node_profile.provides.event:
        logger.debug("node doesn't provide slack messages")
        return
    
    logger.debug("proposing edge")
    # queued for processing
    ctx.handle(bundle=generate_edge_bundle(
        source=kobj.rid,
        target=ctx.identity.rid,
        edge_type=EdgeType.WEBHOOK,
        # subscribes to all events for provided RID types
        rid_types=node_profile.provides.event
    ))
    
    payload = ctx.request_handler.fetch_rids(
        node=kobj.rid, 
        rid_types=[SlackMessage])
    
    logger.debug(f"fetched {len(payload.rids)} slack messages")
    
    for rid in payload.rids:
        ctx.handle(rid=rid, source=kobj.rid)