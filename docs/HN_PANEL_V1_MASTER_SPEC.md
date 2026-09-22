# HN Panel V1 — Master Specification

Status: LOCKED FOR IMPLEMENTATION
Target: `neshatiradiology.com/panel`
Product: HN Radiology Suite / HN Panel
Release principle: build in controlled phases, deploy once after end-to-end verification.

## 1. Goal

HN Panel is the operational reception + scheduling + radiologist worklist layer connected to HN Radiology Suite (HNRS).

The daily workflow must be:

Reception creates appointment / admission → patient appears in the selected center's daily list → radiologist sees today's worklist → one click opens the patient in HNRS with demographic and exam data prefilled → report is completed → panel status updates → prior visits remain available in Patient Registry.

The panel must be usable by secretary and radiologist without duplicate typing.

## 2. Roles

### Secretary
- Work only inside authorized center(s).
- Create/edit/cancel appointments and admissions.
- Register/search patients.
- See daily schedule for authorized center.
- See visit status.
- Must not manage radiologist-center permissions.

### Radiologist
- See worklist for authorized center(s).
- Switch active center.
- Open patient directly in HNRS.
- See prior visits/reports where permitted.
- Change operational status when appropriate.

### Admin
- Manage users, radiologist-center access, and center configuration.
- Admin controls must live in a separate Settings/Admin area, not on the main operational dashboard.

## 3. Main Dashboard

The main page must not be an admin console.

Top summary cards:
- Today: total appointments
- Tomorrow: total appointments
- Waiting / admitted
- Completed / reported

Controls:
- Active center selector
- Persian/Jalali date selector as the visible primary date
- Today button
- Tomorrow button
- Sync/refresh action
- Primary CTA: `+ پذیرش / نوبت جدید`

Gregorian dates may be stored internally but should not be the main date shown to Iranian users.

## 4. New Appointment / Admission Form

Required fields:
- First name
- Last name
- Patient ID / internal identifier
- Mobile number (optional unless clinic policy requires it)
- Exam type
- Center
- Appointment date (Jalali UI)
- Appointment time
- Referring physician
- Notes (optional)

Behavior:
- Search existing Patient Registry before creating duplicate patient.
- Persian digits must be accepted where numerical input is expected.
- Saving an appointment/admission must create or reuse the patient record.
- A Visit Number must be generated for each visit.
- Editing appointment information must update the daily schedule immediately.

## 5. Patient Registry

Patient Registry is organization-wide where permissions allow.

Search by:
- Patient name
- Patient ID
- Visit Number where useful

Patient detail:
- Demographics
- Prior appointments/visits
- Prior exam types
- Prior reports / report references when available
- Center of each prior visit

Do not force re-entry of an existing patient.

## 6. Daily Schedule

Views:
- Today
- Tomorrow
- Selected date

Each row should include:
- Appointment time
- Patient name
- Patient ID / Visit Number
- Exam type
- Referring physician
- Status
- Center
- Main action button

Useful sorting:
1. Appointment time
2. Admission/arrival order when relevant

## 7. Worklist State Machine

Use a controlled state machine rather than arbitrary free-text status.

Minimum statuses:
- Scheduled
- Admitted / Arrived
- Waiting
- In Progress
- Reported / Completed
- Cancelled
- No-show

Transitions must be auditable.

The UI should use clear Persian labels.

## 8. Radiologist Worklist

The radiologist should see only operational items, not admin settings.

For each patient:
- Name
- Time
- Exam
- Status
- Visit Number
- Open in HNRS button

Recommended main action label:
`باز کردن در HNRS`

## 9. HNRS Integration

This is a core V1 requirement.

When `باز کردن در HNRS` is pressed:
- Open HN Radiology Suite.
- Prefill first name and last name.
- Prefill Patient ID.
- Prefill center.
- Prefill referring physician when available.
- Pass Visit Number.
- Pass exam type.
- Route to the appropriate module when an exact module mapping exists.

Examples:
- OB exam → pregnancy/OB module
- Breast exam → breast/mammography module
- General ultrasound → general ultrasound module
- Doppler exam → corresponding Doppler workflow where mapped

Avoid duplicate patient typing.

Integration must use a stable internal handoff mechanism (server-side visit token, signed short-lived token, or another secure mechanism appropriate to the existing architecture). Do not expose sensitive patient data unnecessarily in plain URL query strings.

## 10. Status Synchronization With HNRS

At minimum:
- Opening case may set In Progress if workflow rules allow.
- Saving/finalizing report in HNRS should set Reported / Completed.
- Panel should refresh without requiring full page reload.

## 11. Centers

Initial centers already represented in the current panel:
- Navid
- Aramesh

Center permissions:
- Secretary sees authorized center(s).
- Radiologist sees assigned center(s).
- Admin can assign centers to radiologists/users.

The current `مراکز رادیولوژیست‌ها` section must be moved out of the main dashboard into:
`تنظیمات → کاربران و مراکز`

## 12. UI / UX

- RTL-first.
- Clean clinical UI.
- Persian labels for operational workflow.
- Jalali date in visible UI.
- Mobile-friendly enough for physician review on iPhone.
- Desktop-first efficiency for secretary workflow.
- Avoid large empty cards when no data exists; show useful empty states and a clear create action.
- Keep admin-only tools out of the daily workflow.

## 13. Audit / Safety

Audit important operations:
- Appointment creation
- Appointment edit
- Cancellation
- Status changes
- Patient merge/edit where supported
- Center assignment changes
- HNRS handoff
- Report completion sync

Audit record should include:
- user
- action
- timestamp
- affected entity
- previous/new value when relevant

## 14. Existing Work To Preserve

Do not regress already implemented infrastructure:
- Multi-center structure
- User/center permissions
- Patient Registry foundation
- Appointment/state-machine work already present
- Audit foundation
- Existing production HNRS functionality

Prefer patching current stable architecture rather than replacing the whole application.

## 15. Explicitly Out of Scope For V1

Do not delay V1 for:
- AI triage
- automatic clinical prioritization
- advanced analytics
- smart scheduling optimization
- predictive no-show model
- large dashboard BI
- unrelated redesign of HNRS reporting modules

These can be later phases.

## 16. Implementation Plan

### Phase A — Data / API completion
- Verify current schema.
- Complete Visit Number.
- Complete daily schedule queries.
- Complete appointment/admission CRUD.
- Complete validated status transitions.
- Preserve audit events.

### Phase B — Operational UI
- New appointment/admission form.
- Jalali date UI.
- Today/Tomorrow/selected date.
- Daily schedule.
- Radiologist worklist.
- Patient Registry detail view.
- Move admin center assignment to Settings.

### Phase C — HNRS handoff
- Secure visit handoff.
- Prefill patient + center + referring physician + Visit Number + exam type.
- Module routing where mapping is known.
- Report completion/status sync.

### Phase D — End-to-end verification
Test at minimum:
1. Create new patient + appointment in Navid.
2. Reuse existing patient without duplication.
3. Create next-day appointment.
4. Verify Today/Tomorrow counts.
5. Admit patient.
6. Patient appears in radiologist worklist.
7. Open in HNRS with correct prefill.
8. Finalize report.
9. Status becomes Reported/Completed.
10. Prior visit appears in Patient Registry.
11. Unauthorized user cannot access another center.
12. Admin center assignment still works from Settings.

## 17. Release Rule

Do not deploy partial phases to production for user evaluation.

Implementation may use multiple commits, but production deployment happens only after Phase D passes.

Keep rollback capability.

## 18. Acceptance Criteria

HN Panel V1 is accepted only when:
- Secretary can create a real appointment from the UI.
- Jalali date is the primary visible date.
- Today and Tomorrow schedules work.
- Visit Number exists and is visible where relevant.
- Radiologist worklist works.
- Patient can be opened in HNRS without retyping demographics.
- HNRS receives exam context.
- Completing the report updates panel status.
- Patient history is retained.
- Admin center-permission controls are removed from the main operational page.
- Navid and Aramesh permissions still function.
- No current HNRS production reporting workflow is broken.

## 19. Codex Execution Instruction

Use this file as the source of truth.

Before editing:
1. Inspect the repository and identify the current panel/backend implementation.
2. Do not rewrite stable unrelated modules.
3. Make small, reviewable commits by Phase A/B/C/D.
4. Run available tests/build/lint after each phase.
5. Add missing tests for critical workflow.
6. Do not deploy production until all acceptance criteria pass.
7. If the deployed Cloudflare Worker source differs from GitHub, stop before implementation and reconcile the actual latest source first. Do not overwrite newer production code with an older repository snapshot.
