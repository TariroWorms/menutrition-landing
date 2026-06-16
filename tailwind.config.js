/**
 * Tailwind build config for the MeNutrition landing page.
 *
 * The site's CSS is PRE-COMPILED into an inline <style id="tw"> block in
 * index.html — there is NO runtime CDN (the old cdn.tailwindcss.com script
 * caused a flash of unstyled content / flicker on load). See README →
 * "Стили (Tailwind предкомпилирован)" for how to regenerate after you add or
 * change utility classes in the HTML.
 *
 * Brand tokens live here (previously in the inline `tailwind.config` script).
 */
module.exports = {
  content: ['./index.html', './privacy/index.html'],
  theme: {
    extend: {
      fontFamily: {
        sans: ['Manrope', 'system-ui', 'sans-serif'],
        serif: ['Fraunces', 'Georgia', 'serif'],
      },
      colors: {
        cream:  '#F2EFE8',
        paper:  '#F8F6F1',
        char:   '#272320',
        ink:    '#241F1B',
        // brand: teal #358076 · gold #CF9A3F
        teal:   { 400: '#4A9A8C', 500: '#358076', 600: '#2A6A5F', 700: '#1F5046' },
        gold:   { 400: '#E0B255', 500: '#CF9A3F', 600: '#B5852F' },
      },
      boxShadow: {
        soft: '0 14px 44px -16px rgba(39,35,32,0.22)',
        card: '0 26px 70px -28px rgba(39,35,32,0.40)',
      },
    },
  },
}
