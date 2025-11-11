# Component System Documentation

## Overview

This document describes the complete component system designed for a company website using Strapi v5. The system includes global components, shared reusable components, and dynamic zone components for flexible page building.

## Component Categories

### 1. Global Components
**Location**: `src/components/global/`

Used site-wide for consistent branding and navigation.

#### Header (`global.header`)
**Purpose**: Site-wide navigation and branding

**Fields**:
- `logo` (Media) - Required - Company logo
- `navigationLinks` (Component - repeatable) - Optional - Up to 10 navigation links
- `ctaButton` (Component) - Optional - Call-to-action button
- `showSearch` (Boolean) - Optional - Display search bar
- `sticky` (Boolean) - Optional - Sticky header on scroll

**Nesting**: Contains `shared.link` and `shared.button` components

**Responsive Behavior**:
- Desktop: Horizontal navigation with full menu
- Tablet: Condensed navigation
- Mobile: Hamburger menu with drawer navigation

**Accessibility**:
- ARIA labels for navigation
- Keyboard navigation support
- Focus indicators
- Skip to main content link

#### Footer (`global.footer`)
**Purpose**: Site-wide footer with links and company info

**Fields**:
- `logo` (Media) - Required - Company logo
- `copyrightText` (String) - Required - Max 200 chars
- `socialLinks` (Component - repeatable) - Optional - Up to 10 social links
- `sitemapLinks` (Component - repeatable) - Optional - Up to 20 links
- `newsletterSignup` (Boolean) - Optional - Show newsletter form
- `companyAddress` (Component) - Optional - Physical address

**Nesting**: Contains `shared.link` and `shared.address` components

**Responsive Behavior**:
- Desktop: Multi-column layout
- Tablet: 2-column layout
- Mobile: Single column, stacked layout

**Accessibility**:
- Landmark roles
- Proper heading hierarchy
- Keyboard accessible links

#### SEO (`global.seo`)
**Purpose**: SEO metadata for pages

**Fields**:
- `metaTitle` (String) - Required - 10-60 chars
- `metaDescription` (Text) - Required - 50-160 chars
- `ogImage` (Media) - Optional - Open Graph image
- `canonicalURL` (String) - Optional - Canonical URL
- `keywords` (String) - Optional - SEO keywords
- `structuredData` (JSON) - Optional - Schema.org structured data

**Usage**: Added to every page type for SEO optimization

**Accessibility**: Proper meta tags for screen readers and search engines

### 2. Shared Components
**Location**: `src/components/shared/`

Reusable building blocks used across different sections.

#### Link (`shared.link`)
**Purpose**: Consistent link styling across the site

**Fields**:
- `label` (String) - Required - Max 100 chars
- `url` (String) - Required - Link URL
- `icon` (Media) - Optional - Icon image
- `opensInNewTab` (Boolean) - Optional - Default: false

**Usage**: Navigation menus, footer links, inline links

**Accessibility**:
- Clear link text
- External link indicators
- ARIA labels when needed

#### Button (`shared.button`)
**Purpose**: Consistent button styling with variants

**Fields**:
- `text` (String) - Required - Max 50 chars
- `url` (String) - Required - Button URL
- `style` (Enum) - Required - primary | secondary | tertiary
- `size` (Enum) - Required - small | medium | large
- `icon` (Media) - Optional - Button icon

**Style Variants**:
- **Primary**: Main CTA, high contrast, bold
- **Secondary**: Alternative actions, less prominent
- **Tertiary**: Subtle actions, minimal styling

**Size Guide**:
- **Small**: 32px height, 12px padding
- **Medium**: 40px height, 16px padding
- **Large**: 48px height, 20px padding

**Responsive Behavior**:
- Desktop: Fixed sizes
- Mobile: May expand to full-width for primary buttons

**Accessibility**:
- Sufficient color contrast (WCAG AA)
- Touch target size minimum 44x44px
- Focus indicators

#### Address (`shared.address`)
**Purpose**: Physical address display

**Fields**:
- `streetNumber` (String) - Required
- `streetName` (String) - Required - Max 200 chars
- `city` (String) - Required - Max 100 chars
- `state` (String) - Required - Max 100 chars
- `country` (String) - Required - Max 100 chars
- `postalCode` (String) - Optional - Max 20 chars

**Usage**: Footer, contact pages, location pages

**Responsive Behavior**:
- Desktop: Single line or multi-line format
- Mobile: Multi-line format for readability

**Accessibility**:
- Address semantic markup
- Microdata for local business schema

### 3. Dynamic Zone Components (Sections)
**Location**: `src/components/sections/`

Flexible page sections for content editors.

#### Hero Section (`sections.hero-section`)
**Purpose**: Above-the-fold hero banner

**Required Fields**:
- `title` (String) - Max 100 chars
- `image` (Media) - Images or videos

**Optional Fields**:
- `subtitle` (Text) - Max 300 chars
- `ctaButtons` (Component - repeatable) - Up to 3 buttons
- `alignment` (Enum) - left | center | right - Default: center
- `height` (Enum) - small | medium | large | fullscreen - Default: large
- `overlay` (Boolean) - Default: true
- `overlayOpacity` (Integer) - 0-100 - Default: 50

**Nesting**: Contains up to 3 `shared.button` components

**Size Variants**:
- **Small**: 300px height
- **Medium**: 500px height
- **Large**: 700px height
- **Fullscreen**: 100vh

**Responsive Behavior**:
- Desktop: Full-width with configurable height
- Tablet: Reduce height by 20%
- Mobile: Minimum 400px, stack text above image

**Accessibility**:
- Alt text for images
- Sufficient contrast for text over images
- Semantic heading hierarchy

**When to Use**:
- Homepage hero
- Landing page headers
- Campaign pages

**Alternatives**:
- For simpler pages, use text-only sections
- For product pages, use feature grids

#### Testimonial (`sections.testimonial`)
**Purpose**: Customer reviews and social proof

**Required Fields**:
- `quote` (Text) - Max 500 chars
- `authorName` (String) - Max 100 chars

**Optional Fields**:
- `authorRole` (String) - Max 100 chars
- `authorPhoto` (Media) - Image
- `companyLogo` (Media) - Image
- `rating` (Integer) - 1-5 stars
- `featured` (Boolean) - Highlight this testimonial

**Responsive Behavior**:
- Desktop: Card layout with photo
- Mobile: Stacked layout, smaller photos

**Accessibility**:
- Quote semantic markup
- Alt text for photos and logos
- Rating represented with text and stars

**When to Use**:
- Social proof sections
- Case study pages
- Product pages

#### FAQ Block (`sections.faq-block`)
**Purpose**: Frequently asked questions section

**Required Fields**:
- `title` (String) - Max 100 chars
- `faqs` (Component - repeatable) - Minimum 1 FAQ

**Optional Fields**:
- `subtitle` (Text) - Max 300 chars
- `displayStyle` (Enum) - accordion | grid | list - Default: accordion
- `showSearch` (Boolean) - Default: false

**Nesting**: Contains multiple `sections.faq-item` components

**Display Styles**:
- **Accordion**: Expandable Q&A (best for many FAQs)
- **Grid**: Side-by-side cards (good for 4-6 FAQs)
- **List**: Simple stacked format (best for few FAQs)

**Responsive Behavior**:
- Desktop: Chosen display style
- Mobile: All styles become accordion for easier navigation

**Accessibility**:
- ARIA accordion pattern
- Keyboard navigation
- Focus management

**When to Use**:
- Support pages
- Product pages
- Landing pages with common questions

#### FAQ Item (`sections.faq-item`)
**Purpose**: Individual FAQ question and answer

**Required Fields**:
- `question` (String) - Max 200 chars
- `answer` (Richtext) - Supports formatting, links, lists

**Optional Fields**:
- `category` (String) - Max 50 chars - For filtering
- `order` (Integer) - Display order

**Usage**: Nested within `faq-block` component

#### Feature Grid (`sections.feature-grid`)
**Purpose**: Display products, services, or features

**Required Fields**:
- `title` (String) - Max 100 chars
- `features` (Component - repeatable) - Minimum 1 feature

**Optional Fields**:
- `subtitle` (Text) - Max 300 chars
- `displayStyle` (Enum) - grid | list | carousel - Default: grid
- `columns` (Enum) - 2 | 3 | 4 - Default: 3
- `backgroundColor` (Enum) - white | light | dark | primary

**Nesting**: Contains multiple `sections.feature-item` components

**Display Styles**:
- **Grid**: Responsive grid layout
- **List**: Vertical list with alternating layouts
- **Carousel**: Swipeable carousel (mobile-friendly)

**Column Behavior**:
- **2 columns**: Best for detailed features (4-6 items)
- **3 columns**: Balanced layout (6-9 items)
- **4 columns**: Compact display (8+ items)

**Responsive Behavior**:
- Desktop: Chosen column count
- Tablet: Reduce to 2 columns
- Mobile: Single column stack

**Accessibility**:
- Grid semantic markup
- Keyboard navigation for carousels
- Touch-friendly swipe gestures

**When to Use**:
- Features overview
- Services listing
- Benefits section

**Alternatives**:
- For detailed comparisons, use a table
- For single featured item, use hero section

#### Feature Item (`sections.feature-item`)
**Purpose**: Individual feature or service

**Required Fields**:
- `title` (String) - Max 100 chars
- `description` (Text) - Max 300 chars

**Optional Fields**:
- `icon` (Media) - Small icon (recommended: SVG, 64x64)
- `image` (Media) - Larger image (recommended: 16:9 ratio)
- `link` (Component) - Learn more link

**Nesting**: Can contain one `shared.link` component

**Usage**: Nested within `feature-grid` component

**Note**: Use either `icon` or `image`, not both. Icon for simple graphics, image for photos.

## Component Usage Guidelines

### Spacing and Layout

**Section Spacing**:
- Between major sections: 80px (desktop), 48px (mobile)
- Within sections: 40px (desktop), 24px (mobile)
- Between components: 24px (desktop), 16px (mobile)

**Container Widths**:
- Content container: 1200px max-width
- Hero sections: Full width
- Text sections: 800px max-width for readability

### Color System

**Primary Colors**:
- Primary: #0066CC (Brand Blue)
- Secondary: #00CC66 (Accent Green)
- Tertiary: #666666 (Gray)

**Background Options**:
- White: #FFFFFF
- Light: #F5F5F5
- Dark: #1A1A1A
- Primary: #0066CC

**Contrast Ratios**:
- All text meets WCAG AA (4.5:1 minimum)
- Large text meets WCAG AAA (7:1)
- Interactive elements: Clearly distinguishable

### Typography

**Heading Hierarchy**:
- H1: Hero titles (48px desktop, 32px mobile)
- H2: Section titles (36px desktop, 28px mobile)
- H3: Subsection titles (24px desktop, 20px mobile)
- H4: Component titles (20px desktop, 18px mobile)

**Body Text**:
- Regular: 16px (desktop), 14px (mobile)
- Large: 18px (desktop), 16px (mobile)
- Small: 14px (desktop), 12px (mobile)

### Accessibility Requirements

**Must Have**:
- Semantic HTML5 elements
- ARIA labels where needed
- Keyboard navigation
- Focus indicators
- Alt text for images
- Color contrast compliance (WCAG AA)
- Touch targets minimum 44x44px
- Screen reader compatibility

**Testing**:
- Test with keyboard only
- Test with screen reader
- Test color contrast
- Test with browser zoom at 200%

## Workflow States

### Content Workflow

**States**:
1. **Draft** - Being created, not visible
   - Color: Gray (#999999)
   - Icon: Edit
   - Actions: Edit, Submit for Review, Delete

2. **In Review** - Submitted for editorial review
   - Color: Orange (#FF9900)
   - Icon: Eye
   - Actions: Edit, Approve, Reject, Comment

3. **Scheduled** - Set to publish at future date
   - Color: Blue (#0066CC)
   - Icon: Clock
   - Actions: Edit Schedule, Publish Now, Cancel

4. **Published** - Live and visible
   - Color: Green (#00CC66)
   - Icon: Check
   - Actions: Edit, Unpublish, Archive

5. **Archived** - No longer published
   - Color: Gray (#666666)
   - Icon: Archive
   - Actions: Restore, Delete Permanently

### Visual Indicators

**List View Badges**:
```
┌─────────────────────────────┐
│ [●] Draft     Edit ▸       │
│ [◐] In Review    Review ▸   │
│ [◷] Scheduled   Schedule ▸  │
│ [✓] Published   View ▸      │
│ [▢] Archived    Restore ▸   │
└─────────────────────────────┘
```

**Editor Header**:
- Shows current state prominently
- Displays available actions as buttons
- Shows last edited time and author
- Preview button for draft content

## Implementation Notes

### Dynamic Zones

Create a `Page` collection type with a dynamic zone that can include all section components:

```json
{
  "kind": "collectionType",
  "attributes": {
    "title": { "type": "string" },
    "slug": { "type": "uid", "targetField": "title" },
    "seo": { "type": "component", "component": "global.seo" },
    "sections": {
      "type": "dynamiczone",
      "components": [
        "sections.hero-section",
        "sections.testimonial",
        "sections.faq-block",
        "sections.feature-grid"
      ]
    }
  }
}
```

### AI Integration

Components can be enhanced with AI:
- Generate SEO meta descriptions
- Create FAQ answers
- Write feature descriptions
- Enhance testimonial formatting
- Suggest component ordering

See `AI_INTEGRATION_README.md` for details.

### Performance Optimization

**Images**:
- Use Strapi's image optimization
- Provide multiple sizes for responsive images
- Use lazy loading for below-fold images
- Compress images before upload

**Loading**:
- Lazy load sections below the fold
- Preload critical assets
- Use skeleton screens for loading states

## Testing Checklist

### For Each Component:
- [ ] Displays correctly with all required fields
- [ ] Degrades gracefully with only required fields
- [ ] Responsive on all breakpoints
- [ ] Keyboard accessible
- [ ] Screen reader compatible
- [ ] Color contrast passes WCAG AA
- [ ] Touch targets are adequate
- [ ] Images have alt text
- [ ] Links are descriptive
- [ ] Forms are labeled properly

### For Page Builds:
- [ ] Logical content flow
- [ ] Proper heading hierarchy
- [ ] Consistent spacing
- [ ] No color-only indicators
- [ ] Fast page load
- [ ] Works with JS disabled (graceful degradation)
- [ ] Mobile-friendly navigation
- [ ] Print styles (optional)

## Resources

- [Strapi Components Documentation](https://docs.strapi.io/dev-docs/backend-customization/models#components)
- [Dynamic Zones Documentation](https://docs.strapi.io/dev-docs/backend-customization/models#dynamic-zones)
- [WCAG 2.1 Guidelines](https://www.w3.org/WAI/WCAG21/quickref/)
- [Responsive Design Patterns](https://responsivedesign.is/patterns/)

## Next Steps

1. Start Strapi and verify components load correctly
2. Create sample pages using the dynamic zone
3. Test responsive behavior at all breakpoints
4. Implement frontend rendering
5. Add AI enhancements for content generation
6. Set up workflow states in Strapi admin
7. Create editor documentation
8. Train content team on component usage
