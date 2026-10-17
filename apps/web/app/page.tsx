"use client";

import { useEffect, useState } from "react";
import {
  Activity, AlertCircle, CalendarClock, CarFront, Check, CheckCircle2,
  ChevronRight, ClipboardList, Gauge, History, LayoutDashboard, Menu,
  Moon, Pencil, Plus, Settings2, Sun, Trash2, Wrench, X,
} from "lucide-react";
import { api, type MaintenanceTask, type ServiceRecord, type Vehicle } from "../lib/api";

type Section = "dashboard" | "tasks" | "history" | "vehicle";
type Modal = "vehicle" | "task" | "complete" | "odometer" | "record" | null;
type Theme = "light" | "dark" | "system";

type VehicleForm = { year: string; make: string; model: string; trim: string; engine: string; vin: string; odometer: string };
type TaskForm = { name: string; description: string; interval_days: string; interval_miles: string; next_due_date: string; next_due_mileage: string };
type ServiceForm = { service_type: string; performed_at: string; mileage: string; cost: string; notes: string; parts: string };

const blankVehicle: VehicleForm = { year: String(new Date().getFullYear()), make: "", model: "", trim: "", engine: "", vin: "", odometer: "0" };
const blankTask: TaskForm = { name: "", description: "", interval_days: "", interval_miles: "", next_due_date: "", next_due_mileage: "" };
const localToday = () => {
  const d = new Date();
  return `${d.getFullYear()}-${String(d.getMonth() + 1).padStart(2, "0")}-${String(d.getDate()).padStart(2, "0")}`;
};
const fmtNumber = (n: number) => new Intl.NumberFormat("en-US").format(n);
const fmtDate = (date: string | null) => date ? new Date(`${date}T12:00:00`).toLocaleDateString("en-US", { month: "short", day: "numeric", year: "numeric" }) : "Not set";
const fmtMoney = (n: string | null) => n ? `$${Number(n).toFixed(2)}` : "Not recorded";
const labelStatus = (status: MaintenanceTask["status"]) => ({ overdue: "Overdue", due: "Due now", due_soon: "Due soon", upcoming: "Upcoming", unscheduled: "Unscheduled", completed: "Completed" })[status];
const emptyToNull = (value: string) => value.trim() ? value.trim() : null;
const optionalPositive = (value: string) => value === "" ? null : Number(value);

function TextField({ label, value, onChange, type = "text", placeholder, required = false, min, max, helper }: {
  label: string; value: string; onChange: (s: string) => void; type?: string; placeholder?: string;
  required?: boolean; min?: string; max?: string; helper?: string;
}) {
  return <label className="field"><span>{label}{required && <span className="required"> *</span>}</span>
    <input required={required} type={type} value={value} onChange={e => onChange(e.target.value)} placeholder={placeholder} min={min} max={max} />
    {helper && <small>{helper}</small>}
  </label>;
}

export default function Home() {
  const [vehicles, setVehicles] = useState<Vehicle[]>([]);
  const [selectedVehicleId, setSelectedVehicleId] = useState<string | null>(null);
  const [tasks, setTasks] = useState<MaintenanceTask[]>([]);
  const [records, setRecords] = useState<ServiceRecord[]>([]);
  const [section, setSection] = useState<Section>("dashboard");
  const [modal, setModal] = useState<Modal>(null);
  const [theme, setTheme] = useState<Theme>("system");
  const [loading, setLoading] = useState(true);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState<string | null>(null);
  const [formError, setFormError] = useState<string | null>(null);
  const [mobileNav, setMobileNav] = useState(false);
  const [vehicleForm, setVehicleForm] = useState<VehicleForm>(blankVehicle);
  const [taskForm, setTaskForm] = useState<TaskForm>(blankTask);
  const [recordForm, setRecordForm] = useState<ServiceForm>({service_type: "", performed_at: localToday(), mileage: "", cost: "", notes: "", parts: ""});
  const [mileageInput, setMileageInput] = useState("");
  const [editingTask, setEditingTask] = useState<MaintenanceTask | null>(null);

  const vehicle = vehicles.find(v => v.id === selectedVehicleId) ?? vehicles[0] ?? null;
  const urgent = tasks.filter(t => ["overdue", "due", "due_soon"].includes(t.status));
  const active = tasks.filter(t => t.status !== "completed");
  const overdue = tasks.filter(t => t.status === "overdue");
  const due = tasks.filter(t => t.status === "due" || t.status === "due_soon");
  const recent = records.slice(0, 5);

  useEffect(() => {
    const saved = localStorage.getItem("garage-theme") as Theme | null;
    if (saved === "light" || saved === "dark" || saved === "system") setTheme(saved);
  }, []);
  useEffect(() => {
    document.documentElement.dataset.theme = theme;
    localStorage.setItem("garage-theme", theme);
  }, [theme]);

  async function reload(preferredId?: string | null) {
    try {
      const list = await api.vehicles();
      const chosen = list.find(v => v.id === (preferredId ?? selectedVehicleId)) ?? list[0];
      const [nextTasks, nextRecords] = chosen ? await Promise.all([api.tasks(chosen.id), api.records(chosen.id)]) : [[], []];
      setVehicles(list);
      setSelectedVehicleId(chosen?.id ?? null);
      setTasks(nextTasks);
      setRecords(nextRecords);
      setError(null);
    } catch (e) { setError(e instanceof Error ? e.message : "Unexpected error"); }
    finally { setLoading(false); }
  }
  useEffect(() => { void reload(); /* initial fetch only */ }, []); // eslint-disable-line react-hooks/exhaustive-deps

  const chooseTheme = () => setTheme(theme === "light" ? "dark" : "light");
  const setVehicleField = (key: keyof VehicleForm) => (value: string) => setVehicleForm(f => ({ ...f, [key]: value }));
  const setTaskField = (key: keyof TaskForm) => (value: string) => setTaskForm(f => ({ ...f, [key]: value }));
  const setRecordField = (key: keyof ServiceForm) => (value: string) => setRecordForm(f => ({ ...f, [key]: value }));

  function openModal(next: Modal) { setFormError(null); setModal(next); }
  function openVehicle() {
    setVehicleForm(vehicle ? { year: String(vehicle.year), make: vehicle.make, model: vehicle.model, trim: vehicle.trim ?? "", engine: vehicle.engine ?? "", vin: vehicle.vin ?? "", odometer: String(vehicle.odometer) } : { ...blankVehicle });
    openModal("vehicle");
  }
  function openTask(task?: MaintenanceTask) {
    setEditingTask(task ?? null);
    setTaskForm(task ? {
      name: task.name, description: task.description ?? "", interval_days: task.interval_days?.toString() ?? "",
      interval_miles: task.interval_miles?.toString() ?? "", next_due_date: task.next_due_date ?? "",
      next_due_mileage: task.next_due_mileage?.toString() ?? "",
    } : { ...blankTask });
    openModal("task");
  }
  function openCompletion(task: MaintenanceTask) {
    setEditingTask(task);
    setRecordForm({service_type: task.name, performed_at: localToday(), mileage: String(vehicle?.odometer ?? 0), cost: "", notes: "", parts: ""});
    openModal("complete");
  }
  function openRecord() {
    setRecordForm({service_type: "", performed_at: localToday(), mileage: String(vehicle?.odometer ?? 0), cost: "", notes: "", parts: ""});
    openModal("record");
  }
  function openOdometer() { setMileageInput(String(vehicle?.odometer ?? 0)); openModal("odometer"); }
  function closeModal() { if (!busy) { setModal(null); setEditingTask(null); setFormError(null); } }

  async function submit(action: () => Promise<unknown>, vehicleId?: string | null) {
    setBusy(true); setFormError(null);
    try {
      await action();
      await reload(vehicleId);
      setModal(null); setEditingTask(null);
    } catch (e) { setFormError(e instanceof Error ? e.message : "Unexpected error"); }
    finally { setBusy(false); }
  }

  function saveVehicle(e: React.FormEvent) {
    e.preventDefault();
    const data = { year: Number(vehicleForm.year), make: vehicleForm.make.trim(), model: vehicleForm.model.trim(), trim: emptyToNull(vehicleForm.trim), engine: emptyToNull(vehicleForm.engine), vin: emptyToNull(vehicleForm.vin) };
    if (vehicle) void submit(() => api.updateVehicle(vehicle.id, data), vehicle.id);
    else void submit(async () => { const created = await api.addVehicle({ ...data, odometer: Number(vehicleForm.odometer) }); setSelectedVehicleId(created.id); }, null);
  }
  function saveTask(e: React.FormEvent) {
    e.preventDefault(); if (!vehicle) return;
    const data = {
      name: taskForm.name.trim(), description: emptyToNull(taskForm.description),
      interval_days: optionalPositive(taskForm.interval_days), interval_miles: optionalPositive(taskForm.interval_miles),
      next_due_date: taskForm.next_due_date || null, next_due_mileage: optionalPositive(taskForm.next_due_mileage),
    };
    if (editingTask) void submit(() => api.updateTask(vehicle.id, editingTask.id, data), vehicle.id);
    else void submit(() => api.addTask(vehicle.id, data), vehicle.id);
  }
  function saveService(e: React.FormEvent) {
    e.preventDefault(); if (!vehicle) return;
    const data = {
      performed_at: recordForm.performed_at, mileage: Number(recordForm.mileage),
      cost: optionalPositive(recordForm.cost), notes: emptyToNull(recordForm.notes), parts: emptyToNull(recordForm.parts),
    };
    if (modal === "complete" && editingTask) void submit(() => api.complete(vehicle.id, editingTask.id, data), vehicle.id);
    else void submit(() => api.addRecord(vehicle.id, { ...data, service_type: recordForm.service_type.trim() }), vehicle.id);
  }
  function saveOdometer(e: React.FormEvent) {
    e.preventDefault(); if (!vehicle) return;
    void submit(() => api.updateOdometer(vehicle.id, Number(mileageInput)), vehicle.id);
  }
  async function removeTask(task: MaintenanceTask) {
    if (!vehicle || !window.confirm(`Delete “${task.name}”? Existing service history will be kept.`)) return;
    try { await api.removeTask(vehicle.id, task.id); await reload(vehicle.id); }
    catch (e) { setError(e instanceof Error ? e.message : "Delete failed"); }
  }

  const navItems = [
    { id: "dashboard" as Section, text: "Overview", icon: LayoutDashboard },
    { id: "tasks" as Section, text: "Maintenance", icon: Wrench },
    { id: "history" as Section, text: "Service history", icon: History },
    { id: "vehicle" as Section, text: "Vehicle details", icon: Settings2 },
  ];
  const TaskRow = ({ task }: { task: MaintenanceTask }) => <div className="task-row">
    <div className={`task-symbol symbol-${task.status}`}><Wrench size={19} /></div>
    <div className="task-copy">
      <div className="task-name">{task.name}</div>
      <div className="task-details">
        {task.next_due_date && <span><CalendarClock size={13} />{fmtDate(task.next_due_date)}</span>}
        {task.next_due_mileage !== null && <span><Gauge size={13} />{fmtNumber(task.next_due_mileage)} mi</span>}
        {task.status === "completed" && <span>One-time service recorded</span>}
      </div>
    </div>
    <span className={`status status-${task.status}`}>{labelStatus(task.status)}</span>
    <div className="task-actions">
      {task.status !== "completed" && <button title="Log as completed" className="icon-button action-success" onClick={() => openCompletion(task)}><Check size={17} /></button>}
      <button title="Edit task" className="icon-button" onClick={() => openTask(task)}><Pencil size={16} /></button>
      <button title="Delete task" className="icon-button delete-icon" onClick={() => void removeTask(task)}><Trash2 size={16} /></button>
    </div>
  </div>;

  return <div className="app-shell">
    <aside className={`sidebar ${mobileNav ? "show-mobile" : ""}`}>
      <div className="brand"><div className="brand-mark"><Wrench size={21} strokeWidth={2.4}/></div><div><strong>MY GARAGE</strong><span>MAINTENANCE TRACKER</span></div></div>
      <div className="sidebar-label">WORKSPACE</div>
      <nav className="side-nav">{navItems.map(item => <button key={item.id} className={section === item.id ? "nav-active" : ""} onClick={() => {setSection(item.id); setMobileNav(false);}}><item.icon size={19}/>{item.text}{section === item.id && <ChevronRight className="nav-arrow" size={15}/>}</button>)}</nav>
      <div className="sidebar-bottom"><div className="local-info"><span className="local-dot"/> LOCAL DEVELOPMENT<span className="local-caption">Authentication coming in Milestone 2</span></div>
        <button className="theme-button" onClick={chooseTheme}>{theme === "dark" ? <Sun size={18}/> : <Moon size={18}/>} <span>{theme === "dark" ? "Light mode" : "Dark mode"}</span><span className="theme-shortcut">Toggle</span></button>
      </div>
    </aside>
    {mobileNav && <button className="mobile-scrim" aria-label="Close navigation" onClick={() => setMobileNav(false)}/>}
    <main className="workspace">
      <header className="topbar"><button className="icon-button mobile-menu" title="Open navigation" onClick={() => setMobileNav(true)}><Menu size={22}/></button>
        <div className="topbar-title"><span className="breadcrumb">My Garage</span><ChevronRight size={14}/><span>{navItems.find(n => n.id === section)?.text}</span></div>
        <span className="topbar-right">Maintenance made simple <span className="avatar">MG</span></span>
      </header>
      <div className="main-inner">
        {error && <div className="alert"><AlertCircle size={19}/><div>{error}</div><button onClick={() => void reload()} className="link-button">Retry</button></div>}
        {loading ? <div className="empty-view"><div className="spinner"/><p>Loading your garage...</p></div> : <>
          {!vehicle ? <div className="onboarding"><div className="onboarding-icon"><CarFront size={34}/></div><span className="eyebrow">YOUR GARAGE STARTS HERE</span><h1>Add your first vehicle</h1><p>Keep all maintenance tasks, mileage, and service records in one place. Begin by creating your vehicle profile.</p><button className="primary-button" onClick={openVehicle}><Plus size={17}/> Add a vehicle</button></div> : <>
            {section === "dashboard" && <>
              <div className="page-heading"><div><span className="eyebrow">YOUR VEHICLE AT A GLANCE</span><h1>Garage overview</h1><p>Stay ahead of maintenance. Keep every mile accounted for.</p></div><button className="primary-button" onClick={() => openTask()}><Plus size={17}/> Add maintenance</button></div>
              <div className="vehicle-hero"><div className="hero-icon"><CarFront size={41}/></div><div className="hero-info"><span className="mini-label">CURRENT VEHICLE</span><h2>{vehicle.year} {vehicle.make} {vehicle.model}</h2><p>{[vehicle.trim, vehicle.engine].filter(Boolean).join(" · ") || "Your primary vehicle"}</p></div><div className="hero-mileage"><span>CURRENT ODOMETER</span><strong>{fmtNumber(vehicle.odometer)} <small>mi</small></strong><button onClick={openOdometer}>Update mileage <ChevronRight size={15}/></button></div></div>
              <div className="stats-grid">
                <div className="stat-card"><div className="stat-head"><span>Overdue services</span><div className="stat-icon red"><AlertCircle size={19}/></div></div><strong>{overdue.length}</strong><small>Need immediate attention</small></div>
                <div className="stat-card"><div className="stat-head"><span>Due soon</span><div className="stat-icon amber"><CalendarClock size={19}/></div></div><strong>{due.length}</strong><small>Within 30 days or 500 miles</small></div>
                <div className="stat-card"><div className="stat-head"><span>Active tasks</span><div className="stat-icon blue"><ClipboardList size={19}/></div></div><strong>{active.length}</strong><small>Scheduled maintenance</small></div>
                <div className="stat-card"><div className="stat-head"><span>Services recorded</span><div className="stat-icon green"><CheckCircle2 size={19}/></div></div><strong>{records.length}</strong><small>Total logged services</small></div>
              </div>
              <div className="content-grid">
                <section className="content-card"><div className="card-top"><div><h3>Needs your attention</h3><p>Tasks approaching or past their due point</p></div><button className="plain-link" onClick={() => setSection("tasks")}>View all <ChevronRight size={15}/></button></div>
                  {urgent.length ? urgent.map(task => <TaskRow key={task.id} task={task}/>) : <div className="card-empty"><CheckCircle2 size={29}/><strong>You're all caught up</strong><span>No maintenance is currently due or nearing its due point.</span><button className="text-cta" onClick={() => openTask()}>Schedule maintenance <ChevronRight size={15}/></button></div>}
                </section>
                <section className="content-card"><div className="card-top"><div><h3>Recent service history</h3><p>Your latest recorded work</p></div><button className="plain-link" onClick={() => setSection("history")}>View all <ChevronRight size={15}/></button></div>
                  {recent.length ? recent.map(rec => <div className="history-row" key={rec.id}><div className="history-icon"><CheckCircle2 size={19}/></div><div><strong>{rec.service_type}</strong><small>{fmtDate(rec.performed_at)} · {fmtNumber(rec.mileage)} mi</small></div><span>{fmtMoney(rec.cost)}</span></div>) : <div className="card-empty"><History size={29}/><strong>No service history yet</strong><span>Log a completed service to build your maintenance history.</span><button className="text-cta" onClick={openRecord}>Log service <ChevronRight size={15}/></button></div>}
                </section>
              </div>
            </>}
            {section === "tasks" && <><div className="page-heading"><div><span className="eyebrow">YOUR MAINTENANCE PLAN</span><h1>Maintenance tasks</h1><p>Manage scheduled services and log finished work.</p></div><button className="primary-button" onClick={() => openTask()}><Plus size={17}/> New task</button></div>
              <section className="content-card full-card"><div className="card-top"><div><h3>Scheduled maintenance</h3><p>{tasks.length} tasks for {vehicle.year} {vehicle.make} {vehicle.model}</p></div></div>
                {tasks.length ? [...tasks].sort((a, b) => ({ overdue: 0, due: 1, due_soon: 2, upcoming: 3, unscheduled: 4, completed: 5 })[a.status] - ({ overdue: 0, due: 1, due_soon: 2, upcoming: 3, unscheduled: 4, completed: 5 })[b.status]).map(t => <TaskRow key={t.id} task={t}/>) : <div className="card-empty"><Wrench size={30}/><strong>No tasks added yet</strong><span>Add your first oil change, tire rotation, or inspection.</span><button className="text-cta" onClick={() => openTask()}>Create a task <ChevronRight size={15}/></button></div>}
              </section></>}
            {section === "history" && <><div className="page-heading"><div><span className="eyebrow">EVERY SERVICE, ONE PLACE</span><h1>Service history</h1><p>Track completed work, spending, and mileage.</p></div><button className="primary-button" onClick={openRecord}><Plus size={17}/> Log service</button></div>
              <section className="content-card full-card"><div className="card-top"><div><h3>All service records</h3><p>{records.length} logged services</p></div></div>
                {records.length ? records.map(rec => <div className="record-row" key={rec.id}><div className="history-icon"><Activity size={18}/></div><div className="record-info"><strong>{rec.service_type}</strong><small>{fmtDate(rec.performed_at)} · {fmtNumber(rec.mileage)} mi</small>{rec.notes && <p>{rec.notes}</p>}{rec.parts && <p>Parts: {rec.parts}</p>}</div><span className="record-cost">{fmtMoney(rec.cost)}</span></div>) : <div className="card-empty"><History size={30}/><strong>Your service timeline is empty</strong><span>Start tracking what you've done to your vehicle.</span><button className="text-cta" onClick={openRecord}>Log your first service <ChevronRight size={15}/></button></div>}
              </section></>}
            {section === "vehicle" && <><div className="page-heading"><div><span className="eyebrow">YOUR VEHICLE PROFILE</span><h1>Vehicle details</h1><p>Keep your vehicle information and odometer up to date.</p></div><button className="primary-button" onClick={openVehicle}><Pencil size={17}/> Edit vehicle</button></div>
              <section className="content-card detail-card"><div className="detail-title"><div className="detail-vehicle-icon"><CarFront size={28}/></div><div><h3>{vehicle.year} {vehicle.make} {vehicle.model}</h3><p>Vehicle information</p></div></div>
                <div className="detail-grid">{([ ["Year",vehicle.year], ["Make", vehicle.make], ["Model", vehicle.model], ["Trim", vehicle.trim || "Not recorded"], ["Engine", vehicle.engine || "Not recorded"], ["VIN", vehicle.vin || "Not recorded"], ["Current mileage", `${fmtNumber(vehicle.odometer)} miles`] ] as [string, string | number][]).map(([k, v]) => <div className="detail-item" key={k}><span>{k}</span><strong>{v}</strong></div>)}</div>
                <div className="detail-footer"><button className="secondary-button" onClick={openOdometer}><Gauge size={17}/> Update odometer</button></div></section>
            </>}
          </>}
        </>}
      </div>
    </main>

    {modal && <div className="modal-backdrop" onMouseDown={e => { if (e.target === e.currentTarget) closeModal(); }}><div className="modal-panel" role="dialog" aria-modal="true" aria-label="Garage form">
      <div className="modal-head"><div><span className="eyebrow">MY GARAGE</span><h2>{modal === "vehicle" ? (vehicle ? "Edit vehicle" : "Add your vehicle") : modal === "task" ? (editingTask ? "Edit maintenance task" : "New maintenance task") : modal === "complete" ? "Complete maintenance" : modal === "record" ? "Log service" : "Update odometer"}</h2></div><button className="icon-button" onClick={closeModal} disabled={busy} aria-label="Close"><X size={20}/></button></div>
      {formError && <div className="alert form-alert"><AlertCircle size={18}/>{formError}</div>}
      {modal === "vehicle" && <form onSubmit={saveVehicle}><div className="form-grid"><TextField label="Year" value={vehicleForm.year} onChange={setVehicleField("year")} type="number" min="1886" max="2100" required/><TextField label="Make" value={vehicleForm.make} onChange={setVehicleField("make")} placeholder="e.g. Jeep" required/><TextField label="Model" value={vehicleForm.model} onChange={setVehicleField("model")} placeholder="e.g. Wrangler" required/><TextField label="Trim" value={vehicleForm.trim} onChange={setVehicleField("trim")} placeholder="e.g. Sport"/><TextField label="Engine" value={vehicleForm.engine} onChange={setVehicleField("engine")} placeholder="e.g. 3.6L V6"/><TextField label="VIN (optional)" value={vehicleForm.vin} onChange={setVehicleField("vin")} placeholder="17-character VIN"/>{!vehicle && <TextField label="Current odometer (mi)" value={vehicleForm.odometer} onChange={setVehicleField("odometer")} type="number" min="0" required/>}</div><div className="modal-footer"><button type="button" className="secondary-button" onClick={closeModal}>Cancel</button><button className="primary-button" type="submit" disabled={busy}>{busy ? "Saving..." : "Save vehicle"}</button></div></form>}
      {modal === "task" && <form onSubmit={saveTask}><div className="form-grid"><div className="form-span"><TextField label="Service name" value={taskForm.name} onChange={setTaskField("name")} placeholder="e.g. Engine oil change" required/></div><div className="form-span"><label className="field"><span>Notes (optional)</span><textarea rows={2} value={taskForm.description} onChange={e => setTaskField("description")(e.target.value)} placeholder="Any details or specifications"/></label></div>
        <div className="form-span form-divider"><strong>Next due</strong><small>Enter a date, mileage, or both. Either reaching its limit makes the task due.</small></div><TextField label="Due date" type="date" value={taskForm.next_due_date} onChange={setTaskField("next_due_date")}/><TextField label="Due at mileage" type="number" min="0" value={taskForm.next_due_mileage} onChange={setTaskField("next_due_mileage")} placeholder="e.g. 105000"/>
        <div className="form-span form-divider"><strong>Repeat after completion (optional)</strong><small>Completion automatically calculates the next due date or mileage from these intervals.</small></div><TextField label="Every N days" value={taskForm.interval_days} onChange={setTaskField("interval_days")} type="number" min="1" placeholder="e.g. 180"/><TextField label="Every N miles" value={taskForm.interval_miles} onChange={setTaskField("interval_miles")} type="number" min="1" placeholder="e.g. 5000"/></div><div className="modal-footer"><button type="button" className="secondary-button" onClick={closeModal}>Cancel</button><button className="primary-button" type="submit" disabled={busy}>{busy ? "Saving..." : "Save task"}</button></div></form>}
      {(modal === "record" || modal === "complete") && <form onSubmit={saveService}><div className="form-grid">{modal === "record" && <div className="form-span"><TextField label="Service performed" value={recordForm.service_type} onChange={setRecordField("service_type")} required placeholder="e.g. Replaced air filter"/></div>}{modal === "complete" && <div className="form-span task-to-complete"><CheckCircle2 size={18}/><strong>{editingTask?.name}</strong></div>}
        <TextField label="Service date" type="date" value={recordForm.performed_at} onChange={setRecordField("performed_at")} max={localToday()} required/><TextField label="Odometer (mi)" type="number" min="0" value={recordForm.mileage} onChange={setRecordField("mileage")} required/><TextField label="Cost ($)" type="number" min="0" value={recordForm.cost} onChange={setRecordField("cost")} placeholder="0.00"/><TextField label="Parts used (optional)" value={recordForm.parts} onChange={setRecordField("parts")} placeholder="e.g. Filter, oil"/><div className="form-span"><label className="field"><span>Notes (optional)</span><textarea rows={3} value={recordForm.notes} onChange={e => setRecordField("notes")(e.target.value)} placeholder="Describe the completed work"/></label></div></div>
        <div className="modal-footer"><button type="button" className="secondary-button" onClick={closeModal}>Cancel</button><button className="primary-button" type="submit" disabled={busy}>{busy ? "Saving..." : "Save service record"}</button></div></form>}
      {modal === "odometer" && <form onSubmit={saveOdometer}><p className="modal-note">Current reading: {fmtNumber(vehicle?.odometer ?? 0)} miles. New readings cannot be lower than your current odometer.</p><TextField label="New odometer reading (mi)" type="number" min={String(vehicle?.odometer ?? 0)} value={mileageInput} onChange={setMileageInput} required/><div className="modal-footer"><button type="button" className="secondary-button" onClick={closeModal}>Cancel</button><button className="primary-button" type="submit" disabled={busy}>{busy ? "Saving..." : "Update mileage"}</button></div></form>}
    </div></div>}
  </div>;
}
