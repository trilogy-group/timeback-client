"""PowerPath API endpoints for the TimeBack API.

This module provides methods for interacting with PowerPath-specific endpoints
in the TimeBack API, including syllabus access, assessment progress, and question management.
"""

from typing import Dict, Any, Optional, List
import logging
from ..core.client import TimeBackService

# Set up logger
logger = logging.getLogger(__name__)

class PowerPathAPI(TimeBackService):
    """API client for PowerPath-specific endpoints."""
    
    def __init__(self, base_url: str, client_id: Optional[str] = None, client_secret: Optional[str] = None):
        """Initialize the PowerPath API client.
        
        Args:
            base_url: The base URL of the TimeBack API
            client_id: OAuth2 client ID for authentication
            client_secret: OAuth2 client secret for authentication
        """
        super().__init__(base_url, "powerpath", client_id, client_secret)
        # Override the api_path since PowerPath doesn't use OneRoster path
        self.api_path = "/powerpath"
        
    def get_course_syllabus(self, course_id: str) -> Dict[str, Any]:
        """Get the syllabus for a specific course.
        
        Args:
            course_id: The unique identifier of the course
            
        Returns:
            Dict containing the course syllabus content
            
        Raises:
            requests.exceptions.HTTPError: If course not found (404) or other API error
        """
        return self._make_request(
            endpoint=f"/syllabus/{course_id}"
        )
        
    def get_student_course_progress(self, course_id: str, student_id: str) -> Dict[str, Any]:
        """Get a student's progress in a specific course.
        
        Args:
            course_id: The unique identifier of the course
            student_id: The unique identifier of the student
            
        Returns:
            Dict containing the student's progress data for all components in the course
            
        Raises:
            requests.exceptions.HTTPError: If course/student not found (404) or other API error
            
        Example response:
        {
            "components": [
                {
                    "id": "component-1",
                    "progress": 75,
                    "status": "in_progress",
                    "results": [
                        {
                            "id": "result-1",
                            "score": 0.8,
                            "completed": true
                        }
                    ]
                }
            ]
        }
        """
        logger.info(f"Fetching course progress for student {student_id} in course {course_id}")
        return self._make_request(
            endpoint=f"/lessonPlans/getCourseProgress/{course_id}/student/{student_id}"
        )
        
    def get_assessment_progress(
        self,
        student_id: str,
        lesson_id: str,
        attempt: Optional[str] = None
    ) -> Dict[str, Any]:
        """Get the progress a student has made in a PowerPath100 lesson.
        
        Args:
            student_id: The sourcedId of the student
            lesson_id: The sourcedId of the CourseComponent representing the PowerPath100 lesson
            attempt: Optional attempt number of the lesson
            
        Returns:
            Dict containing:
            - score: Current PowerPath100 score
            - seenQuestions: List of questions seen with their details
            - remainingQuestionsPerDifficulty: Count of remaining questions by difficulty
        """
        # Create params dictionary to send as URL query parameters
        params = {
            "student": student_id,
            "lesson": lesson_id
        }
        
        if attempt:
            params["attempt"] = attempt
            
        return self._make_request(
            endpoint="/getAssessmentProgress",
            method="GET",
            params=params  # Send as URL query parameters
        )
        
    def get_next_question(
        self,
        student_id: str,
        lesson_id: str,
        ignore_answered_questions: bool = False,
        ignore_difficulty_check: bool = False
    ) -> Dict[str, Any]:
        """Get the next question in a PowerPath100 lesson.
        
        Args:
            student_id: The sourcedId of the student
            lesson_id: The sourcedId of the CourseComponent representing the PowerPath100 lesson
            ignore_answered_questions: Whether to allow repeated questions
            ignore_difficulty_check: Whether to ignore difficulty progression
            
        Returns:
            Dict containing:
            - score: Current PowerPath100 score
            - question: Details of the next question
        """
        # Create params dictionary to send as URL query parameters
        params = {
            "student": student_id,
            "lesson": lesson_id
        }
        
        # Add optional parameters
        if ignore_answered_questions:
            params["ignoreAnsweredQuestions"] = "true"
        if ignore_difficulty_check:
            params["ignoreDifficultyCheck"] = "true"
        
        return self._make_request(
            endpoint="/getNextQuestion",
            method="GET",
            params=params  # Send as URL query parameters
        )
        
    def reset_attempt(self, student_id: str, lesson_id: str) -> Dict[str, Any]:
        """Reset a student's attempt at a PowerPath100 lesson.
        
        This removes all previous responses and resets the score to 0.
        
        Args:
            student_id: The sourcedId of the student
            lesson_id: The sourcedId of the CourseComponent representing the PowerPath100 lesson
            
        Returns:
            Dict containing:
            - success: Whether the reset was successful
            - score: The reset score (always 0)
        """
        data = {
            "student": student_id,
            "lesson": lesson_id
        }
        
        return self._make_request(
            endpoint="/resetAttempt",
            method="POST",
            data=data
        )
        
    def update_student_question_response(
        self,
        student_id: str,
        question_id: str,
        response: str | List[str],
        lesson_id: str
    ) -> Dict[str, Any]:
        """Update a student's response to a question and get the updated PowerPath score.
        
        Args:
            student_id: The sourcedId of the student
            question_id: The sourcedId of the ComponentResource representing the question
            response: The student's response (string or list of strings for multiple choice)
            lesson_id: The sourcedId of the Component representing the PowerPath100 lesson
            
        Returns:
            Dict containing:
            - powerpathScore: Updated PowerPath100 score
            - responseResult: Details about the response processing
            - questionResult: Assessment result for debugging
            - quizResult: Assessment result for debugging
        """
        data = {
            "student": student_id,
            "question": question_id,
            "response": response,
            "lesson": lesson_id
        }
        
        return self._make_request(
            endpoint="/updateStudentQuestionResponse",
            method="PUT",
            data=data
        )
        
    def update_student_item_response(
        self,
        student_id: str,
        result: Dict[str, Any],
        component_id: Optional[str] = None,
        component_resource_id: Optional[str] = None
    ) -> Dict[str, Any]:
        """Update a student's response to a specific item in a course component.
        
        Args:
            student_id: The unique identifier of the student
            result: Dict containing the result data with the following structure:
                - status: Status of the result (e.g., "active")
                - metadata: Additional metadata (optional)
                - score: Numeric score (optional)
                - textScore: Text representation of score (optional)
                - scoreDate: Date when score was recorded
                - scorePercentile: Percentile score (optional)
                - scoreStatus: Status of the score (e.g., "exempt", "completed")
                - comment: Optional comment
                - learningObjectiveSet: List of learning objectives with scores
                - inProgress: Whether item is in progress (optional)
                - incomplete: Whether item is incomplete (optional)
                - late: Whether item is late (optional)
                - missing: Whether item is missing (optional)
            component_id: The unique identifier of the course component (mutually exclusive with component_resource_id)
            component_resource_id: The unique identifier of the component resource (mutually exclusive with component_id)
            
        Returns:
            Dict containing the response from the API
            
        Raises:
            requests.exceptions.HTTPError: If student/component not found (404) or other API error
            ValueError: If neither or both component_id and component_resource_id are provided
        """
        if not component_id and not component_resource_id:
            raise ValueError("Either component_id or component_resource_id must be provided")
            
        if component_id and component_resource_id:
            raise ValueError("Cannot provide both component_id and component_resource_id")
            
        logger.info(f"Updating item response for student {student_id}")
        if component_id:
            logger.info(f"Using component_id: {component_id}")
        else:
            logger.info(f"Using component_resource_id: {component_resource_id}")
        
        data = {
            "studentId": student_id,
            **({"componentId": component_id} if component_id else {"componentResourceId": component_resource_id}),
            "result": result
        }
        
        return self._make_request(
            endpoint="/lessonPlans/updateStudentItemResponse",
            method="POST",
            data=data
        ) 