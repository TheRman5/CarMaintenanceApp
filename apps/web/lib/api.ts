export type Vehicle = {
  id: string;
  year: number;
  make: string;
  model: string;
  trim: string | null;
  engine: string | null;
  vin: string | null;
  odometer: number;
  created_at: string;
};

export type TaskStatus = "overdue" | "due" | "due_soon" | "upcoming" | "unscheduled" | "completed";
export type MaintenanceTask = {
  id: string;
  vehicle_id: string;
  name: string;
  description: string | null;
  interval_days: number | null;
  interval_miles: number | null;
  next_due_date: string | null;
  next_due_mileage: number | null;
  last_completed_at: string | null;
  last_completed_mileage: number | null;
  status: TaskStatus;
  created_at: string;
};

export type ServiceRecord = {
  id: string;
  vehicle_id: string;
  task_id: string | null;
  performed_at: string;
  mileage: number;
  service_type: string;
  cost: string | null;
  notes: string | null;
  parts: string | null;
  created_at: string;
};

const ROOT = process.env.NEXT_PUBLIC_API_URL ?? "http://127.0.0.1:8000";

async function request<T>(path: string, options: RequestInit = {}): Promise<T> {
  let response: Response;
  try {
    response = await fetch(`${ROOT}${path}`, {
      cache: "no-store",
      headers: { "Content-Type": "application/json", ...options.headers },
      ...options,
    });
  } catch {
    throw new Error("Cannot reach the backend. Start FastAPI on http://127.0.0.1:8000 and try again.");
  }

  if (!response.ok) {
    const body = (await response.json().catch(() => ({}))) as {detail?: unknown};
    let message = `Request failed (${response.status}).`;
    if (typeof body.detail === "string") message = body.detail;
    else if (Array.isArray(body.detail)) message = body.detail.map((d: {msg?: string}) => d.msg ?? "Invalid field").join("; ");
    throw new Error(message);
  }
  return (response.status === 204 ? undefined : await response.json()) as T;
}

const payload = (method: string, data: unknown): RequestInit => ({method, body: JSON.stringify(data)});
export const api = {
  vehicles: () => request<Vehicle[]>("/api/vehicles"),
  addVehicle: (data: unknown) => request<Vehicle>("/api/vehicles", payload("POST", data)),
  updateVehicle: (id: string, data: unknown) => request<Vehicle>(`/api/vehicles/${id}`, payload("PATCH", data)),
  updateOdometer: (id: string, mileage: number) => request<Vehicle>(`/api/vehicles/${id}/odometer`, payload("POST", { mileage })),
  tasks: (id: string) => request<MaintenanceTask[]>(`/api/vehicles/${id}/tasks`),
  addTask: (id: string, data: unknown) => request<MaintenanceTask>(`/api/vehicles/${id}/tasks`, payload("POST", data)),
  updateTask: (id: string, taskId: string, data: unknown) => request<MaintenanceTask>(`/api/vehicles/${id}/tasks/${taskId}`, payload("PATCH", data)),
  removeTask: (id: string, taskId: string) => request<void>(`/api/vehicles/${id}/tasks/${taskId}`, {method: "DELETE"}),
  complete: (id: string, taskId: string, data: unknown) => request<ServiceRecord>(`/api/vehicles/${id}/tasks/${taskId}/complete`, payload("POST", data)),
  records: (id: string) => request<ServiceRecord[]>(`/api/vehicles/${id}/service-records`),
  addRecord: (id: string, data: unknown) => request<ServiceRecord>(`/api/vehicles/${id}/service-records`, payload("POST", data)),
};
