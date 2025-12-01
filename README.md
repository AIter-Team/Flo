# Flo: Financial Life Orchestrator

Flo is an intelligent, agentic system designed to help you manage your entire financial life. Flo's role is not just as an assistant, but as a proactive partner in your financial decisions. Built with [LangChain](https://langchain.com/) and [LangGraph](https://langchain-ai.github.io/langgraph/), it leverages a team of specialized AI agents to provide comprehensive financial advice.

## Key Features

- **Daily Operations & Cash Flow**: Track income/expenses, manage budgets, and calculate the "time cost" of purchases.
- **Wealth Generation**: Manage liabilities (debts, subscriptions) and track assets (stocks, crypto, fixed deposits) with real-time net worth analysis.
- **Strategic Planning**: Set and track financial goals.
- **Well-being & Oversight**: Manage wishlists and get smart "Can I Afford?" assessments before making purchases.
- **Persistent Memory**: Remembers your preferences, financial history, and past conversations.
- **Conversational Interface**: Natural language interaction for all your financial questions.

For a detailed breakdown of all features, see [`docs/features`](docs/features.md).

## Getting Started

### Prerequisites

- **Python 3.13+**
- **[uv](https://github.com/astral-sh/uv)** (Recommended for dependency management)

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/AIter-Team/Flo
    cd Flo
    ```

2.  **Install dependencies:**
    ```bash
    uv sync
    ```
    *Alternatively, if you are not using `uv`, you can install dependencies from `pyproject.toml` using pip.*

3.  **Configure Environment Variables:**
    Create a `.env` file in the root directory. You will need API keys for LangSmith (for agent prompts) and your LLM providers (OpenAI, Google).

    ```bash
    touch .env
    ```

    Add the following keys to your `.env` file:
    ```env
    # LangSmith (Required for pulling prompts and tracing)
    LANGCHAIN_TRACING_V2=true
    LANGCHAIN_ENDPOINT="https://api.smith.langchain.com"
    LANGCHAIN_API_KEY="your_langchain_api_key"
    LANGCHAIN_PROJECT="flo-app"

    # Model Providers (Add keys for the models you intend to use)
    OPENAI_API_KEY="your_openai_api_key"
    GOOGLE_API_KEY="your_google_api_key"
    ```

### Usage

To start the application, run the main script:

```bash
uv run python -m main
```

The application will initialize the database (if it doesn't exist) and start a conversational session. You can type your questions or commands, and the appropriate agent will respond.

Type `exit`, `quit`, or `q` to end the session.

## Project Structure

- `src/agents`: Contains the logic for each specialized agent (Root, Quant, Capitalist, etc.).
- `src/config`: Configuration files for agents, database, and directories.
- `src/tools`: Custom tools used by the agents.
- `src/memory`: Directory for storing persistent data (SQLite DB, JSON profiles).

## Documentation

For more detailed information about the agents and their capabilities, please refer to the documentation in the `docs` directory:

- [Quant Agent](docs/agents/quant.md): Daily financial operations and cash flow.
- [Capitalist Agent](docs/agents/capitalist.md): Investment advice and wealth generation.
- [Strategist Agent](docs/agents/strategist.md): Long-term financial planning.
- [Steward Agent](docs/agents/steward.md): System oversight and well-being.

## Contributing

We welcome contributions! Please follow these steps:

1.  Fork the repository.
2.  Create a new branch (`git checkout -b feature/YourFeature`).
3.  Make your changes.
4.  Commit your changes (`git commit -m 'Add some feature'`).
5.  Push to the branch (`git push origin feature/YourFeature`).
6.  Open a Pull Request.

## License

This project is licensed under the MIT License - see the [LICENSE.md](LICENSE.md) file for details.
