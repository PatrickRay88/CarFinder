# Auto.dev API Integration Setup

## 🎯 Quick Setup

Your CarFinder application is now ready for Auto.dev integration! Follow these simple steps:

### 1. Get Your API Key
1. Visit [auto.dev](https://auto.dev/signin) and sign up/sign in
2. Go to your dashboard to get your API key
3. The Starter plan includes 1,000 free API calls per month

### 2. Add Your API Key
Open the `.env` file in your CarFinder directory and replace:
```
AUTO_DEV_API_KEY=your_api_key_here
```
With your actual API key:
```
AUTO_DEV_API_KEY=sk-your-actual-api-key-here
```

### 3. Restart the Application
After adding your API key:
1. Stop the current Streamlit app (Ctrl+C in terminal)
2. Restart it: `python -m streamlit run app/main_live.py`

## 🚀 How It Works

### With Live Data Toggle ON:
- **Auto.dev API Available**: Uses real vehicle listings from Auto.dev
- **Auto.dev API Unavailable**: Falls back to mock data sources (Cars.com, AutoTrader, CarGurus)

### With Live Data Toggle OFF:
- Uses local database with sample vehicles
- Perfect for testing and offline use

## 📊 API Features

The Auto.dev integration provides:
- **Real-time vehicle listings** from US dealers
- **Advanced filtering** by make, model, year, price, mileage
- **Detailed vehicle information** including specifications, features, images
- **Dealer contact information** and listing URLs
- **Geographic filtering** by ZIP code and radius

## 🔍 Supported Parameters

The integration supports Auto.dev's full API parameters:
- `vehicle.make` - Vehicle manufacturer
- `vehicle.model` - Vehicle model
- `vehicle.year` - Model year (single year or range)
- `retailListing.price` - Price range (e.g., "10000-30000")
- `vehicle.mileage` - Mileage range (e.g., "0-50000")
- `zip` - ZIP code for location filtering
- `distance` - Radius in miles from ZIP code
- `limit` - Number of results (max 100 per request)

## 🎛️ UI Indicators

The application shows clear indicators:
- **"🟢 Auto.dev API Active"** when using real Auto.dev data
- **"🔴 Using Mock Data Sources"** when falling back to mock sources
- **"📊 Local Database Only"** when live data is disabled

## 🐛 Troubleshooting

### API Key Issues
- Ensure no extra spaces in the API key
- Verify the key starts with appropriate prefix (usually `sk-`)
- Check your Auto.dev dashboard for API usage and limits

### Connection Issues
- Check internet connection
- Verify Auto.dev service status
- API may have rate limits - check your plan limits

### Data Issues
- Auto.dev returns real market data, so results vary by location and availability
- Use the ZIP code filter for location-specific results
- Mock data sources provide consistent test data when Auto.dev is unavailable

## 📈 Performance Notes

- Auto.dev API calls count against your monthly limit
- Mock data sources are always available as fallback
- Local database provides instant responses for testing
- The application caches results to minimize API calls

---

## ✅ Current Status
- ✅ Auto.dev API integration code complete
- ✅ Proper error handling and fallbacks implemented  
- ✅ Mock data sources working as backup
- ✅ Local database integration functional
- 🔄 **Waiting for your API key to activate Auto.dev**

Once you add your API key, you'll have access to millions of real vehicle listings!