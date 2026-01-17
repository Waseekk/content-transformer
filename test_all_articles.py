"""
Comprehensive Test: Generate Hard News and Soft News for all 7 PDF articles
Output to Word document with proper formatting
"""
import os
import sys
import json
import io
from pathlib import Path
from datetime import datetime
from openai import OpenAI
from dotenv import load_dotenv

# Fix Windows console encoding
sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8', errors='replace')

# Load environment variables
load_dotenv(Path(__file__).parent / "backend" / ".env")

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load prompts
json_path = Path(__file__).parent / "backend" / "app" / "config" / "formats" / "bengali_news_styles.json"
with open(json_path, "r", encoding="utf-8") as f:
    STYLES = json.load(f)

# ============================================================================
# ALL 7 ARTICLES FROM PDF
# ============================================================================

ARTICLES = [
    {
        "id": 1,
        "title": "Tourists to face €2 fee to get near Rome's Trevi Fountain",
        "publisher": "BBC News",
        "content": """Tourists in Italy's capital Rome will soon have to pay a €2 (£1.75; $2.34) entrance fee if they want to see its famed Trevi Fountain up close.

The new barrier for visitors to view the Baroque monument will come into force from 1 February 2026.

While the coins tossed into the fountain are donated to charity, the fees collected will go to the city authority to pay for upkeep and managing visitors. The city expects to raise €6.5m a year from the fountain alone.

Announcing the move on Friday, Rome's Mayor Roberto Gualtieri was quoted by news agency Reuters as saying that "two euros isn't very much ... and it will lead to less chaotic tourist flows".

The Trevi levy is part of a new tariff system for certain museums and monuments in the Italian capital.

Access to a number of sites that currently charge for entry will become free for Rome's residents, such as the Sacred Area of Largo Argentina.

At the same time, tourists and non-residents will have to pay to see the Trevi fountain and five other attractions including the Napoleonic Museum.

Children under the age of five, and those with disabilities and an accompanying person, will be exempt from the fees.

The site currently sees an average of 30,000 visitors per day, according to the City of Rome."""
    },
    {
        "id": 2,
        "title": "Thousands of dinosaur footprints found on Italian mountain",
        "publisher": "BBC News",
        "content": """Thousands of dinosaur footprints dating back 210 million years have been found in a national park in northern Italy.

The footprints - some of which are up to 40cm (15in) in diameter - are aligned in parallel rows, and many show clear traces of toes and claws.

It is thought the dinosaurs were prosauropods - herbivores with long necks, small heads and sharp claws.

"I never would have imagined I'd come across such a spectacular discovery in the region where I live," said Milan-based paleontologist Cristiano Dal Sasso.

Last September a photographer spotted the footprints stretching hundreds of metres on a vertical mountain wall in the Stelvio national park, north-east of Milan.

In the Triassic period - between about 250 and 201 million years ago - the wall was a tidal flat, which later became part of the Alpine chain.

"This place was full of dinosaurs; it's an immense scientific treasure," Mr Dal Sasso said.

The herds moved in harmony, he added, "and there are also traces of more complex behaviours, like groups of animals gathering in a circle, perhaps for the purposes of defence."

The prosauropods, which could be up to 10m (33ft) long, walked on two legs but in some cases handprints were found in front of footprints, indicating that they probably stopped and rested their forelimbs on the ground.

Elio Della Ferrera, the photographer who discovered the site, said he hoped the discovery would "spark reflection in all of us, highlighting how little we know about the places we live in: our home, our planet".

The Stelvio national park is located in the Fraele valley by Italy's border with Switzerland, near where the Winter Olympics will take place next year.

"It's as if history itself wanted to pay homage to the greatest global sporting event, combining past and present in a symbolic passing of the baton between nature and sport," said the Italian Ministry of Culture."""
    },
    {
        "id": 3,
        "title": "The six best places to ski in 2026",
        "publisher": "BBC Travel",
        "content": """As the barometer drops in the northern hemisphere, skiers everywhere are preparing to shred black diamonds and show off their mountain 'fits. Tried-and-true hotspots like Aspen and Courchevel never lose their appeal, but according to Sara Haney, head of travel for concierge service Velocity Black which organises bespoke skiing experiences for travellers, skiers in 2026 "want a sense of discovery, not just lift access".

This season, snow reliability also remains a top priority. According to Cat Iwanchuk, vice president of business development at Ski.com, skiers are changing their plans to coincide with optimal snowfall.

Alta Badia, The Dolomites, Italy: The Dolomite Mountains, famed for their dramatic limestone peaks and perfect pink sunsets, have traditionally been an "Italians-only" ski destination. Thanks to hosting this year's Winter Olympics, ski-related searches from the US have risen 82% compared to the same timeframe in 2024.

Big Sky, Montana, US: Can a hotel opening define an entire season? The November 2025 debut of One&Only Moonlight Basin just might. Big Sky's ascent from under-the-radar cult favourite to one of the US' most popular resorts has been a decade in the making.

Banff, Alberta, Canada: Despite its location in the heart of the Canadian Rockies, Banff has traditionally been considered a summer travel destination. On 17 December 2025, Lake Louise Ski Resort unveiled Richardson's Ridge; 200 new acres of terrain.

Hokkaido, Japan: From 2024 to 2025, Niseko, a town in Japan's northernmost Hokkaido region known for its fluffy "Japow" (Japan powder), had a record-breaking season, welcoming more than 11 million visitors.

Méribel, France: In the French Alps, this quaint ski town with wood chalet architecture has access to 600km of trails, a lively après-ski scene and gorgeous views of the Les Allues valley.

Queenstown, New Zealand: Head to Queenstown, home to one of the world's longest winter sports seasons, stretching nearly five months from June to October."""
    },
    {
        "id": 4,
        "title": "Turkey's ornate Ottoman-era 'bird palaces'",
        "publisher": "BBC Travel",
        "content": """On a corner lot in Istanbul's old city, there's what some might call a fixer-upper: a stone-built duplex with gabled roofs and lots of windows. Parts of its exterior walls are crumbling, but there's a unique feature affixed to its walls that makes it a perfectly fine home for its many residents -- the city's birds.

Too grand to be called mere birdhouses, dozens of masterfully stone-carved kuş sarayları ("bird palaces") or kuş köşkleri ("bird pavilions") in varying states of repair are perched under the eaves of Ottoman-era mosques, tombs and other structures in central Istanbul.

"Each bird palace has its own unique architectural style and detailed beauty that also represents a thoughtful display of compassion," says Öykü Demir, an Istanbul-based tour guide.

Charity is one of the five pillars of Islam, and in Ottoman times, this extended to animals across the empire. Birds held a special place within the empire because they were symbolically linked to the soul reaching for the heavens.

"In Istanbul, you often find birdhouses on the qibla walls of mosques (those facing Mecca) so the sound of birds becomes associated with the sound of prayer," says Christiane Gruber, a professor of Islamic art history at the University of Michigan.

The practice reached its creative peak during the 18th Century, a period of prosperity in which Ottoman art and architecture transformed under the influence of the Baroque and Rococo movements from Europe.

Despite being a densely populated megacity, Istanbul is still rich in birdlife, with nearly 300 different species spotted in the city by birdwatchers this year alone.

"These bird houses represent a very old tradition of hospitality, and an idea... that says the city belongs not just to humans," says Gruber."""
    },
    {
        "id": 5,
        "title": "Brazil's lagoon-filled desert you can hike barefoot",
        "publisher": "BBC Travel",
        "content": """I was at least 20 steps behind my group -- and another 30 behind our guide -- when he suddenly stopped, checked his watch and tilted his face toward the sky, as if taking cues from the Sun.

My three friends and I were a few hours into a three-day trek across Lençóis Maranhenses National Park, a humbling expanse of sand in north-eastern Brazil.

Bordered by lush vegetation on one side and the Atlantic Ocean on the other, Lençóis Maranhenses is one of Brazil's most unusual ecosystems. Strong coastal winds push sand inland, creating a desert-like landscape that spans 1,500 sq km, with dunes rising up to 30m.

But Lençóis is no desert. During the wet season (January to June), so much rain falls that water settles in natural basins between the dunes, forming the hundreds of freshwater lagoons that travellers come to swim in.

It's these ephemeral pools that make Lençois like nowhere else on Earth. It's also what helped earn the park Unesco World Heritage status in 2024. In 2024, Lençóis received a record 552,000 visitors.

Our trek began in Lagoa Bonita. From there, we would cross 36km of sand, including two overnight stays in local villages, to finish in Atins.

"We have more than 1,000 families living inside Lençóis Maranhenses," said Cristiane Figueiredo, head of the national park. "To truly get to know this unique environment, there's nothing better than walking."

Nothing here holds its shape for long. The dunes shift. The lagoons appear and disappear. Footprints vanish. The only constant in Lençóis Maranhenses is change -- and the people who have learned, over generations, to live with it."""
    },
    {
        "id": 6,
        "title": "Sabres set sights on extending season-long win streak vs. Islanders",
        "publisher": "Field Level Media",
        "content": """The New York Islanders lost Friday night to a team near the bottom of the standings playing much freer after a major personnel move.

The Islanders hope history doesn't repeat itself Saturday, when they will to salvage the second game of a back-to-back set when they visit the Buffalo Sabres in a battle of Eastern Conference rivals.

The Islanders never led Friday in a 4-1 loss to the Vancouver Canucks in Elmont, N.Y. The host Sabres, meanwhile, earned their fourth straight victory, 5-3 over the Philadelphia Flyers.

The loss was the second straight for the Islanders, who vaulted into second place in the Metropolitan Division by winning six of seven games before Tuesday's 3-2 loss to the Detroit Red Wings.

The Sabres, who have missed the playoffs in each of the last 14 seasons and are in last place in the Atlantic Division, shifted in a different direction last Monday, when general manager Kevyn Adams was fired and replaced by senior adviser Jarmo Kekalainen.

Buffalo won three in a row before the change and extended its longest winning streak of the season in Kekalainen's first game as general manager.

"When you find that next level of desperation to try to win games, ultimately for the guy next to you, I think that's when good things happen," said Sabres goalie Alex Lyon."""
    },
    {
        "id": 7,
        "title": "Kazakhstan Becomes a Prime Choice for Chinese Outbound Tourism",
        "publisher": "Know More",
        "content": """Kazakhstan has rapidly become a preferred destination for Chinese travelers seeking a blend of adventure, winter sports, and urban experiences. The country's growing appeal stems from its diverse offerings: towering snow-capped mountains and world-class ski resorts attract winter sports enthusiasts, while vibrant cities like Almaty and Astana provide modern amenities, cultural landmarks, and dynamic city life.

Kazakhstan has firmly established itself as one of the seven most popular international destinations for Chinese travelers during the New Year holiday, reflecting a rising trend in outbound tourism from China.

Recent data reveals that demand for travel to Kazakhstan from Chinese cities has surged sharply since early December. Air travel bookings have increased by more than 50% compared to last year, while hotel reservations have seen an even more dramatic rise of over 80%.

Almaty and Astana remain the focal points for Chinese tourists visiting Kazakhstan. Almaty, surrounded by snow-capped mountains and scenic valleys, offers a dynamic mix of outdoor adventure and urban culture.

Winter sports tourism has become a key driver of Kazakhstan's growing popularity. Ski resorts such as Shymbulak near Almaty have seen rising interest since late November, drawing both novice and experienced skiers.

Tourism statistics reflect this growing momentum. Over the first eleven months of the current year, more than 876,000 Chinese tourists visited Kazakhstan, a substantial increase from 655,000 recorded for the entire previous year."""
    }
]


def translate_to_bengali(text):
    """Translate to Bengali"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Translate to Bangladeshi Bengali. Keep facts accurate. Keep proper nouns in original language."},
            {"role": "user", "content": text}
        ],
        temperature=0.3,
        max_tokens=3000
    )
    return response.choices[0].message.content


def generate_hard_news(translated_text, article_info):
    """Generate Hard News format"""
    style = STYLES["hard_news"]

    user_prompt = f"""নিচের ভ্রমণ সংবাদটি পুনর্লিখন করুন:

মূল শিরোনাম: {article_info['title']}
উৎস: {article_info['publisher']}

অনুবাদিত বিষয়বস্তু:
{translated_text}

এখন হার্ড নিউজ স্টাইলে লিখুন:"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": style["system_prompt"]},
            {"role": "user", "content": user_prompt}
        ],
        temperature=style["temperature"],
        max_tokens=style["max_tokens"]
    )
    return response.choices[0].message.content


def generate_soft_news(translated_text, article_info):
    """Generate Soft News format"""
    style = STYLES["soft_news"]

    user_prompt = f"""নিচের ভ্রমণ সংবাদটি পুনর্লিখন করুন:

মূল শিরোনাম: {article_info['title']}
উৎস: {article_info['publisher']}

অনুবাদিত বিষয়বস্তু:
{translated_text}

এখন সফট নিউজ স্টাইলে লিখুন:"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": style["system_prompt"]},
            {"role": "user", "content": user_prompt}
        ],
        temperature=style["temperature"],
        max_tokens=style["max_tokens"]
    )
    return response.choices[0].message.content


def analyze_structure(content, news_type):
    """Analyze the structure of news content"""
    paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]

    result = {
        "total_paragraphs": len(paragraphs),
        "structure": [],
        "validation": {}
    }

    for i, para in enumerate(paragraphs[:8], 1):
        is_bold = para.startswith('**')
        words = len(para.split())
        result["structure"].append({
            "paragraph": i,
            "bold": is_bold,
            "words": words,
            "preview": para[:60].replace('\n', ' ') + ("..." if len(para) > 60 else "")
        })

    if news_type == "soft_news" and len(paragraphs) >= 5:
        # Check 2-paragraph rule for soft news
        p3_bold = paragraphs[2].startswith('**') if len(paragraphs) > 2 else False
        p4_bold = paragraphs[3].startswith('**') if len(paragraphs) > 3 else False
        p5_bold = paragraphs[4].startswith('**') if len(paragraphs) > 4 else False

        if p3_bold and not p4_bold and p5_bold:
            result["validation"]["2_paragraph_rule"] = "PASS"
        else:
            result["validation"]["2_paragraph_rule"] = "FAIL"

    return result


def create_word_document(results):
    """Create Word document with all results"""
    try:
        from docx import Document
        from docx.shared import Pt, Inches, RGBColor
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        from docx.enum.style import WD_STYLE_TYPE
    except ImportError:
        print("[!] python-docx not installed. Installing...")
        import subprocess
        subprocess.check_call([sys.executable, "-m", "pip", "install", "python-docx"])
        from docx import Document
        from docx.shared import Pt, Inches, RGBColor
        from docx.enum.text import WD_ALIGN_PARAGRAPH
        from docx.enum.style import WD_STYLE_TYPE

    doc = Document()

    # Title
    title = doc.add_heading('Bengali News Format Test Results', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER

    # Subtitle
    subtitle = doc.add_paragraph(f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    subtitle.alignment = WD_ALIGN_PARAGRAPH.CENTER

    doc.add_paragraph()  # Spacing

    for result in results:
        # Article header
        doc.add_heading(f"Article {result['id']}: {result['title']}", level=1)
        doc.add_paragraph(f"Source: {result['publisher']}")
        doc.add_paragraph()

        # Hard News Section
        doc.add_heading('HARD NEWS (হার্ড নিউজ)', level=2)

        # Add hard news content with formatting
        hard_news_lines = result['hard_news'].split('\n')
        for line in hard_news_lines:
            if line.strip():
                p = doc.add_paragraph()
                if line.startswith('**') and line.endswith('**'):
                    # Bold text
                    run = p.add_run(line.replace('**', ''))
                    run.bold = True
                elif line.startswith('**'):
                    # Partially bold
                    parts = line.split('**')
                    for i, part in enumerate(parts):
                        if part:
                            run = p.add_run(part)
                            run.bold = (i % 2 == 1)
                else:
                    p.add_run(line)

        # Hard News Analysis
        analysis_hard = result.get('analysis_hard', {})
        doc.add_paragraph(f"Total paragraphs: {analysis_hard.get('total_paragraphs', 'N/A')}")

        doc.add_paragraph()

        # Soft News Section
        doc.add_heading('SOFT NEWS (সফট নিউজ)', level=2)

        # Add soft news content with formatting
        soft_news_lines = result['soft_news'].split('\n')
        for line in soft_news_lines:
            if line.strip():
                p = doc.add_paragraph()
                if line.startswith('**') and line.endswith('**'):
                    run = p.add_run(line.replace('**', ''))
                    run.bold = True
                elif line.startswith('**'):
                    parts = line.split('**')
                    for i, part in enumerate(parts):
                        if part:
                            run = p.add_run(part)
                            run.bold = (i % 2 == 1)
                else:
                    p.add_run(line)

        # Soft News Analysis
        analysis_soft = result.get('analysis_soft', {})
        doc.add_paragraph(f"Total paragraphs: {analysis_soft.get('total_paragraphs', 'N/A')}")
        validation = analysis_soft.get('validation', {})
        if '2_paragraph_rule' in validation:
            doc.add_paragraph(f"2-Paragraph Rule: {validation['2_paragraph_rule']}")

        # Page break between articles
        doc.add_page_break()

    return doc


def main():
    print("=" * 70)
    print("COMPREHENSIVE NEWS FORMAT TEST - ALL 7 ARTICLES")
    print("=" * 70)

    results = []

    for article in ARTICLES:
        print(f"\n{'='*70}")
        print(f"Article {article['id']}: {article['title'][:50]}...")
        print("=" * 70)

        # Step 1: Translate
        print(f"  [1/3] Translating to Bengali...")
        translated = translate_to_bengali(article['content'])
        print(f"  [OK] Translation complete ({len(translated)} chars)")

        # Step 2: Generate Hard News
        print(f"  [2/3] Generating Hard News...")
        hard_news = generate_hard_news(translated, article)
        analysis_hard = analyze_structure(hard_news, "hard_news")
        print(f"  [OK] Hard News: {analysis_hard['total_paragraphs']} paragraphs")

        # Step 3: Generate Soft News
        print(f"  [3/3] Generating Soft News...")
        soft_news = generate_soft_news(translated, article)
        analysis_soft = analyze_structure(soft_news, "soft_news")
        validation_status = analysis_soft.get('validation', {}).get('2_paragraph_rule', 'N/A')
        print(f"  [OK] Soft News: {analysis_soft['total_paragraphs']} paragraphs, 2-para rule: {validation_status}")

        results.append({
            "id": article['id'],
            "title": article['title'],
            "publisher": article['publisher'],
            "translated": translated,
            "hard_news": hard_news,
            "soft_news": soft_news,
            "analysis_hard": analysis_hard,
            "analysis_soft": analysis_soft
        })

    # Save to Word document
    print("\n" + "=" * 70)
    print("GENERATING WORD DOCUMENT...")
    print("=" * 70)

    doc = create_word_document(results)
    output_path = Path(__file__).parent / "test_output" / "all_articles_test_results.docx"
    output_path.parent.mkdir(exist_ok=True)
    doc.save(str(output_path))
    print(f"[OK] Word document saved: {output_path}")

    # Also save raw text version
    text_output_path = Path(__file__).parent / "test_output" / "all_articles_test_results.txt"
    with open(text_output_path, "w", encoding="utf-8") as f:
        for result in results:
            f.write("=" * 70 + "\n")
            f.write(f"ARTICLE {result['id']}: {result['title']}\n")
            f.write(f"Source: {result['publisher']}\n")
            f.write("=" * 70 + "\n\n")

            f.write("-" * 40 + "\n")
            f.write("HARD NEWS:\n")
            f.write("-" * 40 + "\n")
            f.write(result['hard_news'] + "\n\n")

            f.write("-" * 40 + "\n")
            f.write("SOFT NEWS:\n")
            f.write("-" * 40 + "\n")
            f.write(result['soft_news'] + "\n\n")

            f.write("-" * 40 + "\n")
            f.write("SOFT NEWS STRUCTURE ANALYSIS:\n")
            f.write("-" * 40 + "\n")
            for item in result['analysis_soft']['structure']:
                bold_tag = "[BOLD]" if item['bold'] else "[normal]"
                f.write(f"P{item['paragraph']}: {bold_tag:10} ({item['words']:3} words) {item['preview']}\n")

            validation = result['analysis_soft'].get('validation', {})
            if '2_paragraph_rule' in validation:
                f.write(f"\n2-Paragraph Rule: {validation['2_paragraph_rule']}\n")

            f.write("\n\n")

    print(f"[OK] Text file saved: {text_output_path}")

    # Summary
    print("\n" + "=" * 70)
    print("SUMMARY")
    print("=" * 70)

    pass_count = 0
    fail_count = 0
    na_count = 0

    for result in results:
        status = result['analysis_soft'].get('validation', {}).get('2_paragraph_rule', 'N/A')
        if status == "PASS":
            pass_count += 1
            icon = "[PASS]"
        elif status == "FAIL":
            fail_count += 1
            icon = "[FAIL]"
        else:
            na_count += 1
            icon = "[N/A]"

        print(f"  Article {result['id']}: {icon} {result['title'][:45]}...")

    print(f"\nResults: {pass_count} PASS, {fail_count} FAIL, {na_count} N/A")
    print(f"\nOutput files:")
    print(f"  - Word: {output_path}")
    print(f"  - Text: {text_output_path}")


if __name__ == "__main__":
    main()
