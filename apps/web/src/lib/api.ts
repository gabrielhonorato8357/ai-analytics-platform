const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL ?? "http://localhost:8000";

export type LoginResponse = {
  access_token: string;
  token_type: "bearer";
};

export type GeneratedSqlResponse = {
  sql: string;
  confidence: number;
  assumptions: string[];
  provider: string;
};

export type QueryExecutionResponse = {
  columns: string[];
  rows: Record<string, unknown>[];
  row_count: number;
  executed_sql: string;
};

export type VisualizationType = "table" | "bar" | "line";

export type SavedReport = {
  id: string;
  owner_user_id: string;
  title: string;
  description: string | null;
  sql: string;
  visualization_type: VisualizationType;
  chart_config: Record<string, unknown>;
  created_at: string;
  updated_at: string;
};

function authHeaders(token: string) {
  return {
    Authorization: `Bearer ${token}`,
    "Content-Type": "application/json",
  };
}

export async function login(email: string, password: string): Promise<LoginResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/auth/login`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ email, password }),
  });

  if (!response.ok) {
    throw new Error("Invalid email or password");
  }

  return response.json() as Promise<LoginResponse>;
}

export async function generateSql(
  token: string,
  question: string,
  schemaContext?: string,
): Promise<GeneratedSqlResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/queries/generate`, {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify({ question, schema_context: schemaContext || null }),
  });

  if (!response.ok) {
    throw new Error("SQL generation provider is not configured");
  }

  return response.json() as Promise<GeneratedSqlResponse>;
}

export async function executeSql(
  token: string,
  sql: string,
  limit: number,
): Promise<QueryExecutionResponse> {
  const response = await fetch(`${API_BASE_URL}/api/v1/queries/execute`, {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify({ sql, limit }),
  });

  if (!response.ok) {
    const body = (await response.json().catch(() => null)) as { detail?: string } | null;
    throw new Error(body?.detail ?? "Query execution failed");
  }

  return response.json() as Promise<QueryExecutionResponse>;
}

export async function listReports(token: string): Promise<SavedReport[]> {
  const response = await fetch(`${API_BASE_URL}/api/v1/reports`, {
    headers: authHeaders(token),
  });

  if (!response.ok) {
    throw new Error("Unable to load reports");
  }

  return response.json() as Promise<SavedReport[]>;
}

export async function createReport(
  token: string,
  report: {
    title: string;
    description?: string;
    sql: string;
    visualization_type: VisualizationType;
    chart_config?: Record<string, unknown>;
  },
): Promise<SavedReport> {
  const response = await fetch(`${API_BASE_URL}/api/v1/reports`, {
    method: "POST",
    headers: authHeaders(token),
    body: JSON.stringify(report),
  });

  if (!response.ok) {
    throw new Error("Unable to save report");
  }

  return response.json() as Promise<SavedReport>;
}

export async function deleteReport(token: string, reportId: string): Promise<void> {
  const response = await fetch(`${API_BASE_URL}/api/v1/reports/${reportId}`, {
    method: "DELETE",
    headers: authHeaders(token),
  });

  if (!response.ok) {
    throw new Error("Unable to delete report");
  }
}
