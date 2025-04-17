"""QTI Data Models for the TimeBack API.

This module provides data models for QTI (Question and Test Interoperability) 
assessment items and tests based on the QTI 3.0 specification.
"""

from enum import Enum
from typing import List, Dict, Any, Optional, Union
from pydantic import BaseModel, Field, field_serializer
from datetime import datetime

class QTIInteractionType(str, Enum):
    """QTI Interaction Types per QTI 3.0 specification."""
    CHOICE = "choice"
    TEXT_ENTRY = "text-entry"
    EXTENDED_TEXT = "extended-text"
    INLINE_CHOICE = "inline-choice"
    MATCH = "match"
    ORDER = "order"
    ASSOCIATE = "associate"
    HOTSPOT = "hotspot"
    SELECT_POINT = "select-point"
    GRAPHIC_ORDER = "graphic-order"
    GRAPHIC_ASSOCIATE = "graphic-associate"
    GRAPHIC_GAP_MATCH = "graphic-gap-match"
    SLIDER = "slider"
    DRAWING = "drawing"
    MEDIA = "media"
    CUSTOM = "custom"
    UPLOAD = "upload"

class QTICardinalityType(str, Enum):
    """QTI Cardinality Types."""
    SINGLE = "single"
    MULTIPLE = "multiple"
    ORDERED = "ordered"
    RECORD = "record"

class QTIObjectAttributes(BaseModel):
    """QTI Object Attributes for media and graphical interactions."""
    data: str
    height: int
    width: int
    type: str
    mediaType: Optional[str] = None

class QTIChoice(BaseModel):
    """Choice option for choice interactions."""
    identifier: str
    content: str
    feedbackInline: Optional[str] = None
    feedbackOutcomeIdentifier: Optional[str] = None

class QTIQuestionStructure(BaseModel):
    """Structure containing the details of a question."""
    prompt: str
    choices: Optional[List[QTIChoice]] = None
    # Other specific fields for different interaction types can be added

class QTIResponseDeclaration(BaseModel):
    """QTI Response Declaration that defines the expected response.
    
    This model corresponds to the response declaration elements in QTI 3.0.
    The key fields are:
    - identifier: A unique identifier for this response
    - cardinality: The cardinality of the response (single, multiple, ordered, record)
    - baseType: The data type of the response (identifier, boolean, integer, etc.)
    - correctResponse: Optional field defining the correct response
    """
    identifier: str
    cardinality: str  # single, multiple, ordered, record
    baseType: str  # identifier, boolean, integer, float, string, point, pair, directedPair, duration, file, uri, intOrIdentifier
    correctResponse: Optional[Dict[str, List[str]]] = None
    
    @field_serializer('cardinality')
    def serialize_cardinality(self, cardinality: str, _info):
        """Ensure cardinality is lowercase as expected by the API."""
        return cardinality.lower()
        
    @field_serializer('baseType')
    def serialize_base_type(self, baseType: str, _info):
        """Ensure baseType is lowercase as expected by the API."""
        return baseType.lower()

class QTIOutcomeDeclaration(BaseModel):
    """QTI Outcome Declaration for test results."""
    identifier: str
    cardinality: str
    baseType: str
    normalMaximum: Optional[float] = None
    normalMinimum: Optional[float] = None
    defaultValue: Optional[Dict[str, Union[str, int, float]]] = None

class QTIElement(BaseModel):
    """QTI Element for item body content."""
    type: str  # "text" | "interaction" | "math" | "feedback"
    content: str
    identifier: Optional[str] = None
    responseIdentifier: Optional[str] = None

class QTIFeedbackBlock(BaseModel):
    """Feedback block for assessment items."""
    outcomeIdentifier: str
    identifier: str
    showHide: str = "show"
    content: str

class QTIRubric(BaseModel):
    """Rubric for assessment items."""
    use: str
    view: str
    body: str

class QTIInlineFeedback(BaseModel):
    """Inline feedback configuration."""
    outcomeIdentifier: str
    variableIdentifier: str

class QTIResponseProcessing(BaseModel):
    """Response processing for assessment items."""
    templateType: str
    responseDeclarationIdentifier: str
    outcomeIdentifier: str
    correctResponseIdentifier: Optional[str] = None
    incorrectResponseIdentifier: Optional[str] = None
    inlineFeedback: Optional[QTIInlineFeedback] = None

class CatalogEntry(BaseModel):
    """Additional guidance or annotations for stimulus content."""
    id: str = Field(..., description="Unique identifier for the catalog entry")
    support: str = Field(..., description="Type of support provided by this entry")
    content: str = Field(..., description="The actual guidance or annotation content")

class QTIStimulus(BaseModel):
    """QTI 3.0 compliant stimulus that can be referenced by assessment items."""
    
    identifier: str = Field(
        ..., 
        description="Unique identifier for the stimulus"
    )
    title: str = Field(
        ..., 
        description="Title or name of the stimulus"
    )
    language: str = Field(
        ..., 
        description="Language code for the stimulus content"
    )
    content: str = Field(
        ..., 
        description="The actual stimulus content in QTI-compliant format"
    )
    catalog_info: Optional[List[CatalogEntry]] = Field(
        None,
        description="Additional guidance or annotations for this stimulus"
    )
    raw_xml: Optional[str] = Field(
        None,
        description="Raw XML representation of the stimulus"
    )
    created_at: Optional[datetime] = Field(
        None,
        description="Timestamp when the stimulus was created"
    )
    updated_at: Optional[datetime] = Field(
        None,
        description="Timestamp when the stimulus was last updated"
    )
    is_valid_xml: Optional[bool] = Field(
        None,
        description="Whether the stimulus XML is valid according to QTI schema"
    )
    
    class Config:
        """Pydantic model configuration."""
        allow_population_by_field_name = True
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class QTIItemBody(BaseModel):
    """QTI Item Body containing elements."""
    elements: List[QTIElement] = Field(default_factory=list)

class QTIInteraction(BaseModel):
    """QTI Interaction that defines the interaction type and properties.
    
    This model corresponds to the various interaction types defined in the QTI 3.0
    specification and validated by the qtiInteractionSchema in the validation schemas.
    
    Each interaction type has its own set of required and optional properties:
    - choice: requires responseIdentifier, shuffle, maxChoices
    - text-entry: requires responseIdentifier, attributes.expected-length
    - extended-text: requires responseIdentifier
    - inline-choice: requires responseIdentifier
    - order: requires responseIdentifier, shuffle
    - associate: requires responseIdentifier, shuffle
    - match: requires responseIdentifier, shuffle
    - hotspot: requires responseIdentifier, maxChoices
    - select-point: requires responseIdentifier
    - graphic-order: requires responseIdentifier, shuffle
    - graphic-associate: requires responseIdentifier, shuffle, maxAssociations
    - graphic-gap-match: requires responseIdentifier, shuffle
    - upload: requires responseIdentifier
    - slider: requires responseIdentifier, lower-bound, upper-bound
    - drawing: requires responseIdentifier
    - media: requires responseIdentifier, autostart, minPlays
    - custom: requires responseIdentifier
    """
    type: QTIInteractionType
    responseIdentifier: str
    prompt: Optional[str] = None
    shuffle: Optional[bool] = None
    maxChoices: Optional[int] = None
    minChoices: Optional[int] = None
    maxAssociations: Optional[int] = None
    attributes: Optional[Dict[str, Any]] = None
    questionStructure: Optional[Union[QTIQuestionStructure, Dict[str, Any]]] = None
    
    # Graphic/Media interaction properties
    object: Optional[QTIObjectAttributes] = None
    
    # Slider-specific properties
    lower_bound: Optional[float] = Field(None, alias="lower-bound") 
    upper_bound: Optional[float] = Field(None, alias="upper-bound")
    step: Optional[float] = None
    step_label: Optional[bool] = Field(None, alias="step-label")
    orientation: Optional[str] = None  # "horizontal" | "vertical"
    reverse: Optional[bool] = None
    
    # Media-specific properties
    minPlays: Optional[int] = None
    maxPlays: Optional[int] = None
    autostart: Optional[bool] = None
    loop: Optional[bool] = None
    
    # Define model_config for serialization of kebab-case properties
    model_config = {
        "populate_by_name": True,
        "extra": "allow",
    }
    
    def model_post_init(self, __context) -> None:
        """Validate that required properties are present for the interaction type."""
        # This could be extended to validate required properties per interaction type
        if self.type:
            if self.type == QTIInteractionType.CHOICE and self.maxChoices is None:
                self.maxChoices = 1
            
            if self.type in (QTIInteractionType.CHOICE, QTIInteractionType.ORDER, 
                            QTIInteractionType.ASSOCIATE, QTIInteractionType.MATCH) and self.shuffle is None:
                self.shuffle = False

class QTIAssessmentItem(BaseModel):
    """QTI Assessment Item model to match the API expectations.
    
    Based on the example payload of the QTI API. This matches
    the structure expected by the API's POST /api/assessment-items
    endpoint.
    
    The key fields required per the QTI DDL documentation are:
    - identifier: A unique code identifying the item
    - title: The name of the item
    - type: Type of question/interaction
    - interaction: The interaction object based on the type
    - responseDeclarations: Array of response declarations
    
    Note that while rawXml is shown as required in the QTI DDL documentation,
    the API examples and validation schemas indicate that JSON submissions
    are supported without XML.
    """
    identifier: str
    title: str
    type: str
    preInteraction: Optional[str] = None
    postInteraction: Optional[str] = None  # Added based on example for text-entry
    interaction: QTIInteraction
    responseDeclarations: List[QTIResponseDeclaration]
    outcomeDeclarations: Optional[List[QTIOutcomeDeclaration]] = None
    responseProcessing: Optional[QTIResponseProcessing] = None
    feedbackBlock: Optional[List[QTIFeedbackBlock]] = None
    rubrics: Optional[List[QTIRubric]] = None
    stimulus: Optional[QTIStimulus] = None
    metadata: Optional[Dict[str, Any]] = None
    
    # Fields from the interface definition, may not be needed for POST requests
    # but included for completeness
    adaptive: Optional[bool] = None
    timeDependent: Optional[bool] = None
    itemBody: Optional[QTIItemBody] = None
    content: Optional[Any] = None
    rawXml: Optional[str] = None
    qtiVersion: Optional[str] = Field(None, description="Version of QTI standard (default: '3.0')")
    
    @field_serializer('interaction')
    def serialize_interaction(self, interaction: QTIInteraction, _info):
        """Ensure interaction type is properly set if not already."""
        data = interaction.model_dump(by_alias=True)
        if 'type' not in data and hasattr(self, 'type'):
            # If type is missing in interaction but available at item level, use that
            data['type'] = self.type
        return data

class QTIItemRef(BaseModel):
    """QTI Item Reference used in sections."""
    identifier: str
    href: str
    required: Optional[bool] = None
    fixed: Optional[bool] = None
    class_: Optional[List[str]] = Field(None, alias="class")
    category: Optional[List[str]] = None

class QTISection(BaseModel):
    """QTI Section model."""
    identifier: str
    title: str
    visible: bool = True
    required: Optional[bool] = None
    fixed: Optional[bool] = None
    class_: Optional[List[str]] = Field(None, alias="class")
    keep_together: Optional[bool] = Field(None, alias="keep-together")
    sequence: Optional[int] = None
    qti_assessment_item_ref: Optional[List[QTIItemRef]] = Field(None, alias="qti-assessment-item-ref")

class QTITestPart(BaseModel):
    """QTI Test Part model."""
    identifier: str
    navigationMode: str = "linear"  # "linear" | "nonlinear"
    submissionMode: str = "individual"  # "individual" | "simultaneous"
    qti_assessment_section: List[QTISection] = Field(alias="qti-assessment-section")

class QTIAssessmentTest(BaseModel):
    """QTI Assessment Test model."""
    identifier: str
    title: str
    toolVersion: Optional[str] = None
    toolName: Optional[str] = None
    qti_test_part: List[QTITestPart] = Field(alias="qti-test-part")
    qti_outcome_declaration: Optional[List[QTIOutcomeDeclaration]] = Field(None, alias="qti-outcome-declaration") 