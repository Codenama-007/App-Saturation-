


App Saturation Analyzer — EXECUTE GUIDE
This guide shows you how to run the project after cloning it.

The project takes an app idea and checks:

Existing similar products

Competitors

Suggested differentiating features

Market Saturation Score

Competition Density

Similarity Score

Market Gap Score

Confidence Score

It also contains a separate Website Security Analyzer.

1. Clone the Repository
git clone https://github.com/Codenama-007/App-Saturation-.git
cd App-Saturation-
2. Create a Virtual Environment
Windows
py -m venv venv
venv\Scripts\activate
Mac / Linux
python3 -m venv venv
source venv/bin/activate
3. Install Dependencies
Run:

pip install -r requirements.txt
Also install these two packages used by the current code:\
## 4. Environment Variables

Before running the project, create your `.env` file.

### Windows

```bash
copy .env.example .env


pip install python-dotenv requests
4. Install Ollama
The project currently uses:

qwen3:1.7b
<!-- do ollama list on cmd and check which one is available and use that one -->
Install Ollama from:

https://ollama.com/

Then download the model:

ollama pull qwen3:1.7b
Make sure Ollama is running before starting the project.

You can check the model with:

ollama list
You should see:

qwen3:1.7b
5. Optional: Product Hunt API Token
The project can also use Product Hunt data.

Create a file called:

.env
in the project root.

Add:

TOKEN=your_product_hunt_api_token
If you do not have a Product Hunt token, the main analyzer can still continue using web search. Product Hunt failures are handled by the application.

6. Run the Main App Saturation Analyzer
Start it with:

python main.py
You will see:

Enter your app idea:
Now enter your idea.

7. Demo Input
For a simple demonstration, use:

A platform for selling Clothes, Grocery items, Sports Gear and Stationery
Then press Enter.

The agent will:

Idea
 ↓
Generate Search Query
 ↓
Search the Web
 ↓
Search Product Hunt
 ↓
Compare Products
 ↓
Calculate Scores
 ↓
Suggest Differentiating Features
 ↓
Save Result to Memory
8. What You Will Get
The application displays three main sections.

Existing Products
This shows products that the agent thinks are similar to your idea.

Example:

STATUS: EXISTS

Top matching products:
...
Suggested Differentiating Features
This gives ideas for features that could help your product stand out.

Example:

SUGGESTED DIFFERENTIATORS:

1. ...
2. ...
3. ...
Market Saturation Score
You will also get:

SATURATION SCORE
47.2/100

SATURATION LEVEL
Moderate

COMPETITION DENSITY
20/100

SIMILARITY SCORE
100/100

MARKET GAP SCORE
52.8/100

CONFIDENCE
60/100
The exact numbers can change because the agent performs a fresh search.

9. Understanding the Scores
Saturation Score
Shows how crowded the market appears based on the competitors found.

0–24   = Low
25–49  = Moderate
50–74  = High
75–100 = Very High
Competition Density
Measures how many direct competitors were found.

Similarity Score
Shows how strongly the identified competitors resemble the submitted idea.

Market Gap Score
This is the inverse of the saturation score.

Market Gap = 100 - Saturation
A higher score means there may be more room to differentiate.

Confidence
Shows how much evidence the analyzer has from the available search results and sources.

10. Try More Ideas
You can keep entering ideas without restarting the program.

For example:

An AI fitness coach that creates personalized workout plans
or:

A platform connecting students with local tutors
or:

An app that helps college students find internships
Try different ideas and compare their results.

11. Exit the Program
Type:

bye
The program will stop.

12. Run the Website Security Analyzer
The repository also contains:

security-analyzer.py
Run:

python security-analyzer.py
It starts a separate AI security assistant.

You can enter a website URL, for example:

https://example.com
The analyzer can check things such as:

Website availability

HTTP status

HTTPS

Response time

Security headers

Cookies

Detectable technologies

It can also provide security recommendations.

Type:

bye
to exit.

13. Important Note About the Scores
The Market Saturation Score is a heuristic score, not an official percentage of the real-world market.

For example:

47.2/100
does NOT mean:

"47.2% of the market is saturated."

It means the analyzer calculated a score from signals such as:

Number of direct competitors

Number of highly similar competitors

Search results

Source coverage

Use the score as a decision-support signal, not as a guaranteed market statistic.

14. Project Structure
The important files are:

App-Saturation-
│
├── main.py
├── graph.py
├── tools.py
├── scoring.py
├── memory.py
├── models.py
│
├── security-analyzer.py
├── vibe-code-app-detector.py
│
├── requirements.txt
└── langgraph_workflow.png
main.py
Runs the main CLI application.

graph.py
Contains the LangGraph workflow.

tools.py
Contains web and Product Hunt search tools.

scoring.py
Calculates the market saturation metrics.

memory.py
Stores previous ideas and results locally using SQLite.

security-analyzer.py
Runs the separate website security analysis agent.

15. Quick Start
If everything is already installed, the whole demo is basically:

git clone https://github.com/Codenama-007/App-Saturation-.git
cd App-Saturation-

py -m venv venv
venv\Scripts\activate

pip install -r requirements.txt
pip install python-dotenv requests

ollama pull qwen3:1.7b

python main.py
Then enter:

A platform for selling Clothes, Grocery items, Sports Gear and Stationery
That's it.

16. Demo Flow
For a presentation/demo, use this flow:

Step 1
Start:

python main.py
Step 2
Enter:

A platform for selling Clothes, Grocery items, Sports Gear and Stationery
Step 3
Show:

Existing Products

↓

Suggested Differentiating Features

↓

Market Saturation Score

This demonstrates the complete workflow from:

APP IDEA
   ↓
MARKET RESEARCH
   ↓
COMPETITOR ANALYSIS
   ↓
FEATURE SUGGESTIONS
   ↓
SCORING
Done
You now have everything required to clone, install, run, and demonstrate the project.