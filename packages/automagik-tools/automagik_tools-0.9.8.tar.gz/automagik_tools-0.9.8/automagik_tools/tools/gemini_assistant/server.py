"""Gemini Assistant MCP Server - Enhanced Gemini consultation with session management"""

import asyncio
import os
import sys
import time
import mimetypes
from typing import Dict, List, Optional, Any
from dataclasses import dataclass, field
from datetime import datetime

from google import genai
from google.genai import types
from mcp.server.fastmcp import FastMCP

from .config import GeminiAssistantConfig


@dataclass
class ProcessedFile:
    """Information about a processed file."""

    file_type: str
    file_uri: str
    mime_type: str
    file_name: str
    file_path: str
    gemini_file_id: str


@dataclass
class Session:
    """Chat session with Gemini."""

    session_id: str
    chat: Any
    created: datetime
    last_used: datetime
    message_count: int
    problem_description: Optional[str] = None
    code_context: Optional[str] = None
    processed_files: Dict[str, ProcessedFile] = field(default_factory=dict)
    requested_files: List[str] = field(default_factory=list)
    search_queries: List[str] = field(default_factory=list)


class GeminiMCPServer:
    """MCP Server for Gemini file attachment functionality."""

    def __init__(self, config: GeminiAssistantConfig):
        self.config = config
        self.client = genai.Client(api_key=config.api_key)
        self.sessions: Dict[str, Session] = {}
        self.last_request_time = 0
        self.min_time_between_requests = 1.0  # 1 second
        self._cleanup_task = None

        # Default system prompt
        self.system_prompt = """You are an expert technical advisor helping Claude (another AI) solve complex programming problems through thoughtful analysis and genuine technical dialogue.

**IMPORTANT CONTEXT CHECK**: First, examine any project-specific context files that have been attached to this session (e.g., MCP-ASSISTANT-RULES.md, project-structure.md, README.md). If such files are available, incorporate their guidelines, project standards, and architectural principles into your approach. If no project context is provided, proceed directly with the analysis.

## Your Role as Technical Advisor
You provide:
- Deep analysis and architectural insights
- Thoughtful discussions about implementation approaches  
- Clarifying questions to understand requirements fully
- Constructive challenges to assumptions when you see potential issues
- Context from comprehensive code analysis
- Alternative solutions with clear trade-offs

## Communication Philosophy
Be conversational and engaging - you're a thinking partner, not just an analyzer:
- Engage in real dialogue, don't just dump analysis
- Ask clarifying questions when requirements are ambiguous
- Challenge ideas constructively when you see better approaches
- Iterate through discussion before settling on solutions
- Think deeply about problems before responding
- Be genuinely curious about the problem space

## Technical Analysis Focus
When examining code:
- Identify patterns, potential issues, and optimization opportunities
- Reference specific files, functions, and line numbers (format: file.py:42)
- Explain complex logic and architectural decisions
- Consider security, performance, and maintainability implications
- Think about edge cases, error handling, and failure modes
- Check adherence to project standards (if provided in context files)
- Suggest testing strategies and validation approaches

## Key Principles
- **Think First**: Take time to understand the problem deeply before suggesting solutions
- **Question Assumptions**: Don't accept requirements at face value if they seem problematic
- **Consider Context**: Always think about how your suggestions fit the broader system
- **Be Honest**: If an approach seems wrong, say so clearly with reasoning
- **Stay Practical**: Balance ideal solutions with pragmatic constraints
- **Remain Curious**: Each problem is an opportunity to learn something new

Remember: The best solutions emerge from genuine technical dialogue. Your goal is to help achieve the best possible implementation through thoughtful analysis, engaging discussion, and collaborative problem-solving."""

    def _ensure_cleanup_task_started(self):
        """Start cleanup task if not already running."""
        if self._cleanup_task is None or self._cleanup_task.done():
            self._cleanup_task = asyncio.create_task(self._cleanup_sessions())

    async def _cleanup_sessions(self):
        """Periodically clean up expired sessions."""
        while True:
            await asyncio.sleep(300)  # Check every 5 minutes
            now = datetime.now()
            expired_sessions = []

            for session_id, session in self.sessions.items():
                if (
                    now - session.last_used
                ).total_seconds() > self.config.session_timeout:
                    expired_sessions.append(session_id)

            for session_id in expired_sessions:
                await self._cleanup_session_files(session_id)
                del self.sessions[session_id]
                print(
                    f"[{datetime.now().isoformat()}] Session {session_id} expired and removed",
                    file=sys.stderr,
                )

    async def _cleanup_session_files(self, session_id: str):
        """Clean up uploaded files for a session."""
        if session_id not in self.sessions:
            return

        session = self.sessions[session_id]
        for file_path, file_info in session.processed_files.items():
            try:
                self.client.files.delete(file_info.gemini_file_id)
                print(
                    f"[{datetime.now().isoformat()}] Session {session_id}: Deleted file {file_info.file_name}",
                    file=sys.stderr,
                )
            except Exception as e:
                print(
                    f"[{datetime.now().isoformat()}] Session {session_id}: Failed to delete file {file_info.file_name}: {e}",
                    file=sys.stderr,
                )

    async def _rate_limit(self):
        """Simple rate limiting."""
        now = time.time()
        time_since_last = now - self.last_request_time
        if time_since_last < self.min_time_between_requests:
            await asyncio.sleep(self.min_time_between_requests - time_since_last)
        self.last_request_time = time.time()

    async def _process_file(self, file_path: str, session: Session) -> ProcessedFile:
        """Upload file to Gemini and return processed file info."""
        # Check if already processed
        if file_path in session.processed_files:
            return session.processed_files[file_path]

        # Check if file exists
        if not os.path.exists(file_path):
            raise FileNotFoundError(f"File not found: {file_path}")

        # Get file info
        file_name = os.path.basename(file_path)
        mime_type, _ = mimetypes.guess_type(file_path)

        # Handle common file extensions that mimetypes doesn't recognize
        if not mime_type:
            ext = os.path.splitext(file_path)[1].lower()
            mime_type_map = {
                ".jsx": "text/javascript",
                ".tsx": "text/typescript",
                ".ts": "text/typescript",
                ".vue": "text/html",
                ".svelte": "text/html",
                ".md": "text/markdown",
                ".json": "application/json",
                ".py": "text/x-python",
                ".js": "text/javascript",
                ".css": "text/css",
                ".html": "text/html",
                ".xml": "text/xml",
                ".yaml": "text/yaml",
                ".yml": "text/yaml",
                ".toml": "text/plain",
                ".ini": "text/plain",
                ".cfg": "text/plain",
                ".conf": "text/plain",
                ".sh": "text/x-shellscript",
                ".bat": "text/plain",
                ".sql": "text/x-sql",
            }
            mime_type = mime_type_map.get(ext, "text/plain")

        print(
            f"[{datetime.now().isoformat()}] Session {session.session_id}: Uploading file {file_name} ({mime_type})",
            file=sys.stderr,
        )

        # Upload to Gemini
        try:
            uploaded_file = self.client.files.upload(file=file_path)

            # Wait for processing with exponential backoff
            wait_intervals = [0.5, 0.5, 1, 1, 2, 3, 5, 8]  # Exponential backoff pattern
            total_wait = 0
            max_wait = 20  # Reduced from 30 seconds

            for interval in wait_intervals:
                if uploaded_file.state != "PROCESSING":
                    break

                print(
                    f"[{datetime.now().isoformat()}] Session {session.session_id}: File {file_name} is processing... ({total_wait:.1f}s)",
                    file=sys.stderr,
                )
                await asyncio.sleep(interval)
                total_wait += interval
                uploaded_file = self.client.files.get(name=uploaded_file.name)

                if total_wait >= max_wait:
                    break

            if uploaded_file.state == "PROCESSING":
                raise Exception(f"File processing timeout after {max_wait} seconds")

            if uploaded_file.state == "FAILED":
                raise Exception(
                    f"File upload failed: {getattr(uploaded_file, 'error', 'Unknown error')}"
                )

            # Create processed file info
            processed_file = ProcessedFile(
                file_type="file_data",
                file_uri=uploaded_file.uri,
                mime_type=uploaded_file.mime_type,
                file_name=file_name,
                file_path=file_path,
                gemini_file_id=uploaded_file.name,
            )

            # Store in session
            session.processed_files[file_path] = processed_file

            print(
                f"[{datetime.now().isoformat()}] Session {session.session_id}: File {file_name} uploaded successfully (URI: {uploaded_file.uri})",
                file=sys.stderr,
            )
            return processed_file

        except Exception as e:
            raise Exception(f"Failed to process file {file_path}: {e}")

    def _get_or_create_session(self, session_id: Optional[str] = None) -> Session:
        """Get existing session or create new one."""
        if not session_id:
            import uuid

            session_id = str(uuid.uuid4())

        if session_id in self.sessions:
            session = self.sessions[session_id]
            session.last_used = datetime.now()
            return session

        # Create new session with system prompt
        chat = self.client.chats.create(
            model=self.config.model,
            config=types.GenerateContentConfig(
                temperature=self.config.temperature,
                max_output_tokens=self.config.max_tokens,
                top_p=0.95,
                top_k=40,
                system_instruction=self.system_prompt,
            ),
        )

        session = Session(
            session_id=session_id,
            chat=chat,
            created=datetime.now(),
            last_used=datetime.now(),
            message_count=0,
        )

        self.sessions[session_id] = session
        print(
            f"[{datetime.now().isoformat()}] New session created: {session_id}",
            file=sys.stderr,
        )
        return session

    def _extract_requests_from_response(self, response_text: str, session: Session):
        """Extract file requests and search queries from Gemini's response."""
        # Track file requests
        import re

        # Pattern for file requests
        file_patterns = [
            r"show me (?:the )?([^\s]+\.[a-zA-Z]+)",
            r"share (?:the )?([^\s]+\.[a-zA-Z]+)",
            r"can you (?:show|share) (?:me )?([^\s]+\.[a-zA-Z]+)",
            r"(?:I need to see|please provide) ([^\s]+\.[a-zA-Z]+)",
        ]

        for pattern in file_patterns:
            matches = re.findall(pattern, response_text, re.IGNORECASE)
            for match in matches:
                if match not in session.requested_files:
                    session.requested_files.append(match)

        # Pattern for search requests
        search_patterns = [
            r"I would search for: ([^\n]+)",
            r"search for (?:the )?([^\n]+)",
            r"Let me search for ([^\n]+)",
        ]

        for pattern in search_patterns:
            matches = re.findall(pattern, response_text, re.IGNORECASE)
            for match in matches:
                if match not in session.search_queries:
                    session.search_queries.append(match.strip())


def create_server(config: Optional[GeminiAssistantConfig] = None) -> FastMCP:
    """Create and configure the Gemini Assistant MCP server"""

    if config is None:
        config = GeminiAssistantConfig()

    # Create server instance
    mcp = FastMCP("gemini-assistant")
    gemini_server = GeminiMCPServer(config)

    @mcp.tool()
    async def consult_gemini(
        specific_question: str,
        session_id: Optional[str] = None,
        problem_description: Optional[str] = None,
        code_context: Optional[str] = None,
        attached_files: Optional[List[str]] = None,
        file_descriptions: Optional[dict] = None,
        additional_context: Optional[str] = None,
        preferred_approach: str = "solution",
    ) -> str:
        """Start or continue a conversation with Gemini about complex coding problems. Supports follow-up questions in the same context.

        Args:
            specific_question: The specific question you want answered
            session_id: Optional session ID to continue a previous conversation
            problem_description: Detailed description of the coding problem (required for new sessions)
            code_context: All relevant code - will be cached for the session (required for new sessions)
            attached_files: Array of file paths to upload and attach to the conversation
            file_descriptions: Optional object mapping file paths to descriptions
            additional_context: Additional context, updates, or what changed since last question
            preferred_approach: Type of assistance needed (solution, review, debug, optimize, explain, follow-up)
        """

        await gemini_server._rate_limit()

        # Start cleanup task if needed
        gemini_server._ensure_cleanup_task_started()

        try:
            # Check session limits
            if (
                len(gemini_server.sessions) >= config.max_sessions
                and session_id not in gemini_server.sessions
            ):
                raise ValueError(
                    f"Maximum sessions ({config.max_sessions}) reached. Please end existing sessions."
                )

            # Get or create session
            session = gemini_server._get_or_create_session(session_id)

            # For new sessions, require problem description and either code_context or attached_files
            if session.message_count == 0:
                if not problem_description:
                    raise ValueError("problem_description is required for new sessions")
                if not code_context and not attached_files:
                    raise ValueError(
                        "Either code_context or attached_files are required for new sessions"
                    )

                # Store initial context
                session.problem_description = problem_description
                session.code_context = code_context

                # Estimate message size for optimization
                total_context_size = len(problem_description) + (
                    len(code_context) if code_context else 0
                )
                is_small_request = total_context_size < 500 and not attached_files

                # Build initial context with simplified format for small requests
                if is_small_request:
                    # Simplified format for small requests
                    context_parts = [f"Problem: {problem_description}"]
                    if code_context:
                        context_parts.append(f"\n\nCode:\n{code_context}")
                    context_parts.append(f"\n\nQuestion: {specific_question}")
                else:
                    # Full format for complex requests
                    context_parts = [
                        f"I'm Claude, an AI assistant, and I need your help with a complex coding problem. Here's the context:\n\n**Problem Description:**\n{problem_description}"
                    ]

                    # Add code context if provided
                    if code_context:
                        context_parts.append(f"\n**Code Context:**\n{code_context}")

                # Handle file attachments (only for complex requests)
                if attached_files and not is_small_request:
                    context_parts.append("\n**Attached Files:**")

                    # Create parallel upload tasks
                    print(
                        f"[{datetime.now().isoformat()}] Session {session.session_id}: Starting parallel upload of {len(attached_files)} files",
                        file=sys.stderr,
                    )
                    upload_tasks = []
                    for file_path in attached_files:
                        task = gemini_server._process_file(file_path, session)
                        upload_tasks.append(task)

                    # Execute all uploads in parallel
                    file_results = await asyncio.gather(
                        *upload_tasks, return_exceptions=True
                    )

                    # Process results
                    for file_path, result in zip(attached_files, file_results):
                        if isinstance(result, Exception):
                            print(
                                f"[{datetime.now().isoformat()}] Session {session.session_id}: Failed to process file {file_path}: {result}",
                                file=sys.stderr,
                            )
                            # Continue with other files instead of failing completely
                            context_parts.append(
                                f"\n- {os.path.basename(file_path)} (failed to upload: {str(result)})"
                            )
                        else:
                            # Success - file was uploaded
                            file_info = result
                            print(
                                f"[{datetime.now().isoformat()}] Session {session.session_id}: File {file_info.file_name} processed successfully",
                                file=sys.stderr,
                            )

                            # Add file description
                            description = (
                                file_descriptions.get(file_path, "")
                                if file_descriptions
                                else ""
                            )
                            if description:
                                description = f" - {description}"
                            context_parts.append(
                                f"\n- {file_info.file_name}{description}"
                            )

                    print(
                        f"[{datetime.now().isoformat()}] Session {session.session_id}: Parallel upload completed",
                        file=sys.stderr,
                    )
                elif attached_files and is_small_request:
                    # For small requests with files, fall back to complex format
                    is_small_request = False
                    context_parts = [
                        f"I'm Claude, an AI assistant, and I need your help with a coding problem.\n\n**Problem:** {problem_description}"
                    ]
                    if code_context:
                        context_parts.append(f"\n**Code:**\n{code_context}")

                if not is_small_request:
                    context_parts.append(
                        "\n\nPlease help me solve this problem. I may have follow-up questions, so please maintain context throughout our conversation."
                    )

                # Build message content
                if is_small_request:
                    # For small requests, send as simple text
                    initial_message = "".join(context_parts)
                    message_content = [initial_message]
                else:
                    # For complex requests, include text and uploaded file objects
                    message_content = ["".join(context_parts)]

                    # Add uploaded file objects for this session's new files
                    for file_path in attached_files or []:
                        if file_path in session.processed_files:
                            file_info = session.processed_files[file_path]
                            # Get the actual uploaded file object from Gemini
                            uploaded_file = gemini_server.client.files.get(
                                name=file_info.gemini_file_id
                            )
                            message_content.append(uploaded_file)

                # Send initial context
                response = await asyncio.get_event_loop().run_in_executor(
                    None, session.chat.send_message, message_content
                )
                session.message_count += 1

                file_count = len(session.processed_files)
                code_length = len(code_context) if code_context else 0
                print(
                    f"[{datetime.now().isoformat()}] Session {session.session_id}: Initial context sent ({code_length} chars, {file_count} files, simplified={is_small_request})",
                    file=sys.stderr,
                )

                # For small requests, return immediately since question was included
                if is_small_request:
                    response_text = response.text

                    # Extract any file requests or search queries from response
                    gemini_server._extract_requests_from_response(
                        response_text, session
                    )

                    # Build response with session info
                    result_parts = [
                        f"**Session ID:** {session.session_id}",
                        f"**Message #{session.message_count}**\n",
                        response_text,
                    ]

                    # Add summary of requests if any
                    if session.requested_files or session.search_queries:
                        result_parts.append("\n\n---")
                        if session.requested_files:
                            result_parts.append(
                                f"\n**Files Requested:** {', '.join(session.requested_files)}"
                            )
                        if session.search_queries:
                            result_parts.append(
                                f"\n**Searches Requested:** {'; '.join(session.search_queries)}"
                            )

                    result_parts.append(
                        f'\n\n---\n*Use session_id: "{session.session_id}" for follow-up questions*'
                    )

                    return "\n".join(result_parts)

            # Build the question (for complex requests or follow-up questions)
            question_parts = [f"**Question:** {specific_question}"]

            if additional_context:
                question_parts.append(
                    f"\n\n**Additional Context/Updates:**\n{additional_context}"
                )

            if preferred_approach != "follow-up":
                question_parts.append(
                    f"\n\n**Type of Help Needed:** {preferred_approach}"
                )

            question_prompt = "".join(question_parts)

            # Log request
            print(
                f"[{datetime.now().isoformat()}] Session {session.session_id}: Question #{session.message_count + 1} ({preferred_approach})",
                file=sys.stderr,
            )

            # Send message and get response
            response = await asyncio.get_event_loop().run_in_executor(
                None, session.chat.send_message, question_prompt
            )
            session.message_count += 1

            response_text = response.text

            # Extract any file requests or search queries from response
            gemini_server._extract_requests_from_response(response_text, session)

            # Build response with session info
            result_parts = [
                f"**Session ID:** {session.session_id}",
                f"**Message #{session.message_count}**\n",
                response_text,
            ]

            # Add summary of requests if any
            if session.requested_files or session.search_queries:
                result_parts.append("\n\n---")
                if session.requested_files:
                    result_parts.append(
                        f"\n**Files Requested:** {', '.join(session.requested_files)}"
                    )
                if session.search_queries:
                    result_parts.append(
                        f"\n**Searches Requested:** {'; '.join(session.search_queries)}"
                    )

            result_parts.append(
                f'\n\n---\n*Use session_id: "{session.session_id}" for follow-up questions*'
            )

            return "\n".join(result_parts)

        except Exception as e:
            print(f"[{datetime.now().isoformat()}] Error: {e}", file=sys.stderr)

            error_message = str(e)
            if "RESOURCE_EXHAUSTED" in error_message:
                error_message = "Gemini API quota exceeded. Please try again later."
            elif (
                "UNAUTHENTICATED" in error_message or "API_KEY_INVALID" in error_message
            ):
                error_message = "Gemini API authentication failed. Please check your GEMINI_API_KEY environment variable."
            elif "PERMISSION_DENIED" in error_message:
                error_message = (
                    "Gemini API access denied. Please check your API key permissions."
                )
            elif "INVALID_ARGUMENT" in error_message:
                error_message = "Request too large. Try reducing code context size."
            elif "Gemini API key is required" in error_message:
                error_message = "Gemini API key is required. Please set the GEMINI_API_KEY environment variable."

            return f"Error: {error_message}"

    @mcp.tool()
    async def get_gemini_requests(session_id: str) -> str:
        """Get the files and searches that Gemini has requested in a session.

        Args:
            session_id: The session ID to check
        """
        if session_id not in gemini_server.sessions:
            return f"Session {session_id} not found"

        session = gemini_server.sessions[session_id]

        result_parts = [f"**Session {session_id} Requests:**"]

        if session.requested_files:
            result_parts.append("\n\n**Files Requested:**")
            for file in session.requested_files:
                result_parts.append(f"- {file}")
        else:
            result_parts.append("\n\nNo files requested")

        if session.search_queries:
            result_parts.append("\n\n**Searches Requested:**")
            for query in session.search_queries:
                result_parts.append(f"- {query}")
        else:
            result_parts.append("\n\nNo searches requested")

        return "\n".join(result_parts)

    @mcp.tool()
    async def list_sessions() -> str:
        """List all active Gemini consultation sessions."""
        session_list = []
        for session_id, session in gemini_server.sessions.items():
            session_info = {
                "id": session_id,
                "created": session.created.isoformat(),
                "last_used": session.last_used.isoformat(),
                "message_count": session.message_count,
                "problem_summary": (
                    (session.problem_description[:100] + "...")
                    if session.problem_description
                    else "No description"
                ),
                "file_count": len(session.processed_files),
                "has_code_context": bool(session.code_context),
                "requests": len(session.requested_files) + len(session.search_queries),
            }
            session_list.append(session_info)

        if session_list:
            session_text = "\n\n".join(
                [
                    f"- **{s['id']}**\n  Messages: {s['message_count']}\n  Created: {s['created']}\n  Last used: {s['last_used']}\n  Files attached: {s['file_count']}\n  Code context: {'Yes' if s['has_code_context'] else 'No'}\n  Requests made: {s['requests']}\n  Problem: {s['problem_summary']}"
                    for s in session_list
                ]
            )
            text = f"Active sessions:\n{session_text}"
        else:
            text = "No active sessions"

        return text

    @mcp.tool()
    async def end_session(session_id: str) -> str:
        """End a specific Gemini consultation session to free up memory."""
        if session_id in gemini_server.sessions:
            await gemini_server._cleanup_session_files(session_id)
            del gemini_server.sessions[session_id]
            print(
                f"[{datetime.now().isoformat()}] Session {session_id} ended by user",
                file=sys.stderr,
            )
            return f"Session {session_id} has been ended"
        else:
            return f"Session {session_id} not found or already expired"

    return mcp
