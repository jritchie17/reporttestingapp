# Consolidate UNION Blocks

The `src/analyzer/arreserve.sql` query repeats similar UNION blocks for
"Facility" and "Anesthesia" sections. These should be consolidated using
`CASE` expressions to reduce duplication. See the discussion in GitHub issue #3
for more background.
