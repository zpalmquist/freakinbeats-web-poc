# AI-Generated Label Overviews

This feature uses Google Gemini AI to automatically generate informative overviews about record labels, displayed on the product detail pages.

## Features

- **AI-Generated Content**: Leverages Google Gemini Pro to generate concise, informative overviews about record labels
- **Intelligent Caching**: Stores generated overviews in the database to minimize API calls and costs
- **Multi-Label Support**: Handles comma-separated label lists, generating unique overviews for each label
- **Graceful Degradation**: Falls back silently if API is unavailable or not configured
- **Cost-Effective**: With caching, you only pay for the first generation of each unique label

## Setup

### 1. Get a Gemini API Key

1. Visit https://ai.google.dev/
2. Sign in with your Google account
3. Click "Get API key" and create a new API key
4. Copy your API key

### 2. Configure Environment Variables

Add to your `.env` file (or set as environment variables):

```bash
# Google Gemini API Configuration
GEMINI_API_KEY=your_gemini_api_key_here
ENABLE_AI_OVERVIEWS=true
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

This will install the `google-generativeai` package.

### 4. Initialize Database

The new `label_info` table will be created automatically when you start the application:

```bash
python3 run.py
```

## How It Works

### Backend Flow

1. **Request**: User navigates to `/detail/<id>` page
2. **API Call**: Frontend requests listing data from `/api/detail/<id>`
3. **Cache Check**: `InventoryService` checks if label overview exists in `label_info` table
4. **Generation** (if not cached):
   - `GeminiService` calls Google Gemini API with a prompt
   - Response is stored in database for future use
5. **Response**: Label overviews are included in API response as `label_overviews` dictionary

### Frontend Display

The detail page displays AI overviews at the top of the "Label Info" section:
- **Single Label**: Overview displayed without label name header
- **Multiple Labels**: Each overview shown with label name header
- Followed by reference links (Discogs, Bandcamp, Google)

### Caching Strategy

Generated overviews are cached indefinitely in the `label_info` table:
- **First request**: Calls Gemini API (~$0.00025 per label)
- **Subsequent requests**: Served from cache (free)
- **Cache invalidation**: Set `cache_valid=False` in database to regenerate

## Cost Estimation

With Google Gemini Pro pricing:
- **Per Label**: ~$0.00025 (300 tokens @ $0.00075/1K tokens)
- **100 unique labels**: ~$0.025
- **500 unique labels**: ~$0.125
- **1000 unique labels**: ~$0.25

Plus free tier includes:
- 15 requests per minute
- 1,500 requests per day

## Configuration Options

### Disable AI Overviews

Set in environment:
```bash
ENABLE_AI_OVERVIEWS=false
```

Or in `config.py`:
```python
ENABLE_AI_OVERVIEWS = False
```

### Customize Prompts

Edit the `_build_label_prompt()` method in `app/services/gemini_service.py` to customize what information is requested from the AI.

## Database Schema

### label_info Table

| Column | Type | Description |
|--------|------|-------------|
| id | Integer | Primary key |
| label_name | String(255) | Unique label name (indexed) |
| overview | Text | AI-generated overview |
| generated_by | String(50) | LLM used ('gemini') |
| generated_at | DateTime | When overview was generated |
| updated_at | DateTime | Last update timestamp |
| cache_valid | Boolean | Whether cache is valid |
| generation_error | Text | Any errors encountered |

## API Response Format

```json
{
  "label_names": "Liquid Sky Music, Home Entertainment",
  "label_overviews": {
    "Liquid Sky Music": "Liquid Sky Music is an independent electronic music label...",
    "Home Entertainment": "Home Entertainment is a vinyl reissue label..."
  },
  "label_urls": [...]
}
```

## Troubleshooting

### No Overviews Appearing

1. Check that `GEMINI_API_KEY` is set correctly
2. Check that `ENABLE_AI_OVERVIEWS=true`
3. Check application logs for errors:
   ```bash
   tail -f logs/app.log  # or check Flask console output
   ```

### API Quota Exceeded

Free tier limits: 15 requests/minute, 1,500/day
- Wait for quota to reset
- Cached labels won't count against quota
- Consider upgrading to paid tier if needed

### Generation Errors

Check the `generation_error` column in the `label_info` table:
```sql
SELECT label_name, generation_error FROM label_info WHERE generation_error IS NOT NULL;
```

## Manual Cache Management

### Clear Cache for Specific Label

```python
from app.models.label_info import LabelInfo
from app.extensions import db

label = LabelInfo.query.filter_by(label_name="Label Name").first()
if label:
    label.cache_valid = False
    db.session.commit()
```

### Clear All Cache

```python
from app.models.label_info import LabelInfo
from app.extensions import db

LabelInfo.query.update({LabelInfo.cache_valid: False})
db.session.commit()
```

### Pre-generate Overviews

Create a script to pre-generate overviews for all labels in your inventory:

```python
from app import create_app
from app.services.inventory_service import InventoryService

app = create_app()
with app.app_context():
    service = InventoryService()
    listings = service.get_all_items()
    
    labels = set()
    for listing in listings:
        if listing.get('label_names'):
            for label in listing['label_names'].split(','):
                labels.add(label.strip())
    
    print(f"Found {len(labels)} unique labels")
    
    for label in labels:
        service._get_label_overviews(label)
        print(f"Generated overview for: {label}")
```

## Security Notes

- Store your `GEMINI_API_KEY` securely (never commit to git)
- Use environment variables or secure secret management
- Consider rate limiting on detail pages if publicly accessible
- The AI-generated content should be reviewed for accuracy

## Future Enhancements

Potential improvements:
- [ ] Admin UI to review/edit AI-generated content
- [ ] Multiple LLM provider support (OpenAI, Claude, etc.)
- [ ] Scheduled cache refresh for outdated overviews
- [ ] User feedback system for overview quality
- [ ] Fact-checking against Discogs API data

