"""
Test Script: Generate Hard News and Soft News for English Articles
Outputs to Excel files for review
"""

import os
import sys
import json
import time
import re
from pathlib import Path
from openai import OpenAI
import pandas as pd
from dotenv import load_dotenv

# Load environment variables
load_dotenv(Path(__file__).parent / "backend" / ".env")

# Initialize OpenAI client
client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"))

# Load prompts from JSON
def load_prompts():
    json_path = Path(__file__).parent / "backend" / "app" / "config" / "formats" / "bengali_news_styles.json"
    with open(json_path, "r", encoding="utf-8") as f:
        return json.load(f)

STYLES = load_prompts()

# ============================================================================
# PARAGRAPH LENGTH ENFORCER (copied from text_processor.py for standalone use)
# ============================================================================

def enforce_paragraph_length(text: str, max_words: int = 35) -> str:
    """
    Enforce maximum paragraph length by splitting long paragraphs at sentence boundaries.
    Target: Max 2 lines on A4 (12pt font) ≈ 30-35 Bengali words per paragraph.
    """
    if not text:
        return text

    paragraphs = text.split('\n\n')
    result = []
    splits_made = 0

    for para in paragraphs:
        para = para.strip()
        if not para:
            continue

        # Skip bold paragraphs (headlines, intros, subheads)
        if para.startswith('**') and '**' in para[2:]:
            result.append(para)
            continue

        # Skip byline
        if 'নিউজ ডেস্ক' in para and 'বাংলার কলম্বাস' in para:
            result.append(para)
            continue

        # Check word count
        words = para.split()
        if len(words) <= max_words:
            result.append(para)
            continue

        # Need to split - find sentence boundaries (।, ?, !)
        sentences = re.split(r'(।|\?|!)', para)

        # Rebuild sentences with their punctuation
        full_sentences = []
        for i in range(0, len(sentences) - 1, 2):
            if i + 1 < len(sentences):
                full_sentences.append(sentences[i] + sentences[i + 1])
            else:
                full_sentences.append(sentences[i])
        if len(sentences) % 2 == 1 and sentences[-1].strip():
            full_sentences.append(sentences[-1])

        # Group sentences into paragraphs of max_words
        current_para = []
        current_word_count = 0

        for sentence in full_sentences:
            sentence = sentence.strip()
            if not sentence:
                continue

            sentence_words = len(sentence.split())

            if current_word_count + sentence_words <= max_words:
                current_para.append(sentence)
                current_word_count += sentence_words
            else:
                if current_para:
                    result.append(' '.join(current_para))
                    splits_made += 1
                current_para = [sentence]
                current_word_count = sentence_words

        if current_para:
            result.append(' '.join(current_para))

    if splits_made > 0:
        print(f"    [POST] Split {splits_made} long paragraph(s)")

    return '\n\n'.join(result)


def apply_word_corrections(text: str) -> str:
    """Apply Bengali word corrections"""
    if not text:
        return text

    corrections = [
        (r'শীঘ্রই', 'শিগগিরই'),
        (r'(\S+)\s+সহ\b', r'\1সহ'),
        (r'([০-৯]+)লা\b', r'\1'),
        (r'([০-৯]+)ই\b', r'\1'),
        (r'([০-৯]+)শে\b', r'\1'),
    ]

    for pattern, replacement in corrections:
        text = re.sub(pattern, replacement, text)

    return text

# Articles extracted from PDF - ALL 7 articles
ARTICLES = [
    {
        "id": 1,
        "title": "Tourists to face €2 fee to get near Rome's Trevi Fountain",
        "publisher": "BBC News",
        "country": "Italy",
        "content": """The Trevi Fountain is one of Rome's key attractions with around nine million visitors this year.

Tourists in Italy's capital Rome will soon have to pay a €2 (£1.75; $2.34) entrance fee if they want to see its famed Trevi Fountain up close.

The new barrier for visitors to view the Baroque monument will come into force from 1 February 2026.

While the coins tossed into the fountain are donated to charity, the fees collected will go to the city authority to pay for upkeep and managing visitors. The city expects to raise €6.5m a year from the fountain alone.

Announcing the move on Friday, Rome's Mayor Roberto Gualtieri was quoted by news agency Reuters as saying that "two euros isn't very much ... and it will lead to less chaotic tourist flows".

The Trevi levy is part of a new tariff system for certain museums and monuments in the Italian capital.

Access to a number of sites that currently charge for entry will become free for Rome's residents, such as the Sacred Area of Largo Argentina.

At the same time, tourists and non-residents will have to pay to see the Trevi fountain and five other attractions including the Napoleonic Museum.

Children under the age of five, and those with disabilities and an accompanying person, will be exempt from the fees.

Tourists will still be able to view the Trevi Fountain - built by Italian architect Nicola Salvi in the 18th Century - for free from a distance.

The site currently sees an average of 30,000 visitors per day, according to the City of Rome.

Following restoration work which took place last year, Gualtieri introduced a queuing system to prevent large crowds massing around the landmark.

Access is capped at 400 people at the same time."""
    },
    {
        "id": 2,
        "title": "Thousands of dinosaur footprints found on Italian mountain",
        "publisher": "BBC News",
        "country": "Italy",
        "content": """Footage supplied by the team of scientists show the scale of the footprints and a recreation of how they were formed.

Thousands of dinosaur footprints dating back 210 million years have been found in a national park in northern Italy.

The footprints - some of which are up to 40cm (15in) in diameter - are aligned in parallel rows, and many show clear traces of toes and claws.

It is thought the dinosaurs were prosauropods - herbivores with long necks, small heads and sharp claws.

"I never would have imagined I'd come across such a spectacular discovery in the region where I live," said Milan-based paleontologist Cristiano Dal Sasso.

Last September a photographer spotted the footprints stretching hundreds of metres on a vertical mountain wall in the Stelvio national park, north-east of Milan.

In the Triassic period - between about 250 and 201 million years ago - the wall was a tidal flat, which later became part of the Alpine chain.

"This place was full of dinosaurs; it's an immense scientific treasure," Mr Dal Sasso said.

The herds moved in harmony, he added, "and there are also traces of more complex behaviours, like groups of animals gathering in a circle, perhaps for the purposes of defence."

The prosauropods, which could be up to 10m (33ft) long, walked on two legs but in some cases handprints were found in front of footprints, indicating that they probably stopped and rested their forelimbs on the ground.

Photographer Elio Della Ferrera snapped the first picture of the mountain wall showing the footprints.

Elio Della Ferrera, the photographer who discovered the site, said he hoped the discovery would "spark reflection in all of us, highlighting how little we know about the places we live in: our home, our planet".

According to a press release from the Italian culture ministry, the area is remote and not accessible by paths, so drones and remote sensing technology will be employed instead.

The Stelvio national park is located in the Fraele valley by Italy's border with Switzerland, near where the Winter Olympics will take place next year.

"It's as if history itself wanted to pay homage to the greatest global sporting event, combining past and present in a symbolic passing of the baton between nature and sport," said the Italian Ministry of Culture."""
    },
    {
        "id": 3,
        "title": "The six best places to ski in 2026",
        "publisher": "BBC Travel",
        "country": "Multiple",
        "content": """From Italian Winter Olympic buzz to brand-new wellness retreats in the Canadian Rockies, these six ski areas are trending for 2026.

As the barometer drops in the northern hemisphere, skiers everywhere are preparing to shred black diamonds and show off their mountain 'fits. Tried-and-true hotspots like Aspen and Courchevel never lose their appeal, but according to Sara Haney, head of travel for concierge service Velocity Black which organises bespoke skiing experiences for travellers, skiers in 2026 "want a sense of discovery, not just lift access".

This season, snow reliability also remains a top priority. According to Cat Iwanchuk, vice president of business development at Ski.com, skiers are changing their plans to coincide with optimal snowfall. Favourable early forecasts boost the season's top contenders.

Alta Badia, The Dolomites, Italy: The Dolomite Mountains, famed for their dramatic limestone peaks and perfect pink sunsets, have traditionally been an "Italians-only" ski destination. Thanks to hosting this year's Winter Olympics, ski-related searches from the US have risen 82% compared to the same timeframe in 2024 and up 16% in the UK.

Big Sky, Montana, US: Can a hotel opening define an entire season? The November 2025 debut of One&Only Moonlight Basin just might. The hotel flaunts world-class dining and a stargazing observatory. None of this overshadows the area's true appeal: 5,850 acres of some of the least crowded slopes in the American West.

Banff, Alberta, Canada: On 17 December 2025, Lake Louise Ski Resort unveiled Richardson's Ridge; 200 new acres of beginner-, intermediate- and tree-skiing terrain. "The combination of a location far north and high altitude means that snow conditions are typically among the best in the world," Cat Iwanchuk explains.

Hokkaido, Japan: From 2024 to 2025, Niseko, a town in Japan's northernmost Hokkaido region known for its fluffy, plentiful "Japow" (Japan powder), had a record-breaking season, welcoming more than 11 million visitors.

Méribel, France: In the French Alps, this quaint ski town with wood chalet architecture has access to 600km (373 miles) of trails, a lively après-ski scene. "We've seen a significant uptick in Méribel enquiries this season -- around 50% more interest than last year."

Queenstown, New Zealand: Head to Queenstown, home to one of the world's longest winter sports seasons, stretching nearly five months from June to October. Winter 2026 also marks the first full season of the Soho Basin expansion."""
    },
    {
        "id": 4,
        "title": "Turkey's ornate Ottoman-era 'bird palaces'",
        "publisher": "BBC Travel",
        "country": "Turkey",
        "content": """Many of Istanbul's visitors are unaware that the city is home to half-a-millennium-old stone-carved bird houses that reflect the Ottomans' reverence for the animals.

On a corner lot in Istanbul's old city, there's what some might call a fixer-upper: a stone-built duplex with gabled roofs and lots of windows. Parts of its exterior walls are crumbling, but there's a unique feature affixed to its walls that makes it a perfectly fine home for its many residents -- the city's birds.

Too grand to be called mere birdhouses, dozens of masterfully stone-carved kuş sarayları ("bird palaces") or kuş köşkleri ("bird pavilions") in varying states of repair are perched under the eaves of Ottoman-era mosques, tombs and other structures in central Istanbul.

"Each bird palace has its own unique architectural style and detailed beauty that also represents a thoughtful display of compassion," says Öykü Demir, an Istanbul-based tour guide.

Charity is one of the five pillars of Islam, and in Ottoman times, this extended to animals across the empire. Birds held a special place within the empire because they were symbolically linked to the soul reaching for the heavens.

"In Istanbul, you often find birdhouses on the qibla walls of mosques (those facing Mecca) so the sound of birds becomes associated with the sound of prayer," says Christiane Gruber, a professor of Islamic art history at the University of Michigan.

The practice reached its creative peak during the 18th Century, a period of prosperity in which there was a new emphasis on public space and leisure. This era yielded such flights of architectural fancy as the gabled, opulent bird dwelling on the wall of the Imperial Mint near Topkapı Palace.

Despite being a densely populated megacity, Istanbul is still rich in birdlife, with nearly 300 different species spotted in the city by birdwatchers this year alone.

"These bird houses represent a very old tradition of hospitality, and an idea... that says the city belongs not just to humans," says Gruber. "They reveal a different way that people related to the environment in the past and might give us a blueprint for ways to reconcile that relationship in the future." """
    },
    {
        "id": 5,
        "title": "Brazil's lagoon-filled desert you can hike barefoot",
        "publisher": "BBC Travel",
        "country": "Brazil",
        "content": """Lençóis Maranhenses looks like a desert, but it's alive with shimmering pools, remote villages and ancient paths that only local guides know how to read.

I was at least 20 steps behind my group -- and another 30 behind our guide -- when he suddenly stopped, checked his watch and tilted his face toward the sky, as if taking cues from the Sun.

My three friends and I were a few hours into a three-day trek across Lençóis Maranhenses National Park, a humbling expanse of sand in north-eastern Brazil, and I had already lost all sense of direction.

Bordered by lush vegetation on one side and the Atlantic Ocean on the other, Lençóis Maranhenses is one of Brazil's most unusual ecosystems. Strong coastal winds push sand inland, creating a desert-like landscape that spans 1,500 sq km, with dunes rising up to 30m.

But Lençóis is no desert. During the wet season (January to June), so much rain falls that water settles in natural basins between the dunes, forming the hundreds of freshwater lagoons that travellers like me come to swim, wade and float in.

It's these ephemeral pools that make Lençois like nowhere else on Earth. It's also what helped earn the park Unesco World Heritage status in 2024. In 2024, Lençóis received a record 552,000 visitors.

"We have more than 1,000 families living inside Lençóis Maranhenses," said Cristiane Figueiredo, head of the national park. "To truly get to know this unique environment, there's nothing better than walking. On foot, you can notice the small things: the shifting sand, the footprints of birds and animals."

Our guide Tav told me he grew up on the outskirts of the park. "Nowadays, it comes naturally," he tells me. "I can close my eyes and remember each dune and each trail. That's what allows us to walk at night, even in complete darkness."

Nothing here holds its shape for long. The dunes shift. The lagoons appear and disappear. Footprints vanish. The only constant in Lençóis Maranhenses is change -- and the people who have learned, over generations, to live with it."""
    },
    {
        "id": 6,
        "title": "Sabres set sights on extending season-long win streak vs. Islanders",
        "publisher": "Field Level Media",
        "country": "USA",
        "content": """The New York Islanders lost Friday night to a team near the bottom of the standings playing much freer after a major personnel move.

The Islanders hope history doesn't repeat itself Saturday, when they will to salvage the second game of a back-to-back set when they visit the Buffalo Sabres in a battle of Eastern Conference rivals.

The Islanders never led Friday in a 4-1 loss to the Vancouver Canucks in Elmont, N.Y. The host Sabres, meanwhile, earned their fourth straight victory, 5-3 over the Philadelphia Flyers.

The loss was the second straight for the Islanders, who vaulted into second place in the Metropolitan Division by winning six of seven games before Tuesday's 3-2 loss to the Detroit Red Wings.

New York squandered an early 5-on-3 power play and fell behind 3-0 in the first period against the Canucks, who climbed out of the Pacific Division basement by improving to 3-0 since trading captain and leading scorer Quinn Hughes to the Minnesota Wild on Dec. 13.

Center Bo Horvat, who leads New York with 19 goals and 31 points, missed his third straight game with a left ankle injury and wasn't expected to travel to Buffalo.

"I feel like we're looking for a perfect play too much," Islanders coach Patrick Roy said. "Some nights, when we don't have the same execution, you've got to find a different way to score goals."

The Sabres, who have missed the playoffs in each of the last 14 seasons and are in last place in the Atlantic Division, shifted in a different direction last Monday, when general manager Kevyn Adams was fired and replaced by senior adviser Jarmo Kekalainen.

Buffalo won three in a row before the change and extended its longest winning streak of the season in Kekalainen's first game as general manager.

The four-game winning streak is the longest for the Sabres since a five-game run from March 30 through April 8.

"When you find that next level of desperation to try to win games, ultimately for the guy next to you, I think that's when good things happen -- when you're paying for the group," said Sabres goalie Alex Lyon."""
    },
    {
        "id": 7,
        "title": "Kazakhstan Becomes a Prime Choice for Chinese Outbound Tourism",
        "publisher": "Know More",
        "country": "Kazakhstan",
        "content": """Kazakhstan has rapidly become a preferred destination for Chinese travelers seeking a blend of adventure, winter sports, and urban experiences. The country's growing appeal stems from its diverse offerings: towering snow-capped mountains and world-class ski resorts attract winter sports enthusiasts, while vibrant cities like Almaty and Astana provide modern amenities, cultural landmarks, and dynamic city life.

Kazakhstan has firmly established itself as one of the seven most popular international destinations for Chinese travelers during the New Year holiday.

Recent data reveals that demand for travel to Kazakhstan from Chinese cities has surged sharply since early December. Air travel bookings have increased by more than 50% compared to last year, while hotel reservations have seen an even more dramatic rise of over 80%.

Almaty and Astana remain the focal points for Chinese tourists visiting Kazakhstan. Almaty, surrounded by snow-capped mountains and scenic valleys, offers a dynamic mix of outdoor adventure and urban culture. Astana, the futuristic capital, attracts visitors with its striking modern architecture.

Winter sports tourism has become a key driver of Kazakhstan's growing popularity. Ski resorts such as Shymbulak near Almaty have seen rising interest since late November.

Tourism statistics reflect this growing momentum. Over the first eleven months of the current year, more than 876,000 Chinese tourists visited Kazakhstan, a substantial increase from 655,000 recorded for the entire previous year.

With its dramatic landscapes, thriving urban centers, world-class winter sports facilities, and deep cultural roots, Kazakhstan is rapidly solidifying its reputation as a must-visit destination for Chinese travelers during the New Year holiday."""
    }
]


def translate_to_bengali(text: str) -> str:
    """Translate English text to Bengali"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {
                "role": "system",
                "content": "You are a professional translator. Translate the following English text to Bangladeshi Bengali. Keep all facts, numbers, names, and quotes accurate. Use natural, fluent Bangladeshi Bengali (not Indian Bengali)."
            },
            {
                "role": "user",
                "content": text
            }
        ],
        temperature=0.3,
        max_tokens=3000
    )
    return response.choices[0].message.content


def generate_news(translated_text: str, article_info: dict, news_type: str) -> str:
    """Generate hard news or soft news from translated text"""
    style = STYLES[news_type]

    user_prompt = f"""নিচের ভ্রমণ সংবাদটি পুনর্লিখন করুন:

মূল শিরোনাম: {article_info['title']}
উৎস: {article_info['publisher']}
দেশ: {article_info['country']}

অনুবাদিত বিষয়বস্তু:
{translated_text}

নির্দেশনা:
১. উপরের বিষয়বস্তু ব্যবহার করে আপনার স্টাইলে নতুন করে লিখুন
২. সম্পূর্ণ বাংলাদেশী বাংলায় লিখুন (ভারতীয় বাংলা নয়)
৩. তথ্য সঠিক রাখুন কিন্তু উপস্থাপনা আকর্ষণীয় করুন
৪. পাঠকদের জন্য মূল্যবান এবং এনগেজিং করুন
৫. উপযুক্ত দৈর্ঘ্য এবং ফরম্যাট মেনে চলুন

এখন লিখুন:"""

    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": style["system_prompt"]},
            {"role": "user", "content": user_prompt}
        ],
        temperature=style["temperature"],
        max_tokens=style["max_tokens"]
    )

    # Get raw content
    raw_content = response.choices[0].message.content

    # Apply post-processing
    # 1. Word corrections
    processed = apply_word_corrections(raw_content)
    # 2. Paragraph length enforcer (max 35 words = ~2 lines on A4)
    processed = enforce_paragraph_length(processed, max_words=35)

    return processed


def process_articles():
    """Process all articles and generate hard news and soft news"""
    hard_news_results = []
    soft_news_results = []

    total = len(ARTICLES)

    for i, article in enumerate(ARTICLES, 1):
        print(f"\n{'='*60}")
        print(f"Processing Article {article['id']}/{total}: {article['title'][:50]}...")
        print(f"{'='*60}")

        # Step 1: Translate to Bengali
        print(f"  [1/3] Translating to Bengali...")
        translated = translate_to_bengali(article['content'])
        time.sleep(1)  # Rate limiting

        # Step 2: Generate Hard News
        print(f"  [2/3] Generating Hard News...")
        hard_news = generate_news(translated, article, "hard_news")
        time.sleep(1)

        # Step 3: Generate Soft News
        print(f"  [3/3] Generating Soft News...")
        soft_news = generate_news(translated, article, "soft_news")
        time.sleep(1)

        # Store results
        hard_news_results.append({
            "Article_ID": article['id'],
            "Original_Title": article['title'],
            "Publisher": article['publisher'],
            "Country": article['country'],
            "Hard_News_Bengali": hard_news
        })

        soft_news_results.append({
            "Article_ID": article['id'],
            "Original_Title": article['title'],
            "Publisher": article['publisher'],
            "Country": article['country'],
            "Soft_News_Bengali": soft_news
        })

        print(f"  [OK] Article {article['id']} completed!")

    return hard_news_results, soft_news_results


def save_to_excel(hard_news_data, soft_news_data, output_dir):
    """Save results to Excel files"""
    output_dir = Path(output_dir)
    output_dir.mkdir(exist_ok=True)

    # Generate timestamp for unique filenames
    from datetime import datetime
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Save Hard News
    hard_df = pd.DataFrame(hard_news_data)
    hard_path = output_dir / f"hard_news_v24_{timestamp}.xlsx"
    hard_df.to_excel(hard_path, index=False, engine='openpyxl')
    print(f"\n[OK] Hard News saved to: {hard_path}")

    # Save Soft News
    soft_df = pd.DataFrame(soft_news_data)
    soft_path = output_dir / f"soft_news_v24_{timestamp}.xlsx"
    soft_df.to_excel(soft_path, index=False, engine='openpyxl')
    print(f"[OK] Soft News saved to: {soft_path}")

    return hard_path, soft_path


def main():
    print("\n" + "="*60)
    print("BENGALI NEWS GENERATOR - TEST SCRIPT")
    print("Using updated prompts v2.4")
    print("="*60)

    print(f"\nArticles to process: {len(ARTICLES)}")
    print("Processing ALL 7 articles from PDF")

    # Process articles
    hard_news, soft_news = process_articles()

    # Save to Excel
    output_dir = Path(__file__).parent / "test_output"
    hard_path, soft_path = save_to_excel(hard_news, soft_news, output_dir)

    print("\n" + "="*60)
    print("COMPLETED!")
    print(f"Hard News: {hard_path}")
    print(f"Soft News: {soft_path}")
    print("="*60)


if __name__ == "__main__":
    main()
