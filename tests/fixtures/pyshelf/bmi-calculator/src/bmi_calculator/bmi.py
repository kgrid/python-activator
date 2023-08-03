

def calculate_bmi(input):
    scaling_factor = 703 if input['unit_system'] == "imperial" else 1
    return (input['weight'] / (input['height'] ** 2)) * scaling_factor


def get_bmi_category(input):
    bmi=input['bmi']
    if bmi < 18.5:
        return "Underweight"
    elif 18.5 <= bmi < 24.9:
        return "Normal weight"
    elif 25 <= bmi < 29.9:
        return "Overweight"
    else:
        return "Obese"