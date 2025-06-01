# CSS Architecture

## Directory Structure

- `base/` - Foundational styles (reset, variables, typography)
- `components/` - Component-specific styles
- `utilities/` - Utility classes and helpers
- `themes/` - Theme variations and responsive styles

## Naming Conventions

- Use BEM methodology for class names
- Component classes: `.component-name`
- Modifier classes: `.component-name--modifier`
- Utility classes: `.u-utility-name`

## CSS Custom Properties

All styling uses CSS custom properties defined in `base/variables.css`.
This enables runtime theme switching and consistent design system.
