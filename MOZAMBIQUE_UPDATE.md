# Mozambique Integration - Setup Instructions

## Changes Made

### Backend
1. ✅ Added Mozambique employment multipliers to `backend/app/data/tiva_multipliers.py`
2. ✅ Added Mozambique to WDI service in `backend/app/services/wdi_service.py`
3. ✅ Created three policy scenarios: Agricultural Modernization, Structural Transformation, Gas-Led Development

### Frontend
1. ✅ Added Mozambique to country selector in `frontend/src/components/Header.jsx`
2. ✅ Added Mozambique to dashboard charts in `frontend/src/components/CountryDashboard.jsx`
3. ✅ Added Mozambique policy scenarios to `frontend/src/components/PresetScenarios.jsx`
4. ✅ Added emoji font support for flag display in `frontend/index.html` and `frontend/src/styles/index.css`

## Required Actions to Activate Mozambique

### Step 1: Restart Backend Server

The backend needs to be restarted to:
- Load the new Mozambique multipliers
- Recognize Mozambique in the WDI service
- Clear the service cache

**Instructions:**
1. Stop the current backend server (if running) - Press `Ctrl+C` in the terminal
2. Navigate to backend directory: `cd backend`
3. Activate virtual environment:
   - Windows: `venv\Scripts\activate`
   - Mac/Linux: `source venv/bin/activate`
4. Start server: `uvicorn app.main:app --reload --port 8000`

### Step 2: Restart Frontend Development Server

The frontend needs to pick up:
- New CSS for emoji fonts
- Updated HTML head section
- New country in Header component

**Instructions:**
1. Stop the current frontend server (if running) - Press `Ctrl+C` in the terminal
2. Navigate to frontend directory: `cd frontend`
3. Clear Node cache (optional but recommended): `npm run dev -- --force`
4. Start server: `npm run dev`

### Step 3: Clear Browser Cache

**Instructions:**
1. Open the browser DevTools (`F12` or `Ctrl+Shift+I`)
2. Right-click the refresh button
3. Select "Empty Cache and Hard Reload"

OR simply:
1. Press `Ctrl+Shift+R` (Windows/Linux) or `Cmd+Shift+R` (Mac)

## Expected Behavior After Restart

### Country Selector
- Should show 5 countries: South Africa 🇿🇦, Tunisia 🇹🇳, Viet Nam 🇻🇳, Thailand 🇹🇭, **Mozambique 🇲🇿**
- Flags should display properly as colored emojis

### Country Dashboard (Data Tab)
- When selecting Mozambique, should fetch and display WDI data:
  - GDP (current US$)
  - GDP per capita
  - Labor force, total
  - Employment in agriculture (%)
  - Unemployment rate (%)
  - Youth unemployment rate (%)

### Policy Simulation
- Three preset scenarios should appear for Mozambique:
  1. **Agricultural Modernization** - Focus on existing sectors
  2. **Structural Transformation** - Industrialization drive
  3. **Gas-Led Development** - Leverage natural gas revenues

## Troubleshooting

### Issue: WDI data still missing for Mozambique

**Solution:**
1. Check that backend restarted successfully - look for "Starting Economic Policy Simulator API..." message
2. Verify WDI API is accessible:
   ```bash
   curl "https://api.worldbank.org/v2/country/MOZ/indicator/NY.GDP.MKTP.CD?format=json&date=2020:2024"
   ```
3. Check backend logs for any WDI API errors

### Issue: Flags still not displaying

**Possible causes:**
- Windows emoji support - Windows 10/11 should support color emojis
- Font not loaded - Check browser DevTools Console for font errors
- Browser cache - Try incognito/private browsing mode

**Solution:**
1. Ensure you've cleared browser cache (see Step 3 above)
2. Try a different browser (Chrome/Edge have best emoji support)
3. Check that `index.html` includes the emoji-text CSS class
4. Inspect the flag element in DevTools - should have class "emoji-text"

### Issue: Mozambique scenarios not appearing

**Solution:**
1. Check that `PresetScenarios.jsx` was saved correctly
2. Verify frontend console for JavaScript errors
3. Clear frontend build cache: `rm -rf node_modules/.vite` then restart dev server

## Data Sources for Mozambique

The multipliers are based on:
- **World Bank WDI 2024**: GDP, employment shares, labor force data
- **ILO Statistics**: Unemployment rates, informal sector (95%), agriculture employment (69.5%)
- **Regional patterns**: Comparable low-income Sub-Saharan African economies

**Data Quality**: Stylized estimates (not research-grade OECD TiVA data)

## Next Steps

After confirming everything works:
1. Update README.md to mention Mozambique support
2. Test all three policy scenarios
3. Verify demographic disaggregation (youth, female, informal) works correctly
4. Consider adding more African countries using similar methodology
