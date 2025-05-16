# Job Search Agent with Bright data and Nebius AI Studio

![GIF](./assets/job-search.gif)

A powerful job search agent that leverages Bright data and Nebius AI Studio to help users find relevant job opportunities.

## Prerequisites

Before running this project, make sure you have the following:

- Python 3.10 or higher
- A [Bright data](https://brightdata.com/) account and API credentials
- [Nebius AI Studio](https://studio.nebius.com/) Account

## Installation

1. Clone the repository:

```bash
git clone https://github.com/Arindam200/awesome-llm-apps.git
cd advance_ai_agents/job_finder_agent
```

2. Create a virtual environment (recommended):

```bash
python -m venv venv
source venv/bin/activate  # On Windows, use: venv\Scripts\activate
```

3. Install the required dependencies:

```bash
pip install -r requirements.txt
```


## Environment Variables

Create a `.env` file in the project root with the following variables:

```
BRIGHT_DATA_API_KEY=your_bright_data_api_key
NEMIUS_API_KEY=your_nemius_api_key
```

## Usage

1. Start the application:

```bash
streamlit run app.py
```

2. Open your web browser and navigate to the provided local URL (typically http://localhost:8501)

3. Use the interface to search for jobs based on your criteria

## Features

- Real-time job search using Bright data
- AI-powered job matching using Nebius AI Studio
- Interactive web interface
- Asynchronous job processing
- Data validation and error handling

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Acknowledgments

- Bright Data for providing the data infrastructure
- Nebius AI Studio for AI capabilities
- All contributors who have helped shape this project
