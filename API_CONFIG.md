# API Configuration (UPDATED)

## ShortAPI → Kling/Vidu (Video Generation)

**Endpoint:** `https://api.shortapi.ai/api/v1/job/create`

**Auth:** `Authorization: Bearer $SHORTAPI_KEY`

**New Key (Active):** `ak-7e46a3e237a211f1bc0caaba74064af8`

**Strategy:** POLLING (not callbacks)
- Submit job → get job_id
- Poll /job/status/$job_id every 30s
- When status == "completed", download video from URL in response

**Models Available:**
- `kwaivgi/kling-o1/text-to-video` (5 or 10 sec)
- `kwaivgi/kling-o1/image-to-video` (with reference images)
- `vidu/vidu-q2/text-to-video` (any length)

---

This is the working flow. Build around polling, not webhooks.
