import os
import replicate
from llama_index.core import SimpleDirectoryReader
from llama_index.multi_modal_llms.openai import OpenAIMultiModal
os.environ["REPLICATE_API_TOKEN"] = "r8_LMZoyy9Hh5CebwLEVDl3Sg8KWj5rxvB3xv6YQ"
os.environ['OPENAI_API_KEY'] = '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'




def generate_response():

    image_documents = SimpleDirectoryReader(input_files=["/home/bili/Desktop/scenario_generation_llm/puzzle_solution_scenarios/env2.png"]).load_data()

    openai_mm_llm = OpenAIMultiModal(
            model="gpt-4o-2024-05-13", api_key='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', max_new_tokens=1500
        )

    tools = ['Ramp: simulate inclined surfaces over which balls can roll or slide. This is used when you want a gradual change in direction or need to guide the ball smoothly over a distance. Length of the ramp can be 10, 14, 18. You must say whether the ball needs to move to the left or right.', 
             'Fixed_Hexagon: This is used when you need a sharp redirection.', 
             'Cannon: This is used when you need to shoot the ball in a specific direction.',]

    response_1 = openai_mm_llm.complete(
            prompt=f"You are a player agent to help the red ball reach the goal based on the CREATE (Chain REAction Tool Environment) toolkit. \
    CREATE is based on the popular Physics puzzle The Incredible Machine. The objective of a player agent is to sequentially select and position tools from an available set, \
    to make the blue ball (marker_ball) push the red ball (target) to make the red ball reach the goal (green) after being hit in a given game environment. \
    You are provided with a set of tools and a game environment. You will need to use the tools to solve the puzzle. \
    Here is a sample solution to a example puzzle: \
    1. A ramp is placed for the blue ball to slide down to the left, land on the floor and fall off the left edge of the floor. \
    2. The blue ball then hits a fixed_triangle after falling off the floor, which helps the blue ball make a turn and changes the blue ball's moving direction to the right.\
    3. The blue ball hits the red ball and push the red ball to fall off the right edge of the floor. \
    4. The red ball slides down the ramp to the right and reaches the goal. \
    The above solution is just an example. You need to solve a different puzzle that is shown in the image. \
    You must first describe what you see in the image.\
    Then Propose one tool or multiple tools from {tools} to help the blue ball reach and push the red ball to the goal. Describe the tool's rule and you must say their relative position (left/right, above/below) to objects (blue ball, red ball or the goal) that you want to place those tools near, such like: 'place the ramp on the right and bottom of the blue ball'.\
    You must also tell whether the blue ball needs to move to the left or right to reach the red ball.",
            image_documents=image_documents
        )


    return (response_1.text)

def main():

    response = generate_response()
    print(response)

if __name__ == "__main__":
    main()