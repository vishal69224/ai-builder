"""Catalog of website types for the Prompt Analyzer.

Hundreds of types are generated from category × vertical combinations
plus curated specialty types so matching works across many domains.
"""

from __future__ import annotations

from dataclasses import dataclass


@dataclass(frozen=True)
class WebsiteType:
    id: str
    label: str
    category: str
    keywords: tuple[str, ...]
    default_pages: tuple[str, ...]
    default_components: tuple[str, ...]
    default_theme: tuple[str, str, str]  # style, primary hint, mood
    default_animations: tuple[str, ...]


_BASE_PAGES = ("Home", "About", "Services", "Contact")
_SHOP_PAGES = ("Home", "Menu", "Shop", "About", "Contact")
_SAAS_PAGES = ("Home", "Features", "Pricing", "Docs", "Blog", "Contact")
_PORTFOLIO_PAGES = ("Home", "Work", "About", "Services", "Contact")
_BLOG_PAGES = ("Home", "Articles", "Categories", "About", "Contact")
_EVENT_PAGES = ("Home", "Schedule", "Speakers", "Tickets", "Venue", "Contact")
_EDU_PAGES = ("Home", "Courses", "Instructors", "Pricing", "FAQ", "Contact")
_HEALTH_PAGES = ("Home", "Services", "Team", "Appointments", "FAQ", "Contact")
_RESTAURANT_PAGES = ("Home", "Menu", "Reservations", "Gallery", "About", "Contact")
_AGENCY_PAGES = ("Home", "Work", "Services", "Process", "About", "Contact")

_BASE_COMPONENTS = ("Navbar", "Hero", "Footer", "CTA", "ContactForm")
_SHOP_COMPONENTS = ("Navbar", "Hero", "ProductGrid", "Testimonials", "Footer", "CTA")
_SAAS_COMPONENTS = ("Navbar", "Hero", "FeatureGrid", "PricingTable", "FAQ", "Footer")
_PORTFOLIO_COMPONENTS = ("Navbar", "Hero", "ProjectGallery", "CaseStudyCard", "Footer")
_BLOG_COMPONENTS = ("Navbar", "FeaturedPost", "PostList", "Newsletter", "Footer")
_EVENT_COMPONENTS = ("Navbar", "Hero", "ScheduleTimeline", "SpeakerGrid", "TicketCTA", "Footer")

_AGENCY_COMPONENTS = ("Navbar", "Hero", "CaseStudyGrid", "ServiceList", "Footer", "CTA")
_ANIM_SOFT = ("fade-in", "subtle-parallax")
_ANIM_MODERN = ("fade-up", "stagger-children", "smooth-scroll")
_ANIM_BOLD = ("scale-in", "marquee", "scroll-reveal")


def _type(
    id_: str,
    label: str,
    category: str,
    keywords: tuple[str, ...],
    pages: tuple[str, ...],
    components: tuple[str, ...],
    theme: tuple[str, str, str],
    animations: tuple[str, ...] = _ANIM_MODERN,
) -> WebsiteType:
    return WebsiteType(id_, label, category, keywords, pages, components, theme, animations)


# Curated high-signal types (matched first)
CURATED_TYPES: list[WebsiteType] = [
    _type("coffee_shop", "Coffee Shop", "food_beverage", ("coffee", "cafe", "espresso", "roaster", "barista"), _RESTAURANT_PAGES, _SHOP_COMPONENTS, ("warm", "brown", "cozy"), _ANIM_SOFT),
    _type("bakery", "Bakery", "food_beverage", ("bakery", "pastry", "bread", "croissant"), _RESTAURANT_PAGES, _SHOP_COMPONENTS, ("warm", "cream", "artisan"), _ANIM_SOFT),
    _type("restaurant", "Restaurant", "food_beverage", ("restaurant", "dining", "bistro", "eatery"), _RESTAURANT_PAGES, _SHOP_COMPONENTS + ("ReservationForm",), ("elegant", "charcoal", "refined")),
    _type("bar_lounge", "Bar & Lounge", "food_beverage", ("bar", "lounge", "cocktail", "nightlife"), ("Home", "Menu", "Events", "Reservations", "Contact"), _SHOP_COMPONENTS, ("dark", "gold", "nightlife"), _ANIM_BOLD),
    _type("saas_startup", "SaaS Startup", "software", ("saas", "startup", "software platform", "b2b", "video generator", "ai video", "text to video", "generator website", "ai tool", "ai app", "software tool", "web app product"), _SAAS_PAGES, _SAAS_COMPONENTS, ("clean", "indigo", "product-led")),
    _type("ai_product", "AI Product", "software", ("ai product", "machine learning", "llm", "chatgpt", "generative ai", "ai generator", "video ai", "image generator", "ai platform"), _SAAS_PAGES, _SAAS_COMPONENTS + ("DemoWidget",), ("futuristic", "violet", "innovative"), _ANIM_BOLD),
    _type("fintech", "Fintech", "finance", ("fintech", "banking app", "payments", "wallet"), _SAAS_PAGES, _SAAS_COMPONENTS + ("SecurityBadges",), ("trust", "navy", "secure")),
    _type("crypto_exchange", "Crypto Exchange", "finance", ("crypto", "bitcoin", "exchange", "web3", "nft"), ("Home", "Markets", "Trade", "Learn", "Security"), _SAAS_COMPONENTS, ("dark", "neon", "tech"), _ANIM_BOLD),
    _type(
        "shoe_store",
        "Shoe Store",
        "retail",
        (
            "shoe store",
            "shoe shop",
            "shoes store",
            "footwear",
            "sneaker",
            "sneakers",
            "shoe",
            "shoes",
            "boots shop",
            "footwear store",
            "footwear shop",
        ),
        ("Home", "Shop", "Lookbook", "About", "Contact"),
        (
            "Navbar",
            "Hero",
            "ShoeCategories",
            "ShoeGrid",
            "ShoeLookbook",
            "Testimonials",
            "Footer",
        ),
        ("modern", "#111827", "stylish"),
        _ANIM_MODERN,
    ),
    _type(
        "mobile_store",
        "Mobile / Electronics Store",
        "retail",
        (
            "mobile store",
            "mobile shop",
            "smartphone",
            "smartphones",
            "mobilehub",
            "electronics store",
            "phone store",
            "mobile phone",
            "iphone store",
            "croma",
            "reliance digital",
        ),
        ("Home", "Smartphones", "Accessories", "Offers", "About", "Contact", "FAQ"),
        (
            "Navbar",
            "Hero",
            "AnnouncementBar",
            "BrandStrip",
            "CategoryGrid",
            "ProductGrid",
            "DealsBanner",
            "WhyChooseUs",
            "Testimonials",
            "Footer",
            "WhatsAppFloat",
            "Newsletter",
        ),
        ("modern", "#2563EB", "premium"),
        _ANIM_MODERN,
    ),
    _type("ecommerce_store", "E-commerce Store", "retail", ("ecommerce", "e-commerce", "online store", "shopify"), ("Home", "Shop", "Product", "Cart", "About", "Contact"), _SHOP_COMPONENTS + ("CartDrawer", "ProductCard"), ("modern", "neutral", "conversion")),
    _type(
        "fashion_brand",
        "Fashion Brand",
        "retail",
        (
            "fashion",
            "apparel",
            "clothing",
            "cloth shop",
            "clothes shop",
            "clothing shop",
            "clothing store",
            "cloth store",
            "garment",
            "boutique",
            "streetwear",
            "menswear",
            "womenswear",
        ),
        ("Home", "Lookbook", "Shop", "About", "Contact"),
        _SHOP_COMPONENTS + ("LookbookGrid", "ProductCard"),
        ("editorial", "#111827", "stylish"),
        _ANIM_BOLD,
    ),
    _type("portfolio_creative", "Creative Portfolio", "portfolio", ("portfolio", "designer", "creative", "photographer"), _PORTFOLIO_PAGES, _PORTFOLIO_COMPONENTS, ("minimal", "mono", "artistic"), _ANIM_SOFT),
    _type("agency", "Creative Agency", "business", ("agency", "studio", "branding agency", "marketing agency"), _AGENCY_PAGES, _AGENCY_COMPONENTS, ("bold", "contrast", "creative"), _ANIM_BOLD),
    _type("law_firm", "Law Firm", "professional", ("law firm", "attorney", "legal", "lawyer"), ("Home", "Practice Areas", "Attorneys", "Insights", "Contact"), _BASE_COMPONENTS + ("PracticeAreas", "AttorneyCards"), ("classic", "navy", "authoritative"), _ANIM_SOFT),
    _type("medical_clinic", "Medical Clinic", "healthcare", ("clinic", "medical", "doctor", "healthcare", "hospital"), _HEALTH_PAGES, _BASE_COMPONENTS + ("ServiceCards", "DoctorGrid", "AppointmentCTA"), ("clean", "teal", "caring"), _ANIM_SOFT),
    _type("dental_practice", "Dental Practice", "healthcare", ("dental", "dentist", "orthodont"), _HEALTH_PAGES, _BASE_COMPONENTS + ("ServiceCards", "SmileGallery"), ("bright", "sky", "friendly"), _ANIM_SOFT),
    _type("fitness_gym", "Fitness Gym", "health_fitness", ("gym", "fitness", "workout", "crossfit"), ("Home", "Classes", "Trainers", "Membership", "Contact"), _BASE_COMPONENTS + ("ClassSchedule", "TrainerCards", "Pricing"), ("energetic", "red", "powerful"), _ANIM_BOLD),
    _type("yoga_studio", "Yoga Studio", "health_fitness", ("yoga", "wellness studio", "meditation"), ("Home", "Classes", "Teachers", "Pricing", "Contact"), _BASE_COMPONENTS + ("ClassSchedule", "TeacherCards"), ("calm", "sage", "serene"), _ANIM_SOFT),
    _type("real_estate", "Real Estate", "property", ("real estate", "realtor", "property listings", "homes for sale"), ("Home", "Listings", "Agents", "Neighborhoods", "Contact"), _BASE_COMPONENTS + ("ListingGrid", "SearchFilters", "AgentCards"), ("trust", "slate", "aspirational")),
    _type("hotel", "Hotel & Hospitality", "travel", ("hotel", "resort", "hospitality", "boutique hotel"), ("Home", "Rooms", "Amenities", "Dining", "Book", "Contact"), _BASE_COMPONENTS + ("RoomCards", "AmenityGrid", "BookingCTA"), ("luxury", "gold", "hospitable"), _ANIM_SOFT),
    _type("travel_agency", "Travel Agency", "travel", ("travel agency", "tours", "vacation", "trip planner"), ("Home", "Destinations", "Packages", "About", "Contact"), _BASE_COMPONENTS + ("DestinationGrid", "PackageCards"), ("vibrant", "azure", "adventurous"), _ANIM_MODERN),
    _type("event_conference", "Conference / Event", "events", ("conference", "summit", "meetup", "event website"), _EVENT_PAGES, _EVENT_COMPONENTS, ("bold", "electric", "community"), _ANIM_BOLD),
    _type("wedding", "Wedding", "events", ("wedding", "bridal", "save the date"), ("Home", "Story", "Schedule", "Gallery", "RSVP", "Travel"), _BASE_COMPONENTS + ("Timeline", "Gallery", "RSVPForm"), ("romantic", "blush", "elegant"), _ANIM_SOFT),
    _type("nonprofit", "Nonprofit", "social", ("nonprofit", "charity", "ngo", "foundation", "donate"), ("Home", "Mission", "Programs", "Impact", "Donate", "Contact"), _BASE_COMPONENTS + ("ImpactStats", "DonateCTA", "ProgramCards"), ("hopeful", "green", "mission-driven"), _ANIM_SOFT),
    _type("education_course", "Online Course", "education", ("online course", "academy", "elearning", "cohort"), _EDU_PAGES, _BASE_COMPONENTS + ("Curriculum", "InstructorBio", "Pricing"), ("clear", "blue", "educational")),
    _type("university", "University / School", "education", ("university", "college", "school campus"), ("Home", "Academics", "Admissions", "Campus", "News", "Contact"), _BASE_COMPONENTS + ("ProgramGrid", "NewsList"), ("institutional", "burgundy", "academic"), _ANIM_SOFT),
    _type(
        "blog_magazine",
        "Blog / Magazine",
        "media",
        (
            "blog",
            "magazine",
            "editorial",
            "newsletter site",
            "seo blog",
            "seo website",
            "seo site",
            "content blog",
            "publishing site",
        ),
        _BLOG_PAGES,
        _BLOG_COMPONENTS,
        ("editorial", "#0F766E", "readable"),
        _ANIM_SOFT,
    ),
    _type("podcast", "Podcast", "media", ("podcast", "episodes", "audio show"), ("Home", "Episodes", "Guests", "About", "Subscribe"), _BASE_COMPONENTS + ("EpisodeList", "Player", "SubscribeLinks"), ("audio", "purple", "conversational")),
    _type("music_artist", "Music Artist", "entertainment", ("musician", "band", "album", "tour dates"), ("Home", "Music", "Tour", "Merch", "About", "Contact"), _BASE_COMPONENTS + ("ReleaseGrid", "TourDates", "MerchGrid"), ("bold", "neon", "expressive"), _ANIM_BOLD),
    _type("gaming", "Gaming", "entertainment", ("gaming", "esports", "game studio", "streamer"), ("Home", "Games", "News", "Community", "Store"), _BASE_COMPONENTS + ("GameCards", "NewsFeed"), ("dark", "neon", "immersive"), _ANIM_BOLD),
    _type("automotive", "Automotive", "automotive", ("car dealership", "auto", "vehicles", "garage"), ("Home", "Inventory", "Services", "Finance", "Contact"), _BASE_COMPONENTS + ("VehicleGrid", "ServiceList"), ("premium", "steel", "performance")),
    _type("construction", "Construction", "industrial", ("construction", "contractor", "builder", "architecture firm"), ("Home", "Projects", "Services", "About", "Contact"), _BASE_COMPONENTS + ("ProjectGallery", "ServiceCards"), ("solid", "orange", "reliable"), _ANIM_SOFT),
    _type("salon_spa", "Salon & Spa", "beauty", ("salon", "spa", "beauty", "hair studio", "nails"), ("Home", "Services", "Pricing", "Gallery", "Book", "Contact"), _BASE_COMPONENTS + ("ServiceMenu", "BookingCTA", "Gallery"), ("soft", "rose", "pampering"), _ANIM_SOFT),
    _type("pet_services", "Pet Services", "lifestyle", ("pet", "dog grooming", "veterinary", "pet shop"), ("Home", "Services", "Pricing", "Gallery", "Contact"), _BASE_COMPONENTS + ("ServiceCards", "PetGallery"), ("playful", "coral", "friendly")),
    _type("church", "Church / Faith", "community", ("church", "ministry", "faith", "parish"), ("Home", "Sermons", "Events", "Ministries", "Give", "Contact"), _BASE_COMPONENTS + ("EventList", "SermonList", "GiveCTA"), ("warm", "earth", "welcoming"), _ANIM_SOFT),
    _type("local_service", "Local Service Business", "local", ("plumber", "electrician", "hvac", "cleaning service", "local business"), ("Home", "Services", "Areas", "Reviews", "Contact"), _BASE_COMPONENTS + ("ServiceCards", "ReviewList", "QuoteForm"), ("practical", "blue", "trustworthy"), _ANIM_SOFT),
    _type("consulting", "Consulting Firm", "professional", ("consulting", "advisory", "strategy firm"), ("Home", "Expertise", "Insights", "Case Studies", "Contact"), _BASE_COMPONENTS + ("ExpertiseGrid", "InsightList"), ("sharp", "slate", "expert"), _ANIM_SOFT),
    _type("marketplace", "Marketplace", "retail", ("marketplace", "two-sided", "vendors", "listings platform"), ("Home", "Browse", "Sell", "How it works", "Pricing"), _SAAS_COMPONENTS + ("ListingGrid", "CategoryNav"), ("marketplace", "teal", "discovery")),
    _type("documentation", "Product Docs", "software", ("documentation", "docs site", "developer docs", "api reference"), ("Home", "Guides", "API", "Changelog", "Support"), ("SidebarNav", "DocSearch", "CodeBlock", "Footer"), ("technical", "gray", "precise"), _ANIM_SOFT),
    _type(
        "personal_brand",
        "Personal Brand",
        "portfolio",
        ("personal brand", "personal branding", "thought leader", "speaker site", "personal website", "branding website"),
        ("Home",),
        (
            "Navbar",
            "Hero",
            "AboutSection",
            "ExperienceSection",
            "SkillsSection",
            "ProjectGallery",
            "BlogSection",
            "Testimonials",
            "ContactForm",
            "Footer",
        ),
        ("minimal", "#111827", "authentic"),
        _ANIM_SOFT,
    ),
    _type("landing_page", "Marketing Landing Page", "marketing", ("landing page", "waitlist", "product launch", "coming soon"), ("Home",), ("Navbar", "Hero", "SocialProof", "FeatureGrid", "FAQ", "Footer", "WaitlistForm"), ("conversion", "brand", "focused"), _ANIM_MODERN),
]


# Expand into hundreds of types via category × vertical matrices
_VERTICALS: dict[str, tuple[tuple[str, tuple[str, ...]], ...]] = {
    "food_beverage": (
        ("juice_bar", ("juice", "smoothie")),
        ("tea_house", ("tea house", "matcha")),
        ("food_truck", ("food truck",)),
        ("steakhouse", ("steakhouse",)),
        ("sushi_bar", ("sushi",)),
        ("pizza_shop", ("pizza", "pizzeria")),
        ("ice_cream", ("ice cream", "gelato")),
        ("wine_bar", ("wine bar", "sommelier")),
        ("brewery", ("brewery", "craft beer")),
        ("vegan_cafe", ("vegan cafe", "plant-based cafe")),
        ("chocolate_shop", ("chocolate shop", "chocolatier")),
        ("catering", ("catering",)),
    ),
    "retail": (
        ("bookstore", ("bookstore", "book store", "bookshop", "book shop", "online bookstore", "buy books", "read books")),
        ("florist", ("florist", "flower shop")),
        ("jewelry", ("jewelry", "jeweller")),
        ("furniture", ("furniture store", "home furnishings")),
        ("electronics", ("electronics store",)),
        ("sports_gear", ("sports store", "outdoor gear")),
        ("toy_store", ("toy store",)),
        ("gift_shop", ("gift shop",)),
        ("thrift_store", ("thrift", "vintage shop")),
        ("sneaker_store", ("sneaker", "footwear")),
        ("cosmetics", ("cosmetics", "beauty store")),
        ("pharmacy_retail", ("pharmacy", "drugstore")),
    ),
    "healthcare": (
        ("physio", ("physiotherapy", "physical therapy")),
        ("mental_health", ("therapy clinic", "mental health", "counseling")),
        ("dermatology", ("dermatology", "skin clinic")),
        ("optometry", ("optometry", "eye care")),
        ("pediatric", ("pediatric", "children clinic")),
        ("chiropractic", ("chiropractic", "chiropractor")),
        ("pharmacy_clinic", ("pharmacy clinic",)),
        ("lab_diagnostics", ("diagnostic lab", "pathology")),
        ("urgent_care", ("urgent care",)),
        ("veterinary_clinic", ("veterinary", "animal hospital")),
    ),
    "software": (
        ("devtools", ("developer tools", "devtools")),
        ("hr_software", ("hr software", "people platform")),
        ("crm", ("crm", "sales platform")),
        ("analytics", ("analytics platform", "bi tool")),
        ("security_saas", ("cybersecurity", "security platform")),
        ("design_tool", ("design tool", "figma alternative")),
        ("project_mgmt", ("project management", "pm tool")),
        ("cms_product", ("headless cms", "content platform")),
        ("automation", ("automation", "workflow tool", "zapier")),
        ("no_code", ("no-code", "nocode")),
    ),
    "education": (
        ("coding_bootcamp", ("bootcamp", "coding school")),
        ("language_school", ("language school", "english school")),
        ("tutoring", ("tutoring", "tutor")),
        ("kids_learning", ("kids learning", "edutainment")),
        ("music_school", ("music school", "music lessons")),
        ("driving_school", ("driving school",)),
        ("corporate_training", ("corporate training", "lms")),
        ("test_prep", ("test prep", "sat prep", "exam prep")),
    ),
    "travel": (
        ("hostel", ("hostel",)),
        ("bnb", ("bed and breakfast", "bnb", "airbnb host")),
        ("tour_operator", ("tour operator", "guided tours")),
        ("airline", ("airline", "flights")),
        ("car_rental", ("car rental",)),
        ("cruise", ("cruise",)),
        ("adventure_travel", ("adventure travel", "hiking tours")),
        ("city_guide", ("city guide", "local guide")),
    ),
    "professional": (
        ("accounting", ("accounting", "cpa", "bookkeeping")),
        ("architecture", ("architecture firm", "architect")),
        ("insurance", ("insurance", "broker")),
        ("recruiting", ("recruiting", "staffing agency")),
        ("pr_agency", ("pr agency", "public relations")),
        ("tax_advisor", ("tax advisor", "tax firm")),
        ("notary", ("notary",)),
        ("translation", ("translation agency", "localization")),
    ),
    "lifestyle": (
        ("interior_design", ("interior design", "home styling")),
        ("photography_studio", ("photography studio", "photo studio")),
        ("wedding_planner", ("wedding planner",)),
        ("gardening", ("garden center", "landscaping")),
        ("home_organizing", ("home organizer",)),
        ("personal_training", ("personal trainer",)),
        ("nutrition", ("nutritionist", "dietitian")),
        ("life_coach", ("life coach", "coaching")),
    ),
    "industrial": (
        ("manufacturing", ("manufacturing", "factory")),
        ("logistics", ("logistics", "shipping company", "freight")),
        ("warehouse", ("warehouse", "fulfillment")),
        ("energy", ("energy company", "solar", "renewable")),
        ("mining", ("mining",)),
        ("agriculture", ("agriculture", "farm", "agritech")),
        ("printing", ("print shop", "printing company")),
        ("packaging", ("packaging company",)),
    ),
    "community": (
        ("sports_club", ("sports club", "athletic club")),
        ("coworking", ("coworking", "shared office")),
        ("makerspace", ("makerspace", "fab lab")),
        ("library", ("public library",)),
        ("museum", ("museum", "gallery museum")),
        ("theater", ("theater", "playhouse")),
        ("community_center", ("community center",)),
        ("alumni", ("alumni network", "alumni association")),
    ),
    "government": (
        ("city_portal", ("city website", "municipal", "gov portal")),
        ("tourism_board", ("tourism board", "visit city")),
        ("public_health", ("public health dept",)),
        ("transit", ("public transit", "metro", "bus authority")),
        ("parks_recreation", ("parks and recreation",)),
        ("open_data", ("open data portal",)),
    ),
    "entertainment": (
        ("cinema", ("cinema", "movie theater")),
        ("comedy_club", ("comedy club",)),
        ("amusement", ("amusement park", "theme park")),
        ("escape_room", ("escape room",)),
        ("bowling", ("bowling alley",)),
        ("arcade", ("arcade",)),
        ("festival", ("music festival", "festival site")),
        ("comedy_show", ("stand-up", "comedy show")),
    ),
}


_CATEGORY_DEFAULTS: dict[str, tuple[tuple[str, ...], tuple[str, ...], tuple[str, str, str], tuple[str, ...]]] = {
    "food_beverage": (_RESTAURANT_PAGES, _SHOP_COMPONENTS, ("warm", "amber", "inviting"), _ANIM_SOFT),
    "retail": (("Home", "Shop", "About", "Contact"), _SHOP_COMPONENTS, ("modern", "neutral", "shoppable"), _ANIM_MODERN),
    "healthcare": (_HEALTH_PAGES, _BASE_COMPONENTS + ("ServiceCards",), ("clean", "teal", "reassuring"), _ANIM_SOFT),
    "software": (_SAAS_PAGES, _SAAS_COMPONENTS, ("clean", "indigo", "product"), _ANIM_MODERN),
    "education": (_EDU_PAGES, _BASE_COMPONENTS + ("CourseGrid",), ("clear", "blue", "learning"), _ANIM_SOFT),
    "travel": (("Home", "Destinations", "Packages", "About", "Contact"), _BASE_COMPONENTS + ("DestinationGrid",), ("vibrant", "sky", "wanderlust"), _ANIM_MODERN),
    "professional": (("Home", "Services", "Insights", "About", "Contact"), _BASE_COMPONENTS + ("ServiceCards",), ("trust", "navy", "expert"), _ANIM_SOFT),
    "lifestyle": (_BASE_PAGES + ("Gallery",), _BASE_COMPONENTS + ("Gallery",), ("soft", "blush", "lifestyle"), _ANIM_SOFT),
    "industrial": (("Home", "Capabilities", "Projects", "About", "Contact"), _BASE_COMPONENTS + ("CapabilityGrid",), ("solid", "steel", "industrial"), _ANIM_SOFT),
    "community": (("Home", "Programs", "Events", "About", "Contact"), _BASE_COMPONENTS + ("EventList",), ("friendly", "green", "community"), _ANIM_SOFT),
    "government": (("Home", "Services", "News", "Resources", "Contact"), _BASE_COMPONENTS + ("ServiceDirectory",), ("official", "blue", "civic"), _ANIM_SOFT),
    "entertainment": (("Home", "Events", "Tickets", "Gallery", "Contact"), _BASE_COMPONENTS + ("EventCards",), ("bold", "magenta", "fun"), _ANIM_BOLD),
}


def _expanded_types() -> list[WebsiteType]:
    items: list[WebsiteType] = []
    for category, verticals in _VERTICALS.items():
        pages, components, theme, animations = _CATEGORY_DEFAULTS[category]
        for slug, keywords in verticals:
            label = slug.replace("_", " ").title()
            items.append(
                _type(
                    f"{category}__{slug}",
                    label,
                    category,
                    keywords + (slug.replace("_", " "),),
                    pages,
                    components,
                    theme,
                    animations,
                )
            )
    return items


def _style_variants(base: list[WebsiteType]) -> list[WebsiteType]:
    """Multiply coverage with style/audience variants."""
    variants: list[WebsiteType] = []
    styles = (
        ("modern", ("modern", "contemporary")),
        ("minimal", ("minimal", "minimalist")),
        ("luxury", ("luxury", "premium", "high-end")),
        ("playful", ("playful", "fun", "colorful")),
        ("corporate", ("corporate", "enterprise")),
        ("vintage", ("vintage", "retro")),
        ("brutalist", ("brutalist",)),
        ("glassmorphism", ("glassmorphism", "glass ui")),
    )
    for wt in base:
        for style_id, style_keys in styles:
            variants.append(
                WebsiteType(
                    id=f"{wt.id}__{style_id}",
                    label=f"{style_id.title()} {wt.label}",
                    category=wt.category,
                    keywords=wt.keywords + style_keys,
                    default_pages=wt.default_pages,
                    default_components=wt.default_components,
                    default_theme=(style_id, wt.default_theme[1], wt.default_theme[2]),
                    default_animations=wt.default_animations,
                )
            )
    return variants


def build_website_type_catalog() -> list[WebsiteType]:
    expanded = _expanded_types()
    # Curated first for matching priority; then expanded; then style variants of curated only
    curated_variants = _style_variants(CURATED_TYPES)
    # Deduplicate by id while preserving order
    seen: set[str] = set()
    catalog: list[WebsiteType] = []
    for item in [*CURATED_TYPES, *expanded, *curated_variants]:
        if item.id in seen:
            continue
        seen.add(item.id)
        catalog.append(item)
    return catalog


WEBSITE_TYPES: list[WebsiteType] = build_website_type_catalog()


def catalog_stats() -> dict[str, int]:
    categories = {t.category for t in WEBSITE_TYPES}
    return {"total_types": len(WEBSITE_TYPES), "categories": len(categories)}
