const t = {
  en: {
    // Header
    subtitle: "Refugee Assistant Switzerland",
    langToggle: "العربية",

    // Sidebar
    yourCanton: "Your Canton",
    cantonHint: "Select your canton for local answers:",
    cantonPlaceholder: "— Select your canton —",
    cantonBadge: (c) => `📍 ${c}`,
    latestNews: "Latest News",
    articlesIndexed: (n) => `${n} articles indexed from SEM & Swiss sources`,
    loadingNews: "Loading news…",
    emergencyContacts: "Emergency Contacts",
    emergencyNumbers: "🚨 Police: 117 · Ambulance: 144 · Emergency: 112",
    osar: "OSAR — Free legal aid",
    sem: "SEM — Migration authority",
    redcross: "Swiss Red Cross",
    chch: "ch.ch — Swiss portal",
    newConversation: "+ Start new conversation",
    storedLocally: "🔒 Conversations stored locally via Groq AI.",

    // PermitBar
    myPermit: "My permit:",
    permits: [
      { code: "N", label: "Asylum seeker — procedure pending" },
      { code: "F", label: "Provisionally admitted" },
      { code: "B", label: "Recognised refugee" },
      { code: "C", label: "Settlement permit" },
      { code: "S", label: "Protection status (e.g. Ukraine)" },
      { code: "?", label: "I don't know my permit type" },
    ],

    // WelcomeScreen
    welcomeInfo1: "What I can help with: Swiss asylum procedure · Permits (N, F, B, C, S) · Work rights · Language courses · Healthcare · Family reunification · Appeals · Housing",
    welcomeInfo2: "Languages: I reply in your language — Arabic, Tigrinya, Somali, Dari, Ukrainian, Turkish, German, French, Italian, English, and more.",
    welcomeInfo3label: "Important:",
    welcomeInfo3: " I give guidance only — not legal advice. For appeals or urgent matters, contact",
    welcomeInfo3osar: "OSAR",
    welcomeInfo3mid: "(free legal aid) or",
    welcomeInfo3sem: "SEM",
    welcomeInfo3end: "directly.",
    welcomeHeading: "What would you like to know today?",
    welcomeHint: "Tap a topic or type your question below — I answer in your language.",
    commonHeading: "Common questions:",

    topics: [
      { emoji: "🔖", label: "Permits",     question: "What types of permits exist in Switzerland and what does each one allow?" },
      { emoji: "📋", label: "Asylum",      question: "What are the steps of the Swiss asylum procedure?" },
      { emoji: "💼", label: "Work",        question: "Can I work in Switzerland and what do I need to do?" },
      { emoji: "🏥", label: "Healthcare",  question: "How do I access healthcare and get health insurance in Switzerland?" },
      { emoji: "🎓", label: "Integration", question: "What language courses and integration programs are available for refugees?" },
      { emoji: "👨‍👩‍👧", label: "Family",   question: "How can I bring my family to Switzerland?" },
      { emoji: "⚖️", label: "Appeals",     question: "How do I appeal a rejected asylum decision?" },
      { emoji: "🏠", label: "Housing",     question: "What housing do asylum seekers receive in Switzerland?" },
    ],
    commonQ: [
      "What do I do when I first arrive in Switzerland as a refugee?",
      "What is Permit F and can I work with it?",
      "How do I appeal a rejected asylum decision?",
      "How can I bring my family to Switzerland?",
      "What is Permit S for Ukrainians?",
      "What are the latest asylum updates in Switzerland?",
    ],

    // ChatInput
    placeholder: "Ask anything — asylum, permits, work, healthcare… (any language)",
    stopRecording: "Stop recording",
    startRecording: "Speak your question",
    micDenied: "Microphone access denied. Please allow microphone access to use voice input.",

    // MessageList
    feedbackRecorded: "Feedback recorded",
    listenBtn: "Listen",
    helpful: "Helpful",
    notHelpful: "Not helpful",
  },

  ar: {
    // Header
    subtitle: "مساعد اللاجئين في سويسرا",
    langToggle: "English",

    // Sidebar
    yourCanton: "منطقتك (الكانتون)",
    cantonHint: "اختر كانتونك للحصول على إجابات محلية:",
    cantonPlaceholder: "— اختر كانتونك —",
    cantonBadge: (c) => `📍 ${c}`,
    latestNews: "آخر الأخبار",
    articlesIndexed: (n) => `${n} مقال مفهرس من مصادر SEM والسويسرية`,
    loadingNews: "جارٍ تحميل الأخبار…",
    emergencyContacts: "جهات الطوارئ",
    emergencyNumbers: "🚨 الشرطة: 117 · الإسعاف: 144 · الطوارئ: 112",
    osar: "OSAR — مساعدة قانونية مجانية",
    sem: "SEM — سلطة الهجرة",
    redcross: "الصليب الأحمر السويسري",
    chch: "ch.ch — البوابة السويسرية",
    newConversation: "+ بدء محادثة جديدة",
    storedLocally: "🔒 المحادثات مخزنة محلياً عبر Groq AI.",

    // PermitBar
    myPermit: "تصريحي:",
    permits: [
      { code: "N", label: "طالب لجوء — الإجراء قيد الانتظار" },
      { code: "F", label: "مقبول بصفة مؤقتة" },
      { code: "B", label: "لاجئ معترف به" },
      { code: "C", label: "تصريح إقامة دائمة" },
      { code: "S", label: "وضع الحماية (مثل أوكرانيا)" },
      { code: "?", label: "لا أعرف نوع تصريحي" },
    ],

    // WelcomeScreen
    welcomeInfo1: "ما يمكنني مساعدتك فيه: إجراءات اللجوء السويسرية · التصاريح (N, F, B, C, S) · حقوق العمل · دورات اللغة · الرعاية الصحية · لمّ شمل الأسرة · الاستئناف · السكن",
    welcomeInfo2: "اللغات: أرد بلغتك — العربية، التيغرينية، الصومالية، الدارية، الأوكرانية، التركية، الألمانية، الفرنسية، الإيطالية، الإنجليزية، والمزيد.",
    welcomeInfo3label: "مهم:",
    welcomeInfo3: " أقدم إرشادات فقط — وليس استشارة قانونية. للاستئنافات أو الحالات العاجلة، تواصل مع",
    welcomeInfo3osar: "OSAR",
    welcomeInfo3mid: "(مساعدة قانونية مجانية) أو",
    welcomeInfo3sem: "SEM",
    welcomeInfo3end: "مباشرةً.",
    welcomeHeading: "ماذا تريد أن تعرف اليوم؟",
    welcomeHint: "اضغط على موضوع أو اكتب سؤالك أدناه — أجيب بلغتك.",
    commonHeading: "أسئلة شائعة:",

    topics: [
      { emoji: "🔖", label: "التصاريح",      question: "ما أنواع التصاريح الموجودة في سويسرا وما الذي يتيحه كل منها؟" },
      { emoji: "📋", label: "اللجوء",         question: "ما هي خطوات إجراءات اللجوء في سويسرا؟" },
      { emoji: "💼", label: "العمل",          question: "هل يمكنني العمل في سويسرا وماذا أحتاج للقيام به؟" },
      { emoji: "🏥", label: "الرعاية الصحية", question: "كيف أحصل على الرعاية الصحية والتأمين الصحي في سويسرا؟" },
      { emoji: "🎓", label: "الاندماج",       question: "ما هي دورات اللغة وبرامج الاندماج المتاحة للاجئين؟" },
      { emoji: "👨‍👩‍👧", label: "العائلة",     question: "كيف يمكنني إحضار عائلتي إلى سويسرا؟" },
      { emoji: "⚖️", label: "الاستئناف",      question: "كيف أستأنف قرار رفض طلب اللجوء؟" },
      { emoji: "🏠", label: "السكن",          question: "ما هو السكن الذي يحصل عليه طالبو اللجوء في سويسرا؟" },
    ],
    commonQ: [
      "ماذا أفعل عند وصولي إلى سويسرا كلاجئ؟",
      "ما هو تصريح F وهل يمكنني العمل به؟",
      "كيف أستأنف قرار رفض طلب اللجوء؟",
      "كيف يمكنني إحضار عائلتي إلى سويسرا؟",
      "ما هو تصريح S للأوكرانيين؟",
      "ما آخر التحديثات المتعلقة باللجوء في سويسرا؟",
    ],

    // ChatInput
    placeholder: "اسأل عن أي شيء — اللجوء، التصاريح، العمل، الرعاية الصحية… (أي لغة)",
    stopRecording: "إيقاف التسجيل",
    startRecording: "انطق سؤالك",
    micDenied: "تم رفض الوصول إلى الميكروفون. يرجى السماح بالوصول لاستخدام الإدخال الصوتي.",

    // MessageList
    feedbackRecorded: "تم تسجيل رأيك",
    listenBtn: "استمع",
    helpful: "مفيد",
    notHelpful: "غير مفيد",
  },
};

export default t;
