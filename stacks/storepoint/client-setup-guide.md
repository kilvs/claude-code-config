# Store locator: what you need (client guide)

Ready to send a client. Swap the bits in [brackets]. Prices checked 25th Nov 2026; recheck the two
pricing links before sending if it's been a while.

---

Hi [name],

For the store locator I'll be using Storepoint. It shows a map and a list of your stores, and
visitors can search by suburb, city or postcode to find the closest one. Here's what it needs.

**1. A Storepoint account**
Sign up at https://storepoint.co. There's a 7-day free trial, and it asks for a card up front.
Plans are monthly, in USD:

- **Starter, $25/month:** up to 200 stores. You upload the store list as a spreadsheet.
- **Pro, $49/month:** up to 2,000 stores. It can sync from a Google Sheet daily, so you can update
  stores without logging in, and it includes visitor analytics.
- **Business, $99/month:** unlimited stores, syncs every 5 minutes, and removes the small
  Storepoint credit link.

For [number] stores, I'd suggest [Starter / Pro]. Full comparison: https://storepoint.co/pricing

Once it's set up, please add me as a team member ([email]) so I can set up the locator for you.

**2. A Mapbox account (the map itself)**
Storepoint draws the map with Mapbox, so it needs a Mapbox key.

- Sign up free at https://account.mapbox.com/auth/signup/
- The free tier covers 50,000 map views and 100,000 searches a month. Most store locators never
  go past that.
- If you don't add a card, Mapbox can't charge you. It just stops at the free limit.
- Before launch I'd recommend adding a card so I can lock the key to your website only. Then
  nobody else can use it. Pricing: https://www.mapbox.com/pricing

Once you're in, send me the token from https://account.mapbox.com/access-tokens/ or add me to the
account. It's a public key, so it's fine to share.

**3. Your store list**
Please fill in the attached spreadsheet, one row per store: store name, street address, suburb or
city, state or region, postcode and country. Phone, website and store type are optional.

**Updating your stores later**
On Pro, I can connect the store list to a Google Sheet. After that you just edit the sheet: add a
row for a new store, change a cell to update one, delete a row to remove one. Storepoint picks it
up once a day. On Starter, you send me the updated spreadsheet and I re-upload it.

**4. Where it goes**
Let me know which page it should sit on. I'll set it up on our staging site first so you can
try it before it goes live.

Any questions, just let me know.

---

**Attach:** `store-list-template.csv` (beside this file).
**Internal notes:** the setup steps and gotchas are in `README.md` beside this file.
