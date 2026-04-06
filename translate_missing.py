#!/usr/bin/env python3
import json, urllib.request, urllib.error, time, sys

MISSING_KEYS = [
    "Account", "Administration", "Display", "Chat", "Personalization", "About", "Links", "Feedback",
    "Manage users & roles", "Chat Behavior", "Haptics, titles, suggestions", "Voice & speed settings",
    "Speech-to-Text", "Voice input settings", "Server Configuration", "What the AI remembers about you",
    "About Open Relay", "1 server saved", "App", "Version", "Build", "Platform", "Server Version", "URL",
    "Open WebUI Website", "Source Code", "Privacy Policy", "Report a Bug", "Something broken? Let us know.",
    "Request a Feature", "Got an idea? We'd love to hear it.", "UI/UX Improvement", "Design or layout feedback.",
    "Performance Issue", "Slow, laggy, or draining battery?", "Ask a Question", "Need help with setup or a feature?",
    "Pure Black Dark Mode", "Use OLED-friendly true black", "Tinted Surfaces", "Add a subtle accent tint to backgrounds",
    "Theme Options", "Server Details", "Actions", "Danger Zone", "Self-Signed Certs", "Check Connection",
    "Allowed", "Not Allowed", "On-Device (Apple)", "Apple Speech framework — fast, private, no internet required",
    "Server (OpenWebUI)", "Server-side transcription via /api/v1/audio/transcriptions",
    "Uploads audio to your OpenWebUI server — transcription happens automatically",
    "Not Loaded", "Not Downloaded", "Transcribing\u2026", "Granted", "Not Granted", "User Information", "Account Status"
]

# All languages except en-GB (already done)
LANGUAGES = [
    "ar","az","eu","bn","bs","bo","bg","ca","ceb","hr","cs","da","nl","et","fi",
    "fr-CA","fr","gl","ka","de","el","he","hi","hu","id","ga","it","ja","kab","ko",
    "lt","lv","ms","nb","fa","pl","pt-BR","pt-PT","pa","ro","ru","sr","sk","es","sv",
    "th","tr","tk","uk","ur","ug","uz","vi","zh-Hans","zh-Hant"
]

LANGUAGE_NAMES = {
    "ar": "Arabic", "az": "Azerbaijani", "eu": "Basque", "bn": "Bengali",
    "bs": "Bosnian", "bo": "Tibetan", "bg": "Bulgarian", "ca": "Catalan",
    "ceb": "Cebuano", "hr": "Croatian", "cs": "Czech", "da": "Danish",
    "nl": "Dutch", "et": "Estonian", "fi": "Finnish", "fr-CA": "French (Canada)",
    "fr": "French", "gl": "Galician", "ka": "Georgian", "de": "German",
    "el": "Greek", "he": "Hebrew", "hi": "Hindi", "hu": "Hungarian",
    "id": "Indonesian", "ga": "Irish", "it": "Italian", "ja": "Japanese",
    "kab": "Kabyle", "ko": "Korean", "lt": "Lithuanian", "lv": "Latvian",
    "ms": "Malay", "nb": "Norwegian Bokmål", "fa": "Persian", "pl": "Polish",
    "pt-BR": "Portuguese (Brazil)", "pt-PT": "Portuguese (Portugal)", "pa": "Punjabi",
    "ro": "Romanian", "ru": "Russian", "sr": "Serbian", "sk": "Slovak",
    "es": "Spanish", "sv": "Swedish", "th": "Thai", "tr": "Turkish",
    "tk": "Turkmen", "uk": "Ukrainian", "ur": "Urdu", "ug": "Uyghur",
    "uz": "Uzbek", "vi": "Vietnamese", "zh-Hans": "Chinese Simplified",
    "zh-Hant": "Chinese Traditional"
}

ENDPOINT = "https://chatapi.abhiinnovate.com/chat/completions"
MODEL = "chatbot"
XCSTRINGS_PATH = "Open UI/Localizable.xcstrings"
BATCH_SIZE = 15

def save_xcstrings(data):
    with open(XCSTRINGS_PATH, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"  ✅ Saved to disk")

def translate_batch(keys, lang_code):
    lang_name = LANGUAGE_NAMES.get(lang_code, lang_code)
    keys_json = json.dumps(keys, ensure_ascii=False)
    prompt = f"""Translate these iOS app UI strings from English to {lang_name} ({lang_code}).
Return ONLY a JSON object mapping each English string to its {lang_name} translation.
Keep the same tone as a mobile app UI. Keep punctuation like "…" as-is. Do not add explanations.

English strings:
{keys_json}

Return format: {{"English string": "Translation", ...}}"""

    payload = json.dumps({
        "model": MODEL,
        "messages": [{"role": "user", "content": prompt}],
        "temperature": 1.0
    }).encode('utf-8')

    req = urllib.request.Request(
        ENDPOINT,
        data=payload,
        headers={"Content-Type": "application/json", "Authorization": "Bearer sk-836194"},
        method="POST"
    )

    for attempt in range(3):
        try:
            with urllib.request.urlopen(req, timeout=60) as resp:
                result = json.loads(resp.read().decode('utf-8'))
                content = result['choices'][0]['message']['content'].strip()
                # Extract JSON from response
                start = content.find('{')
                end = content.rfind('}') + 1
                if start >= 0 and end > start:
                    translations = json.loads(content[start:end])
                    return translations
                else:
                    print(f"    ⚠️  No JSON found in response, retrying...")
        except Exception as e:
            print(f"    ⚠️  Attempt {attempt+1} failed: {e}")
            if attempt < 2:
                time.sleep(3)
    return {}

def main():
    print(f"Loading {XCSTRINGS_PATH}...")
    with open(XCSTRINGS_PATH, 'r', encoding='utf-8') as f:
        data = json.load(f)

    strings = data.get('strings', {})
    total_langs = len(LANGUAGES)

    for lang_idx, lang in enumerate(LANGUAGES):
        lang_name = LANGUAGE_NAMES.get(lang, lang)
        print(f"\n[{lang_idx+1}/{total_langs}] Translating to {lang_name} ({lang})...")

        # Find keys that need translation for this language
        keys_needed = []
        for key in MISSING_KEYS:
            if key not in strings:
                continue
            entry = strings[key]
            locs = entry.get('localizations', {})
            # Check if this lang already has a non-stub translation
            if lang in locs:
                unit = locs[lang].get('stringUnit', {})
                state = unit.get('state', '')
                value = unit.get('value', '')
                # Skip if already translated (state is 'translated' with a value)
                if state == 'translated' and value:
                    continue
            keys_needed.append(key)

        if not keys_needed:
            print(f"  ✓ Already complete, skipping")
            continue

        print(f"  Translating {len(keys_needed)} keys in batches of {BATCH_SIZE}...")
        all_translations = {}

        # Translate in batches
        for i in range(0, len(keys_needed), BATCH_SIZE):
            batch = keys_needed[i:i+BATCH_SIZE]
            batch_num = (i // BATCH_SIZE) + 1
            total_batches = (len(keys_needed) + BATCH_SIZE - 1) // BATCH_SIZE
            print(f"  Batch {batch_num}/{total_batches}: {batch[:3]}{'...' if len(batch)>3 else ''}...")
            translations = translate_batch(batch, lang)
            all_translations.update(translations)
            if batch_num < total_batches:
                time.sleep(1)

        # Apply translations to xcstrings
        applied = 0
        for key in keys_needed:
            if key in all_translations:
                translated_value = all_translations[key]
                if key not in strings:
                    strings[key] = {}
                if 'localizations' not in strings[key]:
                    strings[key]['localizations'] = {}
                strings[key]['localizations'][lang] = {
                    'stringUnit': {
                        'state': 'translated',
                        'value': translated_value
                    }
                }
                applied += 1
            else:
                print(f"    ⚠️  Missing translation for: {key}")

        print(f"  Applied {applied}/{len(keys_needed)} translations")

        # INCREMENTAL SAVE after each language
        save_xcstrings(data)

    print(f"\n🎉 Done! All {total_langs} languages processed.")
    print(f"Final save complete: {XCSTRINGS_PATH}")

if __name__ == '__main__':
    main()
