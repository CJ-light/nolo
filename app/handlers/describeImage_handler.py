from openai import OpenAI
from handlers.tkn_handler import NoloToken
import sys

class ImageDescription:
    def __init__(self) -> None:
        #Use the NoloToken to get the OpenAIKey that you need to send prompts
        self.tkn = NoloToken()
        
        self.client = OpenAI(
            api_key=NoloToken().OpenAIKey
        )
        
        #pageNumbers :: store the page number where that description comes from
        #descriptions :: Stores all the descriptions of images recieved from OpenAI
        #tokensUsed :: Stores a breakdown of the tokens used for each query sent
        self.response = {
            'pageNumbers' : [],
            'descriptions' : [],
            'tokensUsed' : []
        }
        
        #Store the prompts in the different languages we want the response to be made in.
        self.prompts = {
            "es" : {
                "system": u'Eres una maestra para estudiantes de 5 a 12 años.',
                "user": u'Soy un estudiante entre 5 a 12 años, describeme los dibujos de esta pagina de este cuento que estoy leyendo'
            },
            "en" : {
                "system" : "You're a teacher for students aged 5 to 12 years.",
                "user" : "I'm a student from 5 to 12 years old, describe to me the drawings of this page from a story I'm reading"
            }
        }
    
    #openAIDescription :: This is a funciton that makes a query to ChatGPT Vision to get the description of an image
    #Input :: 
    #   imageUrl(str) :: This is the Url of the image we want a description of
    #   pageNumber(int) :: This is the page number where this image comes from
    #   language(str) :: This is the language we want the query to be made with
    #   hasImage(bool) :: This flag lets us know if an iamge was detected in that page, to save money, we can use this flag to prevent having to do queries with pages that only have text
    #       For now, until we find a way to detect if a page has an image beforehand, lets assume that this is always true
    #Output ::
    #   This function will put the description, page number and the amont of tokens used for this query into the self.response dictionary
    def openAIDescription(self, imageUrl, pageNumber, language, hasImage = True) -> str:
       
        #Check if the page was detected with an image
        if (hasImage == False or language not in self.prompts):
            return("Didn't make query: This page doesn't have an image")
        
        #Check if the language selected is one of the options for making queries
        if language not in self.prompts:
            return("Didn't make query: %s is not a language defined in the self.prompts dictionary inside the %s script" % (language, sys.argv[0]))
        
        #Create and send the prompts that you want to send to OpenAI
        response = self.client.chat.completions.create(
            model="gpt-4-vision-preview",
            messages=[
                #Context of query
                {
                    "role": "system",
                    "content": self.prompts[language]["system"]},
                
                #Prompt for query
                {
                    "role": "user",
                    "content": [
                        {"type": "text", "text": self.prompts[language]['user']},
                        {
                            "type": "image_url",
                            "image_url": {
                                "url": imageUrl,
                            },
                        },
                    ],
                }
            ],
            max_tokens = 300,
        )
        self.response['pageNumbers'].append(int(pageNumber))
        self.response["descriptions"].append(response.choices[0].message.content)
        self.response["tokensUsed"].append(response.usage)
        
        return("Completed description")
        
    #responseOutput :: Function that returns the list of page numbers, descriptions and tokens used and then delete them from this object
    #Input :: No input
    #Output :: Return the page numbers (list int), image descriptions (list string), and tokens used for each page (list string) 
    def responseOutput(self) -> ([int],[str],[str]):
        pageNumbers, descriptions, tokensUsed = self.response['pageNumbers'], self.response['descriptions'], self.response['tokensUsed']
        self.response['pageNumbers'], self.response['descriptions'], self.response['tokensUsed'] = [], [], []
        return (pageNumbers, descriptions, tokensUsed)

    
#Examples on how to use ::
# temp = ImageDescription()
# temp.openAIDescription("https://img.freepik.com/premium-vector/cool-shark_26838-85.jpg?w=740", 2, "es")
# temp.responseOutput()