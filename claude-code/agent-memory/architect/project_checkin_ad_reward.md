---
name: checkin-and-ad-reward-design
description: Daily check-in (7-day cycle, streak bonus) and rewarded ad direct point features designed for the Dalgyeol saju app. Migration 014, new tables wallet.daily_checkins and wallet.ad_rewards.
type: project
---

Designed combined check-in + ad reward point system for Dalgyeol (달결) saju app (2026-03-16).

**Why:** Free-to-play users need daily engagement incentives (DAU/retention) and an alternative point acquisition path beyond IAP purchases. These features fill the "Stage 1-2" gap in the BM_PLAN.md conversion funnel.

**How to apply:** When implementing backend services (checkin_service.rs, ad_reward_service.rs), reuse existing `point_service::add_points_tx()` for all point grants. Migration is 014. wallet_ledger reasons: `daily_checkin`, `checkin_bonus`, `ad_reward`. New API routes: `/v1/checkin`, `/v1/checkin/status`, `/v1/rewards/ad-watch`, `/v1/rewards/ad-status`. All date logic uses KST (UTC+9).
