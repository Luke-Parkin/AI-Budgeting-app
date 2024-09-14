import csv
import datetime
from decimal import Decimal
from enum import Enum

from tqdm import tqdm
import requests
import json


class Categories(Enum):
    SUPERMARKET = (0, "british supermarkets")
    EATING_OUT = (1, "Names of restaurants")
    WORK_CATERING = (2, "ONLY T N S CATERING")
    MANDATORY_BILLS = (3, "Insurance or rent")
    SERVICES = (4, "Spotify or Proton or Apple")
    SAVINGS = (5, "Trading 212 or LUKE M A Parkin or 'FROM A/C'")
    TRANSPORT = (6, "stagecoach or trains")
    TRANSFERS_FROM_FRIENDS = (7, "Where peoples names are listed at start")
    PAY = (8, "Pay from Arm")
    OTHER = (9, "If it does not fit in any previous categories")

    def __init__(self, id, description):
        self.id = id
        self.description = description

    def prompt_segment(self):
        return


class AiApi:
    def __init__(self):
        return

    def categorise(self):
        return None


class OpenAi_Api(AiApi):
    def __init__(self):
        import openai

        self.model = "gpt-4o-mini"
        self.client = openai.OpenAI(api_key="API-TOKEN")

    def completion(self, prompt: str) -> str:
        completion = self.client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[
                {"role": "system", "content": prompt},
            ],
        )
        return completion.choices[0].message.content


class Local_Api(AiApi):
    def __init__(self):
        self.url = "http://localhost:11434/api/generate"  # Ollama
        self.headers = {"Content-Type": "application/json"}

    def completion(self, prompt: str) -> str:
        request = {"model": "llama3.1", "prompt": prompt, "stream": False}
        response = requests.post(
            self.url, headers=self.headers, data=json.dumps(request)
        )

        if response.status_code == 200:
            return response.json()["response"]
        else:
            print("Error:", response.status_code, response.text)


class Transaction:
    def __init__(self, arr: list[str], api_obj):
        self.date = datetime.datetime.strptime(arr[0], "%d %b %Y")  # dd-MMM-yy
        self.type = arr[1]  # transaction type
        self.description = arr[2]
        self.value = arr[3]
        self.category = Categories.OTHER
        self.short_description = ""
        self.api = api_obj

    def categorise(self) -> None:
        categories = list(Categories.__members__.keys())
        # query = f"Instruction: Categorise the following bank transaction: '{self.description}' into one of the following categories.\n"
        query = "Here are example categories in the following format: 'CATEGORY, description'\n"
        query += ", ".join(
            [f"{str(key)}, {Categories[key].description}" for key in categories]
        )
        query += f"\nCategorise the transaction: '{self.description}' return the response like this: 'CATEGORY,short description' The short description should be a 2/3 word guess at what the transaction is. Return nothing else. Do not provide thoughts or explanation"

        response = self.api.completion(query)
        # print(response)
        response = response.split(",")
        self.category = response[0]
        self.short_description = response[1]


def categorise_transactions(transactions: list[Transaction]) -> None:
    # this could be multithreaded
    for transaction in tqdm(transactions):
        transaction.categorise()


ai_api = Local_Api()
transactions = []


def transactions_from_csv(path: str) -> list[Transaction]:
    with open(path, "r") as csvfile:
        reader = csv.reader(csvfile, delimiter=",")
        next(reader)
        for row in reader:
            transactions.append(Transaction(row, ai_api))
    return transactions


class Statistics:
    def __init__(self, transactions, api_obj):
        self.transactions = transactions
        self.paid_out = 0
        self.reimbursements = 0
        self.paid_in = 0
        self.api = api_obj

    def find_high_spenders(self):
        print("Tabulating..")
        for transaction in tqdm(self.transactions):
            if transaction.category == "PAY":
                self.paid_in += float(transaction.value)
            elif transaction.category == "TRANSFERS_FROM_FRIENDS":
                self.reimbursements += float(transaction.value)
            else:
                self.paid_out += float(transaction.value)
        print(f"You paid out: {self.paid_out}")
        print(f"Got paid in: {self.paid_in}")
        print(f"With {self.reimbursements} reimbursements")

    def sum_categories(self):
        category_totals = {category: float("0") for category in Categories}

        for transaction in self.transactions:
            try:
                category_totals[Categories[transaction.category]] += float(
                    transaction.value
                )
            except:
                category_totals[Categories["OTHER"]] += float(transaction.value)

        return category_totals

    def find_trends(self):
        prompt = ""
        print("Intelligently finding trends..")
        for transaction in tqdm(self.transactions):
            prompt += f"{transaction.short_description}: £{transaction.value}\n"
        for category, total in self.sum_categories().items():
            prompt += f"{category.name}: £{total:.2f}, "
        prompt += "\n Category totals: "
        prompt += "Using that list of transactions containing a short description then value, write a report for the customer intelligently identifying common trends in spending and then suggesting ways to save money."
        print(prompt)
        return self.api.completion(prompt)


# path = input("Input path to transaction csv")
transactions = transactions_from_csv("csv.csv")
print("Transaction imported")
print("Categorising transactions using LLM")
categorise_transactions(transactions)
print("Transactions categorised successfully")

print("I'm now going to identify some of your high spenders, and common trends.")
stats = Statistics(transactions, ai_api)
stats.find_high_spenders()
print(stats.find_trends())
