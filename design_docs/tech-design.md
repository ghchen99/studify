# AI Learning Platform - Technical Design Document

## Technology Stack

- **Frontend**: Next.js (React)
- **Backend**: Azure Functions (Python FastAPI)
- **Database**: Azure Cosmos DB (NoSQL)
- **Storage**: Azure Blob Storage
- **AI**: Azure OpenAI Service
- **Cache**: Azure Cache for Redis
- **Gateway**: Azure API Management
- **Auth**: Azure AD B2C

---

## Architecture

```
Next.js Frontend
       ↓
Azure API Management
       ↓
Azure Functions (FastAPI)
  ├── Lesson Plans Service
  ├── Lessons Service
  ├── Quiz Service
  ├── AI Tutor Service
  └── Progress Service
       ↓
  ┌────┴────┐
  ↓         ↓
Cosmos DB   Blob Storage
  ↓
Redis Cache
```

---

## Database Schema (Cosmos DB)

### Container: Users
**Partition Key**: `userId`

```json
{
  "id": "user_uuid",
  "userId": "user_uuid",
  "type": "user",
  "email": "student@example.com",
  "name": "John Doe",
  "profile": {
    "level": "GCSE",
    "subjects": ["Biology", "Chemistry"],
    "learningStyle": "visual",
    "studyGoals": {
      "hoursPerWeek": 10,
      "examDates": {
        "Biology": "2025-06-15"
      }
    }
  },
  "createdAt": "2025-01-15T10:00:00Z"
}
```

### Container: LessonPlans
**Partition Key**: `userId`

```json
{
  "id": "plan_uuid",
  "userId": "user_uuid",
  "type": "lessonPlan",
  "subject": "Biology",
  "topic": "Cell Biology",
  "status": "approved",
  "structure": [
    {
      "subtopicId": "subtopic_1",
      "title": "Cell Structure",
      "order": 1,
      "estimatedDuration": 15,
      "concepts": ["Prokaryotic cells", "Eukaryotic cells"]
    }
  ],
  "aiGeneratedAt": "2025-01-15T10:00:00Z",
  "approvedAt": "2025-01-15T10:30:00Z"
}
```

### Container: Lessons
**Partition Key**: `userId`

```json
{
  "id": "lesson_uuid",
  "userId": "user_uuid",
  "type": "lesson",
  "lessonPlanId": "plan_uuid",
  "subtopicId": "subtopic_1",
  "subject": "Biology",
  "topic": "Cell Biology",
  "subtopic": "Cell Structure",
  "content": {
    "introduction": "Cells are the basic building blocks...",
    "sections": [
      {
        "sectionId": "section_1",
        "title": "Prokaryotic Cells",
        "content": "Prokaryotic cells are simple...",
        "expanded": null,
        "diagrams": ["blob://diagrams/prokaryote.png"]
      }
    ],
    "summary": "Key points: prokaryotic vs eukaryotic...",
    "keyTerms": ["nucleus", "mitochondria"]
  },
  "mediaAssets": [
    {
      "type": "diagram",
      "url": "blob://diagrams/cell_structure.png",
      "caption": "Comparison of cell types"
    }
  ],
  "status": "completed",
  "completedAt": "2025-01-16T14:00:00Z"
}
```

### Container: Quizzes
**Partition Key**: `userId`

```json
{
  "id": "quiz_uuid",
  "userId": "user_uuid",
  "type": "quiz",
  "lessonId": "lesson_uuid",
  "subtopicId": "subtopic_1",
  "questions": [
    {
      "questionId": "q1",
      "type": "multiple_choice",
      "question": "What is the powerhouse of the cell?",
      "options": ["Nucleus", "Mitochondria", "Ribosome", "Golgi Body"],
      "correctAnswer": "Mitochondria",
      "explanation": "Mitochondria produce ATP.",
      "difficulty": "easy"
    },
    {
      "questionId": "q2",
      "type": "short_answer",
      "question": "Describe the function of the cell membrane.",
      "markScheme": ["Controls entry/exit", "Semi-permeable"],
      "difficulty": "medium"
    },
    {
      "questionId": "q3",
      "type": "long_answer",
      "question": "Compare prokaryotic and eukaryotic cells.",
      "markScheme": [
        "Prokaryotes lack nucleus",
        "Eukaryotes have organelles",
        "Size difference"
      ],
      "difficulty": "hard"
    }
  ],
  "createdAt": "2025-01-16T14:30:00Z"
}
```

### Container: QuizAttempts
**Partition Key**: `userId`

```json
{
  "id": "attempt_uuid",
  "userId": "user_uuid",
  "type": "quizAttempt",
  "quizId": "quiz_uuid",
  "lessonId": "lesson_uuid",
  "subtopicId": "subtopic_1",
  "responses": [
    {
      "questionId": "q1",
      "userAnswer": "Mitochondria",
      "isCorrect": true,
      "timeSpent": 5
    },
    {
      "questionId": "q2",
      "userAnswer": "Controls what goes in and out",
      "aiGeneratedAnswer": "The cell membrane controls entry/exit...",
      "marksAwarded": 2,
      "maxMarks": 3,
      "feedback": "Good, but mention semi-permeable nature."
    },
    {
      "questionId": "q3",
      "userBulletPoints": ["No nucleus in prokaryotes", "Eukaryotes bigger"],
      "aiGeneratedAnswer": "Prokaryotic cells lack a nucleus while eukaryotic...",
      "marksAwarded": 3,
      "maxMarks": 6,
      "feedback": "Cover organelles for full marks."
    }
  ],
  "score": {
    "correct": 1,
    "total": 3,
    "percentage": 33.33,
    "marksAwarded": 5,
    "maxMarks": 9
  },
  "completedAt": "2025-01-16T15:00:00Z"
}
```

### Container: TutorSessions
**Partition Key**: `userId`

```json
{
  "id": "session_uuid",
  "userId": "user_uuid",
  "type": "tutorSession",
  "trigger": "quiz_struggle",
  "context": {
    "lessonId": "lesson_uuid",
    "subtopicId": "subtopic_1",
    "questionId": "q2",
    "concept": "Cell membrane function"
  },
  "conversation": [
    {
      "role": "user",
      "content": "I don't understand semi-permeable",
      "timestamp": "2025-01-16T15:05:00Z"
    },
    {
      "role": "assistant",
      "content": "Semi-permeable means...",
      "timestamp": "2025-01-16T15:05:15Z",
      "mediaAssets": ["blob://diagrams/semipermeable.png"]
    }
  ],
  "resolved": true,
  "createdAt": "2025-01-16T15:05:00Z"
}
```

### Container: Progress
**Partition Key**: `userId`

```json
{
  "id": "progress_uuid",
  "userId": "user_uuid",
  "type": "progress",
  "lessonPlanId": "plan_uuid",
  "subtopicProgress": {
    "subtopic_1": {
      "status": "completed",
      "lessonCompleted": true,
      "quizAttempts": 2,
      "bestScore": 66.67,
      "averageScore": 50.0,
      "masteryLevel": "intermediate",
      "weakConcepts": ["Semi-permeable membrane"],
      "lastAttemptAt": "2025-01-16T15:00:00Z"
    },
    "subtopic_2": {
      "status": "not_started"
    }
  },
  "overallProgress": {
    "totalSubtopics": 2,
    "completedSubtopics": 1,
    "percentComplete": 50.0,
    "totalStudyTime": 45,
    "averageScore": 50.0
  },
  "updatedAt": "2025-01-16T15:00:00Z"
}
```

---

## API Endpoints

### Lesson Plans Service

#### `POST /api/lessonplans/generate`
Generate a lesson plan.

**Request:**
```json
{
  "userId": "user_uuid",
  "subject": "Biology",
  "topic": "Cell Biology",
  "preferences": {
    "detailLevel": "detailed",
    "duration": "medium"
  }
}
```

**Response:**
```json
{
  "lessonPlanId": "plan_uuid",
  "subject": "Biology",
  "topic": "Cell Biology",
  "structure": [...],
  "status": "draft"
}
```

#### `PUT /api/lessonplans/{planId}`
Update/approve a lesson plan.

**Request:**
```json
{
  "userId": "user_uuid",
  "structure": [...],
  "status": "approved"
}
```

#### `GET /api/lessonplans/{planId}`
Retrieve a lesson plan.

---

### Lessons Service

#### `POST /api/lessons/generate`
Generate a lesson for a subtopic.

**Request:**
```json
{
  "userId": "user_uuid",
  "lessonPlanId": "plan_uuid",
  "subtopicId": "subtopic_1"
}
```

**Response:**
```json
{
  "lessonId": "lesson_uuid",
  "content": {
    "introduction": "...",
    "sections": [...],
    "summary": "...",
    "keyTerms": [...]
  },
  "mediaAssets": [...]
}
```

#### `POST /api/lessons/{lessonId}/expand`
Expand a specific section.

**Request:**
```json
{
  "userId": "user_uuid",
  "sectionId": "section_1"
}
```

**Response:**
```json
{
  "sectionId": "section_1",
  "expandedContent": "...",
  "additionalDiagrams": [...]
}
```

#### `PUT /api/lessons/{lessonId}/complete`
Mark lesson as completed.

---

### Quiz Service

#### `POST /api/quizzes/generate`
Generate a quiz.

**Request:**
```json
{
  "userId": "user_uuid",
  "lessonId": "lesson_uuid",
  "subtopicId": "subtopic_1",
  "questionTypes": ["multiple_choice", "short_answer", "long_answer"],
  "difficulty": "mixed",
  "count": 5
}
```

#### `POST /api/quizzes/{quizId}/submit`
Submit quiz answers.

**Request:**
```json
{
  "userId": "user_uuid",
  "responses": [
    {
      "questionId": "q1",
      "userAnswer": "Mitochondria"
    },
    {
      "questionId": "q3",
      "userBulletPoints": ["No nucleus", "Eukaryotes bigger"]
    }
  ]
}
```

**Response:**
```json
{
  "attemptId": "attempt_uuid",
  "responses": [
    {
      "questionId": "q1",
      "isCorrect": true,
      "feedback": "Correct!"
    },
    {
      "questionId": "q3",
      "aiGeneratedAnswer": "Full answer generated from bullets...",
      "marksAwarded": 3,
      "maxMarks": 6,
      "feedback": "Cover DNA structure for full marks."
    }
  ],
  "score": {
    "percentage": 50.0,
    "marksAwarded": 5,
    "maxMarks": 9
  },
  "triggerTutor": true,
  "weakConcepts": [...]
}
```

---

### AI Tutor Service

#### `POST /api/tutor/sessions`
Start a tutor session.

**Request:**
```json
{
  "userId": "user_uuid",
  "trigger": "quiz_struggle",
  "context": {
    "lessonId": "lesson_uuid",
    "questionId": "q2",
    "concept": "Cell membrane function"
  }
}
```

**Response:**
```json
{
  "sessionId": "session_uuid",
  "message": "Let's break down 'semi-permeable'...",
  "mediaAssets": [...],
  "suggestions": [
    "Would you like a diagram?",
    "Should we try a simpler example?"
  ]
}
```

#### `POST /api/tutor/sessions/{sessionId}/message`
Send message in session.

**Request:**
```json
{
  "userId": "user_uuid",
  "message": "Can you explain with an example?"
}
```

---

### Progress Service

#### `GET /api/progress/{userId}`
Get overall progress.

**Response:**
```json
{
  "userId": "user_uuid",
  "lessonPlans": [
    {
      "lessonPlanId": "plan_uuid",
      "subject": "Biology",
      "overallProgress": {
        "percentComplete": 50.0,
        "averageScore": 50.0
      }
    }
  ]
}
```

#### `GET /api/progress/{userId}/lessonplans/{planId}`
Get detailed progress for a lesson plan.

#### `POST /api/progress/update`
Update progress (internal trigger).

---

## Data Flows

### 1. Lesson Plan Creation
```
User → Generate → OpenAI → Save Draft → User Reviews → Approve → Initialize Progress
```

### 2. Lesson with Expansion
```
User → Generate Lesson → OpenAI + Blob Storage → Save
User → Expand Section → OpenAI → Update Lesson
```

### 3. Quiz with Tutor Trigger
```
User → Submit Quiz → AI Grades → Save Attempt → Update Progress
         ↓
  Score < 40% OR 3+ similar mistakes?
         ↓
  Trigger Tutor → User Accepts → Start Session → AI Tutor
```

---

## Caching Strategy (Redis)

```python
# Cache keys and TTLs
"lessonplan:{plan_id}" → 1 hour
"lesson:{lesson_id}" → 1 hour
"quiz:{quiz_id}" → 30 minutes
"progress:{user_id}" → 5 minutes

# Invalidation
- Lesson plan update → Clear plan cache
- Quiz submission → Clear progress cache
- Lesson expansion → Clear lesson cache
```

---

## Code Structure

```
backend/
├── shared/
│   ├── cosmos_client.py      # Cosmos DB operations
│   ├── openai_client.py      # Azure OpenAI wrapper
│   ├── redis_client.py       # Redis caching
│   └── models.py             # Pydantic models
├── lesson_plans/
│   └── __init__.py           # Generate, get, update
├── lessons/
│   └── __init__.py           # Generate, expand, complete
├── quizzes/
│   └── __init__.py           # Generate, submit
├── tutor/
│   └── __init__.py           # Sessions, messages
├── progress/
│   └── __init__.py           # Get, update
└── requirements.txt
```

### Sample: Cosmos Client

```python
from azure.cosmos import CosmosClient
import os

class CosmosService:
    def __init__(self):
        self.client = CosmosClient(
            os.getenv('COSMOS_ENDPOINT'),
            os.getenv('COSMOS_KEY')
        )
        self.db = self.client.get_database_client('learning-platform-db')
    
    async def create_item(self, container: str, item: dict):
        return self.db.get_container_client(container).create_item(item)
    
    async def get_item(self, container: str, id: str, partition_key: str):
        return self.db.get_container_client(container).read_item(
            item=id, 
            partition_key=partition_key
        )
    
    async def query_items(self, container: str, query: str, partition_key: str):
        return list(self.db.get_container_client(container).query_items(
            query=query,
            partition_key=partition_key
        ))
```

### Sample: OpenAI Client

```python
from openai import AzureOpenAI
import os

class OpenAIService:
    def __init__(self):
        self.client = AzureOpenAI(
            azure_endpoint=os.getenv('OPENAI_ENDPOINT'),
            api_key=os.getenv('OPENAI_KEY'),
            api_version="2024-02-15-preview"
        )
    
    async def generate_lesson_plan(self, subject: str, topic: str):
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are an educational expert."},
                {"role": "user", "content": f"Generate lesson plan for {subject} - {topic}"}
            ],
            response_format={"type": "json_object"}
        )
        return response.choices[0].message.content
    
    async def grade_answer(self, question: str, mark_scheme: list, answer: str):
        # AI grading logic
        pass
```

---

## Infrastructure (Bicep)

### Key Resources

```bicep
// Cosmos DB
resource cosmosAccount 'Microsoft.DocumentDB/databaseAccounts@2023-04-15' = {
  name: 'cosmos-learning-platform'
  location: 'ukwest'
  properties: {
    databaseAccountOfferType: 'Standard'
    consistencyPolicy: {
      defaultConsistencyLevel: 'Session'
    }
  }
}

// Containers
var containers = [
  'users', 'lessonPlans', 'lessons', 
  'quizzes', 'quizAttempts', 'tutorSessions', 'progress'
]

// Function App (Consumption)
resource functionApp 'Microsoft.Web/sites@2022-09-01' = {
  name: 'func-learning-platform'
  kind: 'functionapp,linux'
  properties: {
    serverFarmId: appServicePlan.id
    siteConfig: {
      linuxFxVersion: 'Python|3.11'
      appSettings: [
        { name: 'COSMOS_ENDPOINT', value: cosmosAccount.properties.documentEndpoint }
        { name: 'COSMOS_KEY', value: cosmosAccount.listKeys().primaryMasterKey }
        { name: 'OPENAI_ENDPOINT', value: openAI.properties.endpoint }
        { name: 'OPENAI_KEY', value: openAI.listKeys().key1 }
      ]
    }
  }
}

// Storage Account
resource storageAccount 'Microsoft.Storage/storageAccounts@2023-01-01' = {
  name: 'stlearningplatform'
  sku: { name: 'Standard_LRS' }
  kind: 'StorageV2'
}

// Azure OpenAI
resource openAI 'Microsoft.CognitiveServices/accounts@2023-05-01' = {
  name: 'openai-learning-platform'
  location: 'uksouth'
  sku: { name: 'S0' }
  kind: 'OpenAI'
}

// Redis Cache
resource redis 'Microsoft.Cache/redis@2023-08-01' = {
  name: 'redis-learning-platform'
  properties: {
    sku: { name: 'Basic', family: 'C', capacity: 0 }
  }
}

// API Management
resource apim 'Microsoft.ApiManagement/service@2023-05-01-preview' = {
  name: 'apim-learning-platform'
  sku: { name: 'Consumption', capacity: 0 }
}
```

---

## Security

- **Auth**: Azure AD B2C with JWT validation
- **API Management**: Rate limiting (100 req/min), CORS, JWT validation
- **RBAC**: Managed identities for service-to-service auth
- **Secrets**: Key Vault for API keys and connection strings

---

## Monitoring

- **Application Insights**: API performance, errors, dependencies
- **Cosmos DB Metrics**: RU consumption, latency, throttling
- **Custom Metrics**: Quiz completion rates, tutor trigger frequency, average scores
- **Alerts**: High error rates, RU throttling, slow API responses