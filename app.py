"""
Travel News Translator - Integrated Web Application
With built-in scraper and scheduler - LIGHT POLLING VERSION
"""

import streamlit as st
import json
from datetime import datetime
from pathlib import Path
import glob
import threading
import time
import sys

# Translation - Legacy (keeping for fallback)
from deep_translator import GoogleTranslator

# Import modules
from config.settings import *
from utils.logger import get_webapp_logger
from core.scraper import TravelNewsScraper
from core.scheduler import get_scheduler

# AI Enhancement
from core.enhancer import ContentEnhancer, enhance_translation
from core.prompts import get_format_config
from config.settings import AI_CONFIG

# NEW: OpenAI Translation
from core.translator import OpenAITranslator, translate_webpage

# NEW: Review Agent for Quality Checking
from core.review_agent import ReviewAgent

logger = get_webapp_logger()

# ============================================================================
# PAGE CONFIGURATION
# ============================================================================
st.set_page_config(
    page_title=WEBAPP_CONFIG['title'],
    page_icon=WEBAPP_CONFIG['icon'],
    layout=WEBAPP_CONFIG['layout'],
    initial_sidebar_state="expanded"
)

# ============================================================================
# AUTHENTICATION - Password Protection
# ============================================================================
import os

# Initialize authentication state
if 'authenticated' not in st.session_state:
    st.session_state.authenticated = False

# Get password from environment variable (set in Streamlit Cloud Secrets)
APP_PASSWORD = os.getenv('APP_PASSWORD', 'demo1_2025')  # Default password for local dev

if not st.session_state.authenticated:
    st.markdown("<h1 style='text-align: center; color: #1E88E5;'>🔒 Travel News Translator</h1>", unsafe_allow_html=True)
    st.markdown("<h3 style='text-align: center;'>Please login to continue</h3>", unsafe_allow_html=True)

    col1, col2, col3 = st.columns([1, 2, 1])

    with col2:
        st.write("")
        st.write("")

        password = st.text_input("🔑 Enter Password:", type="password", key="login_password")

        col_a, col_b = st.columns(2)
        with col_a:
            if st.button("🚀 Login", use_container_width=True, type="primary"):
                if password == APP_PASSWORD:
                    st.session_state.authenticated = True
                    logger.info("User authenticated successfully")
                    st.success("✅ Login successful!")
                    time.sleep(0.5)
                    st.rerun()
                else:
                    st.error("❌ Incorrect password")
                    logger.warning("Failed login attempt")

        with col_b:
            if st.button("ℹ️ Contact Admin", use_container_width=True):
                st.info("📧 Contact: your-email@example.com")

        st.write("")
        st.write("")
        st.markdown("---")
        st.caption("🔐 Secure access to Travel News Translation System")
        st.caption("💡 For demo access, please contact the administrator")

    st.stop()  # Stop execution here if not authenticated

# If authenticated, show logout button in sidebar (will be added later in sidebar section)

# Custom CSS
st.markdown("""
<style>
    .main-header {
        font-size: 3rem;
        color: #1E88E5;
        text-align: center;
        margin-bottom: 2rem;
    }
    .article-card {
        background-color: #f0f2f6;
        padding: 1.5rem;
        border-radius: 10px;
        margin-bottom: 1rem;
        border-left: 5px solid #1E88E5;
    }
    .article-title {
        font-size: 1.2rem;
        font-weight: bold;
        color: #1E88E5;
        margin-bottom: 0.5rem;
    }
    .article-meta {
        font-size: 0.9rem;
        color: #666;
    }
    .translation-box {
        background-color: #e3f2fd;
        padding: 2rem;
        border-radius: 10px;
        border: 2px solid #1E88E5;
    }
    .status-box {
        background-color: #fff3cd;
        padding: 1rem;
        border-radius: 5px;
        border-left: 5px solid #ffc107;
        margin: 1rem 0;
    }
    .success-box {
        background-color: #d4edda;
        padding: 1rem;
        border-radius: 5px;
        border-left: 5px solid #28a745;
        margin: 1rem 0;
    }
    .stButton > button {
        width: 100%;
    }
</style>
""", unsafe_allow_html=True)

# ============================================================================
# SESSION STATE INITIALIZATION
# ============================================================================
if 'articles' not in st.session_state:
    st.session_state.articles = []
if 'selected_article' not in st.session_state:
    st.session_state.selected_article = None
if 'translations' not in st.session_state:
    st.session_state.translations = []
if 'target_lang' not in st.session_state:
    st.session_state.target_lang = TRANSLATION_CONFIG['default_language']
if 'translation_method' not in st.session_state:
    st.session_state.translation_method = 'openai'  # 'openai' or 'google'
if 'translation_tokens' not in st.session_state:
    st.session_state.translation_tokens = 0
# Pagination and filters
if 'current_page' not in st.session_state:
    st.session_state.current_page = 1
if 'articles_per_page' not in st.session_state:
    st.session_state.articles_per_page = 10
if 'selected_sources' not in st.session_state:
    st.session_state.selected_sources = []
if 'current_original' not in st.session_state:
    st.session_state.current_original = ''
if 'current_translated' not in st.session_state:
    st.session_state.current_translated = ''
if 'scraper_status' not in st.session_state:
    st.session_state.scraper_status = None
if 'scheduler' not in st.session_state:
    st.session_state.scheduler = get_scheduler()
if 'is_polling' not in st.session_state:
    st.session_state.is_polling = False
if 'notification_shown' not in st.session_state:
    st.session_state.notification_shown = False
if 'ai_provider' not in st.session_state:
    st.session_state.ai_provider = AI_CONFIG['default_provider']
if 'ai_model' not in st.session_state:
    st.session_state.ai_model = AI_CONFIG['default_openai_model']
if 'enhancement_results' not in st.session_state:
    st.session_state.enhancement_results = {}
if 'enhancement_in_progress' not in st.session_state:
    st.session_state.enhancement_in_progress = False
if 'selected_article_id' not in st.session_state:
    st.session_state.selected_article_id = None
if 'enhanced_articles' not in st.session_state:
    st.session_state.enhanced_articles = []
if 'search_keyword' not in st.session_state:
    st.session_state.search_keyword = ''
if 'search_results' not in st.session_state:
    st.session_state.search_results = {}
if 'search_in_progress' not in st.session_state:
    st.session_state.search_in_progress = False
if 'search_max_results' not in st.session_state:
    st.session_state.search_max_results = 10

# ============================================================================
# HELPER FUNCTIONS
# ============================================================================
def get_latest_data_file():
    """Get the most recent data file"""
    json_files = list(RAW_DATA_DIR.glob('travel_news_*.json'))
    if not json_files:
        return None
    return max(json_files, key=lambda p: p.stat().st_mtime)

def load_articles(json_file=None):
    """Load articles from JSON"""
    try:
        if not json_file:
            json_file = get_latest_data_file()
        
        if not json_file or not Path(json_file).exists():
            logger.warning(f"No data file found")
            return []
        
        with open(json_file, 'r', encoding='utf-8') as f:
            data = json.load(f)
            articles = data.get('all_articles', [])
        
        logger.info(f"Loaded {len(articles)} articles from {json_file}")
        return articles
    except Exception as e:
        logger.error(f"Error loading articles: {e}")
        return []

def translate_text_google(text, target_lang):
    """Translate text using Google Translate (Legacy method)"""
    try:
        translator = GoogleTranslator(source='auto', target=target_lang)
        max_length = TRANSLATION_CONFIG['chunk_size']

        if len(text) <= max_length:
            translated = translator.translate(text)
        else:
            chunks = [text[i:i+max_length] for i in range(0, len(text), max_length)]
            translated_chunks = [translator.translate(chunk) for chunk in chunks]
            translated = ' '.join(translated_chunks)

        logger.info(f"Google translation completed: {len(text)} -> {len(translated)} chars")
        return translated, 0  # Return tokens=0 for Google Translate
    except Exception as e:
        logger.error(f"Google translation error: {e}")
        return f"Translation error: {e}", 0


def translate_text_openai(pasted_content):
    """Translate text using OpenAI (Smart extraction + translation)"""
    try:
        logger.info(f"Starting OpenAI translation: {len(pasted_content)} chars")

        # Use OpenAI translator
        translator = OpenAITranslator(
            provider_name=AI_CONFIG['default_provider'],
            model=AI_CONFIG['default_openai_model']
        )

        result = translator.extract_and_translate(pasted_content, target_lang='bn')

        if result['success']:
            logger.info(f"OpenAI translation successful: {result['tokens_used']} tokens")
            return result['translated_text'], result['tokens_used']
        else:
            logger.error(f"OpenAI translation failed: {result['error']}")
            return f"Translation error: {result['error']}", 0

    except Exception as e:
        logger.error(f"OpenAI translation error: {e}")
        return f"Translation error: {e}", 0


def translate_text(text, target_lang, method='openai'):
    """
    Main translation function - routes to OpenAI or Google

    Args:
        text: Text to translate
        target_lang: Target language code
        method: 'openai' or 'google'

    Returns:
        tuple: (translated_text, tokens_used)
    """
    if method == 'openai':
        return translate_text_openai(text)
    else:
        return translate_text_google(text, target_lang)

def save_translation(original, translated, article_info):
    """Save translation to file"""
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"translation_{timestamp}.txt"
    filepath = TRANSLATIONS_DIR / filename
    
    try:
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write("="*100 + "\n")
            f.write("ARTICLE INFORMATION\n")
            f.write("="*100 + "\n")
            f.write(f"Headline: {article_info.get('headline', 'N/A')}\n")
            f.write(f"Publisher: {article_info.get('publisher', 'N/A')}\n")
            f.write(f"Published: {article_info.get('published_time', 'N/A')}\n")
            f.write(f"URL: {article_info.get('article_url', 'N/A')}\n")
            f.write(f"Saved: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n")
            f.write("\n" + "="*100 + "\n")
            f.write("ORIGINAL TEXT\n")
            f.write("="*100 + "\n\n")
            f.write(original)
            f.write("\n\n" + "="*100 + "\n")
            f.write("TRANSLATED TEXT\n")
            f.write("="*100 + "\n\n")
            f.write(translated)
        
        logger.info(f"Translation saved: {filepath}")
        return str(filepath)
    except Exception as e:
        logger.error(f"Error saving translation: {e}")
        return None

def run_scraper_async(scraper):
    """Run scraper in background thread"""
    try:
        articles, filepath = scraper.scrape_all_views()
        logger.info(f"Background scraping completed: {len(articles)} articles")
    except Exception as e:
        logger.error(f"Background scraping failed: {e}")

# ============================================================================
# MAIN APP
# ============================================================================

# Header
st.markdown('<h1 class="main-header">✈️ Travel News Translator 🌍</h1>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Control Panel")

    # ========================================================================
    # AUTHENTICATION STATUS & LOGOUT
    # ========================================================================
    st.success("✅ Logged in")
    if st.button("🚪 Logout", use_container_width=True):
        st.session_state.authenticated = False
        logger.info("User logged out")
        st.rerun()

    st.divider()

    # ========================================================================
    # SCRAPER CONTROL
    # ========================================================================
    st.subheader("🕷️ Scraper Control")
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("▶️ Start Scraping", use_container_width=True, type="primary"):
            scraper = TravelNewsScraper()
            
            # Run in background thread
            thread = threading.Thread(target=run_scraper_async, args=(scraper,))
            thread.start()
            
            st.session_state.scraper_status = scraper.status
            st.session_state.is_polling = True  # Enable polling
            st.session_state.notification_shown = False  # Reset notification flag
            st.success("Scraper started!")
            logger.info("Manual scraping started")
            time.sleep(0.5)
            st.rerun()
    
    with col2:
        if st.button("🔄 Load Latest", use_container_width=True):
            st.session_state.articles = load_articles()
            if st.session_state.articles:
                st.success(f"✅ Loaded {len(st.session_state.articles)} articles!")
            else:
                st.warning("No data found. Run scraper first!")
    
    # Show scraper status
    if st.session_state.scraper_status:
        status = st.session_state.scraper_status
        
        if status.is_running:
            st.markdown(f"""
            <div class="status-box">
                <strong>⏳ Scraping in progress...</strong><br>
                <strong>Progress:</strong> {status.progress}%<br>
                <strong>Current Site:</strong> {status.current_site or 'Initializing...'}<br>
                <strong>Status:</strong> {status.status_message}<br>
                <strong>Articles Found:</strong> {status.articles_count}
            </div>
            """, unsafe_allow_html=True)

            # Progress bar
            st.progress(status.progress / 100.0)

            # Show per-site stats if available
            if status.site_stats:
                st.caption("**Sites Completed:**")
                for site_name, count in status.site_stats.items():
                    st.caption(f"  ✓ {site_name}: {count} articles")

            # Keep polling active while running
            st.session_state.is_polling = True
            
        elif status.error:
            st.error(f"❌ Error: {status.error}")
            st.session_state.is_polling = False  # Stop polling on error
            
        else:
            # Scraping completed!
            st.markdown(f"""
            <div class="success-box">
                <strong>✅ Scraping completed!</strong><br>
                <strong>Total Articles:</strong> {status.articles_count}<br>
                <strong>Duration:</strong> {(status.end_time - status.start_time).total_seconds():.1f}s
            </div>
            """, unsafe_allow_html=True)

            # Show per-site breakdown
            if status.site_stats:
                st.caption("**Breakdown by Site:**")
                for site_name, count in status.site_stats.items():
                    st.caption(f"  ✓ {site_name}: {count} articles")
            
            # Show notification only once
            if not st.session_state.notification_shown:
                st.balloons()
                st.toast(f"✅ {status.articles_count} articles scraped successfully!", icon="✅")
                st.session_state.notification_shown = True
                
                # Auto-load articles
                if status.articles_count > 0:
                    st.session_state.articles = load_articles()
                    if st.session_state.articles:
                        st.success(f"🎉 Auto-loaded {len(st.session_state.articles)} articles!")
            
            # Stop polling after completion
            st.session_state.is_polling = False
    
    st.divider()
    
    # ========================================================================
    # SCHEDULER CONTROL
    # ========================================================================
    st.subheader("⏰ Automated Scheduling")
    
    scheduler = st.session_state.scheduler
    scheduler_status = scheduler.get_status()
    
    # Interval selection
    interval = st.selectbox(
        "Scraping Interval",
        options=SCHEDULER_CONFIG['available_intervals'],
        index=SCHEDULER_CONFIG['available_intervals'].index(SCHEDULER_CONFIG['default_interval']),
        format_func=lambda x: f"Every {x} hour{'s' if x > 1 else ''}"
    )
    
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("▶️ Start Schedule", use_container_width=True):
            if scheduler.start(interval_hours=interval):
                st.success(f"✅ Scheduler started! Interval: {interval}h")
                logger.info(f"Scheduler started with interval: {interval}h")
                st.rerun()
    
    with col2:
        if st.button("⏸️ Stop Schedule", use_container_width=True):
            if scheduler.stop():
                st.success("⏸️ Scheduler stopped")
                logger.info("Scheduler stopped")
                st.rerun()
    
    # Show scheduler status
    if scheduler_status['is_running']:
        st.markdown(f"""
        <div class="success-box">
            <strong>✅ Scheduler Active</strong><br>
            Interval: {scheduler_status['interval_hours']}h<br>
            Next run: {scheduler_status['time_until_next']}<br>
            Total runs: {scheduler_status['run_count']}
        </div>
        """, unsafe_allow_html=True)
    else:
        st.info("Scheduler is idle")
    
    st.divider()
    
    # ========================================================================
    # TRANSLATION SETTINGS
    # ========================================================================
    st.subheader("🌐 Translation")
    
    st.session_state.target_lang = st.selectbox(
        "Target Language",
        options=list(TRANSLATION_CONFIG['available_languages'].keys()),
        format_func=lambda x: TRANSLATION_CONFIG['available_languages'][x],
        index=list(TRANSLATION_CONFIG['available_languages'].keys()).index(st.session_state.target_lang)
    )
    
    st.divider()
    
    # ========================================================================
    # STATISTICS
    # ========================================================================
    st.subheader("📊 Statistics")
    col1, col2 = st.columns(2)
    
    with col1:
        st.metric("Articles", len(st.session_state.articles))
    
    with col2:
        st.metric("Translations", len(st.session_state.translations))
    
    st.divider()
    
    # Info
    with st.expander("ℹ️ About"):
        st.markdown("""
        ### How to Use
        1. **Start Scraper** - Scrape travel news
        2. **Load Latest** - Load scraped data
        3. **Select Article** - Choose an article
        4. **Translate** - Paste & translate content
        5. **Schedule** - Automate scraping
        
        ### Data Location
        - **Articles**: `data/raw/`
        - **Translations**: `translations/`
        - **Logs**: `logs/`
        """)

# Main content area
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📰 Articles", "🔄 Translate", "🔍 Search", "🚀 Future Enhancement", "⚙️ Settings"])

# ============================================================================
# TAB 1: ARTICLES
# ============================================================================
with tab1:
    st.header("📰 Available Travel Articles")

    # (Removed top-level notification - now showing inline below Select buttons)

    if not st.session_state.articles:
        st.info("👆 Click 'Load Latest' or 'Start Scraping' in the sidebar")
    else:
        # Get unique sources
        all_sources = sorted(list(set([a.get('publisher', 'Unknown') for a in st.session_state.articles])))

        # Filters Section
        st.subheader("🔍 Filters")
        col1, col2 = st.columns([3, 1])

        with col1:
            # Search box
            search = st.text_input("Search articles", placeholder="Enter keywords...")

        with col2:
            # Articles per page
            articles_per_page = st.selectbox(
                "Per page",
                options=[10, 20, 50, 100],
                index=0
            )
            st.session_state.articles_per_page = articles_per_page

        # Website filter
        selected_sources = st.multiselect(
            "🌐 Filter by Website",
            options=all_sources,
            default=all_sources,
            help="Select websites to display articles from"
        )

        st.divider()

        # Apply filters
        filtered_articles = st.session_state.articles

        # Filter by source
        if selected_sources:
            filtered_articles = [
                a for a in filtered_articles
                if a.get('publisher', 'Unknown') in selected_sources
            ]

        # Filter by search
        if search:
            filtered_articles = [
                a for a in filtered_articles
                if search.lower() in a.get('headline', '').lower()
            ]

        # Pagination calculation
        total_articles = len(filtered_articles)
        total_pages = max(1, (total_articles + articles_per_page - 1) // articles_per_page)

        # Reset to page 1 if current page is out of bounds
        if st.session_state.current_page > total_pages:
            st.session_state.current_page = 1

        start_idx = (st.session_state.current_page - 1) * articles_per_page
        end_idx = min(start_idx + articles_per_page, total_articles)

        paginated_articles = filtered_articles[start_idx:end_idx]

        # Display stats and source breakdown
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Articles", total_articles)
        with col2:
            # Source breakdown
            source_counts = {}
            for article in filtered_articles:
                source = article.get('publisher', 'Unknown')
                source_counts[source] = source_counts.get(source, 0) + 1

            breakdown_text = " | ".join([f"{src}: {count}" for src, count in sorted(source_counts.items())])
            st.info(f"📊 {breakdown_text}")

        st.write(f"Showing {start_idx + 1}-{end_idx} of {total_articles} articles (Page {st.session_state.current_page}/{total_pages})")

        # Pagination controls (top)
        if total_pages > 1:
            col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])

            with col1:
                if st.button("⏮️ First", disabled=(st.session_state.current_page == 1)):
                    st.session_state.current_page = 1
                    st.rerun()

            with col2:
                if st.button("◀️ Prev", disabled=(st.session_state.current_page == 1)):
                    st.session_state.current_page -= 1
                    st.rerun()

            with col3:
                # Page selector
                new_page = st.selectbox(
                    "Go to page",
                    options=list(range(1, total_pages + 1)),
                    index=st.session_state.current_page - 1,
                    key="page_selector_top"
                )
                if new_page != st.session_state.current_page:
                    st.session_state.current_page = new_page
                    st.rerun()

            with col4:
                if st.button("Next ▶️", disabled=(st.session_state.current_page == total_pages)):
                    st.session_state.current_page += 1
                    st.rerun()

            with col5:
                if st.button("Last ⏭️", disabled=(st.session_state.current_page == total_pages)):
                    st.session_state.current_page = total_pages
                    st.rerun()

        st.divider()

        # Display articles
        for idx, article in enumerate(paginated_articles):
            with st.container():
                col1, col2 = st.columns([4, 1])

                with col1:
                    st.markdown(f"""
                    <div class="article-card">
                        <div class="article-title">{article.get('headline', 'No title')}</div>
                        <div class="article-meta">
                            📰 {article.get('publisher', 'Unknown')} |
                            ⏰ {article.get('published_time', 'N/A')} |
                            🌍 {article.get('country', 'Unknown')}
                        </div>
                        {f"<div class='article-meta'>🏷️ {', '.join(article.get('tags', [])[:3])}</div>" if article.get('tags') else ""}
                    </div>
                    """, unsafe_allow_html=True)

                with col2:
                    if st.button("Select", key=f"select_{start_idx + idx}", use_container_width=True):
                        st.session_state.selected_article = article
                        st.session_state.selected_article_id = f"article_{start_idx + idx}"
                        logger.info(f"Article selected: {article.get('headline', 'N/A')[:50]}")
                        # Force a rerun to update all tabs with new selected_article
                        st.rerun()

                    # Show notification if this article was just selected
                    if (st.session_state.get('selected_article') and
                        st.session_state.get('selected_article_id') == f"article_{start_idx + idx}" and
                        st.session_state.selected_article.get('headline') == article.get('headline')):
                        st.success("✅ Selected!")
                        st.caption("👉 Go to Translate tab")

        # Pagination controls (bottom)
        if total_pages > 1:
            st.divider()
            col1, col2, col3, col4, col5 = st.columns([1, 1, 2, 1, 1])

            with col1:
                if st.button("⏮️ First", key="first_bottom", disabled=(st.session_state.current_page == 1)):
                    st.session_state.current_page = 1
                    st.rerun()

            with col2:
                if st.button("◀️ Prev", key="prev_bottom", disabled=(st.session_state.current_page == 1)):
                    st.session_state.current_page -= 1
                    st.rerun()

            with col3:
                # Page selector
                new_page_bottom = st.selectbox(
                    "Go to page",
                    options=list(range(1, total_pages + 1)),
                    index=st.session_state.current_page - 1,
                    key="page_selector_bottom"
                )
                if new_page_bottom != st.session_state.current_page:
                    st.session_state.current_page = new_page_bottom
                    st.rerun()

            with col4:
                if st.button("Next ▶️", key="next_bottom", disabled=(st.session_state.current_page == total_pages)):
                    st.session_state.current_page += 1
                    st.rerun()

            with col5:
                if st.button("Last ⏭️", key="last_bottom", disabled=(st.session_state.current_page == total_pages)):
                    st.session_state.current_page = total_pages
                    st.rerun()

# ============================================================================
# TAB 2: TRANSLATE
# ============================================================================
with tab2:
    st.header("🔄 Translate Article")

    # Show selected article info if available
    if st.session_state.selected_article:
        article = st.session_state.selected_article

        st.success("✅ Selected Article:")
        st.markdown(f"""
        <div class="article-card">
            <div class="article-title">{article.get('headline', 'No title')}</div>
            <div class="article-meta">
                📰 {article.get('publisher', 'Unknown')} |
                🌍 {article.get('country', 'Unknown')}
            </div>
        </div>
        """, unsafe_allow_html=True)

        if article.get('article_url'):
            st.markdown(f"[🔗 Open in Browser]({article['article_url']})")

        st.divider()

    # Always show paste option
    # Always use AI translation (best quality)
    st.session_state.translation_method = 'openai'
    st.info("✨ **Smart AI Translation** - Automatically extracts and translates articles to Bengali")

    st.divider()

    st.subheader("📝 Paste Article Content")

    st.markdown("""
    **Instructions:**
    1. Open the article in your browser
    2. Press `Ctrl+A` (Select All)
    3. Press `Ctrl+C` (Copy)
    4. Paste below - AI will extract the article automatically!
    """)

    original_text = st.text_area(
        "Paste content here:",
        height=300,
        placeholder="Paste entire webpage here (Ctrl+A → Ctrl+C → Ctrl+V)..."
    )

    col1, col2 = st.columns(2)

    with col1:
        translate_btn = st.button("🔄 Translate", use_container_width=True, type="primary")

    with col2:
        clear_btn = st.button("🗑️ Clear", use_container_width=True)

    if clear_btn:
        st.session_state.current_original = ''
        st.session_state.current_translated = ''
        st.session_state.translation_tokens = 0
        st.rerun()

    if translate_btn:
        if not original_text.strip():
            st.error("❌ Paste some text first")
        else:
            with st.spinner("🔄 Translating to Bengali..."):
                translated, tokens = translate_text(
                    original_text,
                    st.session_state.target_lang,
                    method=st.session_state.translation_method
                )
                st.session_state.current_original = original_text
                st.session_state.current_translated = translated
                st.session_state.translation_tokens = tokens

                st.success("✅ Translation Complete!")

    if st.session_state.current_translated:
        st.divider()
        st.subheader("✨ Translation")
        st.markdown(f"""
        <div class="translation-box">
            {st.session_state.current_translated}
        </div>
        """, unsafe_allow_html=True)

        col1, col2 = st.columns(2)

        with col1:
            if st.button("💾 Save", use_container_width=True):
                # Create article object if not exists
                article = st.session_state.selected_article if st.session_state.selected_article else {
                    'headline': 'Direct Paste',
                    'publisher': 'Manual Entry',
                    'country': 'N/A'
                }
                filepath = save_translation(
                    st.session_state.current_original,
                    st.session_state.current_translated,
                    article
                )
                if filepath:
                    st.success(f"✅ Saved!")
                    st.session_state.translations.append({
                        'article': article,
                        'original': st.session_state.current_original,
                        'translated': st.session_state.current_translated,
                        'timestamp': datetime.now().isoformat(),
                        'filepath': filepath
                    })

        with col2:
            article = st.session_state.selected_article if st.session_state.selected_article else {
                'headline': 'Direct Paste',
                'publisher': 'Manual Entry'
            }
            download_content = f"""ARTICLE: {article.get('headline', 'N/A')}
PUBLISHER: {article.get('publisher', 'N/A')}
DATE: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

{'='*80}
ORIGINAL
{'='*80}

{st.session_state.current_original}

{'='*80}
TRANSLATION
{'='*80}

{st.session_state.current_translated}
"""
            st.download_button(
                "📥 Download",
                download_content,
                file_name=f"translation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                use_container_width=True
            )

        # ========================================================================
        # AI ENHANCEMENT SECTION (Integrated)
        # ========================================================================
        st.divider()
        st.subheader("✨ AI-Powered Enhancement")

        with st.expander("🤖 Enhance Translation with AI", expanded=False):
            # Simplified AI Model Selection (client-friendly)
            st.write("**🎯 AI Model Selection**")

            # Model mapping: Simple names → Actual models
            model_options = {
                "Model 1 (Fast & Economical)": ("openai", "gpt-3.5-turbo"),
                "Model 2 (Advanced & Precise)": ("openai", "gpt-4-turbo")
            }

            selected_model_name = st.selectbox(
                "Choose AI Model",
                options=list(model_options.keys()),
                index=1,  # Default to Model 2 (gpt-4-turbo)
                key='simple_model_select',
                help="Model 1: Faster, lower cost | Model 2: Higher quality, better accuracy"
            )

            # Set provider and model in session state (hidden from user)
            st.session_state.ai_provider, st.session_state.ai_model = model_options[selected_model_name]

            st.write("")
            st.write("**📝 Output Format**")

            # Format selection as dropdown
            format_options = {
                "Hard News Only": ['hard_news'],
                "Soft News Only": ['soft_news'],
                "Both (Hard + Soft News)": ['hard_news', 'soft_news']
            }

            selected_format_option = st.selectbox(
                "Choose format type",
                options=list(format_options.keys()),
                index=2,  # Default to "Both"
                key='format_dropdown',
                help="Hard News: Professional factual reporting | Soft News: Literary travel feature"
            )

            selected_formats = format_options[selected_format_option]

            st.write("")

            # Generate Button
            enhance_btn = st.button(
                "🚀 Generate Enhanced Content",
                use_container_width=True,
                type="primary",
                disabled=st.session_state.enhancement_in_progress or not selected_formats,
                key='enhance_translate_btn'
            )

            # Generate content
            if enhance_btn:
                st.session_state.enhancement_in_progress = True
                st.session_state.enhancement_results = {}

                # Progress tracking
                progress_bar = st.progress(0)
                status_text = st.empty()

                try:
                    status_text.text("🚀 Initializing AI provider...")

                    # Progress callback
                    def progress_callback(format_type, progress, result):
                        progress_bar.progress(progress)
                        config = get_format_config(format_type)
                        status_text.text(f"✨ Generating {config['name']}... ({progress}%)")

                    # Get article info
                    article = st.session_state.selected_article if st.session_state.selected_article else {
                        'headline': 'Direct Paste',
                        'publisher': 'Manual Entry',
                        'country': 'N/A'
                    }

                    # Generate content
                    results, enhancer = enhance_translation(
                        translated_text=st.session_state.current_translated,
                        article_info=article,
                        provider=st.session_state.ai_provider,
                        model=st.session_state.ai_model,
                        formats=selected_formats,
                        progress_callback=progress_callback
                    )

                    # Store results without auto-review
                    st.session_state.enhancement_results = results
                    st.session_state.enhancement_in_progress = False

                    # Complete
                    progress_bar.progress(100)
                    status_text.text("✅ Enhancement completed!")

                    # Show summary
                    summary = enhancer.get_summary()
                    st.success(f"✅ Generated {summary['successful']} formats | Tokens used: {summary['total_tokens']}")

                    # Save to history
                    st.session_state.enhanced_articles.append({
                        'article': article,
                        'results': results,
                        'provider': st.session_state.ai_provider,
                        'model': st.session_state.ai_model,
                        'timestamp': datetime.now().isoformat(),
                        'tokens': summary['total_tokens']
                    })

                    time.sleep(1)
                    st.rerun()

                except Exception as e:
                    st.session_state.enhancement_in_progress = False
                    st.error(f"❌ Error: {str(e)}")
                    logger.error(f"Enhancement failed: {e}")

        # Display Enhancement Results (if any)
        if st.session_state.enhancement_results:
            st.divider()
            st.subheader("✨ Enhanced Versions")

            # Optional AI Review Button (after generation)
            col1, col2 = st.columns([3, 1])
            with col1:
                st.info("💡 Edit the content below, then copy or download")
            with col2:
                if st.button("🔍 AI Review & Improve", use_container_width=True, help="Use AI to review and improve grammar, coherence, and tone"):
                    with st.spinner("Reviewing content..."):
                        review_agent = ReviewAgent(
                            provider_name=st.session_state.ai_provider,
                            model=st.session_state.ai_model
                        )

                        total_review_tokens = 0
                        for format_type, result in st.session_state.enhancement_results.items():
                            review_result = review_agent.review_content(
                                content=result.content,
                                format_type=format_type
                            )

                            if review_result['success']:
                                result.content = review_result['reviewed_content']
                                total_review_tokens += review_result['tokens_used']

                        st.success(f"✅ Review completed! Tokens used: {total_review_tokens}")
                        st.rerun()

            st.write("")

            for format_type, result in st.session_state.enhancement_results.items():
                config = get_format_config(format_type)

                with st.expander(f"{config['icon']} {config['name']}", expanded=True):
                    # Editable markdown text area
                    edited_content = st.text_area(
                        "Edit content:",
                        value=result.content,
                        height=400,
                        key=f"edit_{format_type}_translate",
                        help="You can edit this content before copying or downloading"
                    )

                    # Buttons row
                    col1, col2, col3, col4 = st.columns([1, 1, 1, 2])

                    with col1:
                        # Preview toggle
                        show_preview = st.checkbox("👁️ Preview", key=f"preview_{format_type}_translate")

                    with col2:
                        # Copy button (using Streamlit's native functionality)
                        if st.button(f"📋 Copy", key=f"copy_{format_type}_translate", use_container_width=True):
                            st.code(edited_content, language=None)
                            st.success("✅ Ready to copy!")

                    with col3:
                        # Download button
                        st.download_button(
                            f"📥 Download",
                            edited_content,
                            file_name=f"{format_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                            key=f"download_{format_type}_translate",
                            use_container_width=True
                        )

                    # Token count hidden from client view

                    # Show markdown preview if checkbox is checked
                    if show_preview:
                        st.markdown("---")
                        st.markdown("**Preview:**")
                        st.markdown(edited_content)



# ============================================================================
# NOTE: Enhancement feature is now integrated into the Translate tab (tab2)





# ============================================================================
# TAB 4: FUTURE ENHANCEMENT (Playwright Web Content Extractor)
# ============================================================================
with tab4:
    st.header("🚀 Future Enhancement - Web Content Extractor")

    st.info("💡 **Feature**: Extract complete content from any website using Playwright browser automation")

    # Initialize session state for extraction
    if 'extraction_result' not in st.session_state:
        st.session_state.extraction_result = None
    if 'extraction_in_progress' not in st.session_state:
        st.session_state.extraction_in_progress = False

    # URL Input
    col1, col2 = st.columns([3, 1])

    with col1:
        website_url = st.text_input(
            "Website URL",
            placeholder="https://example.com/article",
            help="Enter the full URL of the website you want to extract content from",
            key="website_url_input"
        )

    with col2:
        st.write("")
        st.write("")
        extract_btn = st.button(
            "🔍 Extract Content",
            use_container_width=True,
            type="primary",
            disabled=st.session_state.extraction_in_progress or not website_url
        )

    # Extract button action
    if extract_btn and website_url:
        st.session_state.extraction_in_progress = True
        st.session_state.extraction_result = None

        progress_placeholder = st.empty()
        status_placeholder = st.empty()

        try:
            progress_placeholder.info("🌐 Starting browser automation...")

            # Import required libraries
            import subprocess
            import json
            import tempfile

            logger.info(f"Starting content extraction from: {website_url}")

            # Create a temporary Python script to run Playwright
            extraction_script = f"""
import sys
import json
from playwright.sync_api import sync_playwright

url = {repr(website_url)}

try:
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        page = browser.new_page()
        page.goto(url, wait_until='networkidle', timeout=60000)

        extraction_data = page.evaluate('''() => {{
            const fullText = document.body.innerText;

            const links = Array.from(document.querySelectorAll('a[href]')).map(a => ({{
                text: a.innerText.trim(),
                href: a.href,
                title: a.title || ''
            }})).filter(link => link.text && link.href);

            const images = Array.from(document.querySelectorAll('img[src]')).map(img => ({{
                src: img.src,
                alt: img.alt || '',
                title: img.title || ''
            }}));

            const headings = Array.from(document.querySelectorAll('h1, h2, h3, h4, h5, h6')).map(h => ({{
                level: h.tagName,
                text: h.innerText.trim()
            }}));

            const lists = Array.from(document.querySelectorAll('ul, ol')).map(list => ({{
                type: list.tagName,
                items: Array.from(list.querySelectorAll('li')).map(li => li.innerText.trim())
            }}));

            const paragraphs = Array.from(document.querySelectorAll('p')).map(p => p.innerText.trim()).filter(text => text);

            const html = document.documentElement.outerHTML;

            const title = document.title;
            const metaDescription = document.querySelector('meta[name="description"]')?.content || '';
            const metaKeywords = document.querySelector('meta[name="keywords"]')?.content || '';

            return {{
                fullText,
                links,
                images,
                headings,
                lists,
                paragraphs,
                html,
                metadata: {{
                    title,
                    description: metaDescription,
                    keywords: metaKeywords,
                    url: window.location.href,
                    characterCount: fullText.length,
                    htmlLength: html.length
                }}
            }};
        }}''')

        browser.close()

        print(json.dumps({{"success": True, "data": extraction_data}}))

except Exception as e:
    print(json.dumps({{"success": False, "error": str(e)}}))
    sys.exit(1)
"""

            # Write script to temp file
            with tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False, encoding='utf-8') as f:
                temp_script = f.name
                f.write(extraction_script)

            status_placeholder.info("📡 Navigating to website...")

            # Run the script in a subprocess
            result = subprocess.run(
                [sys.executable, temp_script],
                capture_output=True,
                text=True,
                timeout=120
            )

            # Clean up temp file
            import os
            try:
                os.unlink(temp_script)
            except:
                pass

            if result.returncode == 0:
                # Parse JSON output
                try:
                    output = json.loads(result.stdout)

                    if output['success']:
                        extraction_data = output['data']

                        # Store result
                        st.session_state.extraction_result = {
                            'url': website_url,
                            'data': extraction_data,
                            'timestamp': datetime.now().isoformat()
                        }

                        logger.info(f"Extraction completed: {len(extraction_data['fullText'])} characters extracted")
                        progress_placeholder.empty()
                        status_placeholder.success(f"✅ Successfully extracted content from {website_url}")
                    else:
                        raise Exception(output['error'])
                except json.JSONDecodeError as e:
                    # Show raw output if JSON parsing fails
                    logger.error(f"JSON decode error. Stdout: {result.stdout}")
                    logger.error(f"Stderr: {result.stderr}")
                    raise Exception(f"Failed to parse extraction output. Stdout: {result.stdout[:500]}, Stderr: {result.stderr[:500]}")
            else:
                # Show detailed error information
                error_msg = f"Subprocess failed with return code {result.returncode}"
                logger.error(f"Stdout: {result.stdout}")
                logger.error(f"Stderr: {result.stderr}")
                raise Exception(f"{error_msg}\n\nStderr: {result.stderr}\n\nStdout: {result.stdout}")

        except subprocess.TimeoutExpired:
            logger.error("Extraction timeout")
            progress_placeholder.empty()
            status_placeholder.error("❌ Extraction timed out (120 seconds). The website may be too slow or unresponsive.")
        except Exception as e:
            logger.error(f"Extraction error: {e}")
            progress_placeholder.empty()
            status_placeholder.error(f"❌ Extraction failed: {str(e)}")
            st.info("💡 Make sure Playwright is installed: `pip install playwright && playwright install chromium`")
        finally:
            st.session_state.extraction_in_progress = False
            if st.session_state.extraction_result:
                st.rerun()

    # Display extraction results
    if st.session_state.extraction_result:
        result = st.session_state.extraction_result
        data = result['data']

        st.divider()
        st.subheader("📊 Extraction Results")

        # Metadata
        with st.expander("📋 Page Metadata", expanded=True):
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Total Characters", f"{data['metadata']['characterCount']:,}")
            with col2:
                st.metric("Total Links", len(data['links']))
            with col3:
                st.metric("Total Images", len(data['images']))

            st.write("**Page Title:**", data['metadata']['title'])
            if data['metadata']['description']:
                st.write("**Description:**", data['metadata']['description'])
            st.write("**URL:**", data['metadata']['url'])

        # Tabs for different content types
        content_tab1, content_tab2, content_tab3, content_tab4, content_tab5, content_tab6 = st.tabs([
            "📄 Full Text",
            "🔗 Links",
            "📝 Headings",
            "📋 Lists",
            "🖼️ Images",
            "💾 Actions"
        ])

        with content_tab1:
            st.subheader("📄 Complete Text Content")
            st.text_area(
                "Full Text",
                value=data['fullText'],
                height=400,
                key="extracted_full_text"
            )
            if st.button("📋 Copy Full Text", key="copy_fulltext"):
                st.code(data['fullText'], language=None)

        with content_tab2:
            st.subheader(f"🔗 All Links ({len(data['links'])})")
            if data['links']:
                # Filter options
                link_filter = st.text_input("Filter links", placeholder="Search links...", key="link_filter")

                filtered_links = [
                    link for link in data['links']
                    if not link_filter or link_filter.lower() in link['text'].lower() or link_filter.lower() in link['href'].lower()
                ]

                st.write(f"Showing {len(filtered_links)} of {len(data['links'])} links")

                for idx, link in enumerate(filtered_links[:100]):  # Limit to first 100
                    with st.container():
                        col1, col2 = st.columns([3, 1])
                        with col1:
                            st.markdown(f"**{idx+1}. {link['text'][:100]}**")
                            st.caption(f"🔗 {link['href']}")
                        with col2:
                            if st.button("Open", key=f"open_link_{idx}"):
                                st.write(f"[Open Link]({link['href']})")
                        st.divider()

                if len(filtered_links) > 100:
                    st.info(f"Showing first 100 links. Total: {len(filtered_links)}")
            else:
                st.info("No links found on this page")

        with content_tab3:
            st.subheader(f"📝 Headings ({len(data['headings'])})")
            if data['headings']:
                for heading in data['headings']:
                    level = int(heading['level'][1])  # Extract number from 'H1', 'H2', etc.
                    indent = "  " * (level - 1)
                    st.markdown(f"{indent}**{heading['level']}:** {heading['text']}")
            else:
                st.info("No headings found on this page")

        with content_tab4:
            st.subheader(f"📋 Lists ({len(data['lists'])})")
            if data['lists']:
                for idx, list_data in enumerate(data['lists']):
                    with st.expander(f"{list_data['type']} - {len(list_data['items'])} items", expanded=idx==0):
                        for item in list_data['items']:
                            st.write(f"• {item}")
            else:
                st.info("No lists found on this page")

        with content_tab5:
            st.subheader(f"🖼️ Images ({len(data['images'])})")
            if data['images']:
                cols = st.columns(3)
                for idx, img in enumerate(data['images'][:30]):  # Limit to first 30
                    with cols[idx % 3]:
                        try:
                            st.image(img['src'], caption=img['alt'] or img['title'] or f"Image {idx+1}", use_column_width=True)
                        except:
                            # Fallback if image fails to load
                            st.caption(f"🖼️ Image {idx+1}")
                        st.caption(f"🔗 {img['src'][:50]}...")

                if len(data['images']) > 30:
                    st.info(f"Showing first 30 images. Total: {len(data['images'])}")
            else:
                st.info("No images found on this page")

        with content_tab6:
            st.subheader("💾 Save & Export Options")

            col1, col2, col3 = st.columns(3)

            with col1:
                # Save full text
                if st.button("💾 Save Full Text", use_container_width=True):
                    filename = f"extracted_content_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                    filepath = TRANSLATIONS_DIR / filename
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(f"URL: {result['url']}\n")
                        f.write(f"Extracted: {result['timestamp']}\n")
                        f.write(f"Title: {data['metadata']['title']}\n\n")
                        f.write("="*80 + "\n\n")
                        f.write(data['fullText'])
                    st.success(f"✅ Saved to: {filepath}")

            with col2:
                # Save links as CSV
                if st.button("💾 Save Links as CSV", use_container_width=True):
                    import csv
                    filename = f"extracted_links_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
                    filepath = TRANSLATIONS_DIR / filename
                    with open(filepath, 'w', encoding='utf-8', newline='') as f:
                        writer = csv.DictWriter(f, fieldnames=['text', 'href', 'title'])
                        writer.writeheader()
                        writer.writerows(data['links'])
                    st.success(f"✅ Saved to: {filepath}")

            with col3:
                # Send to Translation tab
                if st.button("🔄 Send to Translation", use_container_width=True):
                    # Create article object for translation
                    st.session_state.selected_article = {
                        'headline': data['metadata']['title'],
                        'article_url': result['url'],
                        'publisher': 'Web Extract',
                        'country': 'Web',
                        'source': 'Playwright Extraction',
                        'extracted_content': data['fullText']
                    }
                    st.session_state.selected_article_id = f"extract_{datetime.now().timestamp()}"
                    st.success("✅ Content sent to Translation tab! Go to the 'Translate' tab to translate.")
                    logger.info(f"Extracted content sent to translation: {data['metadata']['title']}")

# ============================================================================
# TAB 5: SETTINGS (History, Files, Logs, App Settings)
# ============================================================================
with tab5:
    st.header("⚙️ Settings & Management")

    # Sub-tabs within Settings
    settings_tab1, settings_tab2, settings_tab3, settings_tab4 = st.tabs([
        "📚 Translation History",
        "📁 Files",
        "📋 Logs",
        "⚙️ App Settings"
    ])

    # ========================================================================
    # SETTINGS SUB-TAB 1: TRANSLATION HISTORY
    # ========================================================================
    with settings_tab1:
        st.subheader("📚 Translation History")

        if not st.session_state.translations:
            st.info("No translations yet")
        else:
            for idx, trans in enumerate(reversed(st.session_state.translations)):
                with st.expander(
                    f"📄 {trans['article'].get('headline', 'No title')[:60]}... - "
                    f"{datetime.fromisoformat(trans['timestamp']).strftime('%Y-%m-%d %H:%M')}"
                ):
                    st.write(f"**Publisher:** {trans['article'].get('publisher', 'Unknown')}")
                    st.write(f"**File:** {trans['filepath']}")

                    col1, col2 = st.columns(2)
                    with col1:
                        st.text_area("Original", trans['original'], height=150, disabled=True, key=f"o_{idx}")
                    with col2:
                        st.text_area("Translation", trans['translated'], height=150, disabled=True, key=f"t_{idx}")

    # ========================================================================
    # SETTINGS SUB-TAB 2: FILES
    # ========================================================================
    with settings_tab2:
        st.subheader("📁 Data Files")

        # Scraped files
        st.markdown("### 🕷️ Scraped Data")
        json_files = sorted(RAW_DATA_DIR.glob('*.json'), key=lambda p: p.stat().st_mtime, reverse=True)

        if json_files:
            for file in json_files[:10]:  # Show last 10
                col1, col2, col3 = st.columns([3, 1, 1])

                with col1:
                    st.text(file.name)

                with col2:
                    size_kb = file.stat().st_size / 1024
                    st.text(f"{size_kb:.1f} KB")

                with col3:
                    if st.button("Load", key=f"load_{file.name}"):
                        st.session_state.articles = load_articles(file)
                        st.success(f"Loaded {len(st.session_state.articles)} articles!")
        else:
            st.info("No data files yet")

        st.divider()

        # Translation files
        st.markdown("### 📝 Translations")
        trans_files = sorted(TRANSLATIONS_DIR.glob('*.txt'), key=lambda p: p.stat().st_mtime, reverse=True)

        if trans_files:
            st.text(f"Total: {len(trans_files)} files")
            for file in trans_files[:5]:
                st.text(f"📄 {file.name}")
        else:
            st.info("No translations yet")

    # ========================================================================
    # SETTINGS SUB-TAB 3: LOGS
    # ========================================================================
    with settings_tab3:
        st.subheader("📋 Application Logs")

        # Get log files
        from config.settings import LOGS_DIR
        log_files = sorted(LOGS_DIR.glob('*.log'), key=lambda p: p.stat().st_mtime, reverse=True)

        if not log_files:
            st.info("No log files found")
        else:
            # Log type selector
            col1, col2 = st.columns([3, 1])

            with col1:
                log_types = {
                    'scraper': '🕷️ Scraper Logs',
                    'webapp': '🌐 Web App Logs',
                    'scheduler': '⏰ Scheduler Logs',
                    'enhancer': '✨ AI Enhancer Logs'
                }

                selected_log_type = st.selectbox(
                    "Select Log Type",
                    options=list(log_types.keys()),
                    format_func=lambda x: log_types[x],
                    index=0
                )

            with col2:
                auto_refresh = st.checkbox("🔄 Auto-refresh", value=False, help="Refresh logs every 5 seconds")

            # Find logs of selected type
            matching_logs = [f for f in log_files if selected_log_type in f.name]

            if not matching_logs:
                st.warning(f"No {log_types[selected_log_type]} found")
            else:
                # Date selector
                log_dates = {}
                for log_file in matching_logs:
                    # Extract date from filename (format: type_YYYYMMDD.log)
                    parts = log_file.stem.split('_')
                    if len(parts) >= 2:
                        date_str = parts[-1]
                        try:
                            log_date = datetime.strptime(date_str, '%Y%m%d').strftime('%Y-%m-%d')
                            log_dates[log_date] = log_file
                        except:
                            pass

                if log_dates:
                    selected_date = st.selectbox(
                        "Select Date",
                        options=sorted(log_dates.keys(), reverse=True),
                        index=0
                    )

                    selected_log_file = log_dates[selected_date]

                    # Display controls
                    col1, col2, col3 = st.columns([2, 1, 1])

                    with col1:
                        st.info(f"📄 **File:** `{selected_log_file.name}` | **Size:** {selected_log_file.stat().st_size / 1024:.1f} KB")

                    with col2:
                        max_lines = st.number_input("Max lines", min_value=50, max_value=5000, value=500, step=50)

                    with col3:
                        show_all = st.checkbox("Show all", value=False)

                    st.divider()

                    # Read and display log
                    try:
                        with open(selected_log_file, 'r', encoding='utf-8') as f:
                            lines = f.readlines()

                        if not show_all:
                            lines = lines[-max_lines:]  # Show last N lines

                        # Display log content
                        st.markdown(f"### 📜 Log Content ({len(lines)} lines)")

                        # Add filter
                        filter_text = st.text_input("🔍 Filter logs", placeholder="Enter text to filter...", key="log_filter")

                        if filter_text:
                            filtered_lines = [line for line in lines if filter_text.lower() in line.lower()]
                            st.write(f"Showing {len(filtered_lines)} matching lines")
                            log_content = ''.join(filtered_lines)
                        else:
                            log_content = ''.join(lines)

                        # Display in code block
                        st.code(log_content, language='log')

                        # Download button
                        st.download_button(
                            "📥 Download Full Log",
                            ''.join(lines),
                            file_name=selected_log_file.name,
                            mime='text/plain'
                        )

                    except Exception as e:
                        st.error(f"Error reading log file: {e}")

                    # Auto-refresh mechanism
                    if auto_refresh:
                        time.sleep(5)
                        st.rerun()
                else:
                    st.warning("No valid log files found")

    # ========================================================================
    # SETTINGS SUB-TAB 4: APP SETTINGS
    # ========================================================================
    with settings_tab4:
        st.subheader("⚙️ Application Settings")

        st.markdown("### 🤖 AI Configuration")

        col1, col2 = st.columns(2)

        with col1:
            # AI Provider selection (read-only display)
            st.info("**AI Provider:** OpenAI (Default)")
            st.caption("Translation and content enhancement use OpenAI's models")

        with col2:
            # Model selection (read-only display)
            st.info("**Model:** GPT-4 Turbo")
            st.caption("Optimized for natural Bengali translation")

        st.divider()

        st.markdown("### 🔍 Search Settings")

        col1, col2 = st.columns(2)

        with col1:
            default_max_results = st.number_input(
                "Default Max Search Results",
                min_value=5,
                max_value=30,
                value=st.session_state.search_max_results,
                step=5,
                help="Set default number of search results"
            )
            if default_max_results != st.session_state.search_max_results:
                st.session_state.search_max_results = default_max_results
                st.success("✅ Search settings updated!")

        with col2:
            articles_per_page_default = st.selectbox(
                "Default Articles Per Page",
                options=[10, 20, 50, 100],
                index=[10, 20, 50, 100].index(st.session_state.articles_per_page),
                help="Set default pagination size"
            )
            if articles_per_page_default != st.session_state.articles_per_page:
                st.session_state.articles_per_page = articles_per_page_default
                st.success("✅ Pagination settings updated!")

        st.divider()

        st.markdown("### 📊 System Information")

        info_col1, info_col2 = st.columns(2)

        with info_col1:
            st.metric("Total Articles Loaded", len(st.session_state.articles))
            st.metric("Total Translations", len(st.session_state.translations))

        with info_col2:
            # Count files
            json_files = list(RAW_DATA_DIR.glob('*.json'))
            trans_files = list(TRANSLATIONS_DIR.glob('*.txt'))
            st.metric("Scraped Data Files", len(json_files))
            st.metric("Translation Files", len(trans_files))

        st.divider()

        st.markdown("### 🗂️ Data Directories")
        st.code(f"""
Raw Data:        {RAW_DATA_DIR}
Translations:    {TRANSLATIONS_DIR}
Enhanced:        {RAW_DATA_DIR.parent / 'enhanced'}
Logs:            {LOGS_DIR}
        """, language="text")

# ============================================================================
# TAB 3: SEARCH
# ============================================================================
with tab3:
    st.header("🔍 Search Articles")

    # (Removed top-level notification - now showing inline below Select buttons)

    # Search Input Section
    col1, col2, col3 = st.columns([3, 1, 1])

    with col1:
        keyword = st.text_input(
            "Search Query (Bengali or English)",
            value=st.session_state.search_keyword,
            placeholder="e.g., রোহিঙ্গা, Cox's Bazar tourism, Bangladesh news",
            help="Search the entire web for news articles",
            key="main_search_input"
        )

    with col2:
        max_results = st.number_input(
            "Max Results",
            min_value=5,
            max_value=30,
            value=st.session_state.search_max_results,
            step=5,
            help="Maximum number of articles",
            key="max_results_input"
        )
        # Update session state when changed
        st.session_state.search_max_results = max_results

    with col3:
        st.write("")  # Spacing
        search_btn = st.button(
            "🔍 Search",
            use_container_width=True,
            type="primary",
            disabled=not keyword or st.session_state.search_in_progress
        )

    # Perform search
    if search_btn:
        st.session_state.search_in_progress = True
        st.session_state.search_keyword = keyword

        with st.spinner(f"🌐 Searching for '{keyword}'..."):
            try:
                from core.keyword_search import KeywordSearcher
                searcher = KeywordSearcher()
                articles = searcher.search_web(keyword=keyword, max_results=max_results)

                st.session_state.search_results = {
                    'web_search': articles,
                    'total_results': len(articles)
                }
                st.session_state.search_in_progress = False

                if articles:
                    st.success(f"✅ Found {len(articles)} articles")
                else:
                    st.warning("No results found")

            except Exception as e:
                st.error(f"❌ Search failed: {str(e)}")
                logger.error(f"Keyword search error: {e}")
                st.session_state.search_in_progress = False

    st.divider()

    # SIMPLIFIED SEARCH RESULTS - Just show list and redirect to Translate tab
    if st.session_state.search_results:
        results = st.session_state.search_results
        articles = results.get('web_search', [])

        if articles:
            st.subheader(f"📋 Search Results ({len(articles)})")
            st.info("💡 Click 'Select' to open the article in the Translate tab")

            # Display search results in a simple list
            for idx, article in enumerate(articles):
                with st.container():
                    col1, col2 = st.columns([4, 1])

                    with col1:
                        st.markdown(f"**#{idx+1}. {article['headline']}**")

                        source_badge = f"🌐 {article.get('source', 'Unknown')}"
                        lang_badge = "🇧🇩 Bengali" if article.get('language') == 'bn' else "🇬🇧 English"

                        st.caption(f"{source_badge} | {lang_badge} | 🔗 [Open Article]({article['url']})")
                        st.caption(article.get('snippet', '')[:150] + '...')

                    with col2:
                        # Select button - same behavior as Articles tab
                        if st.button("Select", key=f"select_search_{idx}", use_container_width=True):
                            # Set this as selected article (MUST match Articles tab format)
                            st.session_state.selected_article = {
                                'headline': article['headline'],
                                'article_url': article['url'],
                                'publisher': article.get('source', 'Web Search'),  # Map 'source' to 'publisher'
                                'country': 'Web' if article.get('language') == 'en' else 'Bangladesh',  # Map language to country
                                'source': article.get('source', 'Web Search'),
                                'language': article.get('language', 'en')
                            }
                            st.session_state.selected_article_id = f"search_{idx}"
                            logger.info(f"Article selected from search: {article['headline'][:50]}")
                            # Force a rerun to update all tabs with new selected_article
                            st.rerun()

                        # Show notification if this article was just selected
                        if (st.session_state.get('selected_article') and
                            st.session_state.get('selected_article_id') == f"search_{idx}" and
                            st.session_state.selected_article.get('headline') == article['headline']):
                            st.success("✅ Selected!")
                            st.caption("👉 Go to Translate tab")

                    st.divider()

# Footer
st.divider()
st.markdown("""
<div style='text-align: center; color: #666; padding: 1rem;'>
    ✈️ Travel News Translator | Built with Streamlit<br>
    📝 Data: <code>data/</code> | Translations: <code>translations/</code> | Logs: <code>logs/</code>
</div>
""", unsafe_allow_html=True)

# ============================================================================
# LIGHT POLLING MECHANISM - 4 SECOND INTERVAL
# ============================================================================
if st.session_state.is_polling:
    time.sleep(4)  # Wait 4 seconds
    st.rerun()  # Refresh page to check status