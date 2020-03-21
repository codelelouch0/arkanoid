"""
The template of the main script of the machine learning process
"""

import games.arkanoid.communication as comm
from games.arkanoid.communication import ( \
    SceneInfo, GameStatus, PlatformAction
)

def ml_loop():
    """
    The main loop of the machine learning process

    This loop is run in a separate process, and communicates with the game process.

    Note that the game process won't wait for the ml process to generate the
    GameInstruction. It is possible that the frame of the GameInstruction
    is behind of the current frame in the game process. Try to decrease the fps
    to avoid this situation.
    """

    # === Here is the execution order of the loop === #
    # 1. Put the initialization code here.
    ball_served = False

    # 2. Inform the game process that ml process is ready before start the loop.
    comm.ml_ready()
    ball_previous = [0,0]
    ball_present = [0,0]
    vector = [0,0]

    # 3. Start an endless loop.
    while True:
        # 3.1. Receive the scene information sent from the game process.
        scene_info = comm.get_scene_info()

        # 3.2. If the game is over or passed, the game process will reset
        #      the scene and wait for ml process doing resetting job.
        if scene_info.status == GameStatus.GAME_OVER or \
            scene_info.status == GameStatus.GAME_PASS:
            # Do some stuff if needed
            ball_served = False

            # 3.2.1. Inform the game process that ml process is ready
            comm.ml_ready()
            continue

        # 3.3. Put the code here to handle the scene information
        ball_previous = ball_present
        ball_present = scene_info.ball
        vector[0] = ball_present[0] - ball_previous[0]#x分量
        vector[1] = ball_present[1] - ball_previous[1]#y分量
        prediction = [0,0]
        prediction[0] = ball_present[0]
        prediction[1] = ball_present[1]
        platform_x = scene_info.platform[0] + 20
        # 3.4. Send the instruction for this frame to the game process
        if not ball_served:
            comm.send_instruction(scene_info.frame, PlatformAction.SERVE_TO_LEFT)
            ball_served = True
        else:
            if vector != [0,0]:
                while prediction[1]<=400:
                    if prediction[0]<=0 or prediction[0]>=200:
                        vector[0]*=-1
                        prediction[0]+=vector[0]
                    else:
                        prediction[0]+=vector[0]
                    if prediction[1]<=0:
                        vector[1]*=-1
                        prediction[1]+=vector[1]
                    else:
                        prediction[1]+=vector[1]
            if platform_x < prediction[0]:
                comm.send_instruction(scene_info.frame, PlatformAction.MOVE_RIGHT)
            elif platform_x > prediction[0]:
                comm.send_instruction(scene_info.frame, PlatformAction.MOVE_LEFT)
