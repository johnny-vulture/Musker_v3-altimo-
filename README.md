# Musker v3

A Django web application that combines social networking with cryptocurrency portfolio tracking and head-to-head portfolio challenges. Users can follow each other, manage crypto holdings via the CoinGecko API, and compete in portfolio performance battles.

## Features

- **Authentication** — Register, login, logout, and profile editing
- **Social profiles** — Bio, profile image, social links, follow/unfollow system
- **Bitcoin wallets** — SegWit testnet wallet auto-created on registration (`bitcoinlib`)
- **Crypto portfolio** — Search coins, add/remove holdings, track total portfolio value
- **Dashboard** — Top 10 cryptocurrencies by market cap plus 24h price changes for user holdings
- **Portfolio challenges** — Challenge another user to a portfolio performance match on a set date
- **Challenge invoices** — Snapshot of both portfolios when a challenge is accepted
- **Notifications** — Created when a challenge is accepted
- **Admin panel** — Manage users, profiles, challenges, portfolios, and more

## Tech Stack

| Layer | Technology |
|-------|------------|
| Backend | Django 5.0.4 |
| Database | SQLite (default) |
| Frontend | Bootstrap 5, Font Awesome |
| Crypto data | [CoinGecko API](https://www.coingecko.com/en/api) |
| Bitcoin | `bitcoinlib` (testnet) |
| Images | Pillow |

## Project Structure

```
Musker_v3-altimo--main/
├── manage.py                 # Django CLI entry point
├── requirements.txt          # Python dependencies
├── social/                   # Django project configuration
│   ├── settings.py             # App settings, DB, email, media
│   ├── urls.py                 # Root URL routing + media serving
│   ├── wsgi.py
│   └── asgi.py
└── musker/                   # Main application
    ├── models.py               # Profile, Portfolio, Challenge, Cryptocurrency, etc.
    ├── views.py                # Request handlers
    ├── urls.py                 # App URL routes
    ├── forms.py                # SignUp, Profile, Challenge, Portfolio forms
    ├── signals.py              # Challenge accept/reject side effects
    ├── admin.py                # Django admin configuration
    ├── apps.py                 # App config (loads signals)
    ├── migrations/             # Database migrations
    └── templates/              # HTML templates (Bootstrap)
        ├── base.html
        ├── navbar.html
        ├── home.html
        ├── login.html / register.html
        ├── profile.html / profile_list.html
        ├── portfolio.html / dash.html
        ├── create_challenge.html / user_challenges.html
        └── crypto_search_form.html / crypto_search_result.html
```

## Data Models

| Model | Purpose |
|-------|---------|
| `Profile` | One-to-one with `User`; bio, image, social links, follow graph |
| `Portfolio` | Per-user portfolio with total USD value |
| `Cryptocurrency` | Individual coin holdings (name, symbol, price, quantity) |
| `Challenge` | Portfolio battle between sender and receiver |
| `ChallengeInvoice` | Portfolio snapshot when a challenge is accepted |
| `Notification` | Sent when a challenge is accepted |

## URL Routes

| Path | View | Description |
|------|------|-------------|
| `/` | `home` | Home page with challenges and invoices |
| `/register/` | `register_user` | Create account + Bitcoin testnet wallet |
| `/login/` | `login_user` | Sign in |
| `/logout` | `logout_user` | Sign out |
| `/update_user/` | `update_user` | Edit profile and account info |
| `/profile_list/` | `profile_list` | Browse other users |
| `/profile/<pk>` | `profile` | View a user profile |
| `/profile/followers/<pk>` | `followers` | List followers |
| `/profile/follows/<pk>` | `follows` | List following |
| `/follow/<pk>` | `follow` | Follow a user |
| `/unfollow/<pk>` | `unfollow` | Unfollow a user |
| `/portfolio/` | `portfolio_view` | View and manage holdings |
| `/dash/` | `dash_view` | Crypto market dashboard |
| `/crypto/` | `search_crypto` | Search coins via CoinGecko |
| `/add_to_portfolio/` | `add_to_portfolio_view` | Add coin to portfolio |
| `/delete_from_portfolio/<pk>/` | `delete_from_portfolio_view` | Remove coin |
| `/fight/` | `challenge_page` | Create a challenge form |
| `/fight1/` | `create_challenge` | Submit a challenge |
| `/user_challenges/` | `user_challenges` | Incoming challenges |
| `/accept/<challenge_id>/` | `accept_challenge` | Accept a challenge |
| `/reject/<challenge_id>/` | `reject_challenge` | Reject a challenge |
| `/admin/` | Django admin | Admin interface |

## Getting Started

### Prerequisites

- Python 3.10+
- pip

### Installation

1. **Clone the repository**

   ```bash
   git clone <repository-url>
   cd Musker_v3-altimo--main
   ```

2. **Create and activate a virtual environment**

   ```bash
   python -m venv venv

   # Windows
   venv\Scripts\activate

   # macOS / Linux
   source venv/bin/activate
   ```

3. **Install dependencies**

   ```bash
   pip install -r requirements.txt
   ```

4. **Run migrations**

   ```bash
   python manage.py migrate
   ```

5. **Create a superuser (optional, for admin access)**

   ```bash
   python manage.py createsuperuser
   ```

6. **Start the development server**

   ```bash
   python manage.py runserver
   ```

7. Open [http://127.0.0.1:8000/](http://127.0.0.1:8000/) in your browser.

## How It Works

### Registration flow

1. User submits the sign-up form.
2. A `Profile` and empty `Portfolio` are created automatically via a `post_save` signal on `User`.
3. A Bitcoin SegWit testnet wallet is generated with `bitcoinlib` on signup.

### Portfolio management

1. Search for a coin on `/crypto/` (CoinGecko search API).
2. Add it to your portfolio with a quantity.
3. Current price is fetched from CoinGecko and stored; total portfolio value is recalculated on each visit to `/portfolio/`.

### Challenge flow

1. Sender creates a challenge targeting another user's username and a match date.
2. Receiver accepts or rejects on `/user_challenges/`.
3. On accept, a `Notification` and `ChallengeInvoice` are created with both users' portfolio values at that moment.
4. On reject, the challenge record is deleted.

## External APIs

- **CoinGecko** — Used for coin search, market data, and price lookups. Free tier has rate limits (~10–30 calls/min); the dashboard is designed with this in mind.
- **Bitcoin testnet** — Wallets are created on registration; no mainnet funds are involved.

## Development Notes

- Media uploads (profile images) are stored in `media/` and served in development via `social/urls.py`.
- Signals in `musker/signals.py` are loaded through `MuskerConfig.ready()` in `apps.py`.
- The legacy `Meep` model was removed in migration `0013_delete_meep.py`.

## License

**Proprietary — All Rights Reserved**

Copyright © 2026 Aaron. All rights reserved.

This software and its source code may not be copied, modified, distributed, or used in any way without the express written permission of the copyright holder. See [LICENSE](LICENSE) for full terms.
