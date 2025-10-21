# Auto SRP

![pypi latest version](https://img.shields.io/pypi/v/autosrp?label=latest)
![python versions](https://img.shields.io/pypi/pyversions/autosrp)
![django versions](https://img.shields.io/badge/django-3.2%2B-blue)
![license](https://img.shields.io/badge/license-GPLv3-green)

A streamlined Ship Replacement Program (SRP) management app for [AllianceAuth](https://gitlab.com/allianceauth/allianceauth).

## Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Installation](#installation)
- [Updating](#updating)
- [Settings](#settings)
- [Permissions](#permissions)

## Overview

Auto SRP helps alliances and corporations manage ship replacement submissions, reviews,
and payouts end to end. Automatically. Without user submissions.

**This project requires Fittings and EveUniverse to be installed.**

## Key Features

- FC-driven submissions
  - Pilots do not submit losses, FCs (or users with the submit permission) create SRP reports.
  - Automatic: paste a zKill “related” link or a **_(beta)_** EVE Tools BR link to auto-fill systems and time.
  - Manual: specify systems and time window, the expected doctrine, and eligible alliances/corporations (org filter.
    ![fc/Submit SRP](https://i.imgur.com/n7YZtFJ.gif)
  - FCs have access to see reports they have submitted.
    ![fc/My Submissions](https://i.imgur.com/jTVOYnf.png)

- Doctrine fit matching (https://gitlab.com/colcrunch/fittings)
  - Losses are matched against doctrine fits automatically.
  - Reviewers can change the selected fit and re-run the fit check at any time.

- Payout calculation and overrides
  - Suggested payouts are computed from base rewards (if configured, otherwise it uses market data) with configurable penalty schemes.
  - Reviewers can override the payout per kill when needed.
  - The application provides a detailed report of the match, including the doctrine, the fit, and the payout. Simply click details.
    ![](https://i.imgur.com/otYHy7i.png)

- Review workflow
  - Add or remove kills from a report, then approve or reject with optional comments.
    ![](https://i.imgur.com/GxRTvlU.png)
  - If the character is attached to the user in AA and they have Discord configured, the user will be notified on approval/rejection (including comments).
    - Users can disable this notification on an individual level.
      ![user/Discord](https://i.imgur.com/IrOJHRq.png)

- Configurable penalties
  - Define penalty schemes (per-missing/wrong module), optionally include rigs/subsystems, and set a max cap.
    ![](https://i.imgur.com/CgTS6SG.png)

- Flexible rewards
  - Set base rewards per doctrine and ship, enabling fixed payouts independent of market prices.
    ![](https://i.imgur.com/Z0hV5tM.png)

- Analytics
  - Manager and user-level dashboards: submission counts, payouts, loss values, and trends.
    ![](https://i.imgur.com/tBcJRTd.png)
  - Users also have the same stats, but specific to them.

## Installation

### 1. Install the app

Install into your AllianceAuth virtual environment via pip.

```bash
pip install autosrp
```

### 2. Configure AA settings

- Add 'autosrp' to INSTALLED_APPS
- Optionally, configure settings from the Settings section below to enable integrations and tune fit checking

### 3. Finalize install

Run migrations and collect static files.

```bash
python manage.py migrate
python manage.py collectstatic --noinput
```
Then restart your AA services.

Run the following command to create the initial item data.
```bash
python manage.py autosrp_preload_data
```
Once it has finished, you can create the initial price data.
```bash
python manage.py refresh_item_prices
```

## Configuring before use
### 1. Configure Orgranization Filters (done only in the admin menu)
#### 1.1 [99009902] or [99009902, 99009903]
### 2. Configure Doctrine Base Awards If Needed
### 3. Configure Penalties If Needed

## Updating

```bash
pip install -U autosrp
```

Run migrations and collectstatic.

## Settings

| Setting                              | Default                                 | Description                                                                                 |
|--------------------------------------| --------------------------------------- | ------------------------------------------------------------------------------------------- |
| AUTOSRP_JANICE_API_KEY | ""                                      | Optional API key for Janice pricing lookups when available.                                  |
| AUTOSRP_FITCHECK_IGNORE_CATEGORY_IDS | {8, 18, 20, 5}                          | Category IDs to ignore during doctrine/fit comparison.               |

Integrations auto-detection:
- AA Discordbot: enabled when the aadiscordbot app is installed
- AA Discord Notify: enabled when the discordnotify app is installed
- Discord Proxy: detected if discordproxy is installed and importable

### Scheduled task for updating prices
```bash
CELERYBEAT_SCHEDULE['autosrp_update_all_prices'] = {
    'task': 'autosrp.services.services_update.update_all_prices',
    'schedule': crontab(minute=0, hour=3, day_of_week='sun'),
}
```


## Permissions

| Permission     | Appearance in Admin  | Description                   |
|----------------|----------------------|-------------------------------|
| autosrp.manage | autosrp - submission | Can manage Auto SRP settings. |
| autosrp.submit | autosrp - submission | Can submit Auto SRP requests. |
| autosrp.review | autosrp - submission | Can review Auto SRP batches.  |
