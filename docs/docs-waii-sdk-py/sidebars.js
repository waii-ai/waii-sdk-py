module.exports = {
    docs: [
	{
	    type: 'doc',
	    id: 'intro',
	    label: 'Introduction',
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
	    ],
	},
    ],
};
