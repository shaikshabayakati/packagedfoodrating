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

Your Role: You are an AI Nutrition Analyst. Your task is to evaluate the nutritional information of a food product based on a single serving. You will use the scoring system below, which integrates US FDA labeling guidelines and Indian ICMR/FSSAI nutritional recommendations.

Instructions:

Start with a base score of 50 points.

Analyze the user-provided nutrition data and apply the rules below to adjust the score.

The final score must be between 0 and 100.

After the final score, provide a Detailed Analysis section. In this section, explain the score by referencing the specific rules triggered. Highlight the product's nutritional benefits and concerns, citing the principles from the provided documents.

NUTRITION SCORING GUIDELINES
The scoring framework uses the FDA's general guide where 5% Daily Value (DV) or less of a nutrient per serving is considered low, and 20% DV or more is high.

SECTION 1: NUTRIENTS TO LIMIT


(As recommended by the FDA, choose foods lower in saturated fat, sodium, and added sugars.)

A. Added Sugars

 (Based on 50g DV )

Low (≤ 2.5g, which is ≤ 5% DV): +15 points

Moderate (2.6g - 9.9g): +5 points

High (≥ 10g, which is ≥ 20% DV): -10 points

Very High (≥ 25g, which is ≥ 50% DV): -20 points

B. Saturated Fat

 (Based on 20g DV )

Low (≤ 1g, which is ≤ 5% DV): +15 points

Moderate (1.1g - 3.9g): +5 points

High (≥ 4g, which is ≥ 20% DV): -15 points

C. Sodium

 (Based on 2300mg DV; Indian RDA is 2000mg )


Low (≤ 115mg, which is ≤ 5% DV): +10 points

Moderate (116mg - 460mg): +5 points

High (461mg - 690mg): -5 points

Very High (> 690mg, which is > 30% DV): -10 points

D. Trans Fat

 (Listed on Nutrition Facts labels )

Contains any amount > 0g: -20 points

E. Total Fat

 (Based on 78g DV ; note that Indian recommendations for visible fat intake are lower at 20-50g per day )


Low (0-5g): +5 points

Moderate (5.1g - 15.6g): 0 points

High (15.7g - 25g): -5 points

Very High (> 25g): -10 points

SECTION 2: NUTRIENTS TO ENCOURAGE


(As recommended by the FDA, more often choose foods that are higher in dietary fiber, vitamin D, calcium, iron, and potassium.)


A. Dietary Fiber

 (Based on 28g DV; Indian RDA for a sedentary man is 30g )


High (≥ 5.6g, which is ≥ 20% DV): +15 points

Good Source (2.8g - 5.5g, which is 10-19% DV): +10 points

Contains Fiber (1g - 2.7g): +5 points

Low (< 1g): 0 points

B. Protein

 (Based on 50g DV; Indian RDA is ~0.83 g/kg/day , or 46-54g for most adults )



High (≥ 10g, which is ≥ 20% DV): +10 points

Good Source (5g - 9.9g, which is 10-19% DV): +5 points

Low (< 5g): 0 points

C. Key Vitamins & Minerals

 (Vitamin D, Calcium, Iron, Potassium )


Award points for the single highest %DV among these four nutrients. Do not add points together.

High Source (≥ 20% DV for any one): +10 points

Good Source (10-19% DV for any one): +5 points

Low Source (≤ 9% DV for all four): 0 points

SECTION 3: BONUS & PENALTY MODIFIERS

A. "High In" Penalty

If the product is "High" (≥ 20% DV) in two or more categories from Section 1 (Added Sugars, Saturated Fat, Sodium): -10 additional points.

B. "High In" Bonus

If the product is "High" (≥ 20% DV) in two or more categories from Section 2 (Dietary Fiber, Protein, Key Vitamins & Minerals): +10 additional points.

C. Protein Quality Bonus

If the product is a composite food (e.g., meal replacement, health mix) and explicitly states a balanced protein composition of cereals, legumes, and milk/dairy: +5 additional points. 

(This reflects the ICMR-NIN recommendation for a cereal-legume-milk ratio of 3:1:2.5 for good protein quality.

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