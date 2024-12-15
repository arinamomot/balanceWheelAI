from dotenv import load_dotenv
import os
import streamlit as st
import openai
from openai import OpenAI
import matplotlib.pyplot as plt
import numpy as np

# Load environment variables from .env file
load_dotenv()
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    st.error("Please set your OpenAI API key in the .env file.")
    st.stop()

os.environ["OPENAI_API_KEY"] = OPENAI_API_KEY
client = OpenAI(api_key=os.environ['OPENAI_API_KEY'])

# Life areas for analysis
LIFE_AREAS = [
    "Health",
    "Career",
    "Finances",
    "Personal Growth",
    "Relationships",
    "Leisure",
    "Environment",
    "Self-Realization"
]

# Tooltips for LIFE_AREAS
TOOLTIPS = {
    "Health": "Your physical and mental well-being.",
    "Career": "Your job satisfaction and growth.",
    "Finances": "Your financial stability and goals.",
    "Personal Growth": "Your learning and self-improvement.",
    "Relationships": "Your connections with others.",
    "Leisure": "Your hobbies and relaxation time.",
    "Environment": "Your living and working spaces.",
    "Self-Realization": "Your sense of purpose and fulfillment."
}

def plot_life_wheel(scores):
    # Generate a wheel chart
    categories = list(scores.keys())
    values = list(scores.values())
    values += values[:1]  # Close the circle

    angles = np.linspace(0, 2 * np.pi, len(categories) + 1, endpoint=True)

    fig, ax = plt.subplots(figsize=(6, 6), subplot_kw={"polar": True})
    ax.fill(angles, values, color="blue", alpha=0.25)
    ax.plot(angles, values, color="blue", linewidth=2)
    ax.set_yticks(range(0, 11, 2))
    ax.set_xticks(angles[:-1])
    ax.set_xticklabels(categories)
    plt.title("Life Balance Wheel", size=16, y=1.1)
    return fig

def get_recommendations(scores):
    analysis_request = f"""
    Analyze the following life areas based on these scores:
    {scores}
    Provide recommendations for improvement in each area with a score below 8.
    """
    try:
    #OpenAI API request here
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "You are a helpful assistant providing life advice."},
                {"role": "user", "content": analysis_request}
            ],
            max_tokens=500,
            temperature=0.7
        )
        message = response.choices[0].message.content.strip()
        return message
    except openai.APIError as e:
        #Handle API error here, e.g. retry or log
        print(f"OpenAI API returned an API Error: {e}")
        pass
    except openai.APIConnectionError as e:
        #Handle connection error here
        print(f"Failed to connect to OpenAI API: {e}")
        pass
    except openai.RateLimitError as e:
        #Handle rate limit error (we recommend using exponential backoff)
        print(f"OpenAI API request exceeded rate limit: {e}")
        pass

def main():
    # Header
    st.title("🌟 Life Balance Wheel")
    st.write("Reflect on different areas of your life and get actionable insights to improve your well-being.")
    st.info("Tip: Aim for balance, not perfection!")

    # Sidebar for inputs
    st.sidebar.header("Rate Your Life Areas")
    scores = {}
    progress = 0
    for area in LIFE_AREAS:
        tooltip = TOOLTIPS.get(area, "")  # Get tooltip for the current area
        scores[area] = st.sidebar.slider(area, 0, 10, 5, help=tooltip)
        progress += scores[area] / (10 * len(LIFE_AREAS))

    # Analyze button
    if st.sidebar.button("Analyze"):
        with st.spinner("Analyzing your inputs..."):
            recommendations = get_recommendations(scores)
        
        # Display results
        st.subheader("🎯 Your Recommendations")
        if recommendations:
            st.write(recommendations)
        else:
            st.error("Failed to generate recommendations. Please try again.")

        # Display Life Wheel
        st.subheader("🌀 Your Life Balance Wheel")
        fig = plot_life_wheel(scores)
        st.pyplot(fig)

if __name__ == "__main__":
    main()
