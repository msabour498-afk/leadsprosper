# leadsprosper.com

Static site for Leads Prosper. Plain HTML, CSS, and JavaScript, with no framework and no build step on the host.

## Editing

All pages come from `build.py`. Change content or settings there, then run:

```
python3 build.py
```

Commit the regenerated `.html` files along with `build.py`.

Settings at the top of `build.py`:

- `phone`: when set, the floating button becomes "Text us" and "Call us", and the number appears in the footer, on the contact page and in structured data.
- `address`: when set, it appears in the footer and in structured data.
- `gtm_id` / `ga4_id`: when set, the analytics tag is added to every page.
- `form.provider`: `"hubspot"` (plus portal ID, form ID, region), `"formspree"` (plus endpoint), or `None`. With `None`, the visitor's email app opens with the details filled in.

## Hosting (Cloudflare Pages)

Framework preset None, no build command, output directory `/`. Pages serves `/services` from `services.html` and uses `404.html` for missing pages.

## dataLayer events

- `generate_lead`: a form was sent successfully (`form_id`: `audit` or `contact`, `form_destination`)
- `contact_click`: an email, phone or text link was clicked (`contact_method`, `link_location`)
- `lpTrack(event, data)` is available for future tools, such as `tool_used` and `tool_to_offer_click`. The audit form already reads `?tool=` and `?result=` from the URL and adds them to the message.
