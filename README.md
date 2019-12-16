# Sunday Show Scraper
This scraper pulls transcripts from Sunday shows websites, and flags statements made by politicians or pundits on the show that are checkable (factual assertions instead of opinions). It includes ABC, CNN, CBS, NBC and Fox News Sunday. The results are structured in a database, which is passed to the statements to the ClaimBuster, a natural language processing API. Then the results is organized in a spreadsheet wit information related to the shows and the ClaimBuster score. 
