# Fixes Required for Media Scraper

## UI/Layout Fixes

### 1. Navigation Bar Order
- [x] Reorder elements: Credits (clickable to subscription) -> Downloads -> Theme -> Sign In/User
- [x] Fix theme button overlap - ensure proper spacing
- [x] Remove absolute positioning from theme button

### 2. Sources Display
- [x] For locked sources: show ONLY lock icon (no checkbox)
- [x] For unlocked sources: show checkbox
- [x] Clean up the sources page layout
- [x] Sources should be in a scrollable container

### 3. Search Section
- [x] Move "Start Search" button to top row next to search query
- [x] Put search options in second row
- [x] Make sources section scrollable

### 4. Asset Display
- [x] Fix image URLs to use `/api/media/{asset.id}`
- [x] Fix thumbnail URLs to use `/api/media/{asset.id}/thumbnail`
- [x] Add video hover preview functionality
- [x] Fix download URLs to use `/api/media/{asset.id}?download=true`

### 5. Subscription/Billing
- [x] Add proper heading to subscription section
- [x] Add loading state for subscription content
- [ ] Ensure subscription route is properly integrated

### 6. AI Assistant
- [ ] Add API key modal
- [ ] Update toggleApiKeyModal function to use Bootstrap modal
- [ ] Add saveApiKey function
- [ ] Store API key in localStorage

### 7. Developer Mode
- [x] Fix user credits display in navigation (use user_info.user.credits)
- [x] Ensure admin check uses correct property

### 8. Downloads
- [x] Fix download functionality
- [x] Add proper download statistics
- [x] Implement download management

## Backend Integration Points

1. Ensure `/api/media/{id}` endpoint serves images/videos
2. Ensure `/api/media/{id}/thumbnail` endpoint serves thumbnails
3. Ensure `/subscription/plans` endpoint returns subscription HTML
4. Ensure AI assistant endpoint accepts user's API key

## Code Quality
- Remove orphaned code
- Clean up CSS
- Fix any remaining issues with downloads 