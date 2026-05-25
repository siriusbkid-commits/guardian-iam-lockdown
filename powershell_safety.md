\# PowerShell Safety Guide



> 📚 \*\*Learning Note:\*\* Understanding PowerShell command safety is a core skill

> for SC-300 and CyberArk Defender exams — and for real world operations.

> Read this section before running any script in this playbook.



\---



\## Understanding -WhatIf Mode



Every GUARDIAN script uses `-WhatIf` by default. Here is what that means:



\*\*Safe mode — shows what WOULD happen, makes NO changes:\*\*

```powershell

Remove-MgUser -UserId admin@company.com -WhatIf

```

Result: ✅ Displays what would happen. Nothing is changed.



\*\*Live mode — executes the REAL action:\*\*

```powershell

Remove-MgUser -UserId admin@company.com

```

Result: ⚠️ Executes immediately. Changes are real.



> ⚠️ \*\*GUARDIAN Rule:\*\* Always run `-WhatIf` first. Review the output carefully.

> When you are ready to apply — remove ONLY `-WhatIf`.

> Do NOT remove or modify the rest of the command.



\---



\## PowerShell Command Risk Levels



Not all PowerShell commands are equal. GUARDIAN labels every script with

one of the following risk levels so you always know what you are working with:



\### 🟢 Low Risk — Read Only

Safe discovery and audit commands. No changes are made.



\*\*Examples:\*\*

```powershell

Get-MgUser

Get-MgRoleManagementDirectoryRoleAssignment

Get-LocalGroupMember

Get-MgSubscribedSku

```



\*\*Characteristics:\*\*

\- No changes made to your environment

\- Safe for beginners to run

\- Used for auditing and discovery

\- Can be run at any time without approval



\---



\### 🟡 Medium Risk — Configuration Changes

Modifies policies or settings. Usually reversible but should be tested first.



\*\*Examples:\*\*

```powershell

Update-MgPolicyRoleManagementPolicyRule

Set-ExecutionPolicy

auditpol /set

Update-MgUser

```



\*\*Characteristics:\*\*

\- Changes your security posture

\- Always use `-WhatIf` first

\- Test in non-production environment before applying

\- Document what you changed and why

\- Have a rollback plan ready



\---



\### 🔴 High Risk — Destructive or Privileged Actions

Can remove access, lock accounts, or significantly impact production.



\*\*Examples:\*\*

```powershell

Remove-MgUser

Remove-MgRoleAssignment

Set-MsolUserPassword

Disable-MgUser

```



\*\*Characteristics:\*\*

\- Can cause outages if run incorrectly

\- Can remove admin access — including your own

\- Requires approval and change control in most organisations

\- Always run backup script first

\- Should be reviewed by a second person before applying



\---



\### ⚫ Critical Risk — Tenant-Wide Impact

Actions affecting your entire organisation's security posture.



\*\*Examples:\*\*

```powershell

\# Changes to:

\# - Global Administrator role

\# - Conditional Access policies

\# - Break glass accounts

\# - MFA enforcement tenant-wide

\# - Audit log settings

```



\*\*Characteristics:\*\*

\- Affects every user in your organisation

\- Can lock everyone out if misconfigured

\- Requires senior approval and CAB/change management process

\- Must be tested in a lab environment first

\- Rollback plan is mandatory



\---



\## The Golden Rules



Before running ANY script from this playbook:



1\. ✅ \*\*Run the backup script first\*\* — always create a restore point

2\. ✅ \*\*Use -WhatIf first\*\* — review what will happen before it happens

3\. ✅ \*\*Test in non-production\*\* — never test changes on live systems

4\. ✅ \*\*Document everything\*\* — record what you changed, when, and why

5\. ✅ \*\*Have a rollback plan\*\* — know how to undo the change before you make it

6\. ✅ \*\*Get a second pair of eyes\*\* — for 🔴 and ⚫ risk commands



\---



\## Command Type Quick Reference



| Prefix | Risk Level | Makes Changes? | Use -WhatIf? |

|--------|-----------|----------------|--------------|

| Get-\* | 🟢 Low | No | Not needed |

| Find-\* | 🟢 Low | No | Not needed |

| Write-Host | 🟢 Low | No | Not needed |

| Update-\* | 🟡 Medium | Yes | Always |

| Set-\* | 🟡 Medium | Yes | Always |

| New-\* | 🟡 Medium | Yes | Always |

| Add-\* | 🟡 Medium | Yes | Always |

| Remove-\* | 🔴 High | Yes | Always |

| Disable-\* | 🔴 High | Yes | Always |

| Delete-\* | 🔴 High | Yes | Always |

| Tenant-wide | ⚫ Critical | Yes | Mandatory + approval |



\---



\## How This Maps to Real Enterprise Operations



These risk levels align with professional IT frameworks you will encounter

in SC-300 and real world security roles:



| GUARDIAN Risk | ITIL Change Type | ISO 27001 | NIST |

|---------------|-----------------|-----------|------|

| 🟢 Low | Standard Change | A.9.4 | PR.AC |

| 🟡 Medium | Normal Change | A.9.2 | PR.AC-4 |

| 🔴 High | Emergency Change | A.9.2.3 | PR.AC-6 |

| ⚫ Critical | Major Change | A.9.2.3 | PR.AC-6 |



> 📚 \*\*SC-300 Note:\*\* Understanding change management for privileged access

> is tested in the SC-300 exam under Identity Governance.

> CyberArk Defender also tests dual control and approval workflows

> which map directly to 🔴 and ⚫ risk operations.



\---



\## If Something Goes Wrong



If you accidentally run a command without `-WhatIf` and something changes:



1\. \*\*Don't panic\*\* — most changes are reversible

2\. \*\*Stop immediately\*\* — don't run more commands

3\. \*\*Check the backup\*\* — restore from the backup script output

4\. \*\*Review audit logs\*\* — Azure Portal > Entra ID > Monitoring > Audit Logs

5\. \*\*Contact support\*\* — Microsoft support if needed



> ⚠️ \*This guide is part of the GUARDIAN Lockdown Playbook.

> Always validate against your organisation's change management procedures.\*

