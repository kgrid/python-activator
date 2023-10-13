from leftpad import left_pad
import ast


def welcome(user_input):
    #if isinstance(user_input, str):
        #user_input = ast.literal_eval(user_input)
    return "Welcome to Knowledge Grid," + left_pad(user_input['name'], user_input['spaces'])

def welcome_plain(user_input):
    user_input = user_input.decode('utf-8')
    user_input = ast.literal_eval(user_input)
    return     welcome(user_input)



#def welcome_xml