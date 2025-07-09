let lightCodeTheme, darkCodeTheme;
try {
  const {themes} = require('prism-react-renderer');
  lightCodeTheme = themes.github;
  darkCodeTheme = themes.dracula;
} catch (e) {
  lightCodeTheme = {
    plain: {
      color: "#393A34",
      backgroundColor: "#f6f8fa"
    },
    styles: []
  };
  darkCodeTheme = {
    plain: {
      color: "#F8F8F2",
      backgroundColor: "#282A36"
    },
    styles: []
  };
}

(module.exports = {
	title: 'Waii Python SDK',
	tagline: 'World most accurate text-2-sql API',
	url: 'https://doc.waii.ai',
	baseUrl: '/python/',
	onBrokenLinks: 'throw',
	onBrokenMarkdownLinks: 'warn',
	favicon: 'img/favicon.ico',
	organizationName: 'waii',
	projectName: 'waii-sdk-py',

	presets: [
		[
			'@docusaurus/preset-classic',
			({
				docs: {
					sidebarPath: require.resolve('./sidebars.js'),
					editUrl: 'https://github.com/waii-ai/waii-sdk-js/tree/main/docs/docs-waii-sdk-py',
				},
				theme: {
					customCss: require.resolve('./src/css/custom.css'),
				},
			}),
		],
	],

	themeConfig:
		({
			navbar: {
				title: 'Waii Python SDK',
				logo: {
					alt: 'Waii Logo',
					src: 'img/logo.png',
				},
				items: [
					{
						label: 'TypeScript/JavaScript SDK',
						href: 'https://doc.waii.ai/js/docs/intro',
					},
					{
						label: 'Python SDK',
						href: 'https://doc.waii.ai/python/docs/intro',
					},
					{
						label: 'Java SDK',
						href: 'https://doc.waii.ai/java/docs/intro',
					},
					{
						label: 'CLI',
						href: 'https://doc.waii.ai/cli/docs/intro',
					},
					{
						label: 'Deployment & Architecture',
						href: 'https://doc.waii.ai/deployment/docs/intro',
					}
				],
			},
			footer: {
				style: 'dark',
				links: [
					{
						title: 'Company',
						items: [
							{
								label: 'Website',
								href: 'https://waii.ai/',
							},
							{
								label: 'LinkedIn',
								href: 'https://www.linkedin.com/company/96891121/',
							}
						],
					},
					{
						title: 'Community',
						items: [
							{
								label: 'Slack',
								href: 'https://join.slack.com/t/waiicommunity/shared_invite/zt-1xib44mr5-LBa7ub9t_vGvo66QtbUUpg',
							}
						],
					},
					{
						title: 'More',
						items: [
							{
								label: 'GitHub',
								href: 'https://github.com/waii-ai/waii-sdk-py',
							},
						],
					},
				],
				copyright: `Copyright © ${new Date().getFullYear()} Waii, Inc.`,
			},
			prism: {
				theme: lightCodeTheme,
				darkTheme: darkCodeTheme,
			},
		}),
});
