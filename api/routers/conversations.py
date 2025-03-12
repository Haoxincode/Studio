from fastapi import APIRouter, Depends, HTTPException, status
from typing import List, Optional
from datetime import datetime
import uuid

from api.schemas.conversation import ConversationCreateRequest, ConversationResponse, ConversationUpdateRequest, PrdResponse
from api.schemas.user import UserInDB
from api.services.auth_service import get_current_user
from api.services.conversation_service import create_conversation_service, get_conversations_service, get_session_conversations_service, update_conversation_service, get_prd_service
from api.config import logger

router = APIRouter(prefix="/conversations", tags=["对话管理"])

# 创建对话接口
@router.post("", response_model=ConversationResponse)
async def create_conversation(request: ConversationCreateRequest, current_user: UserInDB = Depends(get_current_user)):
    logger.info(f"Creating a conversation for session_id: {request.session_id} by user_id: {current_user.user_id}")
    
    # 验证请求中的 user_id 是否与当前登录的用户一致
    if current_user.user_id != request.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User ID does not match the authenticated user's ID"
        )
    
    # 调用服务层创建对话
    try:
        conversation = await create_conversation_service(request, current_user)
        return conversation
    except Exception as e:
        logger.error(f"Error creating conversation: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# 获取会话的所有对话接口
@router.get("/session/{session_id}", response_model=List[ConversationResponse])
async def get_session_conversations(session_id: int, current_user: UserInDB = Depends(get_current_user)):
    logger.info(f"Fetching conversations for session_id: {session_id}")
    
    # 调用服务层获取会话的所有对话
    try:
        conversations = await get_session_conversations_service(session_id, current_user.user_id)
        return conversations
    except Exception as e:
        logger.error(f"Error fetching conversations for session {session_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# 获取单个对话接口
@router.get("/{conversation_id}", response_model=ConversationResponse)
async def get_conversation_by_id(conversation_id: uuid.UUID, current_user: UserInDB = Depends(get_current_user)):
    logger.info(f"Fetching conversation with id: {conversation_id}")
    
    # 调用服务层获取单个对话
    try:
        conversation = await get_conversations_service(str(conversation_id), current_user.user_id)
        if not conversation:
            raise HTTPException(status_code=404, detail="Conversation not found")
        return conversation
    except HTTPException as e:
        raise e
    except Exception as e:
        logger.error(f"Error fetching conversation {conversation_id}: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")

# 更新对话接口
@router.put("", response_model=ConversationResponse)
async def update_conversation(request: ConversationUpdateRequest, current_user: UserInDB = Depends(get_current_user)):
    logger.info(f"Updating conversation for session_id: {request.session_id}")
    
    # 验证请求中的 user_id 是否与当前登录的用户一致
    if current_user.user_id != request.user_id:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="User ID does not match the authenticated user's ID"
        )
    
    # 调用服务层更新对话
    try:
        updated_conversation = await update_conversation_service(request)
        return updated_conversation
    except Exception as e:
        logger.error(f"Error updating conversation: {e}")
        raise HTTPException(status_code=500, detail="Internal server error")
    


@router.get("/get_prd", response_model=PrdResponse, summary="获取最新PRD内容")
async def get_latest_prd(user_id: int) -> PrdResponse:
    """
    获取当前用户最新会话的PRD内容
    
    Args:
        current_user (UserInDB): 当前登录用户信息，通过token认证获取
        
    Returns:
        PrdResponse: 包含PRD内容的响应对象
        
    Raises:
        HTTPException: 
            - 404: 未找到用户会话或PRD内容
            - 500: 服务器内部错误
    """
    return await get_prd_service(user_id)