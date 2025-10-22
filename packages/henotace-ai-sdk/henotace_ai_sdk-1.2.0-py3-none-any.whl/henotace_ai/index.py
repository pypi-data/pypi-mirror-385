"""
Henotace AI SDK for Python
Official Python SDK for the Henotace AI API
"""

import requests
import json
import time
from typing import Dict, List, Optional, Any, Union
from datetime import datetime

from .types import (
    SDKConfig, HenotaceError, HenotaceAPIError, HenotaceNetworkError,
    SessionStudent, SessionTutor, SessionChat, SessionSubject, ApiResponse,
    StorageConnector, Logger, LogLevel
)
from .logger import create_logger


class HenotaceAI:
    """
    Main client for interacting with the Henotace AI API
    """
    
    def __init__(self, api_key: str, base_url: str = "https://api.djtconcept.ng", 
                 timeout: int = 30, retries: int = 3, storage: Optional[StorageConnector] = None,
                 default_persona: Optional[str] = None, default_preset: str = "tutor_default",
                 default_user_profile: Optional[Dict[str, Any]] = None,
                 default_metadata: Optional[Dict[str, Any]] = None,
                 logging: Optional[Dict[str, Any]] = None):
        """
        Initialize the Henotace AI client
        
        Args:
            api_key: Your Henotace API key
            base_url: Base URL for the API (default: https://api.djtconcept.ng)
            timeout: Request timeout in seconds
            retries: Number of retries for failed requests
            storage: Optional storage connector
            default_persona: Default persona for all tutors
            default_preset: Default AI preset
            default_user_profile: Default user profile
            default_metadata: Default metadata
            logging: Logging configuration
        """
        self.api_key = api_key
        self.base_url = base_url.rstrip('/')
        self.timeout = timeout
        self.retries = retries
        self.storage = storage
        
        # Default configuration
        self.default_persona = default_persona or "You are a helpful and patient tutor. Give short, concise, and easy-to-understand explanations by default. Only provide detailed or lengthy explanations when the user specifically asks for more information, more detail, or a longer explanation. Start simple and build up complexity only when requested."
        self.default_preset = default_preset
        self.default_user_profile = default_user_profile
        self.default_metadata = default_metadata
        
        # Initialize logger
        logging_config = logging or {}
        log_level = logging_config.get('level', LogLevel.INFO)
        log_enabled = logging_config.get('enabled', True)
        self.logger = logging_config.get('logger') or create_logger(log_level, log_enabled)
        
        self.logger.info('Initializing Henotace AI SDK', {
            'baseUrl': self.base_url,
            'timeout': self.timeout,
            'retries': self.retries,
            'logLevel': log_level,
            'logEnabled': log_enabled
        })
        
        self.session = requests.Session()
        self.session.headers.update({
            'Content-Type': 'application/json',
            'Authorization': f'Bearer {self.api_key}',
            'User-Agent': 'henotace-python-sdk/1.2.0'
        })

    def _make_request(self, method: str, endpoint: str, **kwargs) -> requests.Response:
        """
        Make an HTTP request with retry logic and error handling
        
        Args:
            method: HTTP method (GET, POST, etc.)
            endpoint: API endpoint
            **kwargs: Additional request parameters
            
        Returns:
            requests.Response object
            
        Raises:
            HenotaceNetworkError: For network-related errors
            HenotaceAPIError: For API-specific errors
        """
        url = f"{self.base_url}{endpoint}"
        
        for attempt in range(self.retries + 1):
            try:
                self.logger.debug('HTTP Request', {
                    'method': method.upper(),
                    'url': endpoint,
                    'headers': dict(self.session.headers)
                })
                
                response = self.session.request(
                    method=method,
                    url=url,
                    timeout=self.timeout,
                    **kwargs
                )
                
                self.logger.debug('HTTP Response', {
                    'status': response.status_code,
                    'statusText': response.reason,
                    'url': endpoint
                })
                
                # Handle rate limiting
                if response.status_code == 429:
                    retry_after = int(response.headers.get('retry-after', 60))
                    self.logger.warn('Rate limit exceeded', {'retryAfter': retry_after})
                    time.sleep(retry_after)
                    continue
                
                # Handle server errors with retry
                if response.status_code >= 500 and attempt < self.retries:
                    wait_time = 2 ** attempt
                    self.logger.warn('Server error - retrying request', {
                        'attempt': attempt + 1,
                        'maxRetries': self.retries,
                        'status': response.status_code
                    })
                    time.sleep(wait_time)
                    continue
                
                return response
                
            except requests.exceptions.RequestException as e:
                if attempt < self.retries:
                    wait_time = 2 ** attempt
                    self.logger.warn('Network error - retrying request', {
                        'attempt': attempt + 1,
                        'maxRetries': self.retries,
                        'error': str(e)
                    })
                    time.sleep(wait_time)
                    continue
                else:
                    raise HenotaceNetworkError(f"Network error: {str(e)}")

    def _handle_response(self, response: requests.Response) -> Dict[str, Any]:
        """
        Handle API response and raise appropriate errors
        
        Args:
            response: requests.Response object
            
        Returns:
            Parsed response data
            
        Raises:
            HenotaceAPIError: For API-specific errors
        """
        try:
            data = response.json()
        except json.JSONDecodeError:
            raise HenotaceAPIError(f"Invalid JSON response: {response.text}")
        
        if response.status_code == 401:
            raise HenotaceAPIError("Invalid API key. Please check your credentials.")
        elif response.status_code == 429:
            raise HenotaceAPIError("Rate limit exceeded. Please try again later.")
        elif response.status_code >= 400:
            error_msg = data.get('error', f'HTTP {response.status_code} error')
            raise HenotaceAPIError(f"API error: {error_msg}")
        
        return data

    def get_status(self) -> Dict[str, Any]:
        """
        Check API status
        
        Returns:
            Status response data
        """
        try:
            self.logger.debug('Checking API status')
            response = self._make_request('GET', '/api/external/status/')
            data = self._handle_response(response)
            self.logger.info('API status check successful', data)
            return data
        except requests.exceptions.RequestException as e:
            if 'Network Error' in str(e):
                raise HenotaceNetworkError(f"Network Error: {str(e)}")
            raise

    def get_status_ok(self) -> bool:
        """
        Check if API is available (convenience method)
        
        Returns:
            True if API is available, False otherwise
        """
        try:
            status = self.get_status()
            return status.get('success', False) and status.get('data', {}).get('status') in ['ok', 'operational']
        except:
            return False

    def _detect_verbosity(self, input_text: str) -> str:
        """
        Auto-detect verbosity level from user input
        
        Args:
            input_text: User's input message
            
        Returns:
            Verbosity level: 'brief', 'normal', 'detailed', or 'comprehensive'
        """
        input_lower = input_text.lower()
        
        # Keywords that indicate different verbosity levels
        brief_keywords = [
            'brief', 'short', 'quick', 'simple', 'concise', 'summary', 
            'just', 'only', 'basics', 'main points', 'key points'
        ]
        
        detailed_keywords = [
            'detailed', 'comprehensive', 'thorough', 'complete', 'full', 
            'explain more', 'more information', 'elaborate', 'expand',
            'in depth', 'deep dive', 'everything about', 'all about'
        ]
        
        comprehensive_keywords = [
            'comprehensive', 'complete', 'everything', 'all details',
            'step by step', 'from scratch', 'beginner to advanced',
            'full explanation', 'comprehensive guide'
        ]
        
        # Check for comprehensive keywords first (most specific)
        if any(keyword in input_lower for keyword in comprehensive_keywords):
            return 'comprehensive'
        
        # Check for detailed keywords
        if any(keyword in input_lower for keyword in detailed_keywords):
            return 'detailed'
        
        # Check for brief keywords
        if any(keyword in input_lower for keyword in brief_keywords):
            return 'brief'
        
        # Default to normal verbosity
        return 'normal'

    def complete_chat(self, history: List[Dict[str, str]], input_text: str, 
                     preset: str = None, subject: str = None, topic: str = None, 
                     verbosity: str = None, author_name: str = None, language: str = None,
                     personality: str = None, teaching_style: str = None, 
                     branding: Dict[str, Any] = None) -> Dict[str, str]:
        """
        Send a chat completion request to the API
        
        Args:
            history: List of conversation history messages
            input_text: User's input message
            preset: AI behavior preset (default: 'tutor_default')
            subject: Subject for the conversation (default: 'general')
            topic: Topic for the conversation (default: 'general')
            verbosity: Response verbosity level ('brief', 'normal', 'detailed', 'comprehensive')
            author_name: Author name for personalization
            language: Response language (default: 'en')
            personality: AI personality ('friendly', 'professional', 'encouraging', 'direct')
            teaching_style: Teaching approach ('socratic', 'direct', 'problem-based')
            branding: Custom branding information
            
        Returns:
            Dictionary containing the AI response
        """
        if preset is None:
            preset = self.default_preset
        
        # Convert history to the format expected by the API (matching Node.js SDK)
        chat_history = []
        for msg in history:
            if isinstance(msg, dict):
                if 'role' in msg and 'content' in msg:
                    # Convert from {role: 'user'|'assistant', content: '...'} format
                    sender = 'student' if msg['role'] == 'user' else 'tutor'
                    chat_history.append({
                        'sender': sender,
                        'message': msg['content']
                    })
                elif 'sender' in msg and 'message' in msg:
                    # Already in correct format
                    chat_history.append(msg)
                else:
                    # Fallback for other formats
                    chat_history.append({
                        'sender': 'student',
                        'message': str(msg)
                    })
            else:
                # Fallback for non-dict messages
                chat_history.append({
                    'sender': 'student',
                    'message': str(msg)
                })
        
        # Auto-detect verbosity from user input if not specified
        if verbosity is None:
            verbosity = self._detect_verbosity(input_text)
        
        # For now, include verbosity in the preset to work with current backend
        if verbosity != 'normal':
            preset = f"{preset}_verbosity_{verbosity}"
        
        payload = {
            'history': chat_history,
            'input': input_text,
            'subject': subject or 'general',
            'topic': topic or 'general',
            'preset': preset,
            # New customization parameters
            'author_name': author_name,
            'language': language or 'en',
            'personality': personality or 'friendly',
            'teaching_style': teaching_style or 'socratic',
            'branding': branding or {}
        }
        
        try:
            self.logger.debug('Starting chat completion', {
                'inputLength': len(input_text),
                'historyLength': len(history),
                'preset': preset
            })
            
            response = self._make_request(
                'POST', 
                '/api/external/working/chat/completion/',
                json=payload
            )
            data = self._handle_response(response)
            ai_response = data.get('data', {}).get('ai_response', '')
            
            self.logger.debug('Chat completion successful', {
                'responseLength': len(ai_response)
            })
            
            return {'ai_response': ai_response}
        except requests.exceptions.RequestException as e:
            self.logger.error('Chat completion failed', {
                'input': input_text,
                'error': str(e)
            })
            raise

    def chat_completion(self, history: List[Dict[str, str]], input_text: str, 
                       subject: str = None, topic: str = None, preset: str = None,
                       author_name: str = None, language: str = None,
                       personality: str = None, teaching_style: str = None, 
                       branding: Dict[str, Any] = None) -> Dict[str, str]:
        """
        Enhanced chat completion with customization parameters
        
        Args:
            history: List of conversation history messages
            input_text: User's input message
            subject: Subject for the conversation (default: 'general')
            topic: Topic for the conversation (default: 'general')
            preset: AI behavior preset (default: 'tutor_default')
            author_name: Author name for personalization
            language: Response language (default: 'en')
            personality: AI personality ('friendly', 'professional', 'encouraging', 'direct')
            teaching_style: Teaching approach ('socratic', 'direct', 'problem-based')
            branding: Custom branding information
            
        Returns:
            Dictionary containing the AI response
        """
        self.logger.debug('Enhanced chat completion', {
            'inputLength': len(input_text),
            'historyLength': len(history),
            'subject': subject,
            'topic': topic,
            'author_name': author_name,
            'language': language,
            'personality': personality,
            'teaching_style': teaching_style,
            'hasBranding': bool(branding)
        })
        
        return self.complete_chat(
            history=history,
            input_text=input_text,
            subject=subject,
            topic=topic,
            preset=preset,
            author_name=author_name,
            language=language,
            personality=personality,
            teaching_style=teaching_style,
            branding=branding
        )

    def generate_classwork(self, history: List[Dict[str, str]], subject: str = None, 
                          topic: str = None, question_count: int = 5, 
                          difficulty: str = 'medium') -> Dict[str, Any]:
        """
        Generate classwork questions based on conversation history
        
        Args:
            history: List of conversation history messages
            subject: Subject for the classwork (default: 'general')
            topic: Topic for the classwork (default: 'general')
            question_count: Number of questions to generate (default: 5)
            difficulty: Difficulty level ('easy', 'medium', 'hard') (default: 'medium')
            
        Returns:
            Dictionary containing the generated classwork
        """
        # Convert history to the format expected by the API
        chat_history = []
        for msg in history:
            if isinstance(msg, dict):
                if 'role' in msg and 'content' in msg:
                    # Convert from {role: 'user'|'assistant', content: '...'} format
                    sender = 'student' if msg['role'] == 'user' else 'tutor'
                    chat_history.append({
                        'sender': sender,
                        'message': msg['content']
                    })
                elif 'sender' in msg and 'message' in msg:
                    # Already in correct format
                    chat_history.append(msg)
                else:
                    # Fallback for other formats
                    chat_history.append({
                        'sender': 'student',
                        'message': str(msg)
                    })
            else:
                # Fallback for non-dict messages
                chat_history.append({
                    'sender': 'student',
                    'message': str(msg)
                })
        
        payload = {
            'history': chat_history,
            'input': f'Generate {question_count} {difficulty} difficulty questions about {topic or "the topic we discussed"}',
            'subject': subject or 'general',
            'topic': topic or 'general',
            'preset': 'tutor_default',
            'generate_classwork': True,
            'question_count': question_count,
            'difficulty': difficulty
        }
        
        try:
            self.logger.debug('Starting classwork generation', {
                'historyLength': len(history),
                'questionCount': question_count,
                'difficulty': difficulty,
                'subject': subject,
                'topic': topic
            })
            
            response = self._make_request(
                'POST', 
                '/api/external/working/chat/completion/',
                json=payload
            )
            data = self._handle_response(response)
            
            # Parse classwork response
            ai_response = data.get('data', {}).get('ai_response', '')
            
            # Try to parse as JSON if it's a classwork response
            try:
                classwork_data = json.loads(ai_response)
                if isinstance(classwork_data, dict) and 'questions' in classwork_data:
                    self.logger.info('Classwork generation successful', {
                        'questionCount': len(classwork_data.get('questions', [])),
                        'difficulty': difficulty
                    })
                    return classwork_data
            except json.JSONDecodeError:
                pass
            
            # Fallback: return as text response
            self.logger.info('Classwork generation successful (text format)', {
                'responseLength': len(ai_response)
            })
            
            return {
                'questions': [{'question': ai_response, 'type': 'text'}],
                'metadata': {
                    'question_count': question_count,
                    'difficulty': difficulty,
                    'subject': subject,
                    'topic': topic,
                    'format': 'text'
                }
            }
            
        except requests.exceptions.RequestException as e:
            self.logger.error('Classwork generation failed', {
                'historyLength': len(history),
                'questionCount': question_count,
                'difficulty': difficulty,
                'error': str(e)
            })
            raise

    # Storage convenience passthroughs
    def list_students(self) -> List[SessionStudent]:
        """List all students"""
        if not self.storage:
            return []
        return self.storage.list_students()
    
    def upsert_student(self, student: SessionStudent) -> None:
        """Create or update a student"""
        if not self.storage:
            return
        return self.storage.upsert_student(student)
    
    def delete_student(self, student_id: str) -> None:
        """Delete a student"""
        if not self.storage:
            return
        return self.storage.delete_student(student_id)
    
    def list_tutors(self, student_id: str) -> List[SessionTutor]:
        """List tutors for a student"""
        if not self.storage:
            return []
        return self.storage.list_tutors(student_id)
    
    def upsert_tutor(self, student_id: str, tutor: SessionTutor) -> None:
        """Create or update a tutor"""
        if not self.storage:
            return
        return self.storage.upsert_tutor(student_id, tutor)
    
    def delete_tutor(self, student_id: str, tutor_id: str) -> None:
        """Delete a tutor"""
        if not self.storage:
            return
        return self.storage.delete_tutor(student_id, tutor_id)
    
    def list_chats(self, student_id: str, tutor_id: str) -> List[SessionChat]:
        """List chats for a tutor"""
        if not self.storage:
            return []
        return self.storage.list_chats(student_id, tutor_id)

    def set_base_url(self, url: str) -> None:
        """Set a custom base URL (useful for testing)"""
        self.base_url = url.rstrip('/')

    def get_config(self) -> Dict[str, Any]:
        """Get the current configuration"""
        return {
            'api_key': self.api_key,
            'base_url': self.base_url,
            'timeout': self.timeout,
            'retries': self.retries,
            'default_persona': self.default_persona,
            'default_preset': self.default_preset,
            'default_user_profile': self.default_user_profile,
            'default_metadata': self.default_metadata
        }

    def get_logger(self) -> Logger:
        """Get the logger instance"""
        return self.logger
