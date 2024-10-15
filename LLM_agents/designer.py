import os
import replicate
from llama_index.core import SimpleDirectoryReader
from llama_index.multi_modal_llms.openai import OpenAIMultiModal
os.environ["REPLICATE_API_TOKEN"] = "r8_LMZoyy9Hh5CebwLEVDl3Sg8KWj5rxvB3xv6YQ"
os.environ['OPENAI_API_KEY'] = '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'


def design(prompt, ball_trajectory):

    current_dir = os.path.dirname(__file__)
    parent_dir = os.path.dirname(current_dir)

    image_documents = SimpleDirectoryReader(os.path.join(parent_dir, "frames")).load_data()
    openai_mm_llm = OpenAIMultiModal(
            model="gpt-4o-2024-05-13", api_key='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', max_new_tokens=1500
        )

    tools = ['Ramp: simulate inclined surfaces over which balls can roll or slide. This is used when you want a gradual change in direction or need to guide the ball smoothly over a distance. Length of the ramp can be 10, 14, 18. You must say whether the ball needs to move to the left or right.', 
             'Fixed_Hexagon: Both the blue ball and goal must be positioned on the same side of the environment (either both in the right or left), and the red ball must be positioned in the opposite side. The y coordinate of the blue ball must be greater than the y coordinate of the red ball by more than 0.8. You also need to place a seperate new floor, and both of its x and y coordinate should be between the blue ball and red ball, but x and y should both be a little bit closer to the red ball. The hexagon will redirect the blue ball back to the side it came from.', 
             'Cannon: This is used when you need to shoot the ball in a specific direction. The blue ball is on one side of the environment, and it needs to be pushed by a cannon up to reach the red ball which is above the blue ball on the other side. The y coordinate of the blue ball cannot be less or equal to -0.8.']

    objects = ['floor: a flat surface that the blue ball can land on from falling down. Both of the x and y coordinates of this floor must be just a little bit closer to the x and y coordinate of the red ball. The y coordinate of the blue ball must be greater than the y coordinate of the red ball by more than 0.8.',
               'wall: A vertical wall whose y-coordinate must be positioned between the y-coordinates of the blue ball and the red ball, but the y coordinate must be closer to the y coordinate of the red ball. The x coordinate must be closer to the x of the blue ball. The y coordinate of the blue ball must be greater than the y coordinate of the red ball by more than 0.8. ']
    
    response_1 = openai_mm_llm.complete(
            prompt=f"Instructions for the Designer Agent in a 2D Physics Puzzle Game: \
        As the designer agent, your role is to create and adjust puzzles in a 2D physics game environment. The game's objective is for the player to strategically place tools to make the blue ball (marker_ball) push the red ball (target) to reach the goal (green).\
        You have two primary tasks:\
        - Design a new puzzle layout based on the provided prompt.\
        - Adjust object positions within an existing puzzle based on the provided trajectory data.\
        Rules:\
        - Every puzzle must include a red ball, blue ball, and goal. The blue ball will fall down due to gravity initially. The red ball should be placed higher than the goal so the red ball can fall down on the goal. The difference between y coordinate of the blue ball and y coordinate of the red ball must be greater than 0.8.\
        - Do not place a floor to support the red ball, blue ball, or goal, as a floor automatically accompanies the red ball and the goal according to the game rules.\
        - Do not observe or analyze the images or trajectories unless specifically asked to adjust object positions.\
        Coordinate System: \
            - X-axis: Values increase from right to left (left = 1, right = -1).\
            - Y-axis: Values increase from bottom to top (bottom = -1, top = 1). \
            Note: All objects must have unique x and y coordinates. No two objects can share the same x or y coordinate. X coordinate cannot exceed -0.6 or 0.6. Y coordinate cannot exceed -0.8 or 0.8.\
        Tasks: You must first say what the prompt {prompt} is asking, you must also tell me whether the input {ball_trajectory} is an empty string:\
            - If the prompt {prompt} clearly asks you to *design a new puzzle* and input {ball_trajectory} is empty, go to Part A.\
            - If the prompt {prompt} asks you to *propose a new position* for an object, or if the input {ball_trajectory} is not an empty string, go to Part B and do not go to Part A.\
        Part A:\
        1. If the prompt includes any tools (ramp, fixed hexagon, cannon), refer to rule of this tool in {tools} and you must describe the rule for this tool out. You must say 'do not design a coordinate for the tool'. \
        2. If the prompt includes any objects (a seperate floor, wall), refer to the rule of this object in {objects} and you must describe the rule for this object out. If the prompt does not mention any other objects, do not place any. You should not place floors support the red ball and the goal because they come up with a floor. \
        3. Identify all required objects (red ball, blue ball, goal) mentioned in the prompt and their exact coordinates, according to the general rules and your answers in the above questions. The red ball and the goal must not have the same x or y coordinate. All objects must have unique x and y coordinates.\
        4. Stop here and do not proceed to the next section. \
        Part B: choose one of the following two questions:\
        1. If the blue ball has not reached the red ball, answer all of the fours questions: \
            1) Analyze the blue ball's trajectory from {ball_trajectory} and the current puzzle image such that you must say all coordinates in the blue ball's trajectory. You must say the when the blue ball changes its direction such as from moving up to moving down.\
            2) Propose a new position for the red ball to be on one of the blue ball's trajectory to ensure a collision. Specify the new coordinates for the red ball. \
            3) Special Condition - Cannon:  In the images, if you see the blue ball was pushed upward by a cannon, you need to place the red ball on one of the blue ball's downward trajectory coordinates so the blue ball can land on the red ball after falling down.\
              Action: Adjust the red ball's position to a coordinate within this downward interval of the blue ball's trajectory. You must say the red ball's new coordinate.\
            4) Indicate whether the blue ball should move left or right to reach the red ball. Answer this question based on the ball's position in the beginning. If the red ball is on the right of the blue ball in the beginning, the blue ball needs to move to the right.\
            - Ensure no floors are placed for the red ball, blue ball, or goal since a floor automatically comes with the red ball and the goal according to the rules. \
            You must say you need to adjust the red ball's position to the position you propose.\
        2. If the blue ball has reached the red ball but the red ball has not reached the goal:\
            - Analyze the red ball's trajectory from {ball_trajectory} and the current puzzle image.\
            - Explain why the red ball has not reached the goal.\
            - Propose a new position for the goal along the red ball's trajectory to ensure it is reached. Specify the new coordinates for the goal.\
            - Indicate whether the red ball is moving left or right toward the goal.\
            You must say you need to adjust the goal's position to the position you propose.\
    By following these instructions, you will ensure the puzzle design aligns with the game's objectives and prompt requirements.",
            image_documents=image_documents,
        )


    return (response_1.text)


def main():
    prompt = "Design a 2D physics puzzle where the blue ball has to use a cannon to reach the red ball and push it to the goal."
    #prompt = " Design a 2D physics puzzle where the blue ball has to use a fixed hexagon to reach the red ball and push it to the goal."
    message = ''
    response = design(prompt, message)
    print(response)
   

if __name__ == "__main__":
    main()