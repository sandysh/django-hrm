# Template Update Examples

## File 1: templates/core/admin_dashboard.html

### Add at top (after {% extends 'base.html' %}):
```html
{% load attendance_tags %}
```

### Find (around line 113):
```html
<tr {% if attendance.is_late or attendance.status == 'LT' %}style="background-color: #FEE2E2;" {% endif %}>
```

### Replace with:
```html
{% is_late attendance.check_in_time attendance.date as late_status %}
<tr {% if late_status %}style="background-color: #FEE2E2;" {% endif %}>
```

### Find (around line 118):
```html
{% if attendance.is_late %}
    <span style="color: #DC2626; font-size: 0.75rem; margin-left: 0.25rem;">⏰</span>
{% endif %}
```

### Replace with:
```html
{% if late_status %}
    <span style="color: #DC2626; font-size: 0.75rem; margin-left: 0.25rem;">⏰</span>
{% endif %}
```

### Find (around line 125-128):
```html
{% if attendance.status == 'PR' %}
    <span class="badge badge-success">Present</span>
{% elif attendance.status == 'LT' %}
    <span class="badge badge-warning">Late</span>
```

### Replace with:
```html
{% if late_status %}
    <span class="badge badge-warning">Late</span>
{% elif attendance.status == 'HL' %}
    <span class="badge badge-info">Half Day</span>
{% elif attendance.status == 'AB' %}
    <span class="badge badge-danger">Absent</span>
{% else %}
    <span class="badge badge-success">Present</span>
```

---

## File 2: templates/attendance/report.html

### Add at top:
```html
{% load attendance_tags %}
```

### Find:
```html
{% if record.is_late %}
```

### Replace with:
```html
{% is_late record.check_in_time record.date as late_status %}
{% if late_status %}
```

---

## File 3: templates/attendance/my_attendance.html

### Add at top:
```html
{% load attendance_tags %}
```

### Find:
```html
{% if record.is_late %}
```

### Replace with:
```html
{% is_late record.check_in_time record.date as late_status %}
{% if late_status %}
```

---

## File 4: templates/attendance/punch.html

### Add at top:
```html
{% load attendance_tags %}
```

### Find:
```html
{% if today_attendance.is_late %}
```

### Replace with:
```html
{% is_late today_attendance.check_in_time today_attendance.date as late_status %}
{% if late_status %}
```

---

## Quick Find & Replace

You can use these sed commands:

```bash
cd /Users/sandy/projects/python/hrm/templates

# Add template tag to each file
sed -i '' '2i\
{% load attendance_tags %}
' core/admin_dashboard.html attendance/report.html attendance/my_attendance.html attendance/punch.html

# Note: You'll still need to manually update the {% if attendance.is_late %} checks
# to use {% is_late ... as late_status %} {% if late_status %}
```

---

**After making these changes, restart your Django server and the late calculation will use SystemSettings!** ✅
