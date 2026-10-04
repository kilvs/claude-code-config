# Forms

- Every input has a real, visible label — a placeholder is never the label. Related inputs are grouped with fieldset/legend.
- Required fields are marked. Error states are visible, specific, and placed at the field; the success state is designed (inline message or thank-you page), chosen deliberately, and actually configured.
- Correct input types (`email`, `tel`) and autocomplete attributes. No unnecessary fields — every field must earn its place.
- Field names are clean and consistent (Name, Email, Phone, Message) — they become the submission data columns and integration keys.
- Spam protection on every public form (Turnstile / reCAPTCHA or honeypot, per project standard).
- Submission destination verified: notification recipients set in form settings, and a real test submission completed before handoff.
- Never delete, rename, or restructure a live form's fields without checking existing submissions and connected integrations first.
