# **Developer API Guide \- MasteryTrack**

[Thiago De Sa](mailto:thiago@reachbeyond.ai) [Guilherme Colombo](mailto:guilherme@reachbeyond.ai)

## **Table of Contents**

1. System Overview  
2. Getting Started  
3. Authentication  
4. API Endpoints  
   * Authorizer API  
   * Inventory Search API  
   * Delivery Assign API  
   * Invalidate Assignment API  
5. Complete Workflow Example  
6. Error Handling  
7. Additional Information

---

## **System Overview**

The MasteryTrack API provides three core endpoints for managing educational test assignments:

| Endpoint | Purpose | Authentication Required |
| ----- | ----- | ----- |
| **Authorizer** | User authentication and session token generation | API Key |
| **Inventory Search** | Search and filter available tests | JWT Token |
| **Delivery Assign** | Assign tests to students | JWT Token |

### **Key Features**

* **Secure Authentication**: Token-based authentication with 1-hour expiration  
* **Flexible Search**: Filter tests by name, grade, subject, or timeback\_id  
* **Assignment Management**: Assign supported tests to students with duplicate prevention  
* **Comprehensive Error Handling**: Detailed error codes and messages

---

## **Getting Started**

### **Prerequisites**

Before using the API, you need:

1. **Registered User Email** with API access  
   * Contact: Thiago or Gui  
2. **API Key** for authentication  
   * Contact: Thiago or Gui

### **Base URLs**

All API endpoints use the following base URL:

```
https://l407b3xadi.execute-api.us-east-1.amazonaws.com/prod
```

### **Important Notes**

⚠️ **Token Expiration**: JWT tokens expire in **1 hour** (3600 seconds)

⚠️ **Supported Tests Only**: Only tests marked as "supported" can be assigned to students

⚠️ **Duplicate Prevention**: Active assignments prevent reassignment of the same test to the same student

---

## **Authentication**

### **Authentication Flow**

1. **Obtain JWT Token**: Use the Authorizer endpoint with your API key and registered email  
2. **Include in Headers**: Add the JWT token to the `X-Auth-Token` header for all subsequent requests  
3. **Token Refresh**: Refresh tokens before they expire (recommended after 50 minutes)

### **Required Headers for All Authenticated Requests**

```
X-Auth-Token: Bearer {your-jwt-token}
Content-Type: application/json
```

---

## **API Endpoints**

## **Authorizer API**

### **Endpoint Information**

| Method | URL | Purpose |
| ----- | ----- | ----- |
| POST | `/authorizer` | Authenticate users and provide session tokens |

### **Request Details**

**Required Headers:**

```
x-api-key: {your-api-key}
Content-Type: application/json
```

**Request Body:**

```json
{
  "email": "your-registered-email@example.com"
}
```

### **cURL Example**

```shell
curl -X POST "https://l407b3xadi.execute-api.us-east-1.amazonaws.com/prod/authorizer" \
  -H "Content-Type: application/json" \
  -H "x-api-key: YOUR_API_KEY" \
  -d '{
    "email": "your-registered-email@example.com"
  }'
```

### **Response Examples**

#### **✅ Success Response (200 OK)**

```json
{
  "success": true,
  "jwt": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9..."
}
```

#### **❌ Error Responses**

**401 Unauthorized \- Invalid API Key**

```json
{
  "success": false,
  "error": "Invalid API key",
  "code": "UNAUTHORIZED"
}
```

**403 Forbidden \- User Not Found or No API Access**

```json
{
  "success": false,
  "error": "User not found or does not have API access",
  "code": "ACCESS_DENIED"
}
```

**400 Bad Request \- Missing Email**

```json
{
  "success": false,
  "error": "Email is required",
  "code": "MISSING_PARAMETER"
}
```

**500 Internal Server Error**

```json
{
  "success": false,
  "error": "Internal server error",
  "code": "INTERNAL_ERROR"
}
```

---

## **Inventory Search API**

### **Endpoint Information**

| Method | URL | Purpose |
| ----- | ----- | ----- |
| GET | `/authoring/inventory/search` | Search for available tests in the inventory |

### **Query Parameters**

| Parameter | Type | Required | Description |
| ----- | ----- | ----- | ----- |
| `name` | String | No | Filter by test name (case-insensitive) |
| `timeback_id` | String | No | Filter by specific timeback ID |
| `grade` | String | No | Filter by grade level (case-insensitive) |
| `subject` | String | No | Filter by subject (case-insensitive) |
| `all` | Boolean | No | Include non-supported tests (default: false) |

### **cURL Examples**

#### **Basic Search (Supported Tests Only)**

```shell
curl -X GET "https://l407b3xadi.execute-api.us-east-1.amazonaws.com/prod/authoring/inventory/search" \
  -H "X-Auth-Token: Bearer YOUR_JWT_FROM_AUTHORIZER" \
  -H "Content-Type: application/json"
```

#### **Search with Multiple Parameters**

```shell
curl -X GET "https://l407b3xadi.execute-api.us-east-1.amazonaws.com/prod/authoring/inventory/search?name=Alpha%20Standardized%20Math%20G3.1&grade=Third%20grade&subject=math" \
  -H "X-Auth-Token: Bearer YOUR_JWT_FROM_AUTHORIZER" \
  -H "Content-Type: application/json"
```

#### **Search by Timeback ID**

```shell
curl -X GET "https://l407b3xadi.execute-api.us-east-1.amazonaws.com/prod/authoring/inventory/search?timeback_id=_677e37c49e904cafcc66fdb4" \
  -H "X-Auth-Token: Bearer YOUR_JWT_FROM_AUTHORIZER" \
  -H "Content-Type: application/json"
```

#### **Search All Tests (Including Non-Supported)**

```shell
curl -X GET "https://l407b3xadi.execute-api.us-east-1.amazonaws.com/prod/authoring/inventory/search?all=true" \
  -H "X-Auth-Token: Bearer YOUR_JWT_FROM_AUTHORIZER" \
  -H "Content-Type: application/json"
```

### **Response Examples**

#### **✅ Success Response (200 OK)**

```json
{
  "success": true,
  "data": [
    {
      "id": 1,
      "timeback_id": "_677e37c49e904cafcc66fdb4",
      "name": "Alpha Standardized Math G3.1",
      "subject": "Math",
      "grade": "Third Grade",
      "grade_rank": 3,
      "version": 1,
      "active": true,
      "metadata": {
        "url": "https://masterytrack.ai/tests/_677e37c49e904cafcc66fdb4",
        "type": "qti",
        "subType": "qti-test",
        "year": "2025",
        "format": "digital",
        "questionTypes": ["choice", "text-entry"]
      },
      "supported": true,
      "created_at": "2024-01-16T12:00:00Z",
      "updated_at": "2024-01-16T12:00:00Z",
      "invalidated_on": null
    }
  ]
}
```

#### **❌ Error Responses**

**401 Unauthorized \- Invalid JWT**

```json
{
  "success": false,
  "error": "Invalid or expired JWT",
  "code": "UNAUTHORIZED"
}
```

**400 Bad Request \- Invalid Parameters**

```json
{
  "success": false,
  "error": "Invalid search parameters",
  "code": "INVALID_PARAMETERS",
  "details": {
    "grade": "Invalid grade format"
  }
}
```

### **Search Behavior**

* **Default**: Returns only tests marked as "supported"  
* **All Tests**: Use `all=true` to include non-supported tests  
* **Sorting**: Results ordered by subject, grade\_rank, name, and version (descending)  
* **Support Status**: Computed based on whether all question types are supported by the player

---

## **Delivery Assign API**

### **Endpoint Information**

| Method | URL | Purpose |
| ----- | ----- | ----- |
| POST | `/delivery/assignments/assign` | Assign a test to a specific student |

### **Request Details**

**Required Headers:**

```
X-Auth-Token: Bearer {jwt-from-authorizer}
Content-Type: application/json
```

**Request Body:**

```json
{
  "student_email": "student@example.com",
  "timeback_id": "_677e37c49e904cafcc66fdb4", <- Optional
  "subject": "Math", <- Optional
  "grade_rank": 3, <- Optional
  "assessment_line_item_sourced_id": "5af7dacd-11d2-4c1a-93f5-4g6f887ac0f1", <- Optional
  "assessment_result_sourced_id": "3478f4c9-5ujh-49bd-a951-906156d87569" <- Optional
}
```

`v1. (student_email + timeback_id) -> Assigns the specific test to the student`  
`v2. (student_email + subject) -> Attempts to trigger the placement flow for the student/subject`  
`v3. (student_email + timeback_id + assessment_line_item_sourced_id + assessment_result_sourced_id)`  
 `↳ Assigns the specific test to the student and writes the result back to the items sent`  
`v4. (student_email + subject + grade_rank)`  
 `↳ Assigns the first test not yet taken by the student for the grade/subject`  
`v5. (student_email + subject + grade_rank + assessment_line_item_sourced_id + assessment_result_sourced_id)`  
 `↳ Assigns the first test not yet taken by the student for the grade/subject and writes the result back to the items sent`

### **cURL Example**

```shell
curl -X POST "https://l407b3xadi.execute-api.us-east-1.amazonaws.com/prod/delivery/assignments/assign" \
  -H "X-Auth-Token: Bearer YOUR_JWT_FROM_AUTHORIZER" \
  -H "Content-Type: application/json" \
  -d '{
    "student_email": "student@example.com",
    "timeback_id": "_677e37c49e904cafcc66fdb4"
  }'
```

### **Response Examples**

#### **✅ Success Response (201 Created)**

```json
{
  "success": true,
  "platform": "Mastery Track"
  "data": {
    "assignment": {
      "id": 123,
      "student_email": "student@example.com",
      "test_name": "Math Assessment Grade 3",
      "assigned_by": 2,
      "test_url": "https://masterytrack.ai/assignment/123",
      "status": "ASSIGNED",
      "expires_at": "2024-02-15T12:00:00Z",
      "metadata": {
        "url": "https://masterytrack.ai/tests/_677e37c49e904cafcc66fdb4",
        "type": "qti",
        "subType": "qti-test",
        "year": "2025",
        "grade": "Third Grade",
        "state": "TX",
        "format": "digital"
      },
      "created_at": "2024-01-16T12:00:00Z"
    },
    "message": "Test successfully assigned to student@example.com"
  }
}
```

### **Important Note**

⚠️ **test\_url** is the deep link that should be added to the student's Dash.   
If the student is logged in, it will take them directly to the test. If they are not logged in, it will take them to the login page and then to the test after login  
⚠️ **Student** The student must exist in Timeback. If the user exists in Timeback but not in MasteryTrack, this api will automatically create the user in MasteryTrack.  
If the student is logged in, it will take them directly to the test. If they are not logged in, it will take them to the login page and then to the test after login

#### **❌ Error Responses**

**401 Unauthorized \- Invalid JWT**

```json
{
  "success": false,
  "error": "Invalid or expired JWT",
  "code": "UNAUTHORIZED"
}
```

**400 Bad Request \- Missing Parameters**

```json
{
  "success": false,
  "error": "student_email is required",
  "code": "MISSING_PARAMETER"
}
```

**404 Not Found \- Student Not Found**

```json
{
  "success": false,
  "error": "User with email student@example.com not found",
  "code": "USER_NOT_FOUND"
}
```

**404 Not Found \- Test Not Found**

```json
{
  "success": false,
  "error": "Test not found with timeback_id: _677e37c49e904cafcc66fdb4",
  "code": "TEST_NOT_FOUND"
}
```

**422 Unprocessable Entity \- Test Not Supported**

```json
{
  "success": false,
  "error": "The requested test is not yet supported by the system",
  "code": "TEST_NOT_SUPPORTED"
}
```

**409 Conflict \- Assignment Already Exists**

```json
{
  "success": false,
  "error": "Assignment already exists",
  "code": "ASSIGNMENT_EXISTS",
  "data": {
    "existing_assignment": {
      "id": 123,
      "student_email": "student@example.com",
      "test_name": "Math Assessment Grade 3",
      "status": "IN_PROGRESS",
      "test_url": "https://masterytrack.ai/assignment/123"
    }
  }
}
```

### **Assignment Rules**

* **Supported Tests Only**: Only tests marked as "supported" can be assigned  
* **Expiration**: Assignments expire 30 days after creation by default  
* **Duplicate Prevention**: Active assignments (ASSIGNED, IN\_PROGRESS, PAUSED) prevent reassignment  
* **Reassignment**: Completed or abandoned assignments can be reassigned to the same student

---

## **Complete Workflow Example**

### **Step 1: Authenticate and Get Session Token**

```shell
# Request JWT token
curl -X POST "https://l407b3xadi.execute-api.us-east-1.amazonaws.com/prod/authorizer" \
  -H "Content-Type: application/json" \
  -H "x-api-key: YOUR_API_KEY" \
  -d '{
    "email": "your-registered-email@example.com"
  }'

# Expected Response:
# {"success":true,"jwt":"eyJhbGciOiJS...."}
```

### **Step 2: Search for Available Tests**

```shell
# Search for math tests for grade 3
curl -X GET "https://l407b3xadi.execute-api.us-east-1.amazonaws.com/prod/authoring/inventory/search?name=math&grade=3" \
  -H "X-Auth-Token: Bearer YOUR_JWT_FROM_STEP_1" \
  -H "Content-Type: application/json"

# Response includes available tests with their timeback_ids
```

### **Step 3: Assign Test to Student**

```shell
# Assign selected test to student
curl -X POST "https://l407b3xadi.execute-api.us-east-1.amazonaws.com/prod/delivery/assignments/assign" \
  -H "X-Auth-Token: Bearer YOUR_JWT_FROM_STEP_1" \
  -H "Content-Type: application/json" \
  -d '{
    "student_email": "student@example.com",
    "timeback_id": "_677e37c49e904cafcc66fdb4"
  }'

# Response includes assignment details and test URL
```

---

## **Invalidate Assignment API**

### **Endpoint Information**

| Method | URL | Purpose |
| ----- | ----- | ----- |
| POST | `/delivery/assignments/invalidate` | Invalidate a student's test assignment |

### **Request Details**

**Required Headers:**

```
X-Auth-Token: Bearer {jwt-from-authorizer}
Content-Type: application/json
```

**Request Body:**

```json
{
  "student_email": "student@example.com",
  "assignment_id": 123, //<- Optional
  "timeback_id": "_677e37c49e904cafcc66fdb4", //<- Optional
  "subject": "Math", //<- Optional
  "grade_rank": 3 //<- Optional
}
```

* **Invalidation Scenarios:**  
  * (student\_email \+ assignment\_id) \-\> *Invalidates a specific assignment by its ID.*  
  * (student\_email \+ timeback\_id) \-\> *Invalidates all active assignments for a specific test and student.*  
  * (student\_email \+ subject \+ grade\_rank) \-\> *Invalidates the active assignment for a specific subject and grade for a student, if one exists.*

**cURL Examples**

**Invalidate by Assignment ID**

```shell
curl -X POST "https://l407b3xadi.execute-api.us-east-1.amazonaws.com/prod/delivery/assignments/invalidate" \\
  -H "X-Auth-Token: Bearer YOUR_JWT_FROM_AUTHORIZER" \\
  -H "Content-Type: application/json" \\
  -d '{
    "student_email": "student@example.com",
    "assignment_id": 123
  }'
```

**Invalidate by Timeback ID**

```shell
curl -X POST "https://l407b3xadi.execute-api.us-east-1.amazonaws.com/prod/delivery/assignments/invalidate" \\
  -H "X-Auth-Token: Bearer YOUR_JWT_FROM_AUTHORIZER" \\
  -H "Content-Type: application/json" \\
  -d '{
    "student_email": "student@example.com",
    "timeback_id": "_677e37c49e904cafcc66fdb4"
  }'
```

**Invalidate by Subject and Grade**

```shell
curl -X POST "https://l407b3xadi.execute-api.us-east-1.amazonaws.com/prod/delivery/assignments/invalidate" \\
  -H "X-Auth-Token: Bearer YOUR_JWT_FROM_AUTHORIZER" \\
  -H "Content-Type: application/json" \\
  -d '{
    "student_email": "student@example.com",
    "subject": "Math",
    "grade_rank": 3
  }'
```

**Response Examples**

**✅ Success Response (200 OK)**

```shell
{
  "success": true,
  "data": {
    "message": "Assignment(s) invalidated successfully.",
    "total_invalidated": 1,
    "invalidated_assignments": [
      {
        "assignment_id": 123,
        "student_email": "student@example.com"
      }
    ]
  }
}
```

**❌ Error Responses**

**401 Unauthorized \- Invalid JWT**

```shell
{
  "success": false,
  "error": "Unauthorized"
}
```

**400 Bad Request \- Missing Parameters**

```shell
{
  "success": false,
  "error": "student_email is required"
}
```

```json
{
  "success": false,
  "error": "Either assignment_id, timeback_id, or (subject and grade/grade_rank) is required"
}
```

**404 Not Found \- Assignment Not Found**

```json
{
  "success": false,
  "error": "Student with email student@example.com does not exist in timeback"
}
```

```json
{
  "success": false,
  "error": "No active assignments found for student student@example.com with criteria: assignment_id: 123"
}
```

```json
{
  "success": false,
  "error": "No active assignments found for student student@example.com with criteria: subject: Math, grade: 4"
}
```

**400 Bad Request \- Invalid Grade Format**

```json
{
  "success": false,
  "error": "grade_rank must be a valid number between 0-12"
}
```

```json
{
  "success": false,
  "error": "Invalid grade format: K. Use numeric grade (0-12) or grade name."
}
```

```json
{
  "success": false,
  "error": "assignment_id must be a valid positive number"
}
```

**500 Internal Server Error**

```json
{
  "success": false,
  "error": "Internal server error while invalidating assignments",
  "data": {
    "details": "Unexpected database error"
  }
}
```

**Invalidation Rules**

* **Active Assignments Only**: Only assignments with \`ASSIGNED\`, \`IN\_PROGRESS\`, or \`PAUSED\` statuses can be invalidated.  
* **One-Time Invalidation**: An assignment, once invalidated, cannot be reactivated. A new assignment must be created if the student needs to take the test again.  
* **Partial Success**: If invalidating by \`timeback\_id\` or \`subject\`/\`grade\_rank\`, and multiple assignments match, all matching *active* assignments for that student will be invalidated. The \`total\_invalidated\` will reflect the number of assignments successfully invalidated.

---

## **Error Handling**

### **Standard Error Response Format**

All API endpoints return consistent error responses with the following structure:

```json
{
  "success": false,
  "error": "Human-readable error message",
  "code": "MACHINE_READABLE_ERROR_CODE",
  "details": {
    "additional": "context when available"
  }
}
```

### **Common Error Codes**

| Code | Description | Common Causes |
| ----- | ----- | ----- |
| `UNAUTHORIZED` | Invalid or expired authentication | Invalid API key, expired JWT |
| `ACCESS_DENIED` | User lacks required permissions | User not registered for API access |
| `MISSING_PARAMETER` | Required parameter not provided | Missing email, student\_email, or timeback\_id |
| `USER_NOT_FOUND` | Student email not found | Student not registered in system |
| `TEST_NOT_FOUND` | Test ID not found | Invalid timeback\_id |
| `TEST_NOT_SUPPORTED` | Test not yet supported | Test contains unsupported question types |
| `ASSIGNMENT_EXISTS` | Assignment already exists | Active assignment prevents duplicate |
| `INVALID_PARAMETERS` | Invalid parameter format | Malformed grade or subject values |
| `INTERNAL_ERROR` | Server-side error | Database or system issues |

### **Error Handling Best Practices**

1. **Check Response Status**: Always verify the `success` field  
2. **Handle JWT Expiration**: Implement automatic token refresh  
3. **Retry Logic**: Implement exponential backoff for temporary failures  
4. **Logging**: Log error codes and details for debugging  
5. **User Feedback**: Provide meaningful error messages to users

---

## **Additional Information**

### **Rate Limiting**

* **JWT Expiration**: Tokens expire in 1 hour  
* **Refresh Strategy**: Refresh tokens before expiration (recommended after 50 minutes)  
* **Error Handling**: Implement proper error handling for expired JWTs

### **Support and Contact**

For API access requests, technical support, or questions:

* **Technical Contacts**: [thiago@reachbeyond.ai](mailto:thiago@reachbeyond.ai) or [guilherme@reachbeyond.ai](mailto:guilherme@reachbeyond.ai)   
* **Support**: [support@reachbeyond.ai](mailto:support@reachbeyond.ai)   
* **API Access**: Request registered user email and API key

### **Future Enhancements**

As MasteryTrack evolves:

* **Test Support**: More question types will be supported automatically  
* **Advanced Search**: Additional filtering options may be added  
* **Bulk Operations**: Batch assignment capabilities are planned  
* **Analytics**: Assignment tracking and reporting features in development

