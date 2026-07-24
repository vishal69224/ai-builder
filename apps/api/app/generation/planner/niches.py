"""Niche registry stubs for generation v2 (Phase 1 Planner).

23 first-class niches with allowed/forbidden product taxonomies.
Specialty generators are not switched yet — this metadata feeds WebsitePlan only.
"""

from __future__ import annotations

import re
from dataclasses import dataclass, field


@dataclass(frozen=True)
class NicheSpec:
    id: str
    label: str
    industry: str
    default_subcategory: str
    target_audience: str
    brand_style: str
    design_style: str
    token_preset: str
    typography_style: str
    image_style: str
    image_collections: tuple[str, ...]
    product_types: tuple[str, ...]
    forbidden_products: tuple[str, ...]
    default_pages: tuple[str, ...]
    default_sections: tuple[str, ...]
    hero_variant: str
    navbar_variant: str
    footer_variant: str
    type_id_prefixes: tuple[str, ...] = field(default_factory=tuple)
    prompt_keywords: tuple[str, ...] = field(default_factory=tuple)


NICHES: dict[str, NicheSpec] = {}


def _reg(spec: NicheSpec) -> NicheSpec:
    NICHES[spec.id] = spec
    return spec


_reg(
    NicheSpec(
        id="clothing",
        label="Clothing Store",
        industry="Fashion",
        default_subcategory="Branded Apparel",
        target_audience="Men and Women",
        brand_style="Premium lifestyle",
        design_style="Luxury Minimal",
        token_preset="luxury_minimal",
        typography_style="Elegant sans",
        image_style="Editorial fashion",
        image_collections=("fashion", "luxury", "streetwear", "formal"),
        product_types=("T-Shirts", "Hoodies", "Jeans", "Jackets", "Dresses", "Shirts"),
        forbidden_products=("Shoes", "Sneakers", "Football Shoes", "Boots", "Sandals"),
        default_pages=("Home", "Shop", "About", "Contact"),
        default_sections=("Hero", "Collections", "Trending", "Newsletter"),
        hero_variant="HeroFashion",
        navbar_variant="NavbarClassic",
        footer_variant="FooterPremium",
        type_id_prefixes=("fashion", "clothing", "apparel", "boutique"),
        prompt_keywords=("clothing", "apparel", "fashion", "boutique", "garment", "streetwear"),
    )
)

_reg(
    NicheSpec(
        id="footwear",
        label="Footwear Store",
        industry="Fashion",
        default_subcategory="Shoes & Sneakers",
        target_audience="Athletes and lifestyle buyers",
        brand_style="Performance lifestyle",
        design_style="Bold Modern",
        token_preset="bold_modern",
        typography_style="Geometric sans",
        image_style="Product footwear",
        image_collections=("footwear", "sneakers", "streetwear"),
        product_types=("Sneakers", "Running Shoes", "Boots", "Loafers", "Sandals"),
        forbidden_products=("T-Shirts", "Hoodies", "Jeans", "Jackets", "Dresses"),
        default_pages=("Home", "Shop", "Lookbook", "About", "Contact"),
        default_sections=("Hero", "Categories", "Featured", "Reviews"),
        hero_variant="HeroFashion",
        navbar_variant="NavbarClassic",
        footer_variant="FooterMinimal",
        type_id_prefixes=("shoe", "sneaker", "footwear"),
        prompt_keywords=("shoe", "shoes", "sneaker", "sneakers", "footwear", "loafer"),
    )
)

_reg(
    NicheSpec(
        id="electronics",
        label="Electronics Store",
        industry="Retail",
        default_subcategory="Consumer Electronics",
        target_audience="Tech shoppers",
        brand_style="Tech retail",
        design_style="Modern Dark",
        token_preset="tech_dark",
        typography_style="Clean sans",
        image_style="Gadgets and devices",
        image_collections=("electronics", "gadgets", "phones"),
        product_types=("Smartphones", "Laptops", "Accessories", "Audio", "Wearables"),
        forbidden_products=("Shoes", "Sneakers", "Furniture", "Clothing"),
        default_pages=("Home", "Shop", "Offers", "About", "Contact"),
        default_sections=("Hero", "Categories", "Deals", "WhyUs"),
        hero_variant="HeroSplit",
        navbar_variant="NavbarClassic",
        footer_variant="FooterDark",
        type_id_prefixes=("mobile_store", "electronics", "phone"),
        prompt_keywords=("electronics", "smartphone", "phone store", "mobile store", "iphone"),
    )
)

_reg(
    NicheSpec(
        id="restaurant",
        label="Restaurant",
        industry="Food & Beverage",
        default_subcategory="Dining",
        target_audience="Diners",
        brand_style="Warm hospitality",
        design_style="Warm Editorial",
        token_preset="warm_hospitality",
        typography_style="Serif display + sans",
        image_style="Plated food",
        image_collections=("restaurant", "dining", "pizza"),
        product_types=("Starters", "Mains", "Desserts", "Drinks"),
        forbidden_products=("Furniture", "Medical Equipment", "Shoes"),
        default_pages=("Home", "Menu", "About", "Reservations", "Contact"),
        default_sections=("Hero", "MenuHighlights", "About", "Reservations"),
        hero_variant="HeroRestaurant",
        navbar_variant="NavbarTransparent",
        footer_variant="FooterDark",
        type_id_prefixes=("restaurant",),
        prompt_keywords=("restaurant", "dining", "bistro", "eatery"),
    )
)

_reg(
    NicheSpec(
        id="coffee_shop",
        label="Coffee Shop",
        industry="Food & Beverage",
        default_subcategory="Cafe",
        target_audience="Coffee lovers",
        brand_style="Cozy artisan",
        design_style="Warm Minimal",
        token_preset="warm_cafe",
        typography_style="Friendly sans",
        image_style="Coffee and cafe interior",
        image_collections=("coffee", "cafe", "interior"),
        product_types=("Espresso", "Pour Over", "Pastries", "Beans"),
        forbidden_products=("Hospital", "Cars", "Sneakers"),
        default_pages=("Home", "Menu", "About", "Contact"),
        default_sections=("Hero", "Menu", "Story", "Visit"),
        hero_variant="HeroCenter",
        navbar_variant="NavbarClassic",
        footer_variant="FooterMinimal",
        type_id_prefixes=("coffee",),
        prompt_keywords=("coffee", "cafe", "espresso", "barista"),
    )
)

_reg(
    NicheSpec(
        id="bakery",
        label="Bakery",
        industry="Food & Beverage",
        default_subcategory="Pastry",
        target_audience="Local customers",
        brand_style="Artisan bakery",
        design_style="Soft Warm",
        token_preset="warm_cafe",
        typography_style="Rounded sans",
        image_style="Pastries and bread",
        image_collections=("bakery", "pastry"),
        product_types=("Bread", "Croissants", "Cakes", "Cookies"),
        forbidden_products=("Medical", "Electronics"),
        default_pages=("Home", "Menu", "About", "Contact"),
        default_sections=("Hero", "Specials", "About", "Order"),
        hero_variant="HeroImageLeft",
        navbar_variant="NavbarClassic",
        footer_variant="FooterMinimal",
        type_id_prefixes=("bakery",),
        prompt_keywords=("bakery", "pastry", "bread shop"),
    )
)

_reg(
    NicheSpec(
        id="portfolio",
        label="Portfolio",
        industry="Creative",
        default_subcategory="Personal Portfolio",
        target_audience="Clients and employers",
        brand_style="Personal brand",
        design_style="Minimal",
        token_preset="minimal_ink",
        typography_style="Editorial sans",
        image_style="Work samples",
        image_collections=("photography", "creative", "modern"),
        product_types=(),
        forbidden_products=("Product SKUs", "Menu Items"),
        default_pages=("Home",),
        default_sections=("Hero", "About", "Projects", "Contact"),
        hero_variant="HeroCenter",
        navbar_variant="NavbarMinimal",
        footer_variant="FooterMinimal",
        type_id_prefixes=("portfolio", "personal_brand"),
        prompt_keywords=("portfolio", "personal brand", "freelancer", "developer portfolio", "flutter developer", "python developer", "i am a flutter", "i am a python"),
    )
)

_reg(
    NicheSpec(
        id="agency",
        label="Agency",
        industry="Professional Services",
        default_subcategory="Creative / Marketing Agency",
        target_audience="Business clients",
        brand_style="Confident studio",
        design_style="Sharp Modern",
        token_preset="agency_sharp",
        typography_style="Bold sans",
        image_style="Office and creative work",
        image_collections=("office", "modern", "creative"),
        product_types=("Brand Strategy", "Web Design", "Campaigns"),
        forbidden_products=("Clinical Products", "Restaurant Menu"),
        default_pages=("Home", "Services", "Work", "About", "Contact"),
        default_sections=("Hero", "Services", "CaseStudies", "CTA"),
        hero_variant="HeroSaaS",
        navbar_variant="NavbarTransparent",
        footer_variant="FooterPremium",
        type_id_prefixes=("agency", "marketing"),
        prompt_keywords=("agency", "studio", "marketing agency"),
    )
)

_reg(
    NicheSpec(
        id="jewelry",
        label="Jewelry",
        industry="Fashion",
        default_subcategory="Fine Jewelry",
        target_audience="Gift buyers and collectors",
        brand_style="Luxury",
        design_style="Luxury Minimal",
        token_preset="luxury_minimal",
        typography_style="Elegant serif + sans",
        image_style="Luxury jewelry",
        image_collections=("luxury", "jewelry"),
        product_types=("Rings", "Necklaces", "Earrings", "Bracelets"),
        forbidden_products=("Sneakers", "Furniture"),
        default_pages=("Home", "Collections", "About", "Contact"),
        default_sections=("Hero", "Collections", "Craftsmanship", "Newsletter"),
        hero_variant="HeroFashion",
        navbar_variant="NavbarClassic",
        footer_variant="FooterPremium",
        type_id_prefixes=("jewelry",),
        prompt_keywords=("jewelry", "jewellery", "diamond", "rings"),
    )
)

_reg(
    NicheSpec(
        id="furniture",
        label="Furniture",
        industry="Home",
        default_subcategory="Home Furnishings",
        target_audience="Homeowners",
        brand_style="Modern living",
        design_style="Calm Modern",
        token_preset="calm_home",
        typography_style="Neutral sans",
        image_style="Interior furniture",
        image_collections=("furniture", "bedroom", "office", "interior"),
        product_types=("Sofas", "Tables", "Beds", "Chairs", "Storage"),
        forbidden_products=("Food Menu", "Medical Devices"),
        default_pages=("Home", "Shop", "Collections", "About", "Contact"),
        default_sections=("Hero", "Collections", "Materials", "CTA"),
        hero_variant="HeroSplit",
        navbar_variant="NavbarClassic",
        footer_variant="FooterMinimal",
        type_id_prefixes=("furniture",),
        prompt_keywords=("furniture", "sofa", "interior store"),
    )
)

_reg(
    NicheSpec(
        id="medical",
        label="Medical",
        industry="Healthcare",
        default_subcategory="Clinic",
        target_audience="Patients",
        brand_style="Trustworthy clinical",
        design_style="Clean Clinical",
        token_preset="clinical",
        typography_style="Readable sans",
        image_style="Doctors and care",
        image_collections=("medical", "doctors", "hospital", "healthcare"),
        product_types=("Consultations", "Diagnostics", "Treatments"),
        forbidden_products=("Fashion SKUs", "Restaurant Food"),
        default_pages=("Home", "Services", "Doctors", "About", "Contact"),
        default_sections=("Hero", "Services", "Doctors", "Appointments"),
        hero_variant="HeroSplit",
        navbar_variant="NavbarClassic",
        footer_variant="FooterMinimal",
        type_id_prefixes=("clinic", "hospital", "healthcare", "medical"),
        prompt_keywords=("clinic", "hospital", "medical", "doctor", "healthcare"),
    )
)

_reg(
    NicheSpec(
        id="travel",
        label="Travel",
        industry="Travel",
        default_subcategory="Travel Agency",
        target_audience="Travelers",
        brand_style="Adventurous",
        design_style="Bright Editorial",
        token_preset="travel_bright",
        typography_style="Friendly sans",
        image_style="Destinations",
        image_collections=("travel", "landscape"),
        product_types=("Packages", "Flights", "Hotels", "Tours"),
        forbidden_products=("Clinic Services", "Auto Inventory"),
        default_pages=("Home", "Destinations", "Packages", "About", "Contact"),
        default_sections=("Hero", "Destinations", "Packages", "Testimonials"),
        hero_variant="HeroImageLeft",
        navbar_variant="NavbarTransparent",
        footer_variant="FooterPremium",
        type_id_prefixes=("travel",),
        prompt_keywords=("travel", "tour", "holiday", "vacation"),
    )
)

_reg(
    NicheSpec(
        id="gym",
        label="Gym",
        industry="Fitness",
        default_subcategory="Fitness Club",
        target_audience="Fitness members",
        brand_style="Energetic",
        design_style="Bold Athletic",
        token_preset="bold_athletic",
        typography_style="Condensed sans",
        image_style="Training and gym",
        image_collections=("fitness",),
        product_types=("Memberships", "Classes", "Personal Training"),
        forbidden_products=("Fine Dining Menu", "Jewelry"),
        default_pages=("Home", "Classes", "Membership", "About", "Contact"),
        default_sections=("Hero", "Programs", "Trainers", "CTA"),
        hero_variant="HeroCenter",
        navbar_variant="NavbarTransparent",
        footer_variant="FooterDark",
        type_id_prefixes=("gym", "fitness"),
        prompt_keywords=("gym", "fitness", "workout", "crossfit"),
    )
)

_reg(
    NicheSpec(
        id="education",
        label="Education",
        industry="Education",
        default_subcategory="School / Courses",
        target_audience="Students and parents",
        brand_style="Institutional",
        design_style="Clear Academic",
        token_preset="academic",
        typography_style="Readable sans",
        image_style="Campus and learning",
        image_collections=("campus", "learning"),
        product_types=("Programs", "Courses", "Admissions"),
        forbidden_products=("Nightlife", "Auto Sales"),
        default_pages=("Home", "Programs", "Admissions", "About", "Contact"),
        default_sections=("Hero", "Programs", "Campus", "CTA"),
        hero_variant="HeroSplit",
        navbar_variant="NavbarClassic",
        footer_variant="FooterMinimal",
        type_id_prefixes=("university", "school", "education", "course"),
        prompt_keywords=("school", "university", "course", "education", "academy"),
    )
)

_reg(
    NicheSpec(
        id="law_firm",
        label="Law Firm",
        industry="Professional Services",
        default_subcategory="Legal Practice",
        target_audience="Clients seeking counsel",
        brand_style="Authoritative",
        design_style="Formal Minimal",
        token_preset="formal_law",
        typography_style="Serif headings",
        image_style="Office formal",
        image_collections=("office", "formal"),
        product_types=("Corporate Law", "Litigation", "Advisory"),
        forbidden_products=("Product Grid SKUs", "Menu Items"),
        default_pages=("Home", "Practice Areas", "Attorneys", "About", "Contact"),
        default_sections=("Hero", "PracticeAreas", "Attorneys", "Contact"),
        hero_variant="HeroCenter",
        navbar_variant="NavbarClassic",
        footer_variant="FooterPremium",
        type_id_prefixes=("law", "legal"),
        prompt_keywords=("law firm", "attorney", "lawyer", "legal"),
    )
)

_reg(
    NicheSpec(
        id="finance",
        label="Finance",
        industry="Finance",
        default_subcategory="Financial Services",
        target_audience="Individuals and businesses",
        brand_style="Trust finance",
        design_style="Clean Corporate",
        token_preset="finance_clean",
        typography_style="Corporate sans",
        image_style="Office finance",
        image_collections=("finance", "office"),
        product_types=("Advisory", "Planning", "Accounts"),
        forbidden_products=("Restaurant Food", "Apparel"),
        default_pages=("Home", "Services", "Insights", "About", "Contact"),
        default_sections=("Hero", "Services", "Trust", "CTA"),
        hero_variant="HeroSaaS",
        navbar_variant="NavbarClassic",
        footer_variant="FooterMinimal",
        type_id_prefixes=("finance", "bank", "fintech"),
        prompt_keywords=("finance", "bank", "wealth", "investment"),
    )
)

_reg(
    NicheSpec(
        id="bookstore",
        label="Book Store",
        industry="Retail",
        default_subcategory="Books & Reading",
        target_audience="Readers",
        brand_style="Literary",
        design_style="Editorial",
        token_preset="editorial_teal",
        typography_style="Literary serif + sans",
        image_style="Books and reading",
        image_collections=("books", "editorial"),
        product_types=("Fiction", "Non-Fiction", "Children", "Stationery"),
        forbidden_products=("Sneakers", "Medical Devices"),
        default_pages=("Home", "Browse", "Library", "Cart", "About"),
        default_sections=("Hero", "Featured", "Search", "Categories", "Library"),
        hero_variant="HeroBookstore",
        navbar_variant="NavbarBookstore",
        footer_variant="FooterMinimal",
        type_id_prefixes=("book",),
        prompt_keywords=(
            "bookstore",
            "book store",
            "book shop",
            "bookshop",
            "online bookstore",
            "buy books",
            "read books",
            "pdf books",
            "ebook",
        ),
    )
)

_reg(
    NicheSpec(
        id="real_estate",
        label="Real Estate",
        industry="Real Estate",
        default_subcategory="Property Listings",
        target_audience="Buyers and renters",
        brand_style="Professional realty",
        design_style="Clean Listing",
        token_preset="realty_clean",
        typography_style="Neutral sans",
        image_style="Architecture and interiors",
        image_collections=("interior", "architecture"),
        product_types=("Homes", "Apartments", "Commercial"),
        forbidden_products=("Menu Items", "Apparel"),
        default_pages=("Home", "Listings", "Agents", "About", "Contact"),
        default_sections=("Hero", "FeaturedListings", "Neighborhoods", "CTA"),
        hero_variant="HeroSplit",
        navbar_variant="NavbarClassic",
        footer_variant="FooterMinimal",
        type_id_prefixes=("real_estate", "realty", "property"),
        prompt_keywords=("real estate", "property", "listings", "realtor"),
    )
)

_reg(
    NicheSpec(
        id="hotel",
        label="Hotel",
        industry="Hospitality",
        default_subcategory="Hotel / Stay",
        target_audience="Travelers",
        brand_style="Hospitality luxury",
        design_style="Calm Luxury",
        token_preset="hospitality_luxury",
        typography_style="Elegant sans",
        image_style="Hospitality interiors",
        image_collections=("hospitality", "interior"),
        product_types=("Rooms", "Suites", "Experiences", "Dining"),
        forbidden_products=("Auto Inventory", "Clinic"),
        default_pages=("Home", "Rooms", "Experiences", "About", "Contact"),
        default_sections=("Hero", "Rooms", "Amenities", "Book"),
        hero_variant="HeroImageLeft",
        navbar_variant="NavbarTransparent",
        footer_variant="FooterPremium",
        type_id_prefixes=("hotel", "resort"),
        prompt_keywords=("hotel", "resort", "boutique hotel"),
    )
)

_reg(
    NicheSpec(
        id="photography",
        label="Photography",
        industry="Creative",
        default_subcategory="Photo Studio",
        target_audience="Clients booking shoots",
        brand_style="Visual artist",
        design_style="Gallery Minimal",
        token_preset="minimal_ink",
        typography_style="Minimal sans",
        image_style="Portfolio photography",
        image_collections=("photography", "creative"),
        product_types=("Weddings", "Portraits", "Commercial"),
        forbidden_products=("Dense Retail SKUs",),
        default_pages=("Home", "Portfolio", "Services", "About", "Contact"),
        default_sections=("Hero", "Gallery", "Services", "Contact"),
        hero_variant="HeroCenter",
        navbar_variant="NavbarMinimal",
        footer_variant="FooterMinimal",
        type_id_prefixes=("photo", "photography"),
        prompt_keywords=("photographer", "photography", "photo studio"),
    )
)

_reg(
    NicheSpec(
        id="automobile",
        label="Automobile",
        industry="Automotive",
        default_subcategory="Dealership",
        target_audience="Car buyers",
        brand_style="Performance retail",
        design_style="Bold Showroom",
        token_preset="auto_steel",
        typography_style="Strong sans",
        image_style="Vehicles and showroom",
        image_collections=("auto", "showroom"),
        product_types=("Sedans", "SUVs", "EVs", "Used Cars"),
        forbidden_products=("Apparel", "Pastries"),
        default_pages=("Home", "Inventory", "Services", "About", "Contact"),
        default_sections=("Hero", "Inventory", "Finance", "Contact"),
        hero_variant="HeroSplit",
        navbar_variant="NavbarClassic",
        footer_variant="FooterDark",
        type_id_prefixes=("automotive", "auto", "car"),
        prompt_keywords=("car dealership", "automobile", "auto dealer", "vehicles"),
    )
)

_reg(
    NicheSpec(
        id="wedding",
        label="Wedding",
        industry="Events",
        default_subcategory="Wedding Services",
        target_audience="Couples",
        brand_style="Romantic",
        design_style="Soft Romantic",
        token_preset="romantic_soft",
        typography_style="Script accent + sans",
        image_style="Weddings and florals",
        image_collections=("wedding", "floral"),
        product_types=("Packages", "Venues", "Planning"),
        forbidden_products=("Industrial Equipment", "Electronics SKUs"),
        default_pages=("Home", "Packages", "Gallery", "About", "Contact"),
        default_sections=("Hero", "Packages", "Gallery", "Inquiry"),
        hero_variant="HeroCenter",
        navbar_variant="NavbarTransparent",
        footer_variant="FooterMinimal",
        type_id_prefixes=("wedding",),
        prompt_keywords=("wedding", "bridal", "matrimony"),
    )
)

_reg(
    NicheSpec(
        id="salon",
        label="Salon",
        industry="Beauty",
        default_subcategory="Salon & Spa",
        target_audience="Beauty clients",
        brand_style="Pampering",
        design_style="Soft Beauty",
        token_preset="beauty_soft",
        typography_style="Soft sans",
        image_style="Salon and beauty",
        image_collections=("beauty", "salon"),
        product_types=("Hair", "Nails", "Spa", "Makeup"),
        forbidden_products=("Electronics", "Auto Parts"),
        default_pages=("Home", "Services", "Pricing", "Book", "Contact"),
        default_sections=("Hero", "Services", "Gallery", "Book"),
        hero_variant="HeroFashion",
        navbar_variant="NavbarClassic",
        footer_variant="FooterMinimal",
        type_id_prefixes=("salon", "spa", "beauty"),
        prompt_keywords=("salon", "spa", "hair studio", "nails"),
    )
)

_reg(
    NicheSpec(
        id="blog",
        label="SEO Blog",
        industry="Media",
        default_subcategory="Content Publishing",
        target_audience="Readers",
        brand_style="Editorial authority",
        design_style="Readable Editorial",
        token_preset="editorial_teal",
        typography_style="Readable serif + sans",
        image_style="Editorial covers",
        image_collections=("editorial", "workspace"),
        product_types=(),
        forbidden_products=("Ecommerce SKUs",),
        default_pages=("Home", "Articles", "Categories", "About", "Contact"),
        default_sections=("Hero", "Featured", "Latest", "Newsletter"),
        hero_variant="HeroCenter",
        navbar_variant="NavbarClassic",
        footer_variant="FooterMinimal",
        type_id_prefixes=("blog", "magazine"),
        prompt_keywords=("blog", "seo blog", "magazine", "newsletter site"),
    )
)

_reg(
    NicheSpec(
        id="saas",
        label="SaaS Product",
        industry="Software",
        default_subcategory="AI Product",
        target_audience="Creators and teams",
        brand_style="Product-led premium",
        design_style="Modern product",
        token_preset="modern_default",
        typography_style="Geometric sans",
        image_style="Product UI",
        image_collections=("tech", "product", "creative"),
        product_types=("Plans", "Features", "Integrations"),
        forbidden_products=("Shoes", "Clothing"),
        default_pages=("Home", "Features", "Pricing", "About", "Contact"),
        default_sections=("Hero", "Features", "HowItWorks", "Pricing", "FAQ", "CTA"),
        hero_variant="HeroSaaS",
        navbar_variant="NavbarClassic",
        footer_variant="FooterMinimal",
        type_id_prefixes=("saas", "ai_product", "fintech", "software"),
        prompt_keywords=(
            "saas",
            "video generator",
            "ai video",
            "text to video",
            "ai tool",
            "ai app",
            "generator website",
            "software platform",
            "ai product",
            "ai generator",
            "image generator",
            "web app",
            "product landing",
        ),
    )
)

_reg(
    NicheSpec(
        id="generic",
        label="Marketing Site",
        industry="General",
        default_subcategory="Landing",
        target_audience="Visitors",
        brand_style="Clean modern",
        design_style="Modern",
        token_preset="modern_default",
        typography_style="Neutral sans",
        image_style="Abstract modern",
        image_collections=("modern",),
        product_types=(),
        forbidden_products=(),
        default_pages=("Home", "About", "Contact"),
        default_sections=("Hero", "Features", "CTA"),
        hero_variant="HeroCenter",
        navbar_variant="NavbarClassic",
        footer_variant="FooterMinimal",
        type_id_prefixes=("landing",),
        prompt_keywords=("landing page", "website"),
    )
)


def resolve_niche(website_type_id: str, prompt: str) -> NicheSpec:
    """Map analyzer type_id + prompt signals to a first-class niche.

    Footwear and clothing are disambiguated carefully so clothing prompts
    do not inherit the footwear niche (especially when shoes appear only under Avoid/Do NOT).
    """
    from app.generation.understanding.intent_guards import (
        explicitly_forbids_footwear,
        has_strong_clothing_intent,
        positive_clothing_intent,
        positive_footwear_intent,
        sanitize_prompt_for_matching,
    )

    type_id = (website_type_id or "").lower()
    lowered = (prompt or "").lower()
    cleaned = sanitize_prompt_for_matching(prompt)

    # Hard override: online bookstore / ebook intents beat landing-page ML misfires
    if _bookstore_intent(cleaned) or _bookstore_intent(lowered):
        return NICHES["bookstore"]

    # Hard override: AI video / generator product intents
    if (
        ("video" in cleaned and "generator" in cleaned)
        or "text to video" in cleaned
        or "ai video" in cleaned
        or ("ai" in cleaned and "generator" in cleaned and "website" in cleaned)
    ):
        return NICHES["saas"]

    # Hard override: luxury/fashion clothing brand that forbids shoes
    if has_strong_clothing_intent(lowered) or (
        explicitly_forbids_footwear(lowered) and positive_clothing_intent(lowered)
    ):
        if not positive_footwear_intent(prompt):
            return NICHES["clothing"]

    if explicitly_forbids_footwear(lowered) and any(k in type_id for k in ("shoe", "sneaker", "footwear")):
        if positive_clothing_intent(lowered) or "fashion" in cleaned or "clothing" in cleaned:
            return NICHES["clothing"]

    # Explicit specialty type ids first
    for niche_id in (
        "footwear",
        "clothing",
        "electronics",
        "saas",
        "blog",
        "coffee_shop",
        "restaurant",
        "medical",
        "real_estate",
        "salon",
        "hotel",
        "travel",
        "gym",
        "education",
        "law_firm",
        "finance",
        "bookstore",
        "furniture",
        "jewelry",
        "photography",
        "automobile",
        "wedding",
        "bakery",
        "agency",
        "portfolio",
    ):
        spec = NICHES[niche_id]
        if any(
            type_id == p or type_id.startswith(p + "_") or f"{p}_" in type_id or type_id.startswith(p)
            for p in spec.type_id_prefixes
        ):
            if niche_id == "footwear" and (
                explicitly_forbids_footwear(lowered)
                or has_strong_clothing_intent(lowered)
                or _clothing_without_footwear(cleaned)
            ):
                return NICHES["clothing"]
            if niche_id == "clothing" and _footwear_without_clothing(cleaned) and positive_footwear_intent(prompt):
                return NICHES["footwear"]
            return spec

    # Keyword scoring fallback on sanitized text
    scores: list[tuple[int, NicheSpec]] = []
    for spec in NICHES.values():
        if spec.id == "generic":
            continue
        score = sum(3 if kw in cleaned else 0 for kw in spec.prompt_keywords)
        score += sum(2 for kw in spec.prompt_keywords if len(kw.split()) > 1 and kw in cleaned)
        if score:
            scores.append((score, spec))
    if scores:
        scores.sort(key=lambda x: (-x[0], x[1].id))
        best = scores[0][1]
        if best.id == "footwear" and (
            explicitly_forbids_footwear(lowered) or has_strong_clothing_intent(lowered)
        ):
            return NICHES["clothing"]
        return best

    return NICHES["generic"]


def _bookstore_intent(lowered: str) -> bool:
    text = (lowered or "").lower()
    if any(
        p in text
        for p in (
            "bookstore",
            "book store",
            "book shop",
            "bookshop",
            "online bookstore",
            "ebook store",
            "pdf books",
        )
    ):
        return True
    has_books = "book" in text or "ebook" in text or "pdf" in text
    has_commerce = any(w in text for w in ("buy", "purchase", "shop", "store", "download", "read", "search"))
    return has_books and has_commerce and ("store" in text or "shop" in text or "buy" in text)


def _clothing_without_footwear(lowered: str) -> bool:
    clothing_hits = any(
        w in lowered for w in ("clothing", "apparel", "fashion", "boutique", "garment", "streetwear")
    )
    footwear_hits = any(
        w in lowered for w in ("shoe", "shoes", "sneaker", "sneakers", "footwear", "loafer", "loafers")
    )
    return clothing_hits and not footwear_hits


def _footwear_without_clothing(lowered: str) -> bool:
    clothing_hits = any(
        w in lowered for w in ("clothing", "apparel", "fashion", "boutique", "garment", "streetwear")
    )
    footwear_hits = any(
        w in lowered for w in ("shoe", "shoes", "sneaker", "sneakers", "footwear", "loafer", "loafers")
    )
    return footwear_hits and not clothing_hits


def invent_brand_name(existing: str, niche: NicheSpec) -> str:
    """Avoid catalog labels like 'Fashion Brand' as the public brand."""
    name = (existing or "").strip()
    # Strip instructional garbage that leaked into brand extraction
    name = re.split(
        r"\b(?:so|please|and give|create that|make|build|responsive|logo|website|sign)\b",
        name,
        maxsplit=1,
        flags=re.I,
    )[0].strip(" .,!?'\"-")
    parts = name.split()
    if len(parts) > 4:
        name = " ".join(parts[:4])
    # Reject long / instruction-like brands
    if len(name) > 40 or re.search(
        r"\b(create|responsive|website|give me|sign in|sign up|attractive|3d view|logo also)\b",
        name,
        flags=re.I,
    ):
        name = ""

    generic = {
        "",
        niche.label.lower(),
        niche.id.replace("_", " "),
        "fashion brand",
        "shoe store",
        "luxury shoe store",
        "sneaker store",
        "blog / magazine",
        "marketing landing page",
        "generated site",
        "new",
        "untitled",
        "clothing store",
        "electronics store",
        "creative portfolio",
        "portfolio",
        "personal brand",
        "studio north",
        "saas startup",
        "ai product",
        "marketing landing page",
    }
    if name.lower() in generic or name.lower() == niche.industry.lower():
        defaults = {
            "clothing": "Velora",
            "footwear": "Atelier Sole",
            "electronics": "NovaTech",
            "coffee_shop": "Brew House",
            "restaurant": "Harbor Table",
            "blog": "Insight Blog",
            "portfolio": "Alex Rivera",
            "agency": "Beacon Agency",
            "medical": "CarePoint Clinic",
            "salon": "Lume Salon",
            "hotel": "Aurelia Hotel",
            "gym": "Pulse Fitness",
            "bookstore": "Chapter & Co",
            "jewelry": "Atelier Lumina",
            "furniture": "Hearth & Form",
            "real_estate": "Summit Realty",
            "travel": "Wanderline",
            "education": "Brightpath Academy",
            "law_firm": "Ashford & Grey",
            "finance": "Ledger & Co",
            "photography": "Frame & Light",
            "automobile": "Apex Motors",
            "wedding": "Everafter Co",
            "bakery": "Crust & Crumb",
            "saas": "LumaClip",
            "generic": "Northstar",
        }
        return defaults.get(niche.id, "Northstar")
    # Catalog-ish labels ("Luxury Shoe Store", "Fashion Brand") → invent instead
    if re.search(r"\b(store|shop|brand|website|site)\b", name, flags=re.I) and len(name.split()) <= 4:
        if not re.search(r"[\"']", existing or ""):
            # Allow real names like "Hari Shoe Store" if first token looks proper-noun-ish
            first = name.split()[0]
            if first.lower() in {
                "luxury",
                "premium",
                "modern",
                "online",
                "best",
                "new",
                "my",
                "our",
                "the",
                "a",
                "an",
                "shoe",
                "sneaker",
                "fashion",
                "clothing",
                "cloth",
            }:
                defaults = {
                    "clothing": "Velora",
                    "footwear": "Atelier Sole",
                    "electronics": "NovaTech",
                    "saas": "LumaClip",
                    "generic": "Northstar",
                }
                return defaults.get(niche.id, "Northstar")
    return name
