import json

from agents.base_agent import BaseAgent
from agents.schemas import EvaluationFeedback
from prompts.exercise_prompts import get_exercise_prompt, get_message_key
from data.images.girl1 import IMAGE_BASE64 as GIRL1_IMAGE_BASE64
from data.images.girl2 import IMAGE_BASE64 as GIRL2_IMAGE_BASE64
from helpers.logger import logger


class PushPullEvaluator(BaseAgent):
    EXERCISE_KEY = "pushPull"

    def __init__(self, model_name=None):
        system_message = get_exercise_prompt(self.EXERCISE_KEY, "evaluator")

        self.response_schema = EvaluationFeedback
        self.message_key = get_message_key(self.EXERCISE_KEY, "evaluator")

        example1 = [
            {
                "image_url": f"data:image/jpeg;base64,{GIRL1_IMAGE_BASE64}",
                "response": "Hair looks fake but nice try."
            },
            {
                "feedback": "<b>✅ What Landed</b><br>You noticed a specific detail (the hair) â€” that shows you're paying attention.<br><br><b>âš ï¸ The Trap</b><br>All push, zero pull. 'Hair looks fake but nice try' is just a dig. There's no interest signal, no playfulness â€” just criticism. She'd think you don't like her at all.<br><br><b>ðŸš€ Level Up</b><br>Try Backhanded Compliment and add warmth under the tease.<br><br><b>ðŸ§  Mindset Shift</b><br>Teasing without warmth isn't flirting â€” it's just being mean. The push only works when she can feel the pull underneath it.",
                "sample_answer": "<b>🎯 Polished:</b> Hair looks like it took 3 hours and honestly? Time well spent. I'm a little intimidated.<br><br><b>ðŸ˜ Backhanded Compliment:</b> The confidence in this photo is either extremely earned or incredibly well faked. Either way, it's working.<br><br><b>ðŸŽ­ Assumption Flip:</b> You look like you'd be 20 minutes late to every date but somehow make it worth the wait."
            }
        ]

        example2 = [
            {
                "image_url": f"data:image/jpeg;base64,{GIRL2_IMAGE_BASE64}",
                "response": "Nice stripes, I thought the zoo was down the street."
            },
            {
                "feedback": "<b>✅ What Landed</b><br>Good balance! You acknowledged something specific (the stripes) and added a playful zoo comparison. The push and pull are both present â€” this is close to the sweet spot.<br><br><b>âš ï¸ The Trap</b><br>The zoo reference is a tiny bit generic â€” could land as funny or as an insult depending on delivery.<br><br><b>ðŸš€ Level Up</b><br>Try Interest-Plus-Challenge and add more genuine curiosity.<br><br><b>ðŸ§  Mindset Shift</b><br>You're on the right track â€” just make sure the tease feels like an INVITATION to banter, not a judgment.",
                "sample_answer": "<b>🎯 Polished:</b> Funky coat â€” bold move. Just hoping black and white aren't the only modes you operate in.<br><br><b>ðŸ˜ Tease-First:</b> That coat has main character energy... but are YOU the main character, or is the coat doing all the work?<br><br><b>ðŸŽ­ Genuine + Absurd:</b> The style is actually fire. I'd need at least 2 outfit changes just to stand next to you at brunch."
            }
        ]

        few_shot_examples = [
            {
                "role": "user",
                "content": json.dumps(example1[0])
            },
            {
                "role": "assistant",
                "content": json.dumps(example1[1])
            },
            {
                "role": "user",
                "content": json.dumps(example2[0])
            },
            {
                "role": "assistant",
                "content": json.dumps(example2[1])
            }
        ]

        super().__init__(system_message, few_shot_examples=few_shot_examples, model_name=model_name)

    def process(self, question: any, response: str) -> str:
        if isinstance(question, list):
            image_content = None
            for item in question:
                if isinstance(item, dict) and item.get('role') == 'Image':
                    image_content = item.get('content', '')
                    break
            if image_content is None:
                return json.dumps({
                    "feedback": "Error: No image found in v2 format question array",
                    "sample_answer": "Please provide a valid image in the question format"
                })
            image_url = image_content
        else:
            return json.dumps({
                "feedback": "Error: Question must be a list, not " + str(type(question).__name__),
                "sample_answer": "Please provide the question as a dictionary or list object"
            })

        message = {
            self.message_key: image_url,
            "response": response
        }
        llm_messages = self.generate_llm_history(json.dumps(message))

        try:
            result = self.llm.get_response(llm_messages, response_schema=self.response_schema)
            return result.model_dump_json()
        except Exception as e:
            logger.error(f"Error in PushPullEvaluator: {str(e)}")
            return json.dumps({
                "feedback": "I encountered an issue processing your response. Please try again.",
                "sample_answer": "Let's try a different approach to this exercise."
            })
