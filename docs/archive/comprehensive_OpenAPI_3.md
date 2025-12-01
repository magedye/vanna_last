 a comprehensive OpenAPI 3.1 specification. :


openapi_3.1.0.json
+736

@@ -1,0 +1,735 @@
{
  "openapi": "3.1.0",
  "info": {
    "title": "Vanna Insight Engine API",
    "description": "AI-powered Text-to-SQL backend for natural-language query generation, SQL correction, and explanation. Includes admin configuration utilities and Prometheus metrics.",
    "version": "2.3.3",
    "contact": {
      "name": "Vanna Insight Team"
    },
    "license": {
      "name": "MIT"
    }
  },
  "servers": [
    {
      "url": "http://localhost:8000",
      "description": "Local development server"
    },
    {
      "url": "https://api.vannainsight.com",
      "description": "Production server"
    }
  ],
  "paths": {
    "/": {
      "get": {
        "operationId": "root",
        "summary": "Root endpoint with API information",
        "description": "Returns API overview and documentation links.",
        "tags": ["Core"],
        "responses": {
          "200": {
            "description": "Successful response",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "properties": {
                    "message": {
                      "type": "string",
                      "example": "Vanna Insight Engine API v2.3.3"
                    },
                    "docs": {
                      "type": "string",
                      "example": "/docs"
                    },
                    "openapi": {
                      "type": "string",
                      "example": "/openapi.json"
                    },
                    "health": {
                      "type": "string",
                      "example": "/health"
                    },
                    "metrics": {
                      "type": "string",
                      "example": "/metrics"
                    }
                  },
                  "required": ["message", "docs", "openapi", "health", "metrics"]
                }
              }
            }
          }
        }
      }
    },
    "/health": {
      "get": {
        "operationId": "health",
        "summary": "Health check endpoint",
        "description": "Returns service, version, and provider status with feature toggles. Status: healthy (all deps), degraded (some deps missing), or unhealthy (critical failure).",
        "tags": ["Core"],
        "responses": {
          "200": {
            "description": "Service health status",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "properties": {
                    "status": {
                      "type": "string",
                      "enum": ["healthy", "degraded", "unhealthy"],
                      "example": "healthy"
                    },
                    "version": {
                      "type": "string",
                      "example": "2.3.3"
                    },
                    "providers_active": {
                      "type": "integer",
                      "example": 1
                    },
                    "dependencies": {
                      "type": "object",
                      "properties": {
                        "postgres": {
                          "type": "boolean"
                        },
                        "redis": {
                          "type": "boolean"
                        },
                        "chroma": {
                          "type": "boolean"
                        }
                      },
                      "required": ["postgres", "redis", "chroma"]
                    },
                    "features": {
                      "type": "object",
                      "properties": {
                        "circuit_breaker": {
                          "type": "boolean"
                        },
                        "correlation_ids": {
                          "type": "boolean"
                        },
                        "failover": {
                          "type": "boolean"
                        }
                      },
                      "required": ["circuit_breaker", "correlation_ids", "failover"]
                    }
                  },
                  "required": ["status", "version", "providers_active", "dependencies", "features"]
                }
              }
            }
          }
        }
      }
    },
    "/metrics": {
      "get": {
        "operationId": "metrics",
        "summary": "Prometheus-style metrics",
        "description": "Exposes operational metrics for monitoring systems.",
        "tags": ["Core"],
        "responses": {
          "200": {
            "description": "System metrics",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "properties": {
                    "app_info": {
                      "type": "object",
                      "properties": {
                        "version": {
                          "type": "string",
                          "example": "2.3.3"
                        },
                        "name": {
                          "type": "string",
                          "example": "vanna_insight_engine"
                        }
                      },
                      "required": ["version", "name"]
                    },
                    "providers_total": {
                      "type": "integer",
                      "example": 1
                    },
                    "service_status": {
                      "type": "string",
                      "enum": ["healthy", "degraded", "unhealthy"]
                    },
                    "dependencies": {
                      "type": "object",
                      "properties": {
                        "postgres": {
                          "type": "boolean"
                        },
                        "redis": {
                          "type": "boolean"
                        },
                        "chroma": {
                          "type": "boolean"
                        }
                      },
                      "required": ["postgres", "redis", "chroma"]
                    },
                    "features_enabled": {
                      "type": "array",
                      "items": {
                        "type": "string"
                      },
                      "example": ["circuit_breaker", "failover", "correlation_ids"]
                    }
                  },
                  "required": ["app_info", "providers_total", "service_status", "dependencies", "features_enabled"]
                }
              }
            }
          }
        }
      }
    },
    "/api/v1/generate-sql": {
      "post": {
        "operationId": "generate_sql",
        "summary": "Generate SQL from natural language question",
        "description": "Takes a natural language question and generates corresponding SQL. Returns generated SQL statement with correlation ID for tracing.",
        "tags": ["SQL"],
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/GenerateSQLRequest"
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "Successfully generated SQL",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/SQLResponse"
                }
              }
            }
          },
          "422": {
            "description": "Validation error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ValidationError"
                }
              }
            }
          },
          "500": {
            "description": "Server error during SQL generation",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ErrorResponse"
                }
              }
            }
          }
        }
      }
    },
    "/api/v1/fix-sql": {
      "post": {
        "operationId": "fix_sql",
        "summary": "Fix SQL based on error message",
        "description": "Takes broken SQL and error message, returns corrected SQL. Uses correlation ID for request tracing.",
        "tags": ["SQL"],
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/FixSQLRequest"
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "Successfully fixed SQL",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/SQLResponse"
                }
              }
            }
          },
          "422": {
            "description": "Validation error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ValidationError"
                }
              }
            }
          },
          "500": {
            "description": "Server error during SQL fix",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ErrorResponse"
                }
              }
            }
          }
        }
      }
    },
    "/api/v1/explain-sql": {
      "post": {
        "operationId": "explain_sql",
        "summary": "Explain SQL query in natural language",
        "description": "Takes SQL query and returns natural-language explanation. Includes correlation ID for request tracing.",
        "tags": ["SQL"],
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "$ref": "#/components/schemas/ExplainSQLRequest"
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "Successfully explained SQL",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ExplanationResponse"
                }
              }
            }
          },
          "422": {
            "description": "Validation error",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ValidationError"
                }
              }
            }
          },
          "500": {
            "description": "Server error during SQL explanation",
            "content": {
              "application/json": {
                "schema": {
                  "$ref": "#/components/schemas/ErrorResponse"
                }
              }
            }
          }
        }
      }
    },
    "/admin/config": {
      "get": {
        "operationId": "admin_config",
        "summary": "Get current configuration",
        "description": "Returns sanitized runtime configuration for UI dashboards.",
        "tags": ["Admin"],
        "responses": {
          "200": {
            "description": "Current configuration",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "additionalProperties": true
                }
              }
            }
          }
        }
      },
      "post": {
        "operationId": "update_admin_config",
        "summary": "Update configuration",
        "description": "Adjust feature flags and runtime settings dynamically. Feature pending full implementation.",
        "tags": ["Admin"],
        "requestBody": {
          "required": true,
          "content": {
            "application/json": {
              "schema": {
                "type": "object",
                "additionalProperties": true
              }
            }
          }
        },
        "responses": {
          "200": {
            "description": "Configuration update status",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "properties": {
                    "message": {
                      "type": "string"
                    },
                    "status": {
                      "type": "string",
                      "enum": ["planned"]
                    }
                  },
                  "required": ["message", "status"]
                }
              }
            }
          }
        }
      }
    },
    "/admin/approve-sql": {
      "post": {
        "operationId": "approve_sql",
        "summary": "Approve flagged SQL",
        "description": "Marks a flagged SQL query as approved for production use. Feature pending implementation.",
        "tags": ["Admin"],
        "responses": {
          "200": {
            "description": "Feature pending implementation",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "properties": {
                    "message": {
                      "type": "string"
                    },
                    "status": {
                      "type": "string",
                      "enum": ["planned"]
                    }
                  },
                  "required": ["message", "status"]
                }
              }
            }
          }
        }
      }
    },
    "/admin/feedback-metrics": {
      "get": {
        "operationId": "feedback_metrics",
        "summary": "Retrieve feedback metrics",
        "description": "Returns aggregate user feedback statistics. Feature pending implementation.",
        "tags": ["Admin"],
        "responses": {
          "200": {
            "description": "Feature pending implementation",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "properties": {
                    "message": {
                      "type": "string"
                    },
                    "status": {
                      "type": "string",
                      "enum": ["planned"]
                    }
                  },
                  "required": ["message", "status"]
                }
              }
            }
          }
        }
      }
    },
    "/admin/scheduled/create": {
      "post": {
        "operationId": "create_scheduled_report",
        "summary": "Create scheduled report",
        "description": "Feature pending implementation.",
        "tags": ["Admin"],
        "responses": {
          "200": {
            "description": "Feature pending implementation",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "properties": {
                    "message": {
                      "type": "string"
                    },
                    "status": {
                      "type": "string",
                      "enum": ["planned"]
                    }
                  },
                  "required": ["message", "status"]
                }
              }
            }
          }
        }
      }
    },
    "/admin/scheduled/list": {
      "get": {
        "operationId": "list_scheduled_reports",
        "summary": "List scheduled reports",
        "description": "Feature pending implementation.",
        "tags": ["Admin"],
        "responses": {
          "200": {
            "description": "Feature pending implementation",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "properties": {
                    "message": {
                      "type": "string"
                    },
                    "status": {
                      "type": "string",
                      "enum": ["planned"]
                    },
                    "scheduled_reports": {
                      "type": "array",
                      "items": {
                        "type": "object"
                      }
                    }
                  },
                  "required": ["message", "status", "scheduled_reports"]
                }
              }
            }
          }
        }
      }
    },
    "/admin/scheduled/{report_id}": {
      "delete": {
        "operationId": "delete_scheduled_report",
        "summary": "Delete scheduled report",
        "description": "Feature pending implementation.",
        "tags": ["Admin"],
        "parameters": [
          {
            "name": "report_id",
            "in": "path",
            "required": true,
            "schema": {
              "type": "string"
            },
            "description": "The ID of the scheduled report to delete"
          }
        ],
        "responses": {
          "200": {
            "description": "Feature pending implementation",
            "content": {
              "application/json": {
                "schema": {
                  "type": "object",
                  "properties": {
                    "message": {
                      "type": "string"
                    },
                    "status": {
                      "type": "string",
                      "enum": ["planned"]
                    }
                  },
                  "required": ["message", "status"]
                }
              }
            }
          }
        }
      }
    }
  },
  "components": {
    "schemas": {
      "GenerateSQLRequest": {
        "title": "GenerateSQLRequest",
        "type": "object",
        "properties": {
          "question": {
            "type": "string",
            "title": "Question",
            "description": "Natural language question to convert to SQL"
          }
        },
        "required": ["question"]
      },
      "FixSQLRequest": {
        "title": "FixSQLRequest",
        "type": "object",
        "properties": {
          "sql": {
            "type": "string",
            "title": "SQL",
            "description": "The SQL query that needs to be fixed"
          },
          "error_msg": {
            "type": "string",
            "title": "Error Message",
            "description": "The error message from the SQL execution"
          }
        },
        "required": ["sql", "error_msg"]
      },
      "ExplainSQLRequest": {
        "title": "ExplainSQLRequest",
        "type": "object",
        "properties": {
          "sql": {
            "type": "string",
            "title": "SQL",
            "description": "The SQL query to explain in natural language"
          }
        },
        "required": ["sql"]
      },
      "SQLResponse": {
        "title": "SQLResponse",
        "type": "object",
        "properties": {
          "sql": {
            "type": "string",
            "title": "SQL",
            "description": "The generated or modified SQL query"
          },
          "correlation_id": {
            "type": "string",
            "title": "Correlation ID",
            "description": "Unique identifier for request tracing and debugging"
          },
          "status": {
            "type": "string",
            "title": "Status",
            "enum": ["success"],
            "description": "Operation status"
          }
        },
        "required": ["sql", "correlation_id", "status"]
      },
      "ExplanationResponse": {
        "title": "ExplanationResponse",
        "type": "object",
        "properties": {
          "explanation": {
            "type": "string",
            "title": "Explanation",
            "description": "Natural language explanation of the SQL query"
          },
          "correlation_id": {
            "type": "string",
            "title": "Correlation ID",
            "description": "Unique identifier for request tracing and debugging"
          },
          "status": {
            "type": "string",
            "title": "Status",
            "enum": ["success"],
            "description": "Operation status"
          }
        },
        "required": ["explanation", "correlation_id", "status"]
      },
      "ErrorResponse": {
        "title": "ErrorResponse",
        "type": "object",
        "properties": {
          "error": {
            "type": "string",
            "title": "Error",
            "description": "Error message"
          },
          "correlation_id": {
            "type": "string",
            "title": "Correlation ID",
            "description": "Unique identifier for request tracing"
          }
        },
        "required": ["error", "correlation_id"]
      },
      "ValidationError": {
        "title": "ValidationError",
        "type": "object",
        "properties": {
          "detail": {
            "type": "array",
            "items": {
              "type": "object",
              "properties": {
                "loc": {
                  "type": "array",
                  "items": {
                    "oneOf": [
                      {
                        "type": "string"
                      },
                      {
                        "type": "integer"
                      }
                    ]
                  }
                },
                "msg": {
                  "type": "string"
                },
                "type": {
                  "type": "string"
                }
              }
            }
          }
        },
        "required": ["detail"]
      }
    }
  },
  "tags": [
    {
      "name": "Core",
      "description": "Core API endpoints for health checks and metrics"
    },
    {
      "name": "SQL",
      "description": "SQL generation, fixing, and explanation endpoints"
    },
    {
      "name": "Admin",
      "description": "Administrative endpoints for configuration and management"
    }
  ]
}

The specification includes:

12 endpoints across 3 tag groups (Core, SQL, Admin)
Core endpoints: root, health, metrics
SQL endpoints: generate-sql, fix-sql, explain-sql
Admin endpoints: config management, SQL approval, feedback metrics, and scheduled report management
Full schema definitions for all request/response types with proper validation
Error handling with correlation ID tracking
Feature toggles documenting circuit breaker, failover, and correlation ID capabilities
The specification is JSON-formatted, OpenAPI 3.1.0 compliant, and ready for integration with API documentation tools or client code generation.

