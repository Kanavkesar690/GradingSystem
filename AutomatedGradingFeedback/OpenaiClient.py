from dotenv import load_dotenv
from autogen_ext.models.openai import AzureOpenAIChatCompletionClient
from azure.identity import ManagedIdentityCredential
import os

load_dotenv()

Endpoint = os.getenv('AZURE_OPENAI_ENDPOINT')
Api_version = os.getenv('AZURE_OPENAI_VERSION')
Openai_model_name=os.getenv('AZURE_OPENAI_MODEL_NAME')
Openai_deployment_name=os.getenv('AZURE_OPENAI_DEPLOYMENT_NAME')

UAMI_CLIENT_ID=os.getenv('UAMI_CLIENT_ID')
credential = ManagedIdentityCredential(client_id=UAMI_CLIENT_ID)
def provider():
    return credential.get_token("https://cognitiveservices.azure.com/.default").token  
def client():
    return AzureOpenAIChatCompletionClient(
        azure_deployment=Openai_deployment_name,
        model=Openai_model_name,
        api_version=Api_version,
        azure_endpoint=Endpoint,
        temperature=0.3, 
        azure_ad_token_provider=provider,
        model_capabilities={"vision": True, "function_calling": True, "json_output": True, "streaming": True}
    )