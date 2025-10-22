# Vigil Platform API Contract

This document specifies the exact REST API contract between `vigil-client` and `cofactor-api`.

## Base URL
```
https://api.cofactor.app/api/v1
```

## Authentication
All requests require JWT token in Authorization header:
```
Authorization: Bearer <jwt-token>
```

---

## 🔗 Artifacts API

### POST /api/v1/artifacts
Create a new artifact.

**Request:**
```json
{
  "name": "breast_cancer_model",
  "type": "model",
  "uri": "s3://models/cancer/rf.pkl",
  "checksum": "sha256:abc123...",
  "description": "Random Forest classifier",
  "metadata": {
    "accuracy": 0.967,
    "algorithm": "RandomForest",
    "features": 30
  },
  "project_id": "proj-cancer-research",
  "tags": ["classification", "medical"]
}
```

**Response:**
```json
{
  "id": "art-123456",
  "name": "breast_cancer_model",
  "type": "model",
  "uri": "s3://models/cancer/rf.pkl",
  "checksum": "sha256:abc123...",
  "description": "Random Forest classifier",
  "metadata": {
    "accuracy": 0.967,
    "algorithm": "RandomForest",
    "features": 30
  },
  "project_id": "proj-cancer-research",
  "owner_id": "user-789",
  "tags": ["classification", "medical"],
  "status": "draft",
  "created_at": "2025-01-01T10:00:00Z",
  "updated_at": "2025-01-01T10:00:00Z"
}
```

### GET /api/v1/artifacts/:id
Get artifact by ID.

**Response:** Same as create response above.

### PATCH /api/v1/artifacts/:id
Update artifact metadata.

**Request:**
```json
{
  "description": "Updated description",
  "status": "published",
  "metadata": {
    "validation_score": 0.98
  }
}
```

### GET /api/v1/artifacts
List artifacts with filtering.

**Query Parameters:**
- `project_id` - Filter by project
- `type` - Filter by artifact type (dataset, model, note, etc.)
- `owner_id` - Filter by owner
- `status` - Filter by status (draft, published, archived)
- `limit` - Max results (default: 50, max: 100)
- `offset` - Pagination offset

**Response:**
```json
{
  "artifacts": [
    {
      "id": "art-123",
      "name": "dataset-1",
      "type": "dataset",
      // ... full artifact object
    }
  ],
  "total": 150,
  "limit": 50,
  "offset": 0
}
```

---

## 🔗 Links API

### POST /api/v1/links
Create a provenance link between artifacts.

**Request:**
```json
{
  "from_artifact_id": "art-dataset-123",
  "to_artifact_id": "art-run-456",
  "type": "input_of",
  "metadata": {
    "transformation": "feature_extraction",
    "version": "1.0"
  }
}
```

**Response:**
```json
{
  "id": "link-789",
  "from_artifact_id": "art-dataset-123",
  "to_artifact_id": "art-run-456",
  "type": "input_of",
  "metadata": {
    "transformation": "feature_extraction",
    "version": "1.0"
  },
  "created_at": "2025-01-01T10:30:00Z"
}
```

### GET /api/v1/links
Get links for an artifact.

**Query Parameters:**
- `artifact_id` - Required: Get all links for this artifact
- `type` - Optional: Filter by link type

**Response:**
```json
{
  "links": [
    {
      "id": "link-789",
      "from_artifact_id": "art-dataset-123",
      "to_artifact_id": "art-run-456",
      "type": "input_of",
      "metadata": {},
      "created_at": "2025-01-01T10:30:00Z"
    }
  ]
}
```

---

## 🔗 Receipts API

### POST /api/v1/receipts
Store a Vigil receipt from the platform.

**Request:**
```json
{
  "issuer": "Vigil",
  "runlet_id": "rl_1704110400",
  "vigil_url": "vigil://api.cofactor.app/org/cancer-research/diamonds@main",
  "git_ref": "a19b2c3d...",
  "capsule_digest": "sha256:def456...",
  "inputs": [
    {
      "id": "art-dataset-123",
      "name": "training_data",
      "type": "dataset",
      "uri": "s3://data/cancer/features.csv",
      "checksum": "sha256:input123..."
    }
  ],
  "outputs": [
    {
      "id": "art-model-456",
      "name": "trained_model",
      "type": "model",
      "uri": "s3://models/cancer/rf.pkl",
      "checksum": "sha256:output456..."
    }
  ],
  "metrics": {
    "accuracy": 0.967,
    "precision": 0.971,
    "recall": 0.963
  },
  "started_at": "2025-01-01T10:00:00Z",
  "finished_at": "2025-01-01T10:30:00Z",
  "glyphs": ["RECEIPT", "DATA_TABLE"],
  "signature": "UNSIGNED-DEV",
  "profile": "gpu",
  "version": "2.0",
  "platform_metadata": {
    "uploaded_by": "user-789",
    "project_id": "proj-cancer-research"
  }
}
```

**Response:**
```json
{
  "id": "receipt-123",
  "status": "stored",
  "artifacts_created": ["art-model-456"],
  "links_created": ["link-789"],
  "message": "Receipt processed successfully"
}
```

### GET /api/v1/receipts/:id
Get a receipt by ID.

**Response:** Receipt JSON as stored.

---

## 🔗 Graph API

### GET /api/v1/graph/:artifact_id
Get full provenance graph for an artifact.

**Query Parameters:**
- `depth` - How many levels to traverse (default: unlimited)
- `direction` - "upstream", "downstream", or "both" (default: "both")

**Response:**
```json
{
  "nodes": [
    {
      "id": "art-dataset-123",
      "type": "Artifact",
      "data": {
        "name": "training_data",
        "type": "dataset",
        "uri": "s3://data/cancer/features.csv"
      }
    },
    {
      "id": "art-run-456",
      "type": "Artifact",
      "data": {
        "name": "training_run",
        "type": "run"
      }
    },
    {
      "id": "art-model-789",
      "type": "Artifact",
      "data": {
        "name": "trained_model",
        "type": "model",
        "uri": "s3://models/cancer/rf.pkl"
      }
    }
  ],
  "edges": [
    {
      "id": "link-1",
      "source": "art-dataset-123",
      "target": "art-run-456",
      "type": "input_of",
      "data": {
        "transformation": "feature_extraction"
      }
    },
    {
      "id": "link-2",
      "source": "art-run-456",
      "target": "art-model-789",
      "type": "output_of"
    }
  ]
}
```

---

## 🔗 Storage API

### POST /api/v1/storage/upload-url
Get presigned URL for uploading to S3/MinIO.

**Request:**
```json
{
  "filename": "model.pkl",
  "content_type": "application/octet-stream",
  "size_bytes": 1048576
}
```

**Response:**
```json
{
  "upload_url": "https://storage.cofactor.app/upload?signature=...",
  "final_uri": "s3://artifacts/project/models/model.pkl",
  "content_type": "application/octet-stream",
  "expires_at": "2025-01-01T11:00:00Z"
}
```

### GET /api/v1/artifacts/:id/download
Get download URL for an artifact.

**Response:**
```json
{
  "download_url": "https://storage.cofactor.app/download/model.pkl?signature=...",
  "expires_at": "2025-01-01T11:00:00Z"
}
```

---

## 🔗 Error Responses

All endpoints return standard HTTP status codes with error details:

**400 Bad Request:**
```json
{
  "error": "ValidationError",
  "message": "Invalid artifact type",
  "details": {
    "type": "Must be one of: dataset, model, note, receipt, code, environment, run"
  }
}
```

**401 Unauthorized:**
```json
{
  "error": "UnauthorizedError",
  "message": "Invalid or expired token"
}
```

**403 Forbidden:**
```json
{
  "error": "ForbiddenError",
  "message": "Insufficient permissions for project"
}
```

**404 Not Found:**
```json
{
  "error": "NotFoundError",
  "message": "Artifact not found"
}
```

**500 Internal Server Error:**
```json
{
  "error": "InternalError",
  "message": "Storage backend unavailable"
}
```

---

## 🔗 Pagination

List endpoints support pagination:

```json
{
  "data": [...],
  "pagination": {
    "total": 150,
    "limit": 50,
    "offset": 0,
    "has_more": true,
    "next_offset": 50
  }
}
```

---

## 🔗 Rate Limiting

- 100 requests per minute per user
- 1000 requests per hour per user
- Upload/download size limits: 5GB per file

Rate limit headers:
```
X-RateLimit-Limit: 100
X-RateLimit-Remaining: 95
X-RateLimit-Reset: 1640995200
```

---

This contract ensures `vigil-client` and `cofactor-api` work together seamlessly for end-to-end cryptographic provenance and collaborative science.
