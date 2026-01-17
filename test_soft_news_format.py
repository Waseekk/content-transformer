"""
Quick test for Soft News format - checking 2-paragraph rule before first subhead
"""
import os
import sys
import json
import io
from pathlib import Path
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

# Article 1 from PDF
ARTICLE = {
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
}


def translate_to_bengali(text):
    """Translate to Bengali"""
    response = client.chat.completions.create(
        model="gpt-4o-mini",
        messages=[
            {"role": "system", "content": "Translate to Bangladeshi Bengali. Keep facts accurate."},
            {"role": "user", "content": text}
        ],
        temperature=0.3,
        max_tokens=2000
    )
    return response.choices[0].message.content


def generate_soft_news(translated_text, article_info):
    """Generate soft news"""
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


def analyze_structure(content):
    """Analyze the structure of soft news"""
    paragraphs = [p.strip() for p in content.split('\n\n') if p.strip()]

    print("\n" + "="*60)
    print("STRUCTURE ANALYSIS")
    print("="*60)
    print(f"Total paragraphs: {len(paragraphs)}\n")

    # Show first 8 paragraphs
    for i, para in enumerate(paragraphs[:8], 1):
        is_bold = para.startswith('**')
        words = len(para.split())
        # Truncate for display
        display = para[:70].replace('\n', ' ')
        if len(para) > 70:
            display += "..."
        bold_tag = "[BOLD]" if is_bold else "[normal]"
        print(f"P{i}: {bold_tag:10} ({words:3} words) {display}")

    print("\n" + "-"*60)
    print("CHECKING 2-PARAGRAPH RULE:")
    print("-"*60)

    # Expected structure:
    # P1 = Headline (bold)
    # P2 = Byline (not bold)
    # P3 = Intro 1 (bold)
    # P4 = Intro 2 (NOT bold) <-- THIS IS KEY
    # P5 = First Subhead (bold)

    if len(paragraphs) >= 5:
        p1_bold = paragraphs[0].startswith('**')
        p2_bold = paragraphs[1].startswith('**')
        p3_bold = paragraphs[2].startswith('**')
        p4_bold = paragraphs[3].startswith('**')
        p5_bold = paragraphs[4].startswith('**')

        print(f"P1 (Headline):    {'BOLD' if p1_bold else 'normal'}")
        print(f"P2 (Byline):      {'BOLD' if p2_bold else 'normal'}")
        print(f"P3 (Intro 1):     {'BOLD' if p3_bold else 'normal'}")
        print(f"P4 (Intro 2):     {'BOLD' if p4_bold else 'normal'}")
        print(f"P5 (Subhead?):    {'BOLD' if p5_bold else 'normal'}")

        print("\n" + "-"*60)

        # Check the rule: P3=bold, P4=NOT bold, P5=bold (first subhead)
        if p3_bold and not p4_bold and p5_bold:
            print("[PASS] Correct! Bold Intro -> Non-bold Intro -> Bold Subhead")
        elif p3_bold and p4_bold:
            print("[FAIL] Two bold paragraphs in a row before subhead!")
            print("       Should be: 1 bold intro + 1 non-bold intro")
        elif not p3_bold:
            print("[FAIL] Intro 1 should be bold!")
        else:
            print("[CHECK] Structure needs manual review")

    return paragraphs


def main():
    print("="*60)
    print("SOFT NEWS FORMAT TEST")
    print("Article: Trevi Fountain")
    print("="*60)

    # Step 1: Translate
    print("\n[1/2] Translating to Bengali...")
    translated = translate_to_bengali(ARTICLE['content'])
    print("[OK] Translation complete")

    # Step 2: Generate Soft News
    print("[2/2] Generating Soft News...")
    soft_news = generate_soft_news(translated, ARTICLE)
    print("[OK] Generation complete")

    # Analyze structure
    paragraphs = analyze_structure(soft_news)

    # Save full output to file
    output_path = Path(__file__).parent / "test_output" / "soft_news_test_result.txt"
    output_path.parent.mkdir(exist_ok=True)
    with open(output_path, "w", encoding="utf-8") as f:
        f.write("SOFT NEWS OUTPUT:\n")
        f.write("="*60 + "\n\n")
        f.write(soft_news)

    print(f"\n[OK] Full output saved to: {output_path}")


if __name__ == "__main__":
    main()
