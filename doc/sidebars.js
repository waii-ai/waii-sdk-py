module.exports = {
    docs: [
        {
            type: 'doc',
            id: 'intro',
            label: 'Introduction',
        },
        {
            type: 'doc',
            id: 'install',
            label: 'Installation'
        },
        {
            type: 'doc',
            id: 'getting-started',
            label: 'Getting Started',
        },
        {
            type: 'category',
            label: 'Notebooks',
            items: [
                'colab',
                'notebook',
            ],
        },
        {
            type: 'category',
            label: 'Modules',
            items: [
                {
                    type: 'doc',
                    id: 'sql-query-module',
                    label: 'SQL Query',
                },
                {
                    type: 'doc',
                    id: 'semantic-context-module',
                    label: 'Semantic Context',
                },
                {
                    type: 'doc',
                    id: 'database-module',
                    label: 'Database',
                },
                {
                    type: 'doc',
                    id: 'history-module',
                    label: 'History',
                },
                {
                    type: "doc",
                    id: "chart-module",
                    label: "Chart"
                },
				{
					type: 'doc',
					id: 'chat-module',
					label: 'Chat'
				},
				{
					type: 'doc',
					id: 'user-module',
					label: 'User'
				},
				{
					type: 'doc',
					id: 'multi-tenant-client-module',
					label: 'Multi-tenant Waii SDK Client'
				},
                {
                    type: 'doc',
                    id: 'access-rule-module',
                    label: 'Row-level Access Rule'
                }
            ],
        },
    ],
};
