"""
P.I.R.E. Centralized Multilingual Translation Dictionary
Provides complete native UI strings for English, Tamil (தமிழ்), and Hindi (हिन्दी).
Ensures graceful fallback to English for any missing keys.
"""

from typing import Dict

TRANSLATIONS: Dict[str, Dict[str, str]] = {
    # Application Title & Subtitles
    "app_title": {
        "en": "P.I.R.E. — Perishable Inventory Risk Evaluation",
        "ta": "P.I.R.E. — அழுகக்கூடிய சரக்கு ஆபத்து மதிப்பீட்டு அமைப்பு",
        "hi": "P.I.R.E. — शीघ्र नष्ट होने वाले सामान की जोखिम मूल्यांकन प्रणाली"
    },
    "app_subtitle": {
        "en": "XGBoost-Based Multilingual Expiry Risk Prediction & Decision Support System",
        "ta": "எக்ஸ்பூஸ்ட் (XGBoost) சார்ந்த பன்மொழி காலாவதி அபாயக் கணிப்பு மற்றும் முடிவு ஆதரவு அமைப்பு",
        "hi": "XGBoost आधारित बहुभाषी समाप्ति जोखिम पूर्वानुमान एवं निर्णय समर्थन प्रणाली"
    },
    "select_language": {
        "en": "Select Language",
        "ta": "மொழியைத் தேர்ந்தெடுக்கவும்",
        "hi": "भाषा चुनें"
    },

    # Navigation Tabs / Sections
    "nav_overview": {
        "en": "📊 Overview Dashboard",
        "ta": "📊 மேலோட்டக் கட்டுப்பாட்டு அறை",
        "hi": "📊 अवलोकन डैशबोर्ड"
    },
    "nav_inventory": {
        "en": "📦 Inventory Management",
        "ta": "📦 சரக்கு இருப்பு மேலாண்மை",
        "hi": "📦 इन्वेंटरी प्रबंधन"
    },
    "nav_prediction": {
        "en": "🤖 ML Risk Prediction",
        "ta": "🤖 ML அபாயக் கணிப்பு",
        "hi": "🤖 एमएल जोखिम भविष्यवाणी"
    },
    "nav_discounts": {
        "en": "🏷️ Discount Recommendations",
        "ta": "🏷️ தள்ளுபடி பரிந்துரைகள்",
        "hi": "🏷️ छूट की सिफारिशें"
    },
    "nav_simulation": {
        "en": "🌡️ Storage Simulation",
        "ta": "🌡️ சேமிப்பக வெப்பநிலை உருவகப்படுத்துதல்",
        "hi": "🌡️ भंडारण तापमान अनुकरण"
    },
    "nav_model_performance": {
        "en": "📈 Model Performance",
        "ta": "📈 மாதிரி செயல்திறன்",
        "hi": "📈 मॉडल प्रदर्शन"
    },
    "nav_reports": {
        "en": "📄 Reports & Exports",
        "ta": "📄 அறிக்கைகள் மற்றும் பதிவிறக்கம்",
        "hi": "📄 रिपोर्ट और निर्यात"
    },
    "nav_database": {
        "en": "🗄️ Database Status",
        "ta": "🗄️ தரவுத்தள நிலை",
        "hi": "🗄️ डेटाबेस स्थिति"
    },

    # Overview KPI Cards
    "kpi_total_products": {
        "en": "Total Products",
        "ta": "மொத்த பொருட்கள்",
        "hi": "कुल उत्पाद"
    },
    "kpi_expired_products": {
        "en": "Expired (Remove from Sale)",
        "ta": "காலாவதியானது (விற்பனையை நிறுத்தவும்)",
        "hi": "समाप्त (बिक्री से हटाएं)"
    },
    "kpi_expiring_soon": {
        "en": "Expiring Soon (≤ 3 Days)",
        "ta": "விரைவில் காலாவதியாகிறது (≤ 3 நாட்கள்)",
        "hi": "जल्द समाप्त होने वाला (≤ 3 दिन)"
    },
    "kpi_critical_risk": {
        "en": "Critical Risk Items",
        "ta": "அதிதீவிர அபாயப் பொருட்கள்",
        "hi": "अति-गंभीर जोखिम वस्तुएं"
    },
    "kpi_value_at_risk": {
        "en": "Inventory Value at Risk",
        "ta": "அபாயத்திலுள்ள சரக்கு மதிப்பு",
        "hi": "जोखिम में इन्वेंटरी मूल्य"
    },
    "kpi_potential_recovery": {
        "en": "Est. Recoverable Value",
        "ta": "மதிப்பிடப்பட்ட மீட்கக்கூடிய மதிப்பு",
        "hi": "अनुमानित वसूली मूल्य"
    },

    # Risk Categories
    "risk_LOW": {
        "en": "LOW",
        "ta": "குறைவு (LOW)",
        "hi": "कम (LOW)"
    },
    "risk_MEDIUM": {
        "en": "MEDIUM",
        "ta": "நடுத்தரம் (MEDIUM)",
        "hi": "मध्यम (MEDIUM)"
    },
    "risk_HIGH": {
        "en": "HIGH",
        "ta": "அதிகம் (HIGH)",
        "hi": "उच्च (HIGH)"
    },
    "risk_CRITICAL": {
        "en": "CRITICAL",
        "ta": "அதிதீவிரம் (CRITICAL)",
        "hi": "अति-गंभीर (CRITICAL)"
    },
    "risk_EXPIRED": {
        "en": "EXPIRED",
        "ta": "காலாவதியானது (EXPIRED)",
        "hi": "समाप्त (EXPIRED)"
    },

    # Data Ingestion & Upload
    "upload_header": {
        "en": "Upload Inventory Dataset (CSV or Excel)",
        "ta": "சரக்குத் தரவை பதிவேற்றவும் (CSV அல்லது Excel)",
        "hi": "इन्वेंटरी डेटासेट अपलोड करें (CSV या Excel)"
    },
    "upload_button_label": {
        "en": "Drag and drop CSV or Excel file here",
        "ta": "CSV அல்லது Excel கோப்பை இங்கே பதிவேற்றவும்",
        "hi": "यहाँ CSV या Excel फ़ाइल ड्रैग और ड्रॉप करें"
    },
    "btn_load_sample": {
        "en": "Load Built-in Sample Dataset",
        "ta": "மாதிரித் தரவை ஏற்றவும்",
        "hi": "अंतर्निहित नमूना डेटा लोड करें"
    },
    "validation_summary": {
        "en": "Data Quality & Validation Summary",
        "ta": "தரவுத் தரம் மற்றும் சரிபார்ப்பு சுருக்கம்",
        "hi": "डेटा गुणवत्ता और सत्यापन सारांश"
    },
    "valid_rows": {
        "en": "Valid Rows",
        "ta": "சரியான வரிசைகள்",
        "hi": "वैध पंक्तियाँ"
    },
    "warning_rows": {
        "en": "Rows with Warnings",
        "ta": "எச்சரிக்கைகள் உள்ள வரிசைகள்",
        "hi": "चेतावनी वाली पंक्तियाँ"
    },
    "invalid_rows": {
        "en": "Invalid Rows (Action Required)",
        "ta": "செல்லாத வரிசைகள் (திருத்தம் தேவை)",
        "hi": "अवैध पंक्तियाँ (सुधार आवश्यक)"
    },

    # Actions & Buttons
    "btn_train_model": {
        "en": "Train XGBoost Classifier",
        "ta": "எக்ஸ்பூஸ்ட் மாதிரியைப் பயிற்றுவிக்கவும்",
        "hi": "XGBoost मॉडल को प्रशिक्षित करें"
    },
    "btn_run_predictions": {
        "en": "Run Expiry Risk Predictions",
        "ta": "அபாயக் கணிப்புகளை இயக்கவும்",
        "hi": "समाप्ति जोखिम पूर्वानुमान चलाएं"
    },
    "btn_generate_report": {
        "en": "Generate Official PDF Audit Report",
        "ta": "அதிகாரப்பூர்வ PDF தணிக்கை அறிக்கையை உருவாக்கவும்",
        "hi": "आधिकारिक पीडीएफ ऑडिट रिपोर्ट बनाएं"
    },
    "btn_save_mongodb": {
        "en": "Sync Results to MongoDB",
        "ta": "முடிவுகளை மோங்கோடிபியில் சேமிக்கவும்",
        "hi": "परिणामों को MongoDB में सुरक्षित करें"
    },
    "btn_download_csv": {
        "en": "Download Results as CSV",
        "ta": "முடிவுகளை CSV ஆக பதிவிறக்கவும்",
        "hi": "परिणाम CSV के रूप में डाउनलोड करें"
    },

    # Food Safety Alerts
    "safety_alert_expired": {
        "en": "FOOD SAFETY NOTICE: Expired products detected! They must be removed from sale immediately. Do not discount.",
        "ta": "உணவுப் பாதுகாப்பு எச்சரிக்கை: காலாவதியான பொருட்கள் கண்டறியப்பட்டுள்ளன! அவற்றை உடனே அகற்ற வேண்டும். தள்ளுபடி செய்யக்கூடாது.",
        "hi": "खाद्य सुरक्षा सूचना: समाप्त उत्पाद पाए गए! उन्हें तुरंत बिक्री से हटाया जाना चाहिए। छूट न दें।"
    },

    # Simulation Page
    "sim_title": {
        "en": "Retail Cold-Chain What-If Storage Simulation",
        "ta": "சில்லறை குளிர்பதனச் சங்கிலி உருவகப்படுத்துதல்",
        "hi": "कोल्ड-चेन भंडारण 'व्हाट-इफ' सिमुलेशन"
    },
    "sim_desc": {
        "en": "Simulate storage temperature shifts to assess their impact on shelf-life risk tiers without altering raw data.",
        "ta": "அசல் தரவை மாற்றாமல், சேமிப்பக வெப்பநிலை மாற்றங்களால் ஏற்படும் அபாய மாற்றங்களை சோதிக்கவும்.",
        "hi": "मूल डेटा को बदले बिना तापमान परिवर्तन के जोखिम प्रभाव का आकलन करने के लिए सिमुलेशन करें।"
    },
    "sim_temp_slider": {
        "en": "Adjust Ambient / Cold Storage Temperature (°C)",
        "ta": "சேமிப்பக வெப்பநிலையை மாற்றவும் (°C)",
        "hi": "भंडारण तापमान समायोजित करें (°C)"
    },
    "sim_category_select": {
        "en": "Target Specific Category for Temperature Stress",
        "ta": "குறிப்பிட்ட வகைக்கான வெப்பநிலையை மாற்றவும்",
        "hi": "तापमान तनाव के लिए विशिष्ट श्रेणी चुनें"
    },

    # Database Status
    "db_connected": {
        "en": "MongoDB Connected: Persistent database storage active.",
        "ta": "மோங்கோடிபி இணைக்கப்பட்டது: நிரந்தர தரவுத்தள சேமிப்பு செயல்பாட்டில் உள்ளது.",
        "hi": "MongoDB कनेक्टेड: स्थायी डेटाबेस संग्रहण सक्रिय है।"
    },
    "db_fallback": {
        "en": "MongoDB Unavailable: Operating in Local File Fallback Mode.",
        "ta": "மோங்கோடிபி கிடைக்கவில்லை: உள்ளூர் கோப்பு மாற்று முறையில் இயங்குகிறது.",
        "hi": "MongoDB अनुपलब्ध: स्थानीय फ़ाइल फ़ॉलबैक मोड में कार्य कर रहा है।"
    }
}


def t(key: str, lang: str = "en") -> str:
    """
    Retrieves translation for the given key in the requested language.
    Falls back to English if the translation or key is not found.
    """
    if lang not in ("en", "ta", "hi"):
        lang = "en"

    entry = TRANSLATIONS.get(key)
    if not entry:
        return key

    return entry.get(lang, entry.get("en", key))
