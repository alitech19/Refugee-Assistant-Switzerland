const t = {
  en: {
    // Header
    subtitle: "Refugee Assistant Switzerland",

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

  uk: {
    // Header
    subtitle: "Помічник біженців у Швейцарії",

    // Sidebar
    yourCanton: "Ваш кантон",
    cantonHint: "Виберіть кантон для місцевих відповідей:",
    cantonPlaceholder: "— Виберіть ваш кантон —",
    cantonBadge: (c) => `📍 ${c}`,
    latestNews: "Останні новини",
    articlesIndexed: (n) => `${n} статей проіндексовано з SEM та швейцарських джерел`,
    loadingNews: "Завантаження новин…",
    emergencyContacts: "Екстрені контакти",
    emergencyNumbers: "🚨 Поліція: 117 · Швидка допомога: 144 · Надзвичайні: 112",
    osar: "OSAR — Безкоштовна юридична допомога",
    sem: "SEM — Орган з питань міграції",
    redcross: "Швейцарський Червоний Хрест",
    chch: "ch.ch — Швейцарський портал",
    newConversation: "+ Почати нову розмову",
    storedLocally: "🔒 Розмови зберігаються локально через Groq AI.",

    // PermitBar
    myPermit: "Мій дозвіл:",
    permits: [
      { code: "N", label: "Шукач притулку — процедура розглядається" },
      { code: "F", label: "Тимчасово допущена особа" },
      { code: "B", label: "Визнаний біженець" },
      { code: "C", label: "Дозвіл на постійне проживання" },
      { code: "S", label: "Статус захисту (напр. Україна)" },
      { code: "?", label: "Я не знаю свій тип дозволу" },
    ],

    // WelcomeScreen
    welcomeInfo1: "Чим я можу допомогти: Процедура надання притулку · Дозволи (N, F, B, C, S) · Права на роботу · Мовні курси · Охорона здоров'я · Возз'єднання сімей · Апеляції · Житло",
    welcomeInfo2: "Мови: Я відповідаю вашою мовою — арабська, тигринья, сомалі, дарі, українська, турецька, німецька, французька, італійська, англійська та інші.",
    welcomeInfo3label: "Важливо:",
    welcomeInfo3: " Я надаю лише рекомендації — не юридичну пораду. Для апеляцій або термінових питань зверніться до",
    welcomeInfo3osar: "OSAR",
    welcomeInfo3mid: "(безкоштовна юридична допомога) або",
    welcomeInfo3sem: "SEM",
    welcomeInfo3end: "безпосередньо.",
    welcomeHeading: "Що ви хочете дізнатися сьогодні?",
    welcomeHint: "Натисніть на тему або введіть запитання нижче — я відповідаю вашою мовою.",
    commonHeading: "Поширені запитання:",

    topics: [
      { emoji: "🔖", label: "Дозволи",      question: "Які типи дозволів існують у Швейцарії та що дозволяє кожен з них?" },
      { emoji: "📋", label: "Притулок",      question: "Які кроки швейцарської процедури надання притулку?" },
      { emoji: "💼", label: "Робота",        question: "Чи можу я працювати у Швейцарії та що мені потрібно зробити?" },
      { emoji: "🏥", label: "Охорона здоров'я", question: "Як отримати медичну допомогу та медичне страхування у Швейцарії?" },
      { emoji: "🎓", label: "Інтеграція",   question: "Які мовні курси та програми інтеграції доступні для біженців?" },
      { emoji: "👨‍👩‍👧", label: "Сім'я",     question: "Як я можу привезти свою сім'ю до Швейцарії?" },
      { emoji: "⚖️", label: "Апеляції",     question: "Як оскаржити відмову в наданні притулку?" },
      { emoji: "🏠", label: "Житло",        question: "Яке житло отримують шукачі притулку у Швейцарії?" },
    ],
    commonQ: [
      "Що мені робити, коли я вперше приїжджаю до Швейцарії як біженець?",
      "Що таке дозвіл F і чи можу я з ним працювати?",
      "Як оскаржити відмову в наданні притулку?",
      "Як я можу привезти свою сім'ю до Швейцарії?",
      "Що таке дозвіл S для українців?",
      "Які останні оновлення щодо притулку у Швейцарії?",
    ],

    // ChatInput
    placeholder: "Запитайте будь-що — притулок, дозволи, робота, охорона здоров'я… (будь-яка мова)",
    stopRecording: "Зупинити запис",
    startRecording: "Вимовте своє запитання",
    micDenied: "Доступ до мікрофона заборонено. Дозвольте доступ для використання голосового введення.",

    // MessageList
    feedbackRecorded: "Відгук записано",
    listenBtn: "Слухати",
    helpful: "Корисно",
    notHelpful: "Не корисно",
  },

  tr: {
    // Header
    subtitle: "İsviçre Mülteci Asistanı",

    // Sidebar
    yourCanton: "Kantonunuz",
    cantonHint: "Yerel yanıtlar için kantonunuzu seçin:",
    cantonPlaceholder: "— Kantonunuzu seçin —",
    cantonBadge: (c) => `📍 ${c}`,
    latestNews: "Son Haberler",
    articlesIndexed: (n) => `SEM ve İsviçre kaynaklarından ${n} makale dizine eklendi`,
    loadingNews: "Haberler yükleniyor…",
    emergencyContacts: "Acil Durum Kişileri",
    emergencyNumbers: "🚨 Polis: 117 · Ambulans: 144 · Acil: 112",
    osar: "OSAR — Ücretsiz hukuki yardım",
    sem: "SEM — Göç makamı",
    redcross: "İsviçre Kızılhaçı",
    chch: "ch.ch — İsviçre portalı",
    newConversation: "+ Yeni konuşma başlat",
    storedLocally: "🔒 Konuşmalar Groq AI aracılığıyla yerel olarak saklanır.",

    // PermitBar
    myPermit: "İznim:",
    permits: [
      { code: "N", label: "Sığınmacı — prosedür beklemede" },
      { code: "F", label: "Geçici olarak kabul edilmiş" },
      { code: "B", label: "Tanınmış mülteci" },
      { code: "C", label: "Oturma izni" },
      { code: "S", label: "Koruma statüsü (örn. Ukrayna)" },
      { code: "?", label: "İzin türümü bilmiyorum" },
    ],

    // WelcomeScreen
    welcomeInfo1: "Yardımcı olabileceğim konular: İsviçre iltica prosedürü · İzinler (N, F, B, C, S) · Çalışma hakları · Dil kursları · Sağlık hizmetleri · Aile birleşimi · İtirazlar · Konut",
    welcomeInfo2: "Diller: Kendi dilinizde yanıt veriyorum — Arapça, Tigrinya, Somali, Dari, Ukraynaca, Türkçe, Almanca, Fransızca, İtalyanca, İngilizce ve daha fazlası.",
    welcomeInfo3label: "Önemli:",
    welcomeInfo3: " Yalnızca rehberlik sağlıyorum — hukuki tavsiye değil. İtirazlar veya acil durumlar için",
    welcomeInfo3osar: "OSAR",
    welcomeInfo3mid: "(ücretsiz hukuki yardım) veya",
    welcomeInfo3sem: "SEM",
    welcomeInfo3end: "ile doğrudan iletişime geçin.",
    welcomeHeading: "Bugün ne öğrenmek istersiniz?",
    welcomeHint: "Bir konuya dokunun veya aşağıya sorunuzu yazın — kendi dilinizde cevap veriyorum.",
    commonHeading: "Sık sorulan sorular:",

    topics: [
      { emoji: "🔖", label: "İzinler",        question: "İsviçre'de hangi tür izinler var ve her biri ne sağlıyor?" },
      { emoji: "📋", label: "İltica",          question: "İsviçre iltica prosedürünün adımları nelerdir?" },
      { emoji: "💼", label: "Çalışma",         question: "İsviçre'de çalışabilir miyim ve ne yapmam gerekiyor?" },
      { emoji: "🏥", label: "Sağlık",          question: "İsviçre'de sağlık hizmetlerine nasıl erişir ve sağlık sigortası nasıl alırım?" },
      { emoji: "🎓", label: "Entegrasyon",     question: "Mülteciler için hangi dil kursları ve entegrasyon programları mevcut?" },
      { emoji: "👨‍👩‍👧", label: "Aile",         question: "Ailemi İsviçre'ye nasıl getirebilirim?" },
      { emoji: "⚖️", label: "İtiraz",          question: "Reddedilen iltica kararına nasıl itiraz ederim?" },
      { emoji: "🏠", label: "Konut",           question: "İsviçre'de sığınmacılar hangi konutu alıyor?" },
    ],
    commonQ: [
      "İsviçre'ye mülteci olarak ilk geldiğimde ne yapmalıyım?",
      "F izni nedir ve onunla çalışabilir miyim?",
      "Reddedilen iltica kararına nasıl itiraz ederim?",
      "Ailemi İsviçre'ye nasıl getirebilirim?",
      "Ukraynalılar için S izni nedir?",
      "İsviçre'deki en son iltica güncellemeleri nelerdir?",
    ],

    // ChatInput
    placeholder: "Her şeyi sorun — iltica, izinler, çalışma, sağlık… (herhangi bir dil)",
    stopRecording: "Kaydı durdur",
    startRecording: "Sorunuzu söyleyin",
    micDenied: "Mikrofon erişimi reddedildi. Sesli giriş kullanmak için lütfen erişime izin verin.",

    // MessageList
    feedbackRecorded: "Geri bildirim kaydedildi",
    listenBtn: "Dinle",
    helpful: "Yararlı",
    notHelpful: "Yararlı değil",
  },
};

export const LANGUAGES = [
  { code: "en", label: "English" },
  { code: "ar", label: "العربية" },
  { code: "uk", label: "Українська" },
  { code: "tr", label: "Türkçe" },
];

export default t;
