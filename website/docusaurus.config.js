// @ts-check
import {themes as prismThemes} from 'prism-react-renderer';
import remarkMath from 'remark-math';
import rehypeKatex from 'rehype-katex';

/** @type {import('@docusaurus/types').Config} */
const config = {
  title: 'Semantic Event Protocol (SEP)',
  tagline: 'Event-driven distributed intelligence. Triggered by meaning, not time.',
  favicon: 'img/logo.svg',

  url: 'https://seprotocol.ai',
  baseUrl: '/',

  organizationName: 'nick-yudin',
  projectName: 'SEP', 

  onBrokenLinks: 'warn', 
  onBrokenMarkdownLinks: 'warn',

  i18n: {
    defaultLocale: 'en',
    locales: ['en'],
  },

  // --- ENABLE DIAGRAMS ---
  markdown: {
    mermaid: true,
  },
  themes: ['@docusaurus/theme-mermaid'],
  // -----------------------

  // --- ADD KATEX STYLESHEET ---
  stylesheets: [
    {
      href: 'https://cdn.jsdelivr.net/npm/katex@0.13.24/dist/katex.min.css',
      type: 'text/css',
      integrity: 'sha384-odtC+0UGzzFL/6PNoE8rX/SPcQDXBJ+uRepguP4QkPCm2LBxH3FA3y+fKSiJ+AmM',
      crossorigin: 'anonymous',
    },
  ],
  // ---------------------------

  presets: [
    [
      'classic',
      /** @type {import('@docusaurus/preset-classic').Options} */
      ({
        docs: {
          path: '../docs', 
          sidebarPath: './sidebars.js',
          routeBasePath: 'docs',
          // --- ADD MATH PLUGINS ---
          remarkPlugins: [remarkMath],
          rehypePlugins: [rehypeKatex],
          // ------------------------
        },
        blog: false,
        theme: {
          customCss: './src/css/custom.css',
        },
      }),
    ],
  ],

  themeConfig:
    /** @type {import('@docusaurus/preset-classic').ThemeConfig} */
    ({
      metadata: [
        {name: 'description', content: 'Semantic Event Protocol (SEP) — An experimental protocol for event-driven distributed intelligence. Demonstrated bandwidth compression and cross-architecture knowledge transfer in small-scale experiments.'},
        {name: 'keywords', content: 'semantic events, distributed AI, hyperdimensional computing, HDC, edge intelligence, event-driven computing, neural networks'},
        {property: 'og:title', content: 'Semantic Event Protocol (SEP)'},
        {property: 'og:description', content: 'An experimental protocol for event-driven distributed intelligence. Early evidence for bandwidth compression and cross-architecture transfer. Research by Nikolay Yudin.'},
        {property: 'og:type', content: 'website'},
        {property: 'og:url', content: 'https://seprotocol.ai'},
        {property: 'og:image', content: 'https://seprotocol.ai/img/docusaurus-social-card.jpg'},
        {property: 'twitter:card', content: 'summary_large_image'},
        {property: 'twitter:title', content: 'Semantic Event Protocol (SEP)'},
        {property: 'twitter:description', content: 'An experimental protocol for event-driven distributed intelligence. Triggered by meaning, not time.'},
        {property: 'twitter:image', content: 'https://seprotocol.ai/img/docusaurus-social-card.jpg'},
      ],
      colorMode: {
        defaultMode: 'dark',
        disableSwitch: false,
        respectPrefersColorScheme: false,
      },
      navbar: {
        title: 'SEP',
        logo: {
          alt: 'Semantic Event Protocol',
          src: 'img/logo.svg',
          srcDark: 'img/logo.svg', 
        },
        items: [
          {
            to: '/docs/manifesto',
            position: 'left',
            label: 'Manifesto',
          },
          {
            to: '/docs/specs/v1.0_current/spec-v1-final', 
            position: 'left',
            label: 'Specification',
          },
          {
            href: 'https://github.com/nick-yudin/SEP',
            label: 'GitHub',
            position: 'right',
          },
        ],
      },
      footer: {
        style: 'dark',
        links: [
          {
            title: 'Protocol',
            items: [
              { label: 'Manifesto', to: '/docs/manifesto' },
              { label: 'Specification', to: '/docs/specs/v1.0_current/spec-v1-final' }, 
            ],
          },
          {
            title: 'Community',
            items: [
              { label: 'Twitter', href: 'https://twitter.com/Nikolay_Yudin_' },
              { label: 'Email', href: 'mailto:1@seprotocol.ai' },
            ],
          },
        ],
        copyright: `Copyright © ${new Date().getFullYear()} Nikolay Yudin.`,
      },
      prism: {
        theme: prismThemes.github,
        darkTheme: prismThemes.dracula,
      },
    }),
};

export default config;