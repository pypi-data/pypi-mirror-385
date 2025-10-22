import asyncio
import os
from typing import List

import dotenv

from dify_client import AsyncDifyClient, DifyClient
from dify_client import models as dify_models


dotenv.load_dotenv()


dify_client = DifyClient(
    api_base=os.getenv("DIFY_API_BASE"),
    api_key=os.getenv("DIFY_API_KEY"),
)

async_dify_client = AsyncDifyClient(
    api_base=os.getenv("DIFY_API_BASE"),
    api_key=os.getenv("DIFY_API_KEY"),
)


def get_conversations(user: str, limit: int = 20) -> List:
    conversation_request = dify_models.ConversationRequest(
        user=user,
        limit=limit,
    )
    conversation_resp: dify_models.ConversationsResponse = (
        dify_client.get_conversations(conversation_request)
    )
    conversations: List[dify_models.Conversation] = conversation_resp.data
    return conversations


def get_conversation_history_messages(
    user: str, conversation_id: str, limit: int
):
    conversation_message_req = dify_models.ConversationHistoryMessageRequest(
        conversation_id=conversation_id,
        user=user,
        limit=limit,
    )
    conversation_message_resp: dify_models.ConversationHistoryMessageResponse = dify_client.get_conversation_history_messages(
        conversation_message_req,
    )
    hist_messages: List[dify_models.HistoryMessage] = (
        conversation_message_resp.data
    )

    return hist_messages


async def aget_conversation_history_messages(
    user: str, conversation_id: str, limit: int
):
    conversation_message_req = dify_models.ConversationHistoryMessageRequest(
        conversation_id=conversation_id,
        user=user,
        limit=limit,
    )
    conversation_message_resp: dify_models.ConversationHistoryMessageResponse = await async_dify_client.aget_conversation_history_messages(
        conversation_message_req,
    )
    hist_messages: List[dify_models.HistoryMessage] = (
        conversation_message_resp.data
    )

    return hist_messages


if __name__ == "__main__":
    user_id = "264183_reimi"

    conversations: List[dify_models.Conversation] = get_conversations(
        user=user_id
    )
    async_hist_messages = []
    hist_messages = []
    if len(conversations) > 0:
        conversation_id = conversations[0].id
        hist_messages: List[dify_models.HistoryMessage] = (
            get_conversation_history_messages(
                conversation_id=conversation_id,
                user=user_id,
                limit=20,
            )
        )

        print(f"Num messages: {len(hist_messages)} - {hist_messages}")

    if len(conversations) > 0:
        conversation_id = conversations[0].id
        async_hist_messages: List[dify_models.HistoryMessage] = asyncio.run(
            aget_conversation_history_messages(
                user=user_id, conversation_id=conversation_id, limit=20
            )
        )

        print(f"Num messages: {len(hist_messages)} - {hist_messages}")
    assert len(hist_messages) > 0 and len(async_hist_messages) > 0
    assert len(hist_messages) == len(async_hist_messages)
