# Telecommunications Intelligence Scraper

A comprehensive web scraping system for monitoring telecommunications domain news across legal, political, and financial categories using Serper API.

## Overview

This system is designed for PLAY Polska to monitor and analyze telecommunications industry developments in Poland and the EU. It automatically scrapes news from dozens of sources, filters for telecommunications relevance, and generates actionable intelligence reports.

## Features

- **Multi-category Scraping**: Legal (prawo), Political (polityka), and Financial (market) news
- **Serper API Integration**: Efficient Google search-based news scraping
- **Intelligent Filtering**: Telecommunications relevance detection
- **Impact Assessment**: High/medium/low impact categorization
- **Entity Extraction**: Automatic identification of key entities
- **Report Generation**: Weekly and daily intelligence reports
- **Risk Assessment**: Automated risk level evaluation
- **Action Items**: Generated recommendations for business response

## Installation

1. Install dependencies:
```bash
pip install -r requirements.txt
```

2. Set up Serper API key:
```bash
# Copy the environment template
cp env_template.txt .env

# Edit .env file and set your actual API key
# SERPER_API_KEY=your_actual_serper_api_key_here
```

3. Run setup script:
```bash
python setup.py
```

This will:
- Install dependencies
- Create necessary directories
- Create .env file from template
- Check API key configuration

## Usage

### Weekly Report (Recommended)
```bash
python main_scraper.py
```

### Daily Brief
```python
from main_scraper import TelecomIntelligenceOrchestrator
import asyncio

async def run_daily():
    orchestrator = TelecomIntelligenceOrchestrator(serper_api_key)
    return await orchestrator.run_daily_brief(days_back=1)

asyncio.run(run_daily())
```

### Individual Scrapers
```python
# Legal news only
python legal_scraper.py

# Political news only  
python political_scraper.py

# Financial news only
python financial_scraper.py

# General telecom news
python telecom_news_scraper.py
```

## Configuration

Edit `config.py` to customize:
- News sources
- Keywords for relevance filtering
- Impact level criteria
- Report templates
- Output settings

## Output Files

The system generates several output files:

- `telecom_intelligence_YYYYMMDD_HHMMSS.json` - Complete intelligence report
- `telecom_intelligence_YYYYMMDD_HHMMSS_summary.md` - Human-readable summary
- `raw_telecom_data_YYYYMMDD_HHMMSS.json` - Raw scraping data
- `daily_brief_YYYYMMDD_HHMMSS.json` - Daily brief data

## News Sources

### Legal Sources (Prawo)
- legislacja.rcl.gov.pl
- isap.sejm.gov.pl
- gov.pl
- prezydent.pl
- sejm.gov.pl
- senat.gov.pl
- uke.gov.pl
- uokik.gov.pl
- berec.europa.eu
- digital-strategy.ec.europa.eu
- consilium.europa.eu
- europarl.europa.eu
- enisa.europa.eu
- oecd.org

### Political Sources (Polityka)
- reuters.com
- bloomberg.com
- wsj.com
- cnn.com
- nbcnews.com
- foxnews.com
- nytimes.com
- washingtonpost.com
- apnews.com
- theguardian.com
- thetimes.co.uk
- bbc.com
- lemonde.fr
- afp.com
- onet.pl
- biznes.pap.pl
- rp.pl
- ec.europa.eu
- politico.eu
- news.cn
- caixinglobal.com
- japantimes.co.jp
- nhk.or.jp
- ft.com

### Financial Sources (Market)
- reuters.com/markets
- bloomberg.com/markets
- wsj.com/markets
- ft.com/markets
- cnbc.com
- marketwatch.com
- investing.com
- biznes.pap.pl
- rp.pl
- money.pl
- bankier.pl
- stooq.pl
- pulshr.pl
- nbp.pl
- ecb.europa.eu
- fred.stlouisfed.org
- imf.org
- bis.org
- oanda.com

## Report Structure

### Weekly Intelligence Report
- Executive Summary
- Legal Developments Analysis
- Political Developments Analysis  
- Financial Developments Analysis
- Risk Assessment
- Key Insights
- Action Items
- Raw Data

### Daily Brief
- Top Stories
- Market Impact
- Regulatory Updates
- Quick Actions

## Customization

### Adding New Sources
Edit `config.py` and add new sources to the appropriate category lists:
- `LEGAL_SOURCES`
- `POLITICAL_SOURCES` 
- `FINANCIAL_SOURCES`
- `TELECOM_SPECIFIC_SOURCES`

### Modifying Keywords
Update `TELECOM_KEYWORDS` in `config.py` to adjust relevance filtering.

### Custom Queries
Add new search queries to:
- `LEGAL_QUERIES`
- `POLITICAL_QUERIES`
- `FINANCIAL_QUERIES`

## API Rate Limits

The system uses Serper API with the following considerations:
- 2,500 free searches per month
- 20 results per query
- Concurrent request limiting
- Error handling and retry logic

## Error Handling

- Automatic retry for failed requests
- Graceful handling of API rate limits
- Comprehensive logging
- Data validation and sanitization

## Performance

- Concurrent scraping for speed
- Intelligent deduplication
- Efficient data processing
- Optimized API usage

## Security

- API key management via environment variables
- No hardcoded credentials
- Secure data handling
- Input validation

## Monitoring

- Comprehensive logging
- Performance metrics
- Error tracking
- Success/failure reporting

## Future Enhancements

- Database storage
- Email notifications
- Web dashboard
- Machine learning insights
- Real-time monitoring
- API endpoints

## Support

For issues or questions:
1. Check logs in console output
2. Verify API key configuration
3. Ensure internet connectivity
4. Check Serper API status

## License

This project is developed for PLAY Polska telecommunications intelligence monitoring.
