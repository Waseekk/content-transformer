"""
AI-Powered Translation Enhancement
Agentic Workflow for Multi-Format Content Generation
"""

from pathlib import Path
from datetime import datetime
import json
import re

# Import modules
from app.core.ai_providers import get_provider
from app.core.prompts import get_format_config, get_user_prompt
from app.core.text_processor import process_enhanced_content, needs_checker
from app.utils.logger import LoggerManager

logger = LoggerManager.get_logger('enhancer')


# ============================================================================
# COMBINED EXTRACT + TRANSLATE + FORMAT PROMPT
# ============================================================================

CHUNKED_THRESHOLD = 2000   # Words above which chunked pipeline is used
CHUNK_SIZE = 1500          # Target words per chunk

# System prompt for generating ONLY headline + byline + intro from the full article
# Used in chunked pipeline so the intro reflects the WHOLE article, not just the first chunk
INTRO_ONLY_SYSTEM_PROMPT = """আপনি "বাংলার কলম্বাস" পত্রিকার একজন অভিজ্ঞ ভ্রমণ সাংবাদিক।

পুরো নিবন্ধটি পড়ুন এবং শুধুমাত্র এই তিনটি অংশ লিখুন:

১. **শিরোনাম** (সম্পূর্ণ bold) — সংক্ষিপ্ত, তথ্যভিত্তিক
২. নিউজ ডেস্ক, বাংলার কলম্বাস (bold নয়)
৩. **ভূমিকা অনুচ্ছেদ** (সম্পূর্ণ bold) — পুরো নিবন্ধের মূল বিষয় তুলে ধরুন, ৩-৪টি পূর্ণ বাক্য

⚠️ ভূমিকা নিয়ম:
- পুরো ৩-৪ বাক্য একটি **...**-এর মধ্যে মুড়িয়ে দিন
- ❌ ভুল: **একটি বাক্য** তারপর non-bold বাক্য
- ✅ সঠিক: **বাক্য ১। বাক্য ২। বাক্য ৩। বাক্য ৪।**

শুধু এই তিনটি অংশ লিখুন — বডি অনুচ্ছেদ বা সাবহেড লিখবেন না।
সম্পূর্ণ বাংলাদেশী বাংলায় লিখুন।"""

# System prompt for continuation chunks — articles WITH subheads (tips/guides)
CONTINUATION_SYSTEM_PROMPT = """আপনি "বাংলার কলম্বাস" পত্রিকার একজন অভিজ্ঞ ভ্রমণ সাংবাদিক।

এটি একটি চলমান নিবন্ধের অতিরিক্ত অংশ ফরম্যাট করার কাজ।

কঠোর নিষেধাজ্ঞা — এগুলো লিখবেন না:
- নতুন শিরোনাম (headline)
- নতুন বাইলাইন (নিউজ ডেস্ক, বাংলার কলম্বাস)
- নতুন ভূমিকা (intro paragraph)

সরাসরি **প্রথম সাবহেড** দিয়ে শুরু করুন।

ফরম্যাট নিয়ম:
- প্রতিটি টিপস বা গন্তব্যের জন্য **Bold সাবহেড** — মূল ইনপুটে যে নাম/শিরোনাম আছে সেটি অনুবাদ করুন, নতুন নাম বানাবেন না
- সাবহেডের নিচে পূর্ণ বিবরণ — সংক্ষিপ্ত করবেন না
- অনুচ্ছেদ সর্বোচ্চ ২ বাক্য, Bold নয়
- প্রতিটি টিপসের শেষে যদি ইনপুটে একটি ছোট নাম (লেখকের attribution) থাকে — সেটি সাধারণ (non-bold) টেক্সটে রাখুন। ইনপুটে যা নেই তা যোগ করবেন না।
- সব তথ্য, উদ্ধৃতি, পরিসংখ্যান সংরক্ষণ করুন — কিছুই বাদ দেবেন না
- সম্পূর্ণ বাংলাদেশী বাংলায় লিখুন (ভারতীয় বাংলা নয়)"""

# System prompt for continuation chunks — articles WITHOUT subheads (narrative features)
CONTINUATION_SYSTEM_PROMPT_NO_SUBHEADS = """আপনি "বাংলার কলম্বাস" পত্রিকার একজন অভিজ্ঞ ভ্রমণ সাংবাদিক।

এটি একটি চলমান নিবন্ধের অতিরিক্ত অংশ ফরম্যাট করার কাজ।

কঠোর নিষেধাজ্ঞা — এগুলো লিখবেন না:
- নতুন শিরোনাম (headline)
- নতুন বাইলাইন (নিউজ ডেস্ক, বাংলার কলম্বাস)
- নতুন ভূমিকা (intro paragraph)
- ⚠️ কোনো সাবহেড বা বোল্ড সেকশন শিরোনাম নয় — এই নিবন্ধে কোনো সাবহেড নেই
- কোনো লাইন **Bold** করবেন না

সরাসরি body paragraph দিয়ে শুরু করুন।

ফরম্যাট নিয়ম:
- অনুচ্ছেদ সর্বোচ্চ ২ বাক্য, Bold নয়
- উদ্ধৃতি অনুচ্ছেদের শেষে রাখুন (মাঝখানে নয়) — ফরম্যাট: তিনি বলেন, "..." অথবা জানান, "..."
- উদ্ধৃতির পর নতুন অনুচ্ছেদ শুরু করুন
- সব তথ্য, উদ্ধৃতি, পরিসংখ্যান সংরক্ষণ করুন — কিছুই বাদ দেবেন না
- সম্পূর্ণ বাংলাদেশী বাংলায় লিখুন (ভারতীয় বাংলা নয়)"""


COMBINED_EXTRACT_TRANSLATE_PREFIX = """You are a senior journalist at "বাংলার কলম্বাস" newspaper with 20 years of experience.

Your task has THREE steps:

STEP 1 — EXTRACT:
Extract ONLY the main article content from the provided English text.
REMOVE: navigation menus, advertisements, cookie notices, social buttons, comment sections, footer/header content, related article links, weather widgets, any section marked "should not be translated" or "these are links."
KEEP: article headline, body paragraphs, direct quotes, statistics, author name, publication date.

STEP 2 — WRITE IN NEWSPAPER BENGALI:
Based on the extracted content, write as a professional Bangladeshi journalist would — NOT a literal translation.
- Do NOT translate word for word. Adapt the content into natural newspaper Bengali.
- If the original uses first-person (I, me, my, we), convert to third-person journalistic style (he/she/the author/reporters/tourists etc.)
- Transliterate proper names into Bengali script (Paris → প্যারিস, Troy Robinson → ট্রয় রবিনসন, Coffs Harbour → কফস হারবার, she-oak → শি-ওক গাছ)
- ⚠️ Every word must be in Bengali — NO English words should appear in the Bengali output (not even "exclaimed", "impending", etc.)
- Preserve every fact, statistic, quote, and piece of information — but rewrite sentences in journalistic Bengali style

STEP 3 — FORMAT AS BANGLAR COLUMBUS STYLE:
Detect the travel content type and apply the formatting rules below.

---

"""


class EnhancementResult:
    """Store enhancement results"""

    def __init__(self, format_type, content, tokens_used=0):
        self.format_type = format_type
        self.content = content
        self.tokens_used = tokens_used
        self.generated_at = datetime.now().isoformat()
        self.success = True
        self.error = None
        self.checker_used = False
        self.checker_issues = []
        self.checker_tokens = 0


class ContentEnhancer:
    """
    Agentic workflow for enhancing translations
    into multiple formats
    """
    
    def __init__(self, provider_name='openai', model=None):
        """
        Initialize enhancer

        Args:
            provider_name: 'openai' (only supported provider)
            model: Specific model name
        """
        self.provider_name = provider_name
        self.model = model
        self.provider = None
        self.results = {}
        self.total_tokens = 0
        
        logger.info(f"ContentEnhancer initialized: {provider_name}, {model}")
    
    def _initialize_provider(self):
        """Initialize AI provider"""
        try:
            self.provider = get_provider(self.provider_name, self.model)
            logger.info("Provider initialized successfully")
            return True
        except Exception as e:
            logger.error(f"Provider initialization failed: {e}")
            return False

    def _split_into_chunks(self, text: str, chunk_size: int = CHUNK_SIZE) -> list:
        """
        Split text into chunks of ~chunk_size words at paragraph boundaries.
        Used by the chunked enhancement pipeline for very long articles.
        """
        paragraphs = [p for p in text.split('\n') if p.strip()]
        chunks = []
        current_paras = []
        current_words = 0

        for para in paragraphs:
            para_words = len(para.split())
            if current_words + para_words > chunk_size and current_paras:
                chunks.append('\n\n'.join(current_paras))
                current_paras = [para]
                current_words = para_words
            else:
                current_paras.append(para)
                current_words += para_words

        if current_paras:
            chunks.append('\n\n'.join(current_paras))

        return [c for c in chunks if c.strip()]

    def _generate_article_header(self, full_text: str, article_info: dict, config: dict) -> tuple:
        """
        Generate ONLY headline + byline + bold intro paragraph from the FULL article text.
        Used in chunked pipeline so the intro reflects the complete article, not just chunk 1.
        Returns (content, tokens_used).
        """
        headline = article_info.get('headline', 'N/A')
        user_prompt = (
            f"মূল শিরোনাম: {headline}\n\n"
            f"নিচের পুরো নিবন্ধটি পড়ুন এবং শুধু শিরোনাম + বাইলাইন + ভূমিকা অনুচ্ছেদ লিখুন:\n\n"
            f"{full_text}\n\n"
            f"মনে রাখুন: শুধু তিনটি অংশ — শিরোনাম (bold), বাইলাইন (not bold), ভূমিকা (পুরো অনুচ্ছেদ bold)।"
        )
        content, tokens = self.provider.generate(
            system_prompt=INTRO_ONLY_SYSTEM_PROMPT,
            user_prompt=user_prompt,
            temperature=config.get('temperature', 0.68),
            max_tokens=400,
        )
        logger.info(f"Article header generated from full text: {len(content)} chars, {tokens} tokens")
        return content, tokens

    def _enhance_continuation_chunk(self, chunk: str, config: dict, has_subheads: bool = True) -> tuple:
        """
        Format a continuation chunk (no headline/byline/intro — sections only).
        Returns (content, tokens_used).
        """
        word_count = len(chunk.split())
        max_tokens = min(8000, max(2000, int(word_count * 3)))

        if has_subheads:
            sys_prompt = CONTINUATION_SYSTEM_PROMPT
            user_prompt = (
                f"এই অংশের ভ্রমণ টিপস/সেকশনগুলো ফরম্যাট করুন:\n\n{chunk}\n\n"
                f"মনে রাখুন: শুধু সাবহেড + কন্টেন্ট — headline, byline বা intro লিখবেন না।"
            )
        else:
            sys_prompt = CONTINUATION_SYSTEM_PROMPT_NO_SUBHEADS
            user_prompt = (
                f"এই অংশটি চলমান নিবন্ধের ধারাবাহিকতায় লিখুন:\n\n{chunk}\n\n"
                f"মনে রাখুন: শুধু body paragraph — কোনো সাবহেড, headline, byline বা intro লিখবেন না।"
            )

        content, tokens = self.provider.generate(
            system_prompt=sys_prompt,
            user_prompt=user_prompt,
            temperature=config.get('temperature', 0.68),
            max_tokens=max_tokens,
        )
        logger.info(f"Continuation chunk ({'with' if has_subheads else 'no'} subheads): {len(content)} chars, {tokens} tokens")
        return content, tokens

    def _strip_article_header(self, content: str) -> str:
        """
        Strip headline, byline, and intro from a continuation chunk output
        in case the model ignored the instruction and added them anyway.
        """
        lines = content.split('\n')
        # Find where the first subhead or non-header content starts
        # Skip: first **...** line (headline), byline line, bold intro
        header_done = False
        start_idx = 0
        headline_seen = False
        byline_seen = False

        for i, line in enumerate(lines):
            stripped = line.strip()
            if not stripped:
                continue

            # If we see 'নিউজ ডেস্ক' — that's a byline, skip it
            if 'নিউজ ডেস্ক' in stripped and 'বাংলার কলম্বাস' in stripped:
                byline_seen = True
                start_idx = i + 1
                continue

            # First bold line before byline = headline, skip it
            if not headline_seen and not byline_seen and stripped.startswith('**') and stripped.endswith('**'):
                headline_seen = True
                start_idx = i + 1
                continue

            # Bold intro paragraph right after byline — skip it
            if byline_seen and stripped.startswith('**'):
                start_idx = i + 1
                continue

            # If we're past the header area, stop
            if headline_seen or byline_seen:
                break

        return '\n'.join(lines[start_idx:]).strip()

    def _count_body_words(self, content: str) -> int:
        """
        Count words in hard news body (excluding headline and byline).

        Counts from intro paragraph to conclusion.

        Args:
            content: Generated hard news content

        Returns:
            int: Word count of body content
        """
        if not content:
            return 0

        paragraphs = [p for p in re.split(r'\n+', content) if p.strip()]
        body_words = 0

        for i, para in enumerate(paragraphs):
            para = para.strip()
            if not para:
                continue

            # Skip headline (first bold line, usually index 0)
            if i == 0 and para.startswith('**'):
                continue

            # Skip byline
            if 'নিউজ ডেস্ক' in para and 'বাংলার কলম্বাস' in para:
                continue

            # Count words in this paragraph (remove ** markers first)
            clean_para = para.replace('**', '')
            body_words += len(clean_para.split())

        return body_words

    def enhance_single_format(self, translated_text, article_info, format_type, retry_count=0):
        """
        Generate content for a single format with code-based post-processing.

        Workflow (v2.5 - No AI Checker, 100% Code-Based Fixes):
        1. Generate content (AI)
        2. Apply post-processing (code-based, deterministic):
           - Word corrections (শিগগিরই, date suffixes)
           - Smart সহ joining (preserves সহায়ক, সহযোগী, etc.)
           - English word replacement
           - Quote splitting (CRITICAL - paragraph ends at quote)
           - 3-line paragraph fixer
        3. Validate structure
        4. For hard_news: Check minimum 220 words, regenerate if needed
        5. Log any issues that were in original AI output (for analytics)

        Args:
            translated_text: Bengali translated text
            article_info: Article metadata dict
            format_type: 'hard_news', 'soft_news', etc.
            retry_count: Internal counter for regeneration attempts

        Returns:
            EnhancementResult
        """
        try:
            # Get format configuration
            config = get_format_config(format_type)

            logger.info(f"Generating {format_type} with {self.provider_name}" +
                       (f" (retry {retry_count})" if retry_count > 0 else ""))

            # Prepare prompts
            system_prompt = config['system_prompt']
            input_word_count = len(translated_text.split())

            # Chunked pipeline for very long articles (>2000 words).
            # gpt-4o-mini severely summarizes when given 2000+ word inputs.
            # Solution: split into ~1500-word chunks, process first chunk fully
            # (headline + byline + intro + sections), then process subsequent
            # chunks as continuation sections (no header), then combine.
            if input_word_count > CHUNKED_THRESHOLD:
                logger.info(f"Long article ({input_word_count} words) — using chunked enhancement pipeline")
                chunks = self._split_into_chunks(translated_text, CHUNK_SIZE)
                logger.info(f"Split into {len(chunks)} chunks")

                # Detect subheads in full text — used for all continuation chunks
                from app.core.prompts import _input_has_subheads
                has_subheads = _input_has_subheads(translated_text)
                logger.info(f"Subhead detection for chunked pipeline: {has_subheads}")

                # Step 1: Generate headline + byline + intro from FULL article
                # (so the intro reflects the complete article, not just the first 1500 words)
                header_content, header_tokens = self._generate_article_header(
                    translated_text, article_info, config
                )
                tokens = header_tokens
                self.total_tokens += header_tokens
                logger.info(f"Article header generated: {len(header_content)} chars")

                # Step 2: Generate body from all chunks (no headline/byline/intro in any chunk)
                body_parts = []
                for i, chunk in enumerate(chunks, 1):
                    cont_content, cont_tokens = self._enhance_continuation_chunk(chunk, config, has_subheads=has_subheads)
                    cleaned = self._strip_article_header(cont_content)
                    body_parts.append(cleaned)
                    tokens += cont_tokens
                    self.total_tokens += cont_tokens
                    logger.info(f"Body chunk {i}/{len(chunks)} done: {len(cleaned)} chars")

                content = header_content + '\n\n' + '\n\n'.join(body_parts)

            else:
                user_prompt = get_user_prompt(translated_text, article_info, input_word_count=input_word_count)
                # Dynamic max_tokens: scale with input size
                dynamic_max_tokens = min(15000, max(3000, int(input_word_count * 3.5)))

                # Generate content (AI)
                content, tokens = self.provider.generate(
                    system_prompt=system_prompt,
                    user_prompt=user_prompt,
                    temperature=config['temperature'],
                    max_tokens=dynamic_max_tokens
                )

            # Get rules from config for rules-driven pipeline
            rules = config.get('rules', {})

            # EARLY WORD COUNT CHECK — before expensive post-processing
            # Avoids running 10-step pipeline on content that will be retried anyway
            min_words = rules.get('min_words')
            if min_words is None and format_type == 'hard_news':
                min_words = 220  # Backward compatibility
            elif min_words is None and format_type == 'soft_news':
                min_words = 350  # Soft news target is 600-1000 words; retry if too short
            if min_words and retry_count < 2:
                raw_word_count = self._count_body_words(content)
                if raw_word_count < min_words:
                    logger.warning(f"{format_type} too short: ~{raw_word_count} words raw (min {min_words}). Regenerating before post-processing...")
                    return self.enhance_single_format(
                        translated_text, article_info, format_type, retry_count + 1
                    )

            # LOG issues in original AI output BEFORE post-processing (for analytics)
            original_issues_needed = False
            original_issues = []
            if rules or format_type in ['hard_news', 'soft_news']:
                original_issues_needed, original_issues = needs_checker(content.strip(), format_type, rules=rules)
                if original_issues_needed:
                    logger.info(f"AI generated with issues (will be fixed by code): {original_issues}")

            # Apply post-processing (ALL fixes are code-based, 100% reliable)
            # Rules from DB/config drive which steps run
            processed_content, validation = process_enhanced_content(
                content.strip(),
                format_type,
                rules=rules
            )

            # Log validation warnings if any
            if not validation['valid']:
                for warning in validation['warnings']:
                    logger.warning(f"Structure warning for {format_type}: {warning}")

            # Strip newspaper name from byline for generic format
            if format_type == 'hard_news_generic':
                processed_content = processed_content.replace(
                    'নিউজ ডেস্ক, বাংলার কলম্বাস', 'নিউজ ডেস্ক'
                )

            # Initialize result
            result = EnhancementResult(
                format_type=format_type,
                content=processed_content,
                tokens_used=tokens
            )

            # Log that code-based fixes were applied (no AI checker needed)
            result.checker_used = False  # AI checker removed in v2.5
            result.checker_tokens = 0
            if original_issues_needed:
                result.checker_issues = original_issues  # Log what issues were found
                logger.info(f"Code-based fixes applied for {format_type} (no AI checker)")

            self.total_tokens += result.tokens_used

            logger.info(f"{format_type} generated: {len(result.content)} chars, {result.tokens_used} tokens")

            return result

        except Exception as e:
            logger.error(f"Error generating {format_type} (attempt {retry_count + 1}): {e}")

            # Retry on transient errors (timeout, None content, network blip)
            if retry_count < 2:
                logger.warning(f"Retrying {format_type} after error (attempt {retry_count + 1}/3)...")
                return self.enhance_single_format(
                    translated_text, article_info, format_type, retry_count + 1
                )

            # All 3 attempts failed — return empty error result
            result = EnhancementResult(format_type=format_type, content="")
            result.success = False
            result.error = str(e)

            return result
    
    def combined_translate_enhance(self, raw_english_text: str, article_info: dict,
                                   format_type: str = 'hard_news_automate_content') -> tuple:
        """
        Single LLM call: extract + translate + format English text directly.

        Skips the separate translation step by combining extraction, translation,
        and formatting into one prompt. ~30-50% faster than the 2-call pipeline.

        Args:
            raw_english_text: Raw pasted English text (may contain nav/ads)
            article_info: Article metadata dict
            format_type: Format type (default: hard_news_automate_content)

        Returns:
            tuple: (formatted_content, tokens_used)
        """
        if not self._initialize_provider():
            return '', 0

        config = get_format_config(format_type)

        # Combine extraction/translation prefix with the format's own system prompt
        combined_system_prompt = COMBINED_EXTRACT_TRANSLATE_PREFIX + config['system_prompt']

        input_word_count = len(raw_english_text.split())
        dynamic_max_tokens = min(15000, max(3000, int(input_word_count * 4.0)))
        user_prompt = (
            f"Raw English article to extract, translate, and format:\n\n"
            f"{raw_english_text}\n\n"
            f"Note: The article is approximately {input_word_count} English words. "
            f"Preserve all important details — do not summarize or shorten."
        )

        logger.info(f"Combined translate+enhance [{format_type}]: {input_word_count} input words, {dynamic_max_tokens} max_tokens")

        content, tokens = self.provider.generate(
            system_prompt=combined_system_prompt,
            user_prompt=user_prompt,
            temperature=config['temperature'],
            max_tokens=dynamic_max_tokens
        )

        # Apply same post-processing pipeline as regular enhance
        rules = config.get('rules', {})
        processed_content, validation = process_enhanced_content(
            content.strip(),
            format_type,
            rules=rules
        )

        if not validation['valid']:
            for warning in validation['warnings']:
                logger.warning(f"Structure warning for {format_type} (combined): {warning}")

        self.total_tokens += tokens
        logger.info(f"Combined translate+enhance done: {len(processed_content)} chars, {tokens} tokens")

        return processed_content, tokens

    # enhance_all_formats() — UNUSED in web app, kept for reference only.
    # The API now calls enhance_single_format() per format directly.
    # def enhance_all_formats(self, translated_text, article_info,
    #                        formats=['hard_news', 'soft_news'],
    #                        progress_callback=None):
    #     ...removed...
    
    def save_results(self, save_dir, article_info):
        """
        Save all results to files
        
        Args:
            save_dir: Directory to save files
            article_info: Article metadata
        
        Returns:
            dict: {format: filepath}
        """
        save_dir = Path(save_dir)
        save_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        headline_slug = article_info.get('headline', 'article')[:30].replace(' ', '_')
        
        saved_files = {}
        
        for format_type, result in self.results.items():
            if not result.success:
                continue
            
            # Create filename
            filename = f"{headline_slug}_{format_type}_{timestamp}.txt"
            filepath = save_dir / filename
            
            # Prepare content
            config = get_format_config(format_type)
            
            checker_info = ""
            if result.checker_used:
                checker_info = f"""
CHECKER USED: Yes
CHECKER ISSUES: {', '.join(result.checker_issues)}
CHECKER TOKENS: {result.checker_tokens}"""

            file_content = f"""{'='*80}
{config['icon']} {config['name'].upper()}
{'='*80}

ARTICLE INFO:
Headline: {article_info.get('headline', 'N/A')}
Publisher: {article_info.get('publisher', 'N/A')}
Country: {article_info.get('country', 'N/A')}
URL: {article_info.get('article_url', 'N/A')}

GENERATED BY: {self.provider_name} ({self.model})
GENERATED AT: {result.generated_at}
TOKENS USED: {result.tokens_used}{checker_info}

{'='*80}
CONTENT
{'='*80}

{result.content}

{'='*80}
"""
            
            # Save file
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(file_content)
            
            saved_files[format_type] = str(filepath)
            logger.info(f"Saved {format_type} to {filepath}")
        
        # Save combined JSON
        json_filename = f"{headline_slug}_all_formats_{timestamp}.json"
        json_filepath = save_dir / json_filename
        
        json_data = {
            'article_info': article_info,
            'provider': self.provider_name,
            'model': self.model,
            'generated_at': datetime.now().isoformat(),
            'total_tokens': self.total_tokens,
            'formats': {}
        }
        
        for format_type, result in self.results.items():
            json_data['formats'][format_type] = {
                'content': result.content,
                'tokens_used': result.tokens_used,
                'success': result.success,
                'error': result.error,
                'checker_used': result.checker_used,
                'checker_issues': result.checker_issues,
                'checker_tokens': result.checker_tokens
            }
        
        with open(json_filepath, 'w', encoding='utf-8') as f:
            json.dump(json_data, f, ensure_ascii=False, indent=2)
        
        saved_files['json'] = str(json_filepath)
        logger.info(f"Saved combined JSON to {json_filepath}")
        
        return saved_files
    
    def get_summary(self):
        """Get enhancement summary"""
        return {
            'provider': self.provider_name,
            'model': self.model,
            'total_formats': len(self.results),
            'successful': sum(1 for r in self.results.values() if r.success),
            'failed': sum(1 for r in self.results.values() if not r.success),
            'total_tokens': self.total_tokens,
            'formats': list(self.results.keys())
        }


# Convenience function
def enhance_translation(translated_text, article_info, provider='openai',
                       model=None, formats=None, progress_callback=None):
    """
    Quick function to enhance translation

    Args:
        translated_text: Bengali translated text
        article_info: Article metadata dict
        provider: 'openai' (only supported provider)
        model: Model name
        formats: List of format types (default: hard_news, soft_news)
        progress_callback: Optional callback function

    Returns:
        dict: Enhancement results
    """
    if formats is None:
        formats = ['hard_news', 'soft_news']
    
    enhancer = ContentEnhancer(provider_name=provider, model=model)
    results = enhancer.enhance_all_formats(
        translated_text, 
        article_info, 
        formats,
        progress_callback
    )
    
    return results, enhancer


# Test
if __name__ == "__main__":
    print("Testing Content Enhancer...")
    
    # Test data
    test_article = {
        'headline': 'New Beach Resort Opens in Cox\'s Bazar',
        'publisher': 'Travel Today',
        'country': 'Bangladesh',
        'article_url': 'https://example.com/article'
    }
    
    test_translation = """কক্সবাজারে একটি নতুন বিলাসবহুল বিচ রিসোর্ট খোলা হয়েছে। 
রিসোর্টটিতে রয়েছে ১০০টি আধুনিক কক্ষ, সুইমিং পুল এবং সমুদ্র-মুখী রেস্তোরাঁ।"""
    
    try:
        # Test with OpenAI (you need valid API key)
        results, enhancer = enhance_translation(
            translated_text=test_translation,
            article_info=test_article,
            provider='openai',
            model='gpt-3.5-turbo',
            formats=['facebook']  # Test with one format
        )
        
        print("\nResults:")
        for format_type, result in results.items():
            print(f"\n{format_type.upper()}:")
            print(f"Success: {result.success}")
            if result.success:
                print(f"Content: {result.content[:200]}...")
                print(f"Tokens: {result.tokens_used}")
            else:
                print(f"Error: {result.error}")
        
        print(f"\nSummary: {enhancer.get_summary()}")
        
    except Exception as e:
        print(f"Test failed: {e}")