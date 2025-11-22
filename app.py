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
if 'enhanced_articles' not in st.session_state:
    st.session_state.enhanced_articles = []

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
            provider_name=AI_CONFIG['provider'],
            model=AI_CONFIG['model']
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
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📰 Articles", "🔄 Translate", "📚 History", "📁 Files", "📋 Logs"])

# ============================================================================
# TAB 1: ARTICLES
# ============================================================================
with tab1:
    st.header("📰 Available Travel Articles")

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
                        url = article.get('article_url', '')
                        if url:
                            st.success("✅ Selected!")
                            st.markdown(f"[🔗 Open Article]({url})")
                            logger.info(f"Article selected: {article.get('headline', 'N/A')[:50]}")

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
    
    if not st.session_state.selected_article:
        st.warning("⚠️ Select an article from the Articles tab first")
    else:
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

        # Translation method selector
        st.subheader("🤖 Translation Method")
        col1, col2 = st.columns(2)

        with col1:
            st.session_state.translation_method = st.radio(
                "Choose translation engine:",
                options=['openai', 'google'],
                format_func=lambda x: '🤖 OpenAI (Smart)' if x == 'openai' else '🌐 Google Translate (Basic)',
                horizontal=True,
                help="OpenAI: Intelligently extracts article and translates naturally\nGoogle: Fast but basic word-by-word translation"
            )

        with col2:
            if st.session_state.translation_method == 'openai':
                st.info("✨ AI will extract article from page and translate intelligently")
            else:
                st.info("⚡ Fast translation but less context-aware")

        st.divider()

        st.subheader("📝 Paste Article Content")

        if st.session_state.translation_method == 'openai':
            st.markdown("**Instructions:**")
            st.markdown("1. Open the article in your browser")
            st.markdown("2. Press `Ctrl+A` (Select All)")
            st.markdown("3. Press `Ctrl+C` (Copy)")
            st.markdown("4. Paste below - AI will extract the article automatically!")
        else:
            st.markdown("**Instructions:** Copy just the article text and paste below")

        original_text = st.text_area(
            "Paste content here:",
            height=300,
            placeholder="Paste entire webpage here (Ctrl+A → Ctrl+C → Ctrl+V)..." if st.session_state.translation_method == 'openai' else "Paste article text here..."
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
                method_name = "🤖 OpenAI (Smart Translation)" if st.session_state.translation_method == 'openai' else "🌐 Google Translate"
                with st.spinner(f"🔄 Translating with {method_name}..."):
                    translated, tokens = translate_text(
                        original_text,
                        st.session_state.target_lang,
                        method=st.session_state.translation_method
                    )
                    st.session_state.current_original = original_text
                    st.session_state.current_translated = translated
                    st.session_state.translation_tokens = tokens

                    if st.session_state.translation_method == 'openai':
                        st.success(f"✅ Translated! (Used {tokens} tokens)")
                    else:
                        st.success("✅ Translated!")
        
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
                # AI Provider Selection
                col1, col2 = st.columns(2)

                with col1:
                    st.write("**🤖 AI Provider**")

                    provider_options = list(AI_CONFIG['providers'].keys())
                    provider_labels = [
                        f"{AI_CONFIG['providers'][p]['icon']} {AI_CONFIG['providers'][p]['name']}"
                        for p in provider_options
                    ]

                    selected_provider_idx = st.selectbox(
                        "Provider",
                        options=range(len(provider_options)),
                        format_func=lambda x: provider_labels[x],
                        index=provider_options.index(st.session_state.ai_provider),
                        key='provider_select_translate',
                        label_visibility="collapsed"
                    )

                    st.session_state.ai_provider = provider_options[selected_provider_idx]

                with col2:
                    st.write("**🎯 Model**")

                    # Get models for selected provider
                    models = AI_CONFIG['providers'][st.session_state.ai_provider]['models']
                    model_keys = list(models.keys())
                    model_labels = list(models.values())

                    # Default model
                    if st.session_state.ai_provider == 'openai':
                        default_model = AI_CONFIG['default_openai_model']
                    else:
                        default_model = AI_CONFIG['default_groq_model']

                    try:
                        default_idx = model_keys.index(default_model)
                    except:
                        default_idx = 0

                    selected_model_idx = st.selectbox(
                        "Model",
                        options=range(len(model_keys)),
                        format_func=lambda x: model_labels[x],
                        index=default_idx,
                        key='model_select_translate',
                        label_visibility="collapsed"
                    )

                    st.session_state.ai_model = model_keys[selected_model_idx]

                st.write("")
                st.write("**📝 Select Output Formats**")

                col1, col2, col3 = st.columns(3)

                selected_formats = []

                with col1:
                    if st.checkbox("📰 Newspaper", value=True, key='format_newspaper_translate'):
                        selected_formats.append('newspaper')
                    if st.checkbox("📝 Blog", value=True, key='format_blog_translate'):
                        selected_formats.append('blog')

                with col2:
                    if st.checkbox("📱 Facebook", value=True, key='format_facebook_translate'):
                        selected_formats.append('facebook')
                    if st.checkbox("📸 Instagram", value=True, key='format_instagram_translate'):
                        selected_formats.append('instagram')

                with col3:
                    if st.checkbox("📄 Hard News", value=True, key='format_hard_news_translate'):
                        selected_formats.append('hard_news')
                    if st.checkbox("✍️ Soft News", value=True, key='format_soft_news_translate'):
                        selected_formats.append('soft_news')

                if not selected_formats:
                    st.warning("⚠️ Please select at least one format")

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

                        # Generate content
                        results, enhancer = enhance_translation(
                            translated_text=st.session_state.current_translated,
                            article_info=article,
                            provider=st.session_state.ai_provider,
                            model=st.session_state.ai_model,
                            formats=selected_formats,
                            progress_callback=progress_callback
                        )

                        st.session_state.enhancement_results = results
                        st.session_state.enhancement_in_progress = False

                        # Complete
                        progress_bar.progress(100)
                        status_text.text("✅ Enhancement completed!")

                        # Show summary
                        summary = enhancer.get_summary()
                        st.success(f"✅ Generated {summary['successful']} formats using {summary['total_tokens']} tokens")

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

                for format_type, result in st.session_state.enhancement_results.items():
                    config = get_format_config(format_type)

                    with st.expander(f"{config['icon']} {config['name']}", expanded=True):
                        st.markdown(result.content)

                        # Download button for each format
                        st.download_button(
                            f"📥 Download {config['name']}",
                            result.content,
                            file_name=f"{format_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                            key=f"download_{format_type}_translate"
                        )



# ============================================================================
# NOTE: Enhancement feature is now integrated into the Translate tab (tab2)





# ============================================================================
# TAB 3: HISTORY
# ============================================================================
with tab3:
    st.header("📚 Translation History")
    
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

# ============================================================================
# TAB 4: FILES
# ============================================================================
with tab4:
    st.header("📁 Data Files")
    
    # Scraped files
    st.subheader("🕷️ Scraped Data")
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
    st.subheader("📝 Translations")
    trans_files = sorted(TRANSLATIONS_DIR.glob('*.txt'), key=lambda p: p.stat().st_mtime, reverse=True)
    
    if trans_files:
        st.text(f"Total: {len(trans_files)} files")
        for file in trans_files[:5]:
            st.text(f"📄 {file.name}")
    else:
        st.info("No translations yet")

# ============================================================================
# TAB 5: LOGS
# ============================================================================
with tab5:
    st.header("📋 Scraping Logs")

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
                    st.subheader(f"📜 Log Content ({len(lines)} lines)")

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