import sys
from langchain_core.documents import Document
from langchain_community.vectorstores import FAISS
from langchain_openai.embeddings import OpenAIEmbeddings

def main():
    if len(sys.argv) != 2:
        print("You must specify the filepath\npython scripts/create_db.py policies_filepath")
        sys.exit(1)
    policy_filepath = sys.argv[1]

    with open(policy_filepath, "r") as f:
        policies = f.readlines()
    # remove \n at the end due to readlines
    policies = [policy[:-2] for policy in policies]

    documents = [Document(page_content=txt,
                          metadata={
                      "source": policy_filepath
                 })
                 for txt in policies]

    openai_embeds = OpenAIEmbeddings()
    vec_db = FAISS.from_documents(documents, openai_embeds)
    vec_db.save_local("data/policy_index")

if __name__ == "__main__":
    main()
