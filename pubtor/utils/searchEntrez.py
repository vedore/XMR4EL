import os

from Bio import Entrez


class SearchDB():
    
    def __init__(self):
        Entrez.email = os.getenv("ENTREZ_EMAIL")
        
        self.search_record = None
        self.fetch_record=None
    
    def search(self, 
               db="pubmed", 
               term="cancer imunotherapy", 
               retstart=0,
               retmax=5,
               retmode="xml",
               ):
        
        handle = Entrez.esearch(
            db=db,
            term=term,
            retmax=retmax,
            retstart=retstart,
            retmode=retmode
        )
        self.search_record = Entrez.read(handle)
        
    def fetch(self,
              db="pubmed",
              ids=[""],
              retmode="xml"
              ):
        
        handle = Entrez.efetch(
            db=db,
            id=ids,
            retmode=retmode
        ) 
        
        self.fetch_record = Entrez.read(handle)
        
    def extractAbstracts(self):
        
        for article in self.fetch_record["PubmedArticle"]:
            
            article_data = article["MedlineCitation"]["Article"]
            title = article_data["ArticleTitle"]
            abstract = ""
            if "Abstract" in article_data:
                abstract = " ".join(article_data["Abstract"]["AbstractText"])

        return title, abstract
    
    
    
    
    
    