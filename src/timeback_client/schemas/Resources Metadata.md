# Resources Metadata

### 

Here’s a breakdown of the metadata fields we recommend using when creating resources. Adding good metadata makes your content easier to organize, search, and align with learning objectives.

Start with the **Common Metadata** section—these fields apply to all types of resources. Then, depending on the type of content you’re working with (like a QTI question, video, or document), check out the more specific fields for that type.

You can also add your own custom fields if you need to store anything extra. The goal is to make your resources as useful and reusable as possible\!

### 

## Common Metadata

| Name | Description | Example |
| :---- | :---- | :---- |
| type | Resource type identifier (qti-question, text, video, etc.) | “qti”, “text”, “audio”', “video”, “interactive”, “visual”,  “course-material” |
| subject | Academic subject area (Math, Biology, etc.) | "Language" |
| grades | Array or range of grade levels (\[1,2,3\]) | \[5\] |
| learningObjectiveSet | A list of learning objectives that the resource is aligned to, grouped by source or standard framework (e.g., CASE, local district standards). Each group includes one or more objective identifiers. | "learningObjectiveSet": \[   {     "source": "CASE",     "learningObjectiveResults": \[       { "learningObjectiveId": "3fa85f64-5717-4562-b3fc-2c963f66afa6" },       { "learningObjectiveId": "fc6a7e3d-9a9f-4ef4-a3c6-dfa3b2c78cba" }     \]   } \] |
| xp | Experience points if it will be used for a game | 10 |
| url | The direct URL where the resource file or content is stored and can be accessed or downloaded | "https://cdn.example.com/resources/math-1" |
| language | Language of the content, using standard IETF BCP 47 codes. | "en-US", "pt-BR" |
| keywords | Array of topic-related tags or important terms covered by the content. Helps with search and classification. | \["algebra", "linear equations"\] |

## QTI

| Name | Description | Example |
| :---- | :---- | :---- |
| type | Resource type identifier (qti-question, text, video, etc.) | "qti" |
| subType | More specific classification of the QTI resource. | "qti-question", "qti-test", "qti-test-bank" |
| questionType | Defines the format or interaction style of the question, as defined in QTI (IMS). | “'choice”, “order”,  “associate”, “match”, “'hotspot”  “select-point”,  “graphic-order”,  “graphic-associate”,  “graphic-gap-match”,  “text-entry”,  “extended-text”,  'inline-choice”,  “upload”,  “slider”,  “drawing”,  “media”, “custom”  |
| difficulty | Indicates the perceived difficulty level of the question. | "easy", "medium", "hard" |
| subject | Academic subject area (Math, Biology, etc.) | "Chemistry" |
| grades | Array or range of grade levels (\[1,2,3\]) | \[1,2\] |
| language | Language of the content, using standard IETF BCP 47 codes. | "en-US", "pt-BR" |
| url | The direct URL where the resource file or content is stored and can be accessed or downloaded | "https://cdn.example.com/resources/math-1" |
| learningObjectiveSet | A list of learning objectives that the resource is aligned to, grouped by source or standard framework (e.g., CASE, local district standards). Each group includes one or more objective identifiers. | "learningObjectiveSet": \[   {     "source": "CASE",     "learningObjectiveResults": \[       { "learningObjectiveId": "3fa85f64-5717-4562-b3fc-2c963f66afa6" },       { "learningObjectiveId": "fc6a7e3d-9a9f-4ef4-a3c6-dfa3b2c78cba" }     \]   } \] |
| xp | Experience gained when completing the QTI item | 10 |

## Textual

| Name | Description | Example |
| :---- | :---- | :---- |
| type | Resource type identifier (qti-question, text, video, etc.) | text |
| format | The file or content format of the resource. | "pdf", "epub", "docx", "html" |
| author | Name of the person or organization that created or wrote the content. | "John Smith", "Oxford Press"  |
| language | Language of the content using IETF BCP 47 codes. | "en-US", "pt-BR" |
| pageCount | Number of pages (if applicable), typically for PDFs, eBooks, or other paginated documents. | 10 |
| subject | Academic subject area (Math, Biology, etc.) | “Mathematics” |
| grades | Array or range of grade levels (\[1,2,3\]) | \[5\] |
| keywords | Array of topic-related tags or important terms covered by the content. Helps with search and classification. | \["algebra", "linear equations"\] |
| url | The direct URL where the resource file or content is stored and can be accessed or downloaded | "https://cdn.example.com/resources/algebra-2.pdf" |
| learningObjectiveSet | A list of learning objectives that the resource is aligned to, grouped by source or standard framework (e.g., CASE, local district standards). Each group includes one or more objective identifiers. | "learningObjectiveSet": \[   {     "source": "CASE",     "learningObjectiveResults": \[       { "learningObjectiveId": "3fa85f64-5717-4562-b3fc-2c963f66afa6" },       { "learningObjectiveId": "fc6a7e3d-9a9f-4ef4-a3c6-dfa3b2c78cba" }     \]   } \] |

## Audio

| Name | Description | Example |
| :---- | :---- | :---- |
| type | Resource type identifier (qti-question, text, video, etc.) | audio |
| duration | Length of the audio file. HH:MM:SS  | "00:03:03.45" |
| format | The file or content format of the resource. | "mp3", “wav” |
| speaker | Name of the speaker, narrator, or person delivering the content. | "Prof. Jane Doe" |
| language | Language of the content using IETF BCP 47 codes. | "en-US", "pt-BR" |
| subject | Academic subject area (Math, Biology, etc.) | “History” |
| grades | Array or range of grade levels (\[1,2,3\]) | \[1\] |
| keywords | Tags or relevant topics covered in the audio, useful for filtering and search. | \["lecture", "cold war"\] |
| url | The direct URL where the resource file or content is stored and can be accessed or downloaded | "https://cdn.example.com/resources/us-history.mp3" |
| learningObjectiveSet | A list of learning objectives that the resource is aligned to, grouped by source or standard framework (e.g., CASE, local district standards). Each group includes one or more objective identifiers. | "learningObjectiveSet": \[   {     "source": "CASE",     "learningObjectiveResults": \[       { "learningObjectiveId": "3fa85f64-5717-4562-b3fc-2c963f66afa6" },       { "learningObjectiveId": "fc6a7e3d-9a9f-4ef4-a3c6-dfa3b2c78cba" }     \]   } \] |

## Video

| Name | Description | Example |
| :---- | :---- | :---- |
| type | Resource type identifier (qti-question, text, video, etc.) | video |
| duration | Length of the audio file. HH:MM:SS  | "00:03:03.45" |
| captionsAvailable | Indicates whether the video includes closed captions or subtitles for accessibility. | true, false |
| format | The file or content format of the resource. | “mp4”, “webm”, “mov” |
| language | Language of the content using IETF BCP 47 codes. | "en-US", "pt-BR" |
| grades | Array or range of grade levels (\[1,2,3\]) | \[3,4\] |
| subject | Academic subject area (Math, Biology, etc.) | "History’ |
| url | The direct URL where the resource file or content is stored and can be accessed or downloaded | "https://cdn.example.com/resources/us-history.mp4" |
| learningObjectiveSet | A list of learning objectives that the resource is aligned to, grouped by source or standard framework (e.g., CASE, local district standards). Each group includes one or more objective identifiers. | "learningObjectiveSet": \[   {     "source": "CASE",     "learningObjectiveResults": \[       { "learningObjectiveId": "3fa85f64-5717-4562-b3fc-2c963f66afa6" },       { "learningObjectiveId": "fc6a7e3d-9a9f-4ef4-a3c6-dfa3b2c78cba" }     \]   } \] |

## Interactive

| Name | Description | Example |
| :---- | :---- | :---- |
| type | Resource type identifier (qti-question, text, video, etc.) | interactive |
| launchUrl | The URL used to launch the interactive tool, often via LTI or similar protocol. | https://tool.example.com/lti/launch, |
| toolProvider | Name of the external tool provider or platform delivering the content. | "Testing Tool", "Desmos", "Khan Academy" |
| instructionalMethod | Teaching method or pedagogy supported by the resource. | "exploratory", "direct-instruction" |
| grades | Array or range of grade levels (\[1,2,3\]) | \[4\] |
| subject | Academic subject area (Math, Biology, etc.) | “Biology” |
| language | Language of the content using IETF BCP 47 codes. | "en-US", "pt-BR" |
| url | The direct URL where the resource file or content is stored and can be accessed or downloaded | \- |
| learningObjectiveSet | A list of learning objectives that the resource is aligned to, grouped by source or standard framework (e.g., CASE, local district standards). Each group includes one or more objective identifiers. | "learningObjectiveSet": \[   {     "source": "CASE",     "learningObjectiveResults": \[       { "learningObjectiveId": "3fa85f64-5717-4562-b3fc-2c963f66afa6" },       { "learningObjectiveId": "fc6a7e3d-9a9f-4ef4-a3c6-dfa3b2c78cba" }     \]   } \] |

## Visuals

| Name | Description | Example |
| :---- | :---- | :---- |
| type | Resource type identifier (qti-question, text, video, etc.) | visual |
| format | The file format or image type of the visual. | "png", "jpeg", "svg", "pdf" |
| resolution | Dimensions of the visual in pixels. | "1920x1080" |
| subject | Academic subject area (Math, Biology, etc.) | Biology |
| grades | Array or range of grade levels (\[1,2,3\]) | \[2\] |
| language | Language of the content using IETF BCP 47 codes. | "en-US", "pt-BR" |
| url | The direct URL where the resource file or content is stored and can be accessed or downloaded | "https://cdn.example.com/resources/body.png" |
| learningObjectiveSet | A list of learning objectives that the resource is aligned to, grouped by source or standard framework (e.g., CASE, local district standards). Each group includes one or more objective identifiers. | "learningObjectiveSet": \[   {     "source": "CASE",     "learningObjectiveResults": \[       { "learningObjectiveId": "3fa85f64-5717-4562-b3fc-2c963f66afa6" },       { "learningObjectiveId": "fc6a7e3d-9a9f-4ef4-a3c6-dfa3b2c78cba" }     \]   } \] |

## Course Material

| Name | Description | Example |
| :---- | :---- | :---- |
| type | Resource type identifier (qti-question, text, video, etc.) | course-material |
| subType | A more specific classification for the course material based on its purpose. | "unit", "course", "resource-collection" |
| author | Name of the person or organization who created the material. | "Jane Doe", "State Education Board" |
| format | The file format or packaging type of the resource. | "docx", "pdf", "cc" (Common Cartridge) |
| subject | Academic subject area (Math, Biology, etc.) | English Language |
| grades | Array or range of grade levels (\[1,2,3\]) | \[5\] |
| instructionalMethod | Teaching method or pedagogy supported by the resource. | "direct-instruction", "project-based" |
| keywords | Tags or key concepts addressed in the material. | \["reading comprehension", "structure"\] |
| language | Language of the content using IETF BCP 47 codes. | "en-US", "pt-BR" |
| url | The direct URL where the resource file or content is stored and can be accessed or downloaded | "https://cdn.example.com/resources/lesson-plan-5.pdf" |
| learningObjectiveSet | A list of learning objectives that the resource is aligned to, grouped by source or standard framework (e.g., CASE, local district standards). Each group includes one or more objective identifiers. | "learningObjectiveSet": \[   {     "source": "CASE",     "learningObjectiveResults": \[       { "learningObjectiveId": "3fa85f64-5717-4562-b3fc-2c963f66afa6" },       { "learningObjectiveId": "fc6a7e3d-9a9f-4ef4-a3c6-dfa3b2c78cba" }     \]   } \] |

