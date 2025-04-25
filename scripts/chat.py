import os

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
import httpx
import json


# Load the API key from the .env file
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)

def user_question_to_backend_query(user_query: str, history):
    model = ChatOpenAI(
        temperature=0.7,
        model="gpt-3.5-turbo",
        max_tokens=1000,
    )
    """
        {
      "brand": [
        "string"
      ],
      "model": [
        "string"
      ],
      "min_year": 0,
      "max_year": 0,
      "min_price": 0,
      "max_price": 0,
      "fuel_type": [
        "string"
      ],
      "color": [
        "string"
      ],
      "mileage": 0,
      "doors": 0,
      "transmission": [
        "string"
      ]
    }
    """
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Você é uma IA que ajuda os usuários a encontrar carros com base em suas preferências."),
        ("system", "Sua tarefa é converter a pergunta do usuário em uma consulta para o backend no formato JSON."),
        ("system", "A consulta para o backend deve ser um dicionário com as seguintes chaves:"),
        ("system", "Os valores das chaves devem seguir estas regras:"),
        ("system", "- `brand`, `model`, `fuel_type`, `color` e `transmission` devem ser listas de strings."),
        ("system", "- `mileage` e `doors` devem ser inteiros. Se não forem especificados, simplesmente não os inclua."),
        ("system",
         "- `min_year`, `max_year`, `min_price` e `max_price` devem ser inteiros. Se não forem especificados, simplesmente não os inclua."),
        ("system",
         "Exemplo: Se o usuário perguntar 'Quero um Toyota vermelho de 2015 a 2020 por menos de $20.000', a consulta para o backend deve ser assim:"),
        ("system", "{{"
                   "  \"brand\": [\"Toyota\"],"
                   "  \"model\": [],"
                   "  \"min_year\": 2015,"
                   "  \"max_year\": 2020,"
                   "  \"min_price\": 0,"
                   "  \"max_price\": 20000,"
                   "  \"fuel_type\": [],"
                   "  \"color\": [\"red\"],"
                   "  \"mileage\": 0,"
                   "  \"doors\": 0,"
                   "  \"transmission\": []"
                   "}}"),
        ("system", "Note que a base de dados é em inglês, então a consulta deve ser em inglês."),
        *history,
        ("user", "{user_query}"),
    ])
    chain = prompt | model

    response = chain.invoke({
        "user_query": user_query,
        "history": history
    })
    return response.content


def summary_backend_response_to_user(backend_query: str, history):
    model = ChatOpenAI(
        temperature=0.7,
        model="gpt-4o-mini",
        max_tokens=1000,
    )
    prompt = ChatPromptTemplate.from_messages([
        ("system", "Você é uma IA que ajuda os usuários a encontrar carros com base em suas preferências."),
        ("system",
         "A resposta do backend é uma lista de dicionários com as seguintes chaves: brand, model, year, engine, "
         "fuel_type, color, mileage, doors, transmission, price."),
        ("system",
         "Sua tarefa é resumir a resposta do backend, que é uma lista de carros, em um formato amigável para o usuário."),
        ("system",
         "Exemplo: Se a resposta do backend for [{{\"brand\": \"Toyota\", \"model\": \"Camry\", \"year\": 2020}}], "
         "o histórico da pergunta do usuário e da consulta para o backend é:"),
        ("system", "A informação sobre a lista atual de carros na resposta é: {backend_response}"),
        *history,
    ])
    chain = prompt | model

    # Getting backend response
    API_URL = "http://localhost:8000/api/v1/cars/filter"
    headers = {"Content-Type": "application/json"}

    try:
        # Sanitize the backend query
        backend_query = backend_query.replace("```json", "").replace("```", "")
        json_query = json.loads(backend_query)
        #print(f"Sending backend query: {json_query}")
        # Send the backend query as JSON
        response = httpx.post(API_URL, headers=headers, json=json_query)
        response.raise_for_status()  # Raise an error for HTTP issues
        backend_response = response.json()  # Parse the JSON response
        # turn the json response into a string
        # then double the curly braces
        backend_response = json.dumps(backend_response, indent=2)
        backend_response = backend_response.replace("{", "{{").replace("}", "}}")
        #print(f"Received backend response: {backend_response}")
    except (httpx.RequestError, httpx.HTTPStatusError) as e:
        return f"Error communicating with the backend: {e}"
    except json.JSONDecodeError as e:
        return f"Error decoding backend response: {e}"

    # Generate the summary using the AI model
    ai_response = chain.invoke({
        "backend_response": backend_response,
        "history": history
    })
    return ai_response.content

backend_query_history = []
backend_responses_history = []
while True:
    user_query = input("Enter your question: ")
    if user_query.lower() == "exit":
        break

    backend_query = user_question_to_backend_query(user_query, backend_query_history)

    ai_response_to_backend = summary_backend_response_to_user(backend_query, backend_responses_history)

    backend_query_history.append(("human", user_query))
    # Sanitize the ai response to put into history
    backend_query = backend_query.replace("\n", "").replace(" ", "")
    backend_query = backend_query.replace("{", "{{").replace("}", "}}")
    backend_query_history.append(("ai", backend_query))
    backend_query_history.append(("ai", ai_response_to_backend))

    backend_responses_history.append(("human", user_query))
    backend_responses_history.append(("ai", ai_response_to_backend))

    print(f"Backend query: {backend_query}")
    print(f"AI: {ai_response_to_backend}")