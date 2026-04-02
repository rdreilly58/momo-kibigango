# Email Accounts & Sending Methods

## Accounts
| Account | Provider | Status | Use For |
|---------|----------|--------|---------|
| **reillyrd58@gmail.com** | Gmail | ✅ Active | Primary personal, receiving, work email |
| **rdreilly2010@gmail.com** | Gmail | ✅ Active | Default sender (has app password) |
| **robert@reillydesignstudio.com** | Google Workspace | ⏳ Pending | Design studio email |
| **Robert.D.Reilly@Leidos.com** | Leidos | Work | Leidos work email |

## Default Sending: gmail-send skill
- Sender: `rdreilly2010@gmail.com`
- App password: configured
- Script: `~/.openclaw/workspace/skills/gmail-send/scripts/send_email.py`

## Default Reading: gog gmail search
- Account: `reillyrd58@gmail.com`
- Fast (2-5s), already authenticated
- `gog gmail search -a reillyrd58@gmail.com "query"`

## Calendar & Tasks
- Account: `reillyrd58@gmail.com` (primary) or `rdreilly2010@gmail.com`
- `gog calendar list -a reillyrd58@gmail.com`
- Task List ID: `MDE3Mjg4NDY4MTYwNjc5NDE0MDY6MDow`
