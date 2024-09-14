# LLM Budgeting experiemnt

This is a one shot budgeting app idea using some AI.

It works (badly) with unoptimised api calls and very little (if any) error checking!
It takes a csv with the following values:

`Date          Type      Description     Change`

`DD-MMM-YYYY (ignored)   Proton payment  -0.5`

I ran this with llama3.1 8b (as it was the only one that would run on my computer).
It might work better with some better prompting or more powerful LLMS. Feel free to fork or PR or whatever.
