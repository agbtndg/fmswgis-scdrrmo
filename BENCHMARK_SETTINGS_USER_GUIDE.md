# 🎚️ Benchmark Settings - Quick Start Guide

## What Is This Feature?

The **Benchmark Settings** feature allows administrators to customize flood risk thresholds and alert benchmarks **without writing any code**. All changes take effect immediately and affect calculations across the entire monitoring dashboard.

---

## How to Access

### Step 1: Login
1. Go to the Flood Monitoring System
2. Login with your **staff/admin account**

### Step 2: Navigate to Settings
1. Look for the **⚙️ gear icon** in the top-right corner of the navbar
2. Click the gear icon to open the dropdown menu
3. Click **"Benchmark Settings"**

---

## What Can You Configure?

### 1. 📊 Rainfall Benchmarks (millimeters)
Define how much rainfall triggers different risk levels:

| Setting | Current Default | Meaning |
|---------|-----------------|---------|
| **Moderate Risk Threshold** | 30 mm | Rainfall ≥ this amount triggers ORANGE (Moderate) risk |
| **High Risk Threshold** | 50 mm | Rainfall ≥ this amount triggers RED (High) risk |

**Example**: If you set Moderate to 25mm and High to 45mm:
- Less than 25mm → Yellow (Low Risk) ☀️
- 25-45mm → Orange (Moderate Risk) ⚠️
- 45mm or more → Red (High Risk) 🚨

---

### 2. 🌊 Tide Level Benchmarks (meters)
Define how much tide height triggers different risk levels:

| Setting | Current Default | Meaning |
|---------|-----------------|---------|
| **Moderate Risk Threshold** | 1.0 m | Tide ≥ this height triggers ORANGE (Moderate) risk |
| **High Risk Threshold** | 1.5 m | Tide ≥ this height triggers RED (High) risk |

**Example**: If you set Moderate to 0.9m and High to 1.4m:
- Below 0.9m → Yellow (Low Risk) ☀️
- 0.9-1.4m → Orange (Moderate Risk) ⚠️
- 1.4m or higher → Red (High Risk) 🚨

---

### 3. 🔔 Alert Benchmarks
Define thresholds that trigger weather alerts and notifications:

| Setting | Current Default | Meaning |
|---------|-----------------|---------|
| **Heavy Rain Alert Threshold** | 15 mm/day | Daily rainfall > this triggers a heavy rain alert |
| **Total Precipitation Alert** | 50 mm/week | 7-day cumulative rainfall > this triggers a precipitation alert |

**Example**: If forecast shows:
- 12mm rainfall tomorrow → No heavy rain alert (below 15mm)
- 18mm rainfall tomorrow → Heavy rain alert! ⚠️
- 55mm total over next week → Precipitation alert! ⚠️

---

## How to Update Thresholds

1. **Access the page** (see "How to Access" above)
2. **Find the threshold** you want to change
3. **Clear the current value** and type a new number
4. **Check the info box** below each section to see the new risk levels
5. **Click "Save Changes"** button (green button at bottom)
6. **Wait for confirmation** - A success message appears
7. **Dashboard updates automatically** - All future risk calculations use the new thresholds

---

## Important Rules

When entering values, remember these rules:

❌ **Don't**: Make moderate threshold equal to or higher than high threshold
- ✅ Correct: Moderate = 30, High = 50
- ❌ Wrong: Moderate = 50, High = 30

❌ **Don't**: Use negative numbers
- ✅ Correct: Moderate = 25mm
- ❌ Wrong: Moderate = -25mm

❌ **Don't**: Leave fields blank
- ✅ Correct: All fields must have a number

❌ **Don't**: Make heavy rain alert threshold higher than total precip threshold
- ✅ Correct: Heavy Rain = 15, Total Precip = 50
- ❌ Wrong: Heavy Rain = 50, Total Precip = 15

---

## What Happens When You Save?

1. ✅ System validates all values
2. ✅ System checks that values make logical sense
3. ✅ Database updates with new thresholds
4. ✅ **Immediately takes effect** - No waiting, no restarting
5. ✅ Next rainfall/tide reading uses new thresholds
6. ✅ Dashboard risk colors update instantly
7. ✅ All alerts use new benchmarks

---

## Real-World Example

**Scenario**: Your area experiences very heavy rain frequently. The current 50mm threshold for high risk is too high. You want to be alerted earlier.

**Action**:
1. Go to Benchmark Settings
2. Change Rainfall High Risk from **50mm → 40mm**
3. Click "Save Changes"
4. Success! ✅

**Result**:
- Before: 45mm rain → Orange (Moderate Risk)
- After: 45mm rain → Red (High Risk)
- Your emergency team gets notified earlier 🚨

---

## FAQ

### Q: When do the changes take effect?
**A:** Immediately! The next time the dashboard loads or calculates risk levels, it uses the new thresholds.

### Q: Can I change the values multiple times?
**A:** Yes! You can edit as many times as you need.

### Q: What if I make a mistake?
**A:** Just go back to Benchmark Settings and change it to the correct value. No damage is done.

### Q: Will this affect historical data?
**A:** No. Past data stays the same. Only future calculations use the new thresholds.

### Q: Can regular users change the benchmarks?
**A:** No. Only staff/admin members can access this feature. Regular users see a read-only dashboard.

### Q: What if I get an error message?
**A:** Read the error message - it explains what's wrong (e.g., "Moderate threshold must be less than high"). Fix the issue and try again.

---

## Default Benchmark Values

If you ever want to go back to the original defaults, use these values:

| Setting | Default |
|---------|---------|
| Rainfall Moderate | 30 mm |
| Rainfall High | 50 mm |
| Tide Moderate | 1.0 m |
| Tide High | 1.5 m |
| Alert Heavy Rain | 15 mm/day |
| Alert Total Precip | 50 mm/week |

---

## Support

If you have questions or encounter issues:
1. Check the help text on each field (small gray text below the input)
2. Hover over icons for additional information
3. Look at the info boxes that show how your changes affect risk levels
4. Contact your system administrator if you need help

---

**Ready to customize your thresholds?** 🚀 Start by clicking the ⚙️ gear icon!
