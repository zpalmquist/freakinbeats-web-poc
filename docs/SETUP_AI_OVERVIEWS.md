# Quick Setup Guide: AI Label Overviews

## What Was Implemented

✅ **AI-powered label overviews** using Google Gemini API  
✅ **Database caching** to minimize API costs  
✅ **Frontend display** in the Label Info section  
✅ **Multi-label support** with automatic deduplication  
✅ **Graceful fallback** if API is unavailable  

## Quick Start (3 Steps)

### 1. Get Gemini API Key (FREE)

1. Go to https://ai.google.dev/
2. Click "Get API key" → "Create API key"
3. Copy your API key

**Free Tier Includes:**
- 15 requests/minute
- 1,500 requests/day
- Perfect for testing and small stores

### 2. Set Environment Variable

Add to your environment (or create a `.env` file):

```bash
export GEMINI_API_KEY="your_api_key_here"
```

Or create/update `.env` file in the project root:
```bash
GEMINI_API_KEY=your_actual_api_key_here
ENABLE_AI_OVERVIEWS=true
```

### 3. Install Dependencies & Run

```bash
# Install the Google Generative AI library
pip install google-generativeai

# Or install all requirements
pip install -r requirements.txt

# Run the application
python3 run.py
```

That's it! The database table will be created automatically.

## Testing It Out

1. Start the server: `python3 run.py`
2. Navigate to any product detail page: `http://localhost:3000/detail/0`
3. Look for the "Label Info" section
4. You should see an AI-generated overview at the top (if label name is available)

**First time**: Calls Gemini API (takes ~1-2 seconds)  
**Subsequent visits**: Instant (served from cache)

## Expected Output

For a label like "Blue Note Records", you'll see:

```
📀 Label Info

Blue Note Records is a legendary jazz record label founded in 1939 by Alfred Lion and Max Margulis. 
Known for its iconic cover art and groundbreaking jazz recordings, the label has released albums by 
Miles Davis, John Coltrane, Herbie Hancock, and countless other jazz legends.

[Discogs Label Page →]
[Bandcamp Search →]
[Google Search →]
```

## Cost Breakdown

With caching enabled (default):
- **First request per label**: ~$0.00025
- **All subsequent requests**: FREE (served from cache)

**Example scenarios:**
- 50 unique labels: ~$0.0125 (basically free)
- 500 unique labels: ~$0.125
- 5,000 unique labels: ~$1.25

Most small-to-medium stores will stay well within the free tier.

## Troubleshooting

### No overviews appearing?

Check logs when starting the server:
```bash
python3 run.py
```

Look for:
- ✅ `"Database tables created"` (confirms database setup)
- ❌ `"GEMINI_API_KEY not configured"` (need to set API key)
- ❌ `"google-generativeai package not installed"` (run pip install)

### Check if it's working:

```bash
# In Python console
python3 -c "import google.generativeai as genai; print('✅ Package installed')"
```

### Disable the feature:

Set in `.env`:
```bash
ENABLE_AI_OVERVIEWS=false
```

## Files Created/Modified

**New Files:**
- `app/models/label_info.py` - Database model for caching
- `app/services/gemini_service.py` - Gemini API integration
- `AI_LABEL_OVERVIEWS.md` - Comprehensive documentation
- `SETUP_AI_OVERVIEWS.md` - This quick start guide

**Modified Files:**
- `app/services/inventory_service.py` - Added overview fetching
- `app/static/js/detail.js` - Added overview rendering
- `app/static/scss/detail.scss` - Added overview styling
- `config.py` - Added Gemini configuration
- `requirements.txt` - Added google-generativeai
- `env.example` - Added example configuration

## Next Steps

### Optional Enhancements

1. **Pre-generate all overviews** (avoid first-load delays):
   ```python
   python3 -c "from app import create_app; from app.services.inventory_service import InventoryService; app = create_app(); app.app_context().push(); service = InventoryService(); [service._get_label_overviews(l['label_names']) for l in service.get_all_items() if l.get('label_names')]"
   ```

2. **Monitor cache hits**:
   ```python
   # In Flask shell
   from app.models.label_info import LabelInfo
   print(f"Cached labels: {LabelInfo.query.count()}")
   ```

3. **Customize prompts**: Edit `app/services/gemini_service.py` line ~66

## Support & Documentation

- **Full Documentation**: See `AI_LABEL_OVERVIEWS.md`
- **Gemini API Docs**: https://ai.google.dev/docs
- **Get API Key**: https://ai.google.dev/

## What Happens Under the Hood

1. User visits `/detail/123`
2. Backend checks if label overview is cached in database
3. If cached → serve immediately (fast!)
4. If not cached → call Gemini API → generate overview → cache it → serve
5. Frontend displays overview at top of Label Info section

The caching ensures you only pay once per unique label, making this extremely cost-effective even at scale.

---

**Questions?** Check the logs, review `AI_LABEL_OVERVIEWS.md`, or examine the code in `app/services/gemini_service.py`

