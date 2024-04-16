const lightCodeTheme = require('prism-react-renderer/themes/github');
const darkCodeTheme = require('prism-react-renderer/themes/dracula');

(module.exports = {
    title: 'Waii Pythont SDK',
    tagline: 'World most accurate text-2-sql API',
    url: 'https://python.docs.waii.ai',
    baseUrl: '/',
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
		    type: 'dropdown',
		    label: 'API Language',
		    position: 'right',
		    items: [
			{
			    label: 'TypeScript/JavaScript',
			    to: 'https://js.doc.waii.ai',
			},
			{
			    label: 'Python',
			    to: 'https://python.doc.waii.ai', // URL to the Python docs
			},
			{
			    label: 'CLI',
			    to: 'https://rest.doc.waii.ai', // URL to the REST docs
			},
		    ],
		},
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
