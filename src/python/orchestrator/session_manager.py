"""
FloodX: Session Manager
Manages attack sessions, states, and cleanup operations.
"""

import asyncio
import time
import os
import sys
from typing import Dict, Any, List, Optional
from dataclasses import dataclass, field
from datetime import datetime

# Add parent directory to Python path for proper imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from common.logger import logger


@dataclass
class AttackSession:
    """Represents an active attack session."""
    session_id: str
    target: str
    vector: str
    start_time: datetime = field(default_factory=datetime.now)
    config: Dict[str, Any] = field(default_factory=dict)
    status: str = "initializing"
    tasks: List[asyncio.Task] = field(default_factory=list)
    stats: Dict[str, Any] = field(default_factory=dict)


class SessionManager:
    """Manages attack sessions and their lifecycle."""
    
    def __init__(self):
        self.sessions: Dict[str, AttackSession] = {}
        self.active_session_id: Optional[str] = None
        
    def create_session(self, target: str, vector: str, config: Dict[str, Any]) -> str:
        """Create a new attack session."""
        session_id = f"session_{int(time.time())}"
        
        session = AttackSession(
            session_id=session_id,
            target=target,
            vector=vector,
            config=config.copy()
        )
        
        self.sessions[session_id] = session
        self.active_session_id = session_id
        
        logger.info(f"📝 Created session {session_id} for {vector} attack on {target}")
        return session_id
    
    def get_session(self, session_id: str) -> Optional[AttackSession]:
        """Get session by ID."""
        return self.sessions.get(session_id)
    
    def get_active_session(self) -> Optional[AttackSession]:
        """Get the currently active session."""
        if self.active_session_id:
            return self.sessions.get(self.active_session_id)
        return None
    
    def update_session_status(self, session_id: str, status: str):
        """Update session status."""
        if session := self.sessions.get(session_id):
            session.status = status
            logger.debug(f"Session {session_id} status: {status}")
    
    def add_task_to_session(self, session_id: str, task: asyncio.Task):
        """Add a task to a session."""
        if session := self.sessions.get(session_id):
            session.tasks.append(task)
    
    def update_session_stats(self, session_id: str, stats: Dict[str, Any]):
        """Update session statistics."""
        if session := self.sessions.get(session_id):
            session.stats.update(stats)
    
    async def cleanup_session(self, session_id: str):
        """Clean up a specific session."""
        if session := self.sessions.get(session_id):
            logger.info(f"🧹 Cleaning up session {session_id}")
            
            # Cancel all tasks
            for task in session.tasks:
                if not task.done():
                    task.cancel()
                    try:
                        await task
                    except asyncio.CancelledError:
                        pass
            
            session.status = "cleaned_up"
            logger.info(f"✅ Session {session_id} cleaned up")
    
    async def cleanup(self):
        """Clean up all sessions."""
        logger.info("🧹 Cleaning up all sessions...")
        
        cleanup_tasks = []
        for session_id in list(self.sessions.keys()):
            cleanup_tasks.append(self.cleanup_session(session_id))
        
        if cleanup_tasks:
            await asyncio.gather(*cleanup_tasks, return_exceptions=True)
        
        self.sessions.clear()
        self.active_session_id = None
        logger.info("✅ All sessions cleaned up")
    
    def get_session_summary(self) -> Dict[str, Any]:
        """Get summary of all sessions."""
        return {
            'total_sessions': len(self.sessions),
            'active_session': self.active_session_id,
            'sessions': {
                session_id: {
                    'target': session.target,
                    'vector': session.vector,
                    'status': session.status,
                    'start_time': session.start_time.isoformat(),
                    'tasks': len(session.tasks)
                }
                for session_id, session in self.sessions.items()
            }
        }
