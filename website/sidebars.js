/**
 * Creating a sidebar enables you to:
 - create an ordered group of docs
 - render a sidebar for each doc of that group
 - provide next/previous navigation

 The sidebars can be generated from the filesystem, or explicitly defined here.
 */

// @ts-check

/** @type {import('@docusaurus/plugin-content-docs').SidebarsConfig} */
const sidebars = {
  // We define the sidebar manually to control the exact order and hierarchy
  docsSidebar: [
    {
      type: 'category',
      label: 'Level 0: Philosophy',
      collapsed: false,
      items: [
        '00_intro/manifesto',
        // '00_intro/quick-start', // Uncomment if this file exists
      ],
    },
    {
      type: 'category',
      label: 'Level 1: Specifications',
      collapsed: false,
      items: [
        // Path relative to the "docs" folder, without extension
        '01_specs/v1.0_current/resonance_unified_spec',
      ],
    },
  ],
};

module.exports = sidebars;