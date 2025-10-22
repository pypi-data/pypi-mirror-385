domain = "text_utils"
description = "Utilities for text processing and manipulation"

[concept]
TextChunk = "A chunk of text that is part of a larger text"
SplitIdentifier = "Identifiers used to split large text into smaller parts"

[pipe.generate_split_identifiers]
type = "PipeLLM"
description = "Analyze large text and generate optimal split identifiers"
inputs = { text = "Text" }
output = "Text[]"
model = { model = "llm_for_large_codebase", temperature = 0.1 }
system_prompt = "You are an expert at analyzing text structure and finding optimal ways to split large texts into meaningful, coherent chunks."
prompt = """
Analyze the following text and identify the most meaningful structural delimiters for splitting it into logical chunks.

@text

You will receive git diff.
You need to identify delimiters that will separate the git diff between directories.
The diffs should be big enough to be unique.
"""

