---
name: Bug report
about: Create a report to help us improve
title: ''
labels: bug
assignees: ''

---

**Describe the bug**
A clear and concise description of what the bug is.

**Config**
Your anonymized config entry

**Versions**
HA Version an deployment
HACS version
Integration version


**Debug logs**
Add to configuration.yaml:
```
logger:
  default: warning
  logs:
    custom_components.solis: debug
```
And attach the resulting log to the issue. If yo do not know where to find logs you missed an important step in the install of HACS. ;-)

**Screenshots**
If applicable, add screenshots to help explain your problem.
