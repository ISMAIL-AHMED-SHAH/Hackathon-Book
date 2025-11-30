/**
 * Chapter Mapper Plugin for Docusaurus
 *
 * This plugin generates a static mapping from URL pathnames to chapter IDs
 * at build time. The mapping is used by the useChapterId hook to provide
 * chapter context for chatbot queries.
 *
 * @module chapter-mapper-plugin
 */

module.exports = function chapterMapperPlugin(context, options) {
  return {
    name: 'chapter-mapper-plugin',

    /**
     * Load content and generate chapter ID mapping
     * This runs during the build process to create a static JSON file
     */
    async contentLoaded({ actions }) {
      const { setGlobalData } = actions;

      /**
       * Chapter ID Mapping
       * Maps URL pathname to chapter ID for context-aware chatbot queries
       *
       * Format: { '/docs/path': 'ch-id', ... }
       *
       * NOTE: Paths should match the URL structure after baseUrl
       * For GitHub Pages with baseUrl='/hackathon-book/', paths are relative to that
       */
      const chapterMap = {
        // Landing page (no chapter context)
        '/docs/intro': null,

        // Module 1: ROS 2 Fundamentals
        '/docs/module-1-ros2/nodes': 'ch-ros2-nodes',
        '/docs/module-1-ros2/topics': 'ch-ros2-topics',
        '/docs/module-1-ros2/services': 'ch-ros2-services',
        '/docs/module-1-ros2/urdf': 'ch-ros2-urdf',

        // Module 2: Gazebo Simulation
        '/docs/module-2-gazebo/simulation-basics': 'ch-gazebo-basics',
        '/docs/module-2-gazebo/sensors': 'ch-gazebo-sensors',

        // Module 3: NVIDIA Isaac
        '/docs/module-3-isaac/isaac-sim': 'ch-isaac-sim',
        '/docs/module-3-isaac/isaac-ros': 'ch-isaac-ros',

        // Module 4: Vision-Language-Action
        '/docs/module-4-vla/voice-commands': 'ch-vla-voice',
        '/docs/module-4-vla/capstone': 'ch-vla-capstone',
      };

      // Store the chapter map as global data accessible to all components
      setGlobalData({ chapterMap });

      // Log the mapping for debugging
      console.log('[Chapter Mapper Plugin] Loaded chapter mappings:', Object.keys(chapterMap).length, 'chapters');
    },
  };
};
