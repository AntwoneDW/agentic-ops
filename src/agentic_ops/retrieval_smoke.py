from dotenv import load_dotenv

from agentic_ops.retrieval import search_runbook


load_dotenv()
query = (
    "Checkout instances are failing readiness because PAYMENT_API_URL "
    "is missing. Should we restart the service?"
)

documents = search_runbook(query)


print("QUERY")
print(query)

print()
print("RETRIEVED RUNBOOK SECTIONS")

for document in documents:
    print()
    print(document.page_content)
    print("metadata:", document.metadata)