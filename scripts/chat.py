import os

from dotenv import load_dotenv
from langchain_core.prompts import ChatPromptTemplate
from langchain_openai import ChatOpenAI
import httpx
import json

from rich.console import Console
from rich.markdown import Markdown
from rich.panel import Panel
from rich.prompt import Prompt

# Load the API key from the .env file
dotenv_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(dotenv_path)

def user_question_to_backend_query(user_query: str, history):
    model = ChatOpenAI(
        temperature=0.7,
        model="gpt-4o",
        max_tokens=1000,
    )
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
        ("system", "A sua resposta deve ser apenas o json, nada mais."),
        ("system", "O usuário pode também desconsiderar dados antigos se quiser. "
                   "Por exemplo: Desconsidere o tipo de combustível, quero mais opções. "
                   "Exemplo: Desconsidere o preço (nesse caso, max price, min price iriam pra 0). "
                   "Exemplo: Desconsidere o ano de lançamento (nesse caso, min_year e max_year iria pra 0)"),
        ("system", "Se o usuário não especificar nada novo, pedir esclarecimento sobre algo, "
                   "você deve retornar o mesmo json que foi enviado na última consulta."),
        ("system", "Última consulta: {last_query}"),
        ("system", "A sua resposta deve ser apenas o json, nada mais."),
        *history,
        ("user", "{user_query}"),
    ])
    chain = prompt | model

    response = chain.invoke({
        "user_query": user_query,
        "history": history,
        "last_query": backend_query_history[-1] if backend_query_history else "{}"
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
        return f"Error communicating with the backend: {e}", {}
    except json.JSONDecodeError as e:
        return f"Error decoding backend response: {e}", {}

    # Generate the summary using the AI model
    ai_response = chain.invoke({
        "backend_response": backend_response,
        "history": history
    })
    return ai_response.content, backend_response


def display_markdown(content: str, title: str = None):
    """Render and display Markdown content inside a panel."""
    markdown = Markdown(content)
    panel = Panel(markdown, title=title, expand=True)
    console.print(panel)


def show_how_to_use():
    """Display search parameters and example questions."""
    console.print("\n[bold blue]Parâmetros de busca disponíveis:[/bold blue]")

    parameters = [
        "Marca (Toyota, Ford, BMW, etc.)",
        "Modelo (Corolla, Focus, etc.)",
        "Ano (1990-2023)",
        "Motor (1.0L, 2.5L, etc.)",
        "Combustível (Gasolina, Diesel, Elétrico, Híbrido)",
        "Cor (vermelho, azul, preto, etc.)",
        "Quilometragem (em km)",
        "Número de portas (2-5)",
        "Transmissão (Manual, Automático)",
        "Preço (em R$)"
    ]

    for param in parameters:
        console.print(f"• [cyan]{param}[/cyan]")

    console.print("\n[bold blue]Exemplos de perguntas:[/bold blue]")
    examples = [
        "Quero um Toyota vermelho de 2015 a 2020",
        "Carros sedan automáticos",
        "Carros com menos de 50.000 km",
        "Carros híbridos disponíveis"
    ]

    for example in examples:
        console.print(f"• [green]{example}[/green]")

    console.print()



backend_query_history = []
backend_responses_history = []
current_car_options = []

# Initialize the rich console
console = Console()
# Replace these English UI texts with Portuguese translations
console.print("[bold magenta]Bem-vindo ao Aplicativo de Chat para Busca de Carros![/bold magenta]")
console.print("[bold cyan]Digite 'exit' para sair do aplicativo.[/bold cyan]")

while True:
    show_how_to_use()
    user_query = Prompt.ask("[bold green]Digite sua pergunta[/bold green]")
    if user_query.lower() == "exit":
        console.print("[bold yellow]Até logo![/bold yellow]")
        break

    # Add user query to backend_responses_history first
    backend_responses_history.append(("human", user_query))

    # Check if we have current results and determine intent
    has_results = len(backend_responses_history) > 0 and "backend_response" in locals()


    # Original flow for search queries
    with console.status("[bold blue]Processando sua pergunta...") as status:
        backend_query = user_question_to_backend_query(user_query, backend_query_history)

    # Add user query to backend_query_history
    backend_query_history.append(("human", user_query))

    # Format and store backend query in history
    formatted_backend_query = backend_query.replace("\n", "").replace(" ", "")
    formatted_backend_query = formatted_backend_query.replace("{", "{{").replace("}", "}}")
    backend_query_history.append(("ai", formatted_backend_query))

    with console.status("[bold blue]Buscando e analisando opções de carros...") as status:
        ai_response_to_backend, backend_response = summary_backend_response_to_user(
            backend_query, backend_responses_history)

    # Add AI response to backend_query_history
    backend_query_history.append(("ai", ai_response_to_backend))

    display_markdown(f"```json\n{backend_query}\n```", title="Consulta ao Backend")
    display_markdown(ai_response_to_backend, title="Resposta da IA")

    # Set ai_response for the history
    ai_response = ai_response_to_backend

    # Always append AI response to backend_responses_history
    backend_responses_history.append(("ai", ai_response))