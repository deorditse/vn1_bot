## Для документов

```roomsql
create extension if not exists vector;

-- Create a table to store your administrative_law
create table if not exists administrative_law (
  id bigserial primary key,
  content text,
  metadata jsonb,
  embedding vector(1536)
);

-- Create a function to search for administrative_law
create or replace function match_administrative_law (
  query_embedding vector(1536), -- 1536 works for OpenAI embeddings, change if needed
  match_count int default null,
  filter jsonb DEFAULT '{}'
) returns table (
  id bigint,
  content text,
  metadata jsonb,
  similarity float
)
language plpgsql
as $$
#variable_conflict use_column
begin
  return query
  select
    id,
    content,
    metadata,
    1 - (administrative_law.embedding <=> query_embedding) as similarity
  from administrative_law
  where metadata @> filter
  order by administrative_law.embedding <=> query_embedding
  limit coalesce(match_count, 10);
end;
$$;
```

## Для продуктов

```roomsql
-- Create a function to search for administrative_law
create or replace function match_administrative_law (
  query_embedding vector(1536),
  match_count int default null,
  filter jsonb DEFAULT '{}'
) returns table (
  id bigint,
  content text,
  metadata jsonb,
  similarity float
)
language plpgsql
as $$
#variable_conflict use_column
begin
  return query
  select
    d.id,
    d.content,
    d.metadata,
    1 - (d.embedding <=> query_embedding) as similarity
  from administrative_law d
  where
    (filter->>'type' is null or d.metadata->>'type' = filter->>'type') and
    (filter->>'file_id' is null or d.metadata->>'file_id' = filter->>'file_id')
  order by d.embedding <=> query_embedding
  limit coalesce(match_count, 10);
end;
$$;
```
