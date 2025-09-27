"""
Nutrition scoring using LLM analysis module
"""
import os
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from pydantic import BaseModel, Field


class NutritionScore(BaseModel):
    score: int = Field(..., description="A numeric score (0-100) for the product based on its nutrition data.")
    comment: str = Field(..., description="A detailed comment explaining the nutrition score and health implications.")


def calculate_nutrition_score(nutrition_data):
    """Calculate nutrition score using LangChain and Gemini"""
    parser = PydanticOutputParser(pydantic_object=NutritionScore)

    prompt = ChatPromptTemplate.from_messages([
        ("system", "You are a nutrition scoring assistant. Score products based on their nutritional value using the provided guidelines."),
        ("user", """Given this nutrition data, return a numeric score between 0 and 100 AND a detailed comment based on the following scoring guidelines:

NUTRITION SCORING GUIDELINES:
1. CALORIES (per serving):
   - Low (0-150): +20 points
   - Moderate (151-300): +10 points
   - High (301-500): +5 points
   - Very High (500+): 0 points

2. PROTEIN (per serving):
   - High (15g+): +15 points
   - Good (8-14g): +10 points
   - Moderate (3-7g): +5 points
   - Low (0-2g): 0 points

3. SUGAR (per serving):
   - Low (0-5g): +15 points
   - Moderate (6-15g): +10 points
   - High (16-25g): +5 points
   - Very High (25g+): -10 points

4. FIBER (per serving):
   - High (8g+): +15 points
   - Good (4-7g): +10 points
   - Moderate (2-3g): +5 points
   - Low (0-1g): 0 points

5. FAT (per serving):
   - Low (0-5g): +10 points
   - Moderate (6-15g): +5 points
   - High (16-25g): 0 points
   - Very High (25g+): -10 points

6. SODIUM (per serving):
   - Low (0-200mg): +10 points
   - Moderate (201-600mg): +5 points
   - High (601-1200mg): 0 points
   - Very High (1200mg+): -10 points

7. VITAMINS & MINERALS:
   - Rich in vitamins/minerals: +10 points
   - Some vitamins/minerals: +5 points
   - None listed: 0 points

8. ADDITIVES & PRESERVATIVES:
   - No artificial additives: +5 points
   - Few additives: +2 points
   - Many additives: -5 points

BONUS POINTS:
- Organic: +5 points
- Non-GMO: +3 points
- Whole grains: +5 points
- Natural ingredients: +3 points

PENALTY POINTS:
- Trans fats: -15 points
- High fructose corn syrup: -10 points
- Artificial colors/flavors: -5 points

Base score starts at 50. Apply the rules above and ensure final score is between 0-100.
Provide a detailed comment explaining the score, highlighting health benefits/concerns, and giving recommendations.

Nutrition data:
{nutrition_data}

{format_instructions}
""")
    ])

    google_api_key = os.getenv("GOOGLE_API_KEY")
    if not google_api_key:
        google_api_key = "AIzaSyDsv_sbRtEG_u-X-VEA3RmPKUoH6iE_NXM"  # Fallback

    model = ChatGoogleGenerativeAI(
        model="gemini-2.0-flash",
        google_api_key=google_api_key,
        temperature=0.000001,
        transport="rest"
    )

    chain = prompt | model | parser

    result = chain.invoke({
        "nutrition_data": nutrition_data,
        "format_instructions": parser.get_format_instructions()
    })

    return result.score, result.comment