# WAHA API Reference — Cheat Sheet

> Verifikasi terhadap instance WAHA **2026.6.2, engine GOWS, tier PLUS**.
> Auth: header `X-Api-Key: <key>`. Base: `https://waha-anda.example`.

## Sessions

| Aksi | Method | Path | Body/Params |
|---|---|---|---|
| List sessions | GET | `/api/sessions` | `?all=true` untuk include stopped |
| Get session | GET | `/api/sessions/{name}` | |
| Create session | POST | `/api/sessions` | `{"name":"x","start":true,"config":{...}}` |
| Update session | PUT | `/api/sessions/{name}` | full config |
| Delete session | DELETE | `/api/sessions/{name}` | (juga logout) |
| Start session | POST | `/api/sessions/{name}/start` | idempotent |
| Stop session | POST | `/api/sessions/{name}/stop` | idempotent |
| Restart session | POST | `/api/sessions/{name}/restart` | |
| Logout | POST | `/api/sessions/{name}/logout` | hapus linked device |
| Get QR | GET | `/api/{session}/auth/qr` | `?format=image\|raw`, atau `Accept: application/json` base64 |
| Request pairing code | POST | `/api/{session}/auth/request-code` | `{"phoneNumber":"628..."}` |
| Get me | GET | `/api/sessions/{session}/me` | |
| Screenshot | GET | `/api/screenshot?session=x` | `Accept: application/json` base64 |

**Status values:** `STOPPED`, `STARTING`, `SCAN_QR_CODE`, `PASSKEY_REQUIRED`,
`PASSKEY_CONFIRMATION_REQUIRED`, `WORKING`, `FAILED`.

## Send messages

| Aksi | Method | Path | Body |
|---|---|---|---|
| Send text | POST | `/api/sendText` | `{session, chatId, text, reply_to?, mentions?, linkPreview?}` |
| Send image | POST | `/api/sendImage` | `{session, chatId, file:{url\|data,mimetype,filename}, caption}` |
| Send file/doc | POST | `/api/sendFile` | `{session, chatId, file:{...}, caption}` |
| Send voice | POST | `/api/sendVoice` | `{session, chatId, file:{...}, convert?}` (OPUS/OGG) |
| Send video | POST | `/api/sendVideo` | `{session, chatId, file:{...}, caption?, asNote?, convert?}` |
| Send location | POST | `/api/sendLocation` | `{session, chatId, latitude, longitude, title?, address?}` |
| Send contact vCard | POST | `/api/sendContactVcard` | `{session, chatId, contact:{name, phone}}` |
| Send poll | POST | `/api/sendPoll` | `{session, chatId, poll:{name, options[], multipleAnswers}}` |
| Reaction | POST | `/api/reaction` | `{session, chatId, messageId, reaction:"👍"}` |
| Forward | POST | `/api/forwardMessage` | `{session, chatId, message}` |
| Custom link preview | POST | `/api/send/link-custom-preview` | |
| Reply buttons | POST | `/api/send/buttons/reply` | |

**Anti-ban sequence (sebelum sendText):**
1. `POST /api/sendSeen` `{session, chatId}` — mark read
2. `POST /api/startTyping` `{session, chatId}`
3. Sleep random (12-45s + length factor)
4. `POST /api/stopTyping` `{session, chatId}`
5. `POST /api/sendText`

## Read messages/chats

| Aksi | Method | Path | Params |
|---|---|---|---|
| Get chats | GET | `/api/chats` | `?session=&limit=&offset=` |
| Get messages (chat) | GET | `/api/messages` | `?chatId=X%40c.us&session=&limit=&downloadMedia=false` |
| Get 1 message | GET | `/api/{session}/chats/{chatId}/messages/{messageId}` | |
| Search messages | (via filter params) | `/api/messages` | |
| Download media | GET | `/api/files/{filename}` | `X-Api-Key` header |

> **Escape `@`**: untuk chatId `628xxx@c.us` di query string → `628xxx%40c.us`.

## Contacts

| Aksi | Method | Path | Params |
|---|---|---|---|
| All contacts | GET | `/api/contacts/all` | `?session=&limit=&offset=&sortBy=&sortOrder=` |
| Single contact | GET | `/api/contacts` | `?contactId=&session=` |
| Update contact | PUT | `/api/{session}/contacts/{chatId}` | `{firstName, lastName}` |
| Check exists | GET | `/api/contacts/check-exists` | `?phone=&session=` |
| About | GET | `/api/contacts/about` | `?contactId=&session=` |
| Profile picture | GET | `/api/contacts/profile-picture` | `?contactId=&session=&refresh=` |
| Block | POST | `/api/contacts/block` | `{contactId, session}` |
| Unblock | POST | `/api/contacts/unblock` | `{contactId, session}` |

**LID resolution** (Linked ID → phone):
| Aksi | Method | Path |
|---|---|---|
| All LIDs | GET | `/api/{session}/lids` |
| LID count | GET | `/api/{session}/lids/count` |
| LID → phone | GET | `/api/{session}/lids/{lid}` |
| phone → LID | GET | `/api/{session}/lids/pn/{phoneNumber}` |

## Groups

| Aksi | Method | Path | Body/Params |
|---|---|---|---|
| List groups | GET | `/api/{session}/groups` | `?limit=&offset=&exclude=participants` |
| Group count | GET | `/api/{session}/groups/count` | |
| Create group | POST | `/api/{session}/groups` | `{name, participants:[{id}]}` |
| Group info | GET | `/api/{session}/groups/{groupId}` | |
| Refresh groups | POST | `/api/{session}/groups/refresh` | **jarang-jangan, rate limit** |
| Join via invite | POST | `/api/{session}/groups/join` | `{code:"..."}` |
| Leave group | POST | `/api/{session}/groups/{groupId}/leave` | |
| Delete group | DELETE | `/api/{session}/groups/{groupId}` | |
| Set subject | PUT | `/api/{session}/groups/{groupId}/subject` | `{subject}` |
| Set description | PUT | `/api/{session}/groups/{groupId}/description` | `{description}` |
| Set picture | PUT | `/api/{session}/groups/{groupId}/picture` | `{file:{url\|data}}` |
| **Participants** | | | |
| Get participants | GET | `/api/{session}/groups/{groupId}/participants` | |
| Add | POST | `/api/{session}/groups/{groupId}/participants/add` | `{participants:[{id}]}` |
| Remove | POST | `/api/{session}/groups/{groupId}/participants/remove` | `{participants:[{id}]}` |
| Promote admin | POST | `/api/{session}/groups/{groupId}/admin/promote` | `{participants:[{id}]}` |
| Demote admin | POST | `/api/{session}/groups/{groupId}/admin/demote` | `{participants:[{id}]}` |
| **Security** | | | |
| Info admin-only | PUT | `/api/{session}/groups/{groupId}/settings/security/info-admin-only` | `{adminsOnly:true}` |
| Messages admin-only | PUT | `/api/{session}/groups/{groupId}/settings/security/messages-admin-only` | `{adminsOnly:true}` |
| Member-add mode | PUT | `/api/{session}/groups/{groupId}/settings/security/member-add-mode` | `{membersCanAddNewMember:true}` |
| **Invite codes** | | | |
| Get invite code | GET | `/api/{session}/groups/{groupId}/invite-code` | |
| Revoke invite | POST | `/api/{session}/groups/{groupId}/invite-code/revoke` | |

> Group ID format: `12036340xxxx@g.us`. Field names di GOWS engine:
> `Name`, `JID`, `ParticipantCount`, `Participants[]`, `OwnerJID`, `IsAnnounce`, dll.

## Labels (WhatsApp Business)

> Butuh WhatsApp **Business** account/app. Tidak jalan di WhatsApp biasa.

| Aksi | Method | Path | Body |
|---|---|---|---|
| List labels | GET | `/api/{session}/labels` | |
| Create label | POST | `/api/{session}/labels` | `{name, color}` (color int 0-20, atau colorHex) |
| Update label | PUT | `/api/{session}/labels/{labelId}` | `{name, color}` |
| Delete label | DELETE | `/api/{session}/labels/{labelId}` | |
| Chats by label | GET | `/api/{session}/labels/{labelId}/chats` | |
| Labels for chat | GET | `/api/{session}/labels/chats/{chatId}/` | |
| Set labels on chat | PUT | `/api/{session}/labels/chats/{chatId}/` | `{labels:[{id}]}` (full list, replaces) |

> Color int lebih stabil dari colorHex (bisa berubah versi).

## Webhooks/Events

**Setup** (di session create/update):
```json
{
  "name": "default",
  "config": {
    "webhooks": [{
      "url": "https://yourapp.com/webhook",
      "events": ["message", "message.ack", "session.status"],
      "hmac": { "key": "secret-string" }
    }]
  }
}
```

**Event types:**
- Session: `session.status`
- Messages: `message`, `message.any`, `message.reaction`, `message.ack`,
  `message.ack.group`, `message.waiting`, `message.edited`, `message.revoked`
- Chats: `chat.archive`
- Groups: `group.v2.join`, `group.v2.leave`, `group.v2.participants`, `group.v2.update`
- Presence: `presence.update`
- Polls: `poll.vote`, `poll.vote.failed`
- Labels: `label.upsert`, `label.deleted`, `label.chat.added`, `label.chat.deleted`
- Calls: `call.received`, `call.accepted`, `call.rejected`

**HMAC verify:**
- WAHA kirim header `X-Webhook-Hmac` (SHA-512 hex) + `X-Webhook-Hmac-Algorithm: sha512`
- Verifikasi: `hmac_sha512(raw_body, secret_key).hexdigest() == header`

**Payload structure** (incoming message):
```json
{
  "event": "message",
  "session": "all-in-one-device",
  "me": {"id": "...@c.us", "pushName": "..."},
  "payload": {
    "id": "true_...@c.us_...",
    "from": "...@c.us",
    "fromMe": false,
    "to": "...@c.us",
    "body": "Halo!",
    "hasMedia": false,
    "timestamp": 1667561485
  },
  "engine": "GOWS"
}
```

## Config env vars (relevant)

| Var | Default | Effect |
|---|---|---|
| `WAHA_GOWS_STATUS_PARTICIPANTS_BATCH_SIZE` | 500 | Batch size untuk status@broadcast |
| `WAHA_SESSION_CONFIG_IGNORE_STATUS` | false | Skip event dari status@broadcast |
| `WAHA_SESSION_CONFIG_IGNORE_BROADCAST` | false | Skip event broadcast list |
| `WAHA_APPS_JOBS_CONCURRENCY` | 50 | Max concurrent background jobs |
| `WHATSAPP_START_ALL_SESSIONS_ON_START` | true | Auto-restart STOPPED sessions |
| `WAHA_AUTO_START_DELAY_SECONDS` | 0 | Stagger session startup |

## Sumber
- Docs: https://waha.devlike.pro/docs/how-to/
- Swagger: https://waha.devlike.pro/swagger/
- Anti-ban: https://waha.devlike.pro/docs/overview/how-to-avoid-blocking/
- GitHub: https://github.com/devlikeapro/waha
