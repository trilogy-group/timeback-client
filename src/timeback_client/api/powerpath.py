"""PowerPath API endpoints for the TimeBack API.

This module provides methods for interacting with PowerPath-specific endpoints
in the TimeBack API, including syllabus access, assessment progress, and question management.
"""

from typing import Dict, Any, Optional, List, Union
import logging
from ..core.client import TimeBackService
from ..models.lesson_plan import LessonPlan

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
        
    def get_course_syllabus(self, course_id: str, filters: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """Get the syllabus for a specific course, with optional filtering.
        
        Args:
            course_id: The unique identifier of the course
            filters: Optional dict of filter parameters to pass as query params
        
        Returns:
            Dict containing the course syllabus content
        
        Raises:
            requests.exceptions.HTTPError: If course not found (404) or other API error
        """
        # If filters are provided, pass them as query params
        if filters:
            return self._make_request(
                endpoint=f"/syllabus/{course_id}",
                method="GET",
                params=filters
            )
        # Default: no filters
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
        
    def get_lesson_plan(self, course_id: str, user_id: str, return_raw: bool = False) -> Union[LessonPlan, Dict[str, Any]]:
        """Get lesson plan for a specific student in a course.
        
        This endpoint returns the customized lesson plan structure for a student,
        including their progress data overlaid on the plan components. Lesson plans
        are automatically created when courses are assigned to students.
        
        Args:
            course_id: The unique identifier of the course
            user_id: The unique identifier of the student/user
            return_raw: If True, return raw dict instead of LessonPlan object
            
        Returns:
            LessonPlan object or dict containing the lesson plan structure with progress data
            
        Raises:
            requests.exceptions.HTTPError: If course/user not found (404) or other API error
            
        Example response:
        {
            "lessonPlan": {
                "lessonPlan": {
                    "course": {
                        "sourcedId": "course-123",
                        "title": "Mathematics Grade 5",
                        "courseCode": "MATH-5",
                        "subjects": ["mathematics"],
                        "grades": ["5"]
                    },
                    "subComponents": [
                        {
                            "sourcedId": "component-1",
                            "title": "Unit 1: Numbers and Operations",
                            "sortOrder": 10,
                            "type": "container",
                            "componentProgress": {
                                "sourcedId": "component-1",
                                "progress": 75,
                                "status": "in_progress",
                                "xp": 150
                            },
                            "subComponents": [
                                {
                                    "sourcedId": "lesson-1",
                                    "title": "Introduction to Fractions",
                                    "sortOrder": 10,
                                    "type": "lesson",
                                    "componentProgress": {
                                        "sourcedId": "lesson-1",
                                        "progress": 100,
                                        "status": "completed",
                                        "xp": 50,
                                        "results": [
                                            {
                                                "score": 85,
                                                "accuracy": 85,
                                                "completedAt": "2024-01-15T10:30:00Z"
                                            }
                                        ]
                                    },
                                    "componentResources": [...]
                                }
                            ]
                        }
                    ],
                    "metadata": {
                        "createdAt": "2024-01-01T00:00:00Z",
                        "lastModified": "2024-01-15T10:30:00Z",
                        "isCustomized": true
                    }
                }
            }
        }
        """
        logger.info(f"Fetching lesson plan for user {user_id} in course {course_id}")
        response = self._make_request(
            endpoint=f"/lessonPlans/{course_id}/{user_id}"
        )
        
        if return_raw:
            return response
            
        # Parse response into LessonPlan object
        return LessonPlan.from_dict(response)
        
    def create_lesson_plan(self, course_id: str, user_id: str, class_id: str) -> Dict[str, Any]:
        """Create a lesson plan for a specific student in a course.
        
        This endpoint creates a new lesson plan for a student when they are assigned
        to a course. The lesson plan is based on the course structure but can be
        customized per student without affecting the base course.
        
        Args:
            course_id: The unique identifier of the course
            user_id: The unique identifier of the student/user
            class_id: The unique identifier of the class
            
        Returns:
            Dict containing the response from the API, typically including
            the created lesson plan ID and status
            
        Raises:
            requests.exceptions.HTTPError: If creation fails or parameters are invalid
            
        Example usage:
            >>> client = TimeBackClient()
            >>> result = client.powerpath.create_lesson_plan(
            ...     course_id="course-123",
            ...     user_id="user-456",
            ...     class_id="class-789"
            ... )
            >>> print(result)
            {
                "success": true,
                "lessonPlanId": "lesson-plan-abc",
                "message": "Lesson plan created successfully"
            }
        """
        logger.info(f"Creating lesson plan for user {user_id} in course {course_id} for class {class_id}")
        
        data = {
            "courseId": course_id,
            "userId": user_id,
            "classId": class_id
        }
        
        return self._make_request(
            endpoint="/lessonPlans/",
            method="POST",
            data=data
        )
        
    def delete_lesson_plan(self, lesson_plan_id: str) -> Dict[str, Any]:
        """Delete a specific lesson plan.
        
        This will permanently remove a student's lesson plan. This is a destructive
        action and should be used with caution. It will also remove associated
        progress data for that lesson plan.
        
        Args:
            lesson_plan_id: The unique identifier of the lesson plan to delete.
            
        Returns:
            Dict containing the response from the API, typically a success message.
            
        Raises:
            requests.exceptions.HTTPError: If deletion fails, e.g., lesson plan not found (404).
        """
        logger.info(f"Deleting lesson plan with ID: {lesson_plan_id}")
        return self._make_request(
            endpoint=f"/lessonPlans/{lesson_plan_id}",
            method="DELETE"
        )
        
    def update_lesson_plan_item(
        self,
        lesson_plan_item_id: str,
        lesson_plan_id: str,
        type: str = "component",
        component_id: Optional[str] = None,
        component_resource_id: Optional[str] = None,
        order: int = 1,
        parent_id: Optional[str] = None,
        skipped: bool = False
    ) -> Dict[str, Any]:
        """Update a specific item within a lesson plan.
        
        This endpoint allows updating individual items (components or resources) within
        a student's lesson plan. You can reorder items, change their parent, or mark
        them as skipped.
        
        Args:
            lesson_plan_item_id: The unique identifier of the lesson plan item to update
            lesson_plan_id: The unique identifier of the lesson plan
            type: The type of item - "component" or "resource" (default: "component")
            component_id: The component ID if type is "component" (mutually exclusive with component_resource_id)
            component_resource_id: The resource ID if type is "resource" (mutually exclusive with component_id)
            order: The sort order of this item within its parent (default: 1)
            parent_id: The ID of the parent item, or None for root level
            skipped: Whether this item should be marked as skipped (default: False)
            
        Returns:
            Dict containing the response from the API
            
        Raises:
            requests.exceptions.HTTPError: If update fails or parameters are invalid
            ValueError: If both component_id and component_resource_id are provided
            
        Example usage:
            >>> client = TimeBackClient()
            >>> # Update a component's order
            >>> result = client.powerpath.update_lesson_plan_item(
            ...     lesson_plan_item_id="item-123",
            ...     lesson_plan_id="plan-456",
            ...     type="component",
            ...     component_id="comp-789",
            ...     order=3
            ... )
            >>> # Mark a resource as skipped
            >>> result = client.powerpath.update_lesson_plan_item(
            ...     lesson_plan_item_id="item-abc",
            ...     lesson_plan_id="plan-456",
            ...     type="resource",
            ...     component_resource_id="res-def",
            ...     skipped=True
            ... )
        """
        # Validate mutually exclusive parameters
        if component_id is not None and component_resource_id is not None:
            raise ValueError("Cannot provide both component_id and component_resource_id")
        
        if type == "component" and component_resource_id is not None:
            raise ValueError("component_resource_id should not be provided when type is 'component'")
            
        if type == "resource" and component_id is not None:
            raise ValueError("component_id should not be provided when type is 'resource'")
        
        logger.info(f"Updating lesson plan item {lesson_plan_item_id} in plan {lesson_plan_id}")
        
        data = {
            "lessonPlanId": lesson_plan_id,
            "type": type,
            "componentId": component_id,
            "componentResourceId": component_resource_id,
            "order": order,
            "parentId": parent_id,
            "skipped": skipped
        }
        
        return self._make_request(
            endpoint=f"/lessonPlans/items/{lesson_plan_item_id}",
            method="PATCH",
            data=data
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
        
    def post_final_student_assessment_response(
        self,
        lesson_id: str,
        student_id: str
    ) -> Dict[str, Any]:
        """Post the final student assessment response for a lesson.
        
        Args:
            lesson_id: The unique identifier of the lesson
            student_id: The unique identifier of the student
        
        Returns:
            Dict containing the response from the API
        """
        logger.info(f"Posting final student assessment response for student {student_id} and lesson {lesson_id}")
        data = {
            "lesson": lesson_id,
            "student": student_id
        }
        return self._make_request(
            endpoint="/finalStudentAssessmentResponse",
            method="POST",
            data=data
        )
        
    def create_new_attempt(self, student_id: str, lesson_id: str) -> Dict[str, Any]:
        """Create a new attempt for a PowerPath100 lesson.
        
        Args:
            student_id: The sourcedId of the student
            lesson_id: The sourcedId of the PowerPath100 lesson
        
        Returns:
            Dict containing the response from the API
        
        FIXME: Confirm the correct endpoint with PowerPath API docs. This is a placeholder.
        """
        data = {
            "student": student_id,
            "lesson": lesson_id
        }
        # FIXME: Replace '/createNewAttempt' with the actual endpoint if different
        return self._make_request(
            endpoint="/createNewAttempt",
            method="POST",
            data=data
        )
        
    def get_test_out_resource(self, course_id: str, student_id: str) -> Dict[str, Any]:
        """Check if a test-out resource is available for a given course and student.
        
        Args:
            course_id: The sourcedId of the course
            student_id: The sourcedId of the student
        
        Returns:
            Dict containing the test-out availability response from PowerPath API
            Example:
            {
                "lessonType": "test-out",
                "lessonId": null,
                "finalized": false,
                "toolProvider": null
            }
        """
        params = {
            "course": course_id,
            "student": student_id
        }
        # Call the /testOut endpoint with course and student as query params
        return self._make_request(
            endpoint="/testOut",
            method="GET",
            params=params
        )

    # Add external test assignment endpoint
    def make_external_test_assignment(
        self,
        student: str,
        lesson: str,
        application_name: str
    ) -> Dict[str, Any]:
        """
        Create an external test assignment for a student in a lesson via an external application.
        Args:
            student: The sourcedId of the student
            lesson: The sourcedId of the component or resource
            application_name: The external tool provider name (e.g. 'edulastic')
        Returns:
            Dict containing testSessionId, url, username, password
        """
        data = {
            "student": student,
            "lesson": lesson,
            "applicationName": application_name
        }
        return self._make_request(
            endpoint="/makeExternalTestAssignment",
            method="POST",
            data=data
        )

    def import_external_test_assignment_results(
        self,
        student: str,
        lesson: str
    ) -> Dict[str, Any]:
        """
        Fetch results for an external test assignment.
        Args:
            student: The sourcedId of the student
            lesson: The sourcedId of the component or resource
        Returns:
            Dict containing assignment results, scores, questions, credentials, etc.
        """
        params = {
            "student": student,
            "lesson": lesson
        }
        return self._make_request(
            endpoint="/importExternalTestAssignmentResults",
            method="GET",
            params=params
        )

    def create_external_test_out(
        self,
        course_id: str,
        lesson_title: str,
        launch_url: str,
        tool_provider: str,
        unit_title: str,
        description: str,
        vendor_id: str,
        xp: int,
        resource_metadata: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Create or update a ComponentResource to act as a TestOut lesson in a course.
        This allows integrating with external test-taking platforms (like Edulastic) for content delivery.
        
        Args:
            course_id: The sourcedId of the Course to create the external test for
            lesson_title: The title of the external test reference
            launch_url: The URL to the external test system (e.g., Edulastic test)
            tool_provider: The type of external service (currently only 'edulastic' supported)
            unit_title: The title of the unit containing the external test
            description: Description of the external test that will be added to the Resource entity's metadata
            vendor_id: The ID of the test in the spreadsheet
            xp: The XP value for the resource
            resource_metadata: Optional additional metadata for the external test resource
            
        Returns:
            Dict containing the response from the API
            
        Raises:
            requests.exceptions.HTTPError: If course not found (404) or other API error
            
        Note:
            The endpoint creates or updates (if they already exist) the following entities:
            - A CourseComponent for the course to hold the TestOut lesson
            - A Resource with a "lessonType" of "TestOut" and the external service details as metadata
            - A ComponentResource acting as the TestOut lesson
        """
        logger.info(f"Creating external test out for course {course_id} with tool provider {tool_provider}")
        
        data = {
            "courseId": course_id,
            "lessonTitle": lesson_title,
            "launchUrl": launch_url,
            "toolProvider": tool_provider,
            "unitTitle": unit_title,
            "description": description,
            "vendorId": vendor_id,
            "xp": xp
        }
        
        # Only include resourceMetadata if provided
        if resource_metadata:
            data["resourceMetadata"] = resource_metadata
            
        return self._make_request(
            endpoint="/createExternalTestOut",
            method="POST",
            data=data
        ) 