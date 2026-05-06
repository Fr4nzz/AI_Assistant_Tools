---
name: d2l
description: Use this skill whenever the user asks about D2L, Brightspace, USFQ courses, classes, assignments, deadlines, grades, announcements, LMS notifications, course content, course calendar, unread class items, assignment feedback, or downloading course files. This skill uses the local read-only `d2l` CLI command.
metadata:
  requires:
    bins: ["d2l"]
---

# D2L / Brightspace LMS CLI

Use the local read-only `d2l` command for USFQ D2L/Brightspace. Do not say there is no D2L connector before trying this CLI.

The CLI uses the shared Outlook/Office Chromium profile by default and Chrome DevTools Protocol to obtain authenticated D2L cookies. This lets one Microsoft login bootstrap Outlook, OneDrive, and D2L. Override with `D2L_BROWSER_DATA_DIR` only when an isolated D2L profile is needed. Default CDP port is `18801`; avoid `18800` on Franz's setup because it may be bound by an SSH tunnel.

## Core Commands

```powershell
d2l classes
d2l login
d2l announcements
d2l announcements --course COURSE_ID
d2l notifications
d2l assignments
d2l assignments --course COURSE_ID
d2l assignment ASSIGNMENT_ID
d2l grades
d2l grades --course COURSE_ID
d2l deadlines
d2l content
d2l content --course COURSE_ID
d2l calendar --days 14
d2l feedback ASSIGNMENT_ID
d2l download CONTENT_PATH_OR_TOPIC_ID --output ./file.ext
d2l schedule
d2l unread
```

Prefer `--json` when parsing results programmatically:

```powershell
d2l --json classes
d2l --json assignments
d2l --json deadlines
d2l --json grades --course COURSE_ID
```

## Workflow

1. Start with `d2l --json classes` to get course IDs.
2. For pending work, use `d2l --json deadlines`, `d2l --json assignments`, and `d2l --json calendar --days 14`.
3. For course-specific context, use `--course COURSE_ID`.
4. For an assignment, use `d2l assignment ASSIGNMENT_ID`; use `d2l feedback ASSIGNMENT_ID` when the user asks about grades/comments/feedback.
5. For course materials, use `d2l content --course COURSE_ID`; download only files needed for the task.

## Login Safety

Do not repeatedly retry failed logins. If the CLI says the D2L session is missing or auto-login failed, stop and ask the user to log in manually using the D2L helper browser/profile.

For manual login, tell the user to run `d2l login`, sign in through the visible browser if needed, choose "Stay signed in" if prompted, wait until D2L loads, then close that browser before retrying headless commands. If the user already logged into Outlook/OneDrive with the shared profile, D2L may only need a quick SSO redirect rather than a full password login.

Do not print cookies or tokens. Do not expose private course/classmate information unnecessarily.

## Safety

This integration is read-only. Do not submit assignments, delete content, edit content, send messages, or change grades.
