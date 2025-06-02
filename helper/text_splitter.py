from langchain_text_splitters import TokenTextSplitter , RecursiveCharacterTextSplitter
from langchain_text_splitters.spacy import SpacyTextSplitter  # will need to install spacy and download the model

def text_splitter(text:str, type:int = 1, chunk_size:int=2000, chunk_overlap:int=150 ,separators:list[str] =["\n\n", "\n", " ", ""])->list[str]:
    """
    Splits the input text into chunks based on the specified type of text splitter.

    Parameters:
        text (str): The input text to be split.
        type (int, optional): The type of text splitter to use. 
            1 for RecursiveCharacterTextSplitter (default), 
            2 for TokenTextSplitter (More Efficient for a longer text), 
            any other value for SpacyTextSplitter (more Smarter).
        chunk_size (int, optional): The maximum size of each chunk (default is 4000).
        chunk_overlap (int, optional): The overlap between consecutive chunks (default is 200).
        separators (list[str], optional): List of separator strings used to split the text (default is ["\n\n", "\n", " ", ""]).
    
    Returns:
        list[str]: A list of text chunks.
    """
    splitter = None
    if type == 1:
         splitter = RecursiveCharacterTextSplitter(
                                chunk_size=chunk_size,
                                chunk_overlap=chunk_overlap, 
                                separators=separators
                            )
    elif type == 2:
         splitter = TokenTextSplitter()

    else: # will need to install spacy and download the model
        splitter = SpacyTextSplitter(chunk_size=chunk_size, chunk_overlap=chunk_overlap, separator = "\n",  pipeline = 'sentencizer') 
         
    
    return splitter.split_text(text)