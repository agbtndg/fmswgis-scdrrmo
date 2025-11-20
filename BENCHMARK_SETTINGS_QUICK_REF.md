# 🎚️ Benchmark Settings - Quick Reference

## 🎯 What Is It?
Admin-accessible web interface to dynamically configure flood risk thresholds **without coding or deployment**.

## ⚡ Quick Access
1. Login with staff account
2. Click **⚙️ gear icon** (top-right)
3. Select **"Benchmark Settings"**
4. Edit + Save → **Takes effect immediately**

---

## 📊 6 Configurable Settings

### Rainfall Thresholds
```
Moderate: Rainfall ≥ this → ORANGE risk  (default: 30mm)
High:     Rainfall ≥ this → RED risk    (default: 50mm)
```
**Rule**: Moderate MUST be less than High

### Tide Thresholds
```
Moderate: Tide ≥ this → ORANGE risk  (default: 1.0m)
High:     Tide ≥ this → RED risk    (default: 1.5m)
```
**Rule**: Moderate MUST be less than High

### Alert Thresholds
```
Heavy Rain:    Daily rainfall > this → Alert  (default: 15mm/day)
Total Precip:  7-day total > this → Alert    (default: 50mm/week)
```
**Rule**: Heavy Rain MUST be less than Total Precip

---

## ✅ Validation Rules
- ✓ All values must be POSITIVE
- ✓ Moderate < High (both rainfall and tide)
- ✓ Heavy Rain Alert < Total Precip Alert
- ✓ No empty fields

---

## 📱 Visual Guide

```
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  ⚙️ Settings Button (Top Right) ┃
┃  ├─ 👤 Profile                 ┃
┃  ├─ 🎚️ Benchmark Settings      ┃ ← CLICK HERE (Staff Only)
┃  └─ 🚪 Logout                  ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
        ↓
┏━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┓
┃  🎚️ Benchmark Settings Form    ┃
┃                                 ┃
┃  ☔ RAINFALL                     ┃
┃  ├─ Moderate: [  ] mm           ┃
┃  └─ High:     [  ] mm           ┃
┃                                 ┃
┃  🌊 TIDE LEVEL                  ┃
┃  ├─ Moderate: [  ] m            ┃
┃  └─ High:     [  ] m            ┃
┃                                 ┃
┃  🔔 ALERTS                      ┃
┃  ├─ Heavy Rain:    [  ] mm/day  ┃
┃  └─ Total Precip:  [  ] mm/week ┃
┃                                 ┃
┃  [💾 SAVE]  [❌ CANCEL]         ┃
┗━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━┛
        ↓
✅ Changes Applied Instantly
⚡ Dashboard Updates Real-Time
```

---

## 🔢 Default Values Cheat Sheet

| Name | Value | Unit |
|------|-------|------|
| Rainfall Moderate | 30 | mm |
| Rainfall High | 50 | mm |
| Tide Moderate | 1.0 | m |
| Tide High | 1.5 | m |
| Heavy Rain Alert | 15 | mm/day |
| Total Precip Alert | 50 | mm/week |

## 💡 Real-World Examples

### Example 1: Area Gets Less Rain
**Current**: High Risk at 50mm  
**Problem**: Takes too long to trigger alerts  
**Solution**: Change High Risk → 40mm  
**Result**: Faster response time ⚡

### Example 2: Tide Issues
**Current**: Moderate Risk at 1.0m  
**Problem**: Low-lying areas flood at 0.8m  
**Solution**: Change Moderate → 0.8m  
**Result**: Earlier warning ⏰

### Example 3: Want More Aggressive
**Current**: All defaults  
**Problem**: Want 3x more sensitivity  
**Solution**: Divide all by 3  
**Result**: Rainfall: 10/16mm, Tide: 0.3/0.5m  

---

## 🛠️ How It Works Behind the Scenes

```
Staff makes change → Form validates → Database updates → 
Next calculation checks database → Risk uses new threshold → 
Dashboard shows new level
```

---

## ❌ Common Mistakes (Avoid These!)

| ❌ WRONG | ✅ CORRECT |
|---------|-----------|
| Moderate = 50, High = 30 | Moderate = 30, High = 50 |
| Moderate = 30, High = 30 | Moderate = 30, High = 50 |
| Moderate = -20 | Moderate = 20 |
| Heavy Rain = 50, Total = 30 | Heavy Rain = 30, Total = 50 |
| Leaving fields blank | All fields filled with numbers |

---

## 🔐 Security Notes
- ✓ Only staff members can access
- ✓ Prevents accidental deletion
- ✓ Tracks who made changes (updated_by field)
- ✓ No code/deploy needed = less risk

---

## ⏱️ Timeline
- **Changes Made**: Instant
- **Dashboard Updates**: Real-time
- **Alert Recalculation**: Immediate
- **Restart Required**: None

---

## 📞 Support
- Can't find link? → Check if user is staff
- Form rejects input? → Read error message
- Changes not showing? → Reload dashboard
- Need help? → See BENCHMARK_SETTINGS_USER_GUIDE.md

---

## 🎓 Key Takeaway
> Instead of waiting for developers to change code and redeploy, staff can now adjust emergency thresholds in 30 seconds through a simple web form.

**Access Level**: Staff/Admin Only  
**Frequency**: Use as often as needed  
**Side Effects**: None (changes only affect future calculations)
