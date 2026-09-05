FITGEAR Store — updated version

Run:
  pip install -r requirements.txt
  python app.py
Then open http://127.0.0.1:5000

Updates in this version:
- Added FITGEAR favicon for the browser tab.
- Removed the top free-delivery/announcement bar.
- Redesigned login and signup as a split-screen experience.
- Removed sale/discount pricing and crossed-out prices.
- Updated product prices to realistic Egyptian EGP ranges.
- Removed the extra promotional/recovery sections from the bottom of the homepage.
- Reworked the cart into a clear slide-out shopping bag with images, quantity controls, remove buttons, subtotal and checkout.
- Replaced illustrated product artwork with realistic fitness photography.
- Added the same realistic images to category cards and product pages.

Photo sources:
The product and fitness photos use free-to-use Pexels photo CDN images. The site requires an internet connection to display these remote images.

- Removed all pre-populated/fake product reviews and fake review counts.
- Added real customer reviews stored in SQLite.
- Review submission requires a logged-in FITGEAR account.
- Each account can post one review per product; rating is 1–5 stars and comments are limited to 1000 characters.
- Product ratings and review counts are calculated from submitted reviews only.
- Expanded the catalog to 18 fitness accessories across all six categories.


ACCOUNT EMAILS
--------------
Email verification has been removed. Accounts are created immediately and can log in
without receiving or clicking a verification email. No SMTP configuration is required.
Signup still uses the browser's standard email field validation.
