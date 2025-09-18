from azure.search.documents import SearchClient 
from azure.identity import ManagedIdentityCredential 
import os 

searchendpoint = os.getenv("SEARCH_ENDPOINT") 
clientid = os.getenv("UAMI_CLIENT_ID") 
indexname = os.getenv("INDEX_NAME") 
credential = ManagedIdentityCredential(client_id=clientid) 

def _fetch_chunks(file_names: list[str]):
    """Helper: fetch chunks for a list of files from Azure Cognitive Search."""
    if not file_names:
        return []

    client = SearchClient(endpoint=searchendpoint, index_name=indexname, credential=credential)

    file_names_str = ",".join(file_names)  
    filter_expr = f"search.in(title, '{file_names_str}', ',')"

    results = client.search(
        search_text="*",
        select=["chunk"],
        filter=filter_expr,
        include_total_count=True
    )

    chunks = []
    for result in results:
        if "chunk" in result:
            chunks.append(result["chunk"])
    return chunks


def get_chunks(StudyFiles: list[str], AssignmentFiles: list[str]):
    """
    Fetch chunks separately for study files and assignment files in one call.
    """
    study_chunks = _fetch_chunks(StudyFiles) if StudyFiles else []
    assignment_chunks = _fetch_chunks(AssignmentFiles) if AssignmentFiles else []

    return {
        "StudyChunks": study_chunks,
        "AssignmentChunks": assignment_chunks
    }