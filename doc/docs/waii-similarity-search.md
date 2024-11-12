---
id: waii-similarity-search
title: Waii Similarity Search
---

## Waii Similarity Search

A similarity search index is defined over a column. The column values and any additional meanings for the values will be ingested into a embedding storage, 
and these values can be used during query generation. See the database documentation for more details.


`waii_similarity_search` is a virtual user defined table function (UDTF) defined within the Waii query generation engine. 
This function conducts an embedding search over the similarity search index of a column and chooses the best values for a query.
Waii will use this function during query generation if it can't find the best column value to use or if the query requires a similarity search over certain phrases.


When running the query through Waii, this UDTF will be expanded into a `Values` clause with the chosen column values. 
This column value selection behavior can be customized with the following similarity search index properties:

- `enable_llm_rerank`: Enable extra LLM reranking step to pick the best values to use within the query. Default true 

The following args only apply if enable_llm_rerank is set False
- `similarity_score_threshold`: Only use results with an embedding match above a certain amount
- `max_matched_values`: The max match values from embedding match
- `min_matched_values`: The minimum matched values from embedding match.


`waii_similarity_search` accepts the following arguments:
- `column`: The column to conduct similarity search over. This column must have a similarity search index
- `phrase`: The phrase to do similarity search with
- `limit`: Optional arg. Limits the number of matched results, this will be the min of `min_matched_values` and `limit` if both are specified

`waii_similarity_search` outputs the following columns:
- `val`: The value of the column that passes the similarity search
- `score`: The similarity score for the row

#### enable_llm_rerank
This is primary defining behavior for a similarity search index. The default setting is true, this is best for categorical columns. When waii_similarity_search is used, the LLM will pick the best of the categorical values to insert into the query based on the lookup phrase used. 

When enable_llm_rerank is false, waii_similarity_search will skip the LLM rerank step. Instead, all of the values that pass the embedding match will be used. This embedding match operation will respect the properties of the similarity search index.

### Examples

#### Similarity Search Index with LLM Rerank

Given 
- table `brand` with columns: brand_name, brand_id
- table `store` with columns: brand_id, number_of_employees
- similarity search index on the brand_name column with `enable_llm_rerank` True

For the user ask, "How many employees work at a Kohls"

```sql
select sum(number_of_employees)
from brand
join table(waii_similarity_search(brand_name, 'kohls', 1)) as matched_brand(val, score)
on brand.brand_name = matched_stores.val
join store on brand.brand_id = store.brand_id
```

During query generation, if Waii does not have access to the best brand_name column to use, it may make the decision to use waii_similarity_search to pick the best value instead. 
With categorical columns, limit 1 will often be used with the similarity search function to pick the best value from the column for the lookup phrase: 'Kohls'

When running this query, Waii will look through the values of brand_id and pick the best value to insert into the query. waii_similarity_search will be replaced with a `Values` clause with this value.


#### Similarity Search Index without LLM Rerank

Given 
- table `documents` with columns: document_id, summary, title
- similarity search index on the document_id column with summary as an additional meaning with `enable_llm_rerank` False

The similarity search index will identify the document_id values with the summaries that match the phrase. By disabling `enable_llm_rerank` we want to use this index to do similarity search over the document corpus.

For the user ask, "Which documents relate to the fall of Rome"

```sql
select title
from documents
join table(waii_similarity_search(document_id, 'fall of Rome')) as matched_documents(val, score)
on document_id = matched_documents.val
```

Waii will use waii_similarity_search to find the documents which best match the subject: fall of Rome. 
The similarity search index is set up with summary as an additional meaning for each document_id, this will be used for the embedding match.
waii_similarity_search will return all matched documents, obeying the similarity search index properties described above.