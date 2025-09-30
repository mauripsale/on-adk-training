import logging

############################################################

####    FAKE FUNCTION TO RETRIEVE DATA FROM VECTOR DB   ####

############################################################

def get_context_chunks(query: str, language:str) -> str:
    """
    Retrieves relevant document chunks based on a user query.
    Always use this tool to answer a new query.
    Avoid calling it only if the previous retrieved information is enough to answer

    Args:
        query: The user's original question or query needing context.
        language: The language of the query.
        
    Returns:
        A string containing concatenated relevant document chunks, separated by '---'.
        Returns an empty string or error message if no relevant context is found or an error occurs.
    """

    logging.info(f"Tool 'retrieve_context_for_query' called with query='{query}'")
    logging.info(language)

    results = [
        {
            "pdf_uri":"example.pdf",
            "full_content":"testFILE"
        },
        {
            "pdf_uri":"example2.pdf",
            "full_content":"testFILE"
        }
    ]
    if not results:
        return []
    files = []
    context = ""
    for el in results:
        if el["pdf_uri"] not in files:
            files.append(el["pdf_uri"])
            context+=f"""

## DOCUMENT LINK: 
# {el["pdf_uri"]}

### CONTENT:
{el["full_content"]}
"""

    return context