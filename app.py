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

# Translation
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

def translate_text(text, target_lang):
    """Translate text"""
    try:
        translator = GoogleTranslator(source='auto', target=target_lang)
        max_length = TRANSLATION_CONFIG['chunk_size']
        
        if len(text) <= max_length:
            translated = translator.translate(text)
        else:
            chunks = [text[i:i+max_length] for i in range(0, len(text), max_length)]
            translated_chunks = [translator.translate(chunk) for chunk in chunks]
            translated = ' '.join(translated_chunks)
        
        logger.info(f"Translation completed: {len(text)} -> {len(translated)} chars")
        return translated
    except Exception as e:
        logger.error(f"Translation error: {e}")
        return f"Translation error: {e}"

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
                Progress: {status.progress}%<br>
                Status: {status.status_message}<br>
                Articles: {status.articles_count}
            </div>
            """, unsafe_allow_html=True)
            
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
                Articles: {status.articles_count}<br>
                Duration: {(status.end_time - status.start_time).total_seconds():.1f}s
            </div>
            """, unsafe_allow_html=True)
            
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
#tab1, tab2, tab3, tab4 = st.tabs(["📰 Articles", "🔄 Translate", "📚 History", "📁 Files"])
tab1, tab2, tab3, tab4, tab5 = st.tabs(["📰 Articles", "🔄 Translate", "✨ Enhancement", "📚 History", "📁 Files"])

# ============================================================================
# TAB 1: ARTICLES
# ============================================================================
with tab1:
    st.header("📰 Available Travel Articles")
    
    if not st.session_state.articles:
        st.info("👆 Click 'Load Latest' or 'Start Scraping' in the sidebar")
    else:
        # Search/Filter
        search = st.text_input("🔍 Search articles", placeholder="Enter keywords...")
        
        filtered_articles = st.session_state.articles
        if search:
            filtered_articles = [
                a for a in st.session_state.articles 
                if search.lower() in a.get('headline', '').lower()
            ]
        
        st.write(f"Showing {len(filtered_articles)} articles")
        
        # Display articles
        for idx, article in enumerate(filtered_articles):
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
                    if st.button("Select", key=f"select_{idx}", use_container_width=True):
                        st.session_state.selected_article = article
                        url = article.get('article_url', '')
                        if url:
                            st.success("✅ Selected!")
                            st.markdown(f"[🔗 Open Article]({url})")
                            logger.info(f"Article selected: {article.get('headline', 'N/A')[:50]}")

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
        
        st.subheader("📝 Paste Article Content")
        original_text = st.text_area(
            "Paste content here:",
            height=300,
            placeholder="Copy the article and paste here..."
        )
        
        col1, col2 = st.columns(2)
        
        with col1:
            translate_btn = st.button("🔄 Translate", use_container_width=True, type="primary")
        
        with col2:
            clear_btn = st.button("🗑️ Clear", use_container_width=True)
        
        if clear_btn:
            st.session_state.current_original = ''
            st.session_state.current_translated = ''
            st.rerun()
        
        if translate_btn:
            if not original_text.strip():
                st.error("❌ Paste some text first")
            else:
                with st.spinner(f"🔄 Translating to {TRANSLATION_CONFIG['available_languages'][st.session_state.target_lang]}..."):
                    translated = translate_text(original_text, st.session_state.target_lang)
                    st.session_state.current_original = original_text
                    st.session_state.current_translated = translated
        
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



# TAB 3: AI ENHANCEMENT 
# ============================================================================
with tab3:
    st.header("✨ AI-Powered Content Enhancement")
    
    # Check if translation exists
    if not st.session_state.current_translated:
        st.warning("⚠️ Please translate an article first (go to Translate tab)")
    else:
        # Show current translation info
        st.success("✅ Translation Ready for Enhancement")
        
        if st.session_state.selected_article:
            article = st.session_state.selected_article
            st.markdown(f"""
            <div class="article-card">
                <div class="article-title">{article.get('headline', 'No title')}</div>
                <div class="article-meta">
                    📰 {article.get('publisher', 'Unknown')} | 
                    🌍 {article.get('country', 'Unknown')}
                </div>
            </div>
            """, unsafe_allow_html=True)
        
        st.divider()
        
        # AI Provider Selection
        col1, col2 = st.columns(2)
        
        with col1:
            st.subheader("🤖 Select AI Provider")
            
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
                key='provider_select'
            )
            
            st.session_state.ai_provider = provider_options[selected_provider_idx]
        
        with col2:
            st.subheader("🎯 Select Model")
            
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
                key='model_select'
            )
            
            st.session_state.ai_model = model_keys[selected_model_idx]
        
        st.divider()
        
        # Format Selection
        st.subheader("📝 Select Output Formats")
        
        col1, col2, col3, col4 = st.columns(4)
        
        selected_formats = []
        
        with col1:
            if st.checkbox("📰 Newspaper", value=True, key='format_newspaper'):
                selected_formats.append('newspaper')
        
        with col2:
            if st.checkbox("📝 Blog", value=True, key='format_blog'):
                selected_formats.append('blog')
        
        with col3:
            if st.checkbox("📱 Facebook", value=True, key='format_facebook'):
                selected_formats.append('facebook')
        
        with col4:
            if st.checkbox("📸 Instagram", value=True, key='format_instagram'):
                selected_formats.append('instagram')
        
        if not selected_formats:
            st.error("❌ Please select at least one format")
        
        st.divider()
        
        # Generate Button
        col1, col2, col3 = st.columns([2, 1, 1])
        
        with col1:
            generate_btn = st.button(
                "🚀 Generate Enhanced Content", 
                use_container_width=True, 
                type="primary",
                disabled=st.session_state.enhancement_in_progress or not selected_formats
            )
        
        with col2:
            if st.button("🗑️ Clear Results", use_container_width=True):
                st.session_state.enhancement_results = {}
                st.rerun()
        
        with col3:
            st.metric("Formats", len(selected_formats))
        
        # Generate content
        if generate_btn:
            st.session_state.enhancement_in_progress = True
            st.session_state.enhancement_results = {}
            
            # Progress tracking
            progress_bar = st.progress(0)
            status_text = st.empty()
            
            try:
                status_text.text("🚀 Initializing AI provider...")
                
                # Get article info
                article_info = st.session_state.selected_article or {}
                
                # Progress callback
                def progress_callback(format_type, progress, result):
                    progress_bar.progress(progress)
                    config = get_format_config(format_type)
                    status_text.text(f"✨ Generating {config['name']}... ({progress}%)")
                
                # Generate content
                results, enhancer = enhance_translation(
                    translated_text=st.session_state.current_translated,
                    article_info=article_info,
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
                    'article': article_info,
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
        
        # Display Results
        if st.session_state.enhancement_results:
            st.divider()
            st.header("📊 Generated Content")
            
            for format_type, result in st.session_state.enhancement_results.items():
                if not result.success:
                    st.error(f"❌ {format_type} generation failed: {result.error}")
                    continue
                
                config = get_format_config(format_type)
                
                with st.expander(
                    f"{config['icon']} {config['name']} ({result.tokens_used} tokens)", 
                    expanded=True
                ):
                    # Display content
                    st.markdown(f"""
                    <div class="translation-box">
                        <div style="white-space: pre-wrap; font-family: 'Kalpurush', 'Noto Sans Bengali', sans-serif;">
                            {result.content}
                        </div>
                    </div>
                    """, unsafe_allow_html=True)
                    
                    # Action buttons
                    col1, col2, col3 = st.columns(3)
                    
                    with col1:
                        # Copy button
                        if st.button(f"📋 Copy", key=f"copy_{format_type}", use_container_width=True):
                            st.code(result.content, language='text')
                            st.success("✅ Content displayed above - you can copy it!")
                    
                    with col2:
                        # Download button
                        download_filename = f"{format_type}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt"
                        st.download_button(
                            "📥 Download",
                            result.content,
                            file_name=download_filename,
                            use_container_width=True,
                            key=f"download_{format_type}"
                        )
                    
                    with col3:
                        # Save button
                        if st.button(f"💾 Save", key=f"save_{format_type}", use_container_width=True):
                            # Save individual file
                            filepath = AI_CONFIG['enhanced_dir'] / download_filename
                            
                            file_content = f"""{'='*80}
{config['icon']} {config['name'].upper()}
{'='*80}

ARTICLE: {st.session_state.selected_article.get('headline', 'N/A')}
PROVIDER: {st.session_state.ai_provider} ({st.session_state.ai_model})
GENERATED: {result.generated_at}
TOKENS: {result.tokens_used}

{'='*80}
CONTENT
{'='*80}

{result.content}
"""
                            
                            with open(filepath, 'w', encoding='utf-8') as f:
                                f.write(file_content)
                            
                            st.success(f"✅ Saved to {filepath}")
            
            # Save all button
            st.divider()
            
            col1, col2 = st.columns([3, 1])
            
            with col1:
                if st.button("💾 Save All Formats", use_container_width=True, type="primary"):
                    try:
                        enhancer = ContentEnhancer(
                            provider_name=st.session_state.ai_provider,
                            model=st.session_state.ai_model
                        )
                        enhancer.results = st.session_state.enhancement_results
                        enhancer.total_tokens = sum(r.tokens_used for r in enhancer.results.values())
                        
                        saved_files = enhancer.save_results(
                            save_dir=AI_CONFIG['enhanced_dir'],
                            article_info=st.session_state.selected_article or {}
                        )
                        
                        st.success(f"✅ Saved {len(saved_files)} files to {AI_CONFIG['enhanced_dir']}")
                        
                        for format_type, filepath in saved_files.items():
                            st.text(f"📄 {format_type}: {Path(filepath).name}")
                        
                    except Exception as e:
                        st.error(f"❌ Error saving files: {e}")
            
            with col2:
                total_tokens = sum(r.tokens_used for r in st.session_state.enhancement_results.values())
                st.metric("Total Tokens", total_tokens)




# ============================================================================
# TAB 3: HISTORY
# ============================================================================
with tab4:
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
with tab5:
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